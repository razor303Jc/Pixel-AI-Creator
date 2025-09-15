"""
Pixel-AI-Creator Build Queue System
Docker-in-Docker Implementation for Bot Building

This system handles the queuing and building of chatbot projects using
Docker containers. Each bot build is isolated in its own Docker container
with full dependency management.
"""

import asyncio
import docker
import json
import logging
import os
import tempfile
import uuid
from pathlib import Path
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Database imports
from sqlalchemy import update
from core.database import get_db, Project

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BuildStatus(Enum):
    QUEUED = "queued"
    BUILDING = "building"
    TESTING = "testing"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BuildJob:
    """Build job configuration"""
    id: str
    project_id: int
    user_id: int
    chatbot_config: Dict[str, Any]
    build_spec: Dict[str, Any]
    status: BuildStatus = BuildStatus.QUEUED
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    error_message: str = None
    build_logs: List[str] = None
    container_id: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.build_logs is None:
            self.build_logs = []


class DockerBuildManager:
    """Docker-in-Docker build manager for chatbot projects"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.build_queue: asyncio.Queue = asyncio.Queue()
        self.active_builds: Dict[str, BuildJob] = {}
        self.completed_builds: Dict[str, BuildJob] = {}
        self.max_concurrent_builds = int(os.getenv('MAX_CONCURRENT_BUILDS', '3'))
        self.base_image = os.getenv('CHATBOT_BASE_IMAGE', 'python:3.11-slim')
        self.network_name = os.getenv('DOCKER_NETWORK', 'pixel-ai-network')
        
        # Build configuration paths
        self.workspace_dir = Path(os.getenv("BUILD_WORKSPACE_DIR", "../generated-bots"))
        self.template_dir = Path(os.getenv("BUILD_TEMPLATE_DIR", "../build-templates"))
        
    async def queue_build(self, project_id: int, user_id: int, chatbot_config: Dict[str, Any]) -> str:
        """Queue a new build job"""
        build_id = str(uuid.uuid4())
        
        # Create build specification based on chatbot config
        build_spec = self._create_build_spec(chatbot_config)
        
        build_job = BuildJob(
            id=build_id,
            project_id=project_id,
            user_id=user_id,
            chatbot_config=chatbot_config,
            build_spec=build_spec
        )
        
        await self.build_queue.put(build_job)
        logger.info(f"Build job {build_id} queued for project {project_id}")
        
        return build_id
    
    def _create_build_spec(self, chatbot_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Docker build specification based on chatbot configuration"""
        personality = chatbot_config.get('personality_config', {})
        template = personality.get('template', 'general-basic')
        complexity = chatbot_config.get('complexity', 'basic')
        
        # Map templates to Docker build configurations
        template_configs = {
            'general-basic': {
                'dependencies': ['openai', 'fastapi', 'uvicorn', 'python-multipart'],
                'model': 'gpt-3.5-turbo',
                'features': ['basic_chat', 'context_memory']
            },
            'customer-support': {
                'dependencies': ['openai', 'fastapi', 'uvicorn', 'sqlalchemy', 'redis'],
                'model': 'gpt-4',
                'features': ['ticket_management', 'knowledge_base', 'escalation']
            },
            'sales-assistant': {
                'dependencies': ['openai', 'fastapi', 'uvicorn', 'crm-integration', 'analytics'],
                'model': 'gpt-4',
                'features': ['lead_qualification', 'pipeline_management', 'reporting']
            },
            'project-manager': {
                'dependencies': ['openai', 'fastapi', 'uvicorn', 'jira-api', 'slack-sdk'],
                'model': 'gpt-4',
                'features': ['task_management', 'team_coordination', 'progress_tracking']
            }
        }
        
        config = template_configs.get(template, template_configs['general-basic'])
        
        return {
            'template': template,
            'complexity': complexity,
            'base_image': self.base_image,
            'dependencies': config['dependencies'],
            'model': config['model'],
            'features': config['features'],
            'environment': {
                'CHATBOT_NAME': chatbot_config.get('name', 'My Chatbot'),
                'CHATBOT_PERSONALITY': personality.get('personality', 'helpful'),
                'CHATBOT_INSTRUCTIONS': chatbot_config.get('description', ''),
                'MODEL_NAME': config['model'],
                'MAX_TOKENS': '2048',
                'TEMPERATURE': '0.7'
            },
            'ports': {
                'api': 8000,
                'health': 8001
            },
            'resources': {
                'memory': '1g' if complexity == 'basic' else '2g',
                'cpu': '0.5' if complexity == 'basic' else '1.0'
            }
        }
    
    async def start_build_workers(self):
        """Start background workers to process build queue"""
        workers = []
        for i in range(self.max_concurrent_builds):
            worker = asyncio.create_task(self._build_worker(f"worker-{i}"))
            workers.append(worker)
        
        logger.info(f"Started {self.max_concurrent_builds} build workers")
        return workers
    
    async def _build_worker(self, worker_name: str):
        """Background worker to process build jobs"""
        logger.info(f"Build worker {worker_name} started")
        
        while True:
            try:
                # Get next build job from queue
                build_job = await self.build_queue.get()
                self.active_builds[build_job.id] = build_job
                
                logger.info(f"Worker {worker_name} processing build {build_job.id}")
                
                # Update job status
                build_job.status = BuildStatus.BUILDING
                build_job.started_at = datetime.utcnow()
                await self._update_project_status(build_job.project_id, "building", 10)
                
                # Execute build process
                success = await self._execute_build(build_job)
                
                if success:
                    build_job.status = BuildStatus.COMPLETED
                    build_job.completed_at = datetime.utcnow()
                    await self._update_project_status(build_job.project_id, "completed", 100)
                    logger.info(f"Build {build_job.id} completed successfully")
                else:
                    build_job.status = BuildStatus.FAILED
                    build_job.completed_at = datetime.utcnow()
                    await self._update_project_status(build_job.project_id, "failed", 0)
                    logger.error(f"Build {build_job.id} failed: {build_job.error_message}")
                
                # Move to completed builds
                self.completed_builds[build_job.id] = build_job
                del self.active_builds[build_job.id]
                
                # Mark task as done
                self.build_queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {str(e)}")
                if 'build_job' in locals():
                    build_job.status = BuildStatus.FAILED
                    build_job.error_message = str(e)
                    build_job.completed_at = datetime.utcnow()
                    await self._update_project_status(build_job.project_id, "failed", 0)
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _execute_build(self, build_job: BuildJob) -> bool:
        """Execute the Docker build process"""
        try:
            # Create temporary build context
            with tempfile.TemporaryDirectory() as temp_dir:
                build_context = Path(temp_dir)
                
                # Generate build files
                await self._generate_build_files(build_job, build_context)
                
                # Update progress
                await self._update_project_status(build_job.project_id, "building", 30)
                
                # Build Docker image
                image_tag = f"pixel-ai-chatbot-{build_job.project_id}:{build_job.id[:8]}"
                image = await self._build_docker_image(build_job, build_context, image_tag)
                
                if not image:
                    return False
                
                # Update progress
                await self._update_project_status(build_job.project_id, "testing", 60)
                
                # Test the built chatbot
                test_success = await self._test_chatbot(build_job, image_tag)
                
                if not test_success:
                    build_job.error_message = "Chatbot tests failed"
                    return False
                
                # Update progress
                await self._update_project_status(build_job.project_id, "deploying", 80)
                
                # Deploy the chatbot
                deploy_success = await self._deploy_chatbot(build_job, image_tag)
                
                return deploy_success
                
        except Exception as e:
            build_job.error_message = str(e)
            build_job.build_logs.append(f"Build error: {str(e)}")
            return False
    
    async def _generate_build_files(self, build_job: BuildJob, build_context: Path):
        """Generate all necessary build files"""
        spec = build_job.build_spec
        config = build_job.chatbot_config
        
        # Generate Dockerfile
        dockerfile_content = f"""
FROM {spec['base_image']}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
{self._generate_env_vars(spec['environment'])}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8001/health || exit 1

# Expose ports
EXPOSE {spec['ports']['api']} {spec['ports']['health']}

# Start the application
CMD ["python", "main.py"]
"""
        
        (build_context / "Dockerfile").write_text(dockerfile_content)
        
        # Generate requirements.txt
        requirements = "\\n".join(spec['dependencies'])
        (build_context / "requirements.txt").write_text(requirements)
        
        # Generate main.py
        main_py_content = self._generate_main_py(build_job)
        (build_context / "main.py").write_text(main_py_content)
        
        # Generate configuration file
        config_json = json.dumps(config, indent=2)
        (build_context / "config.json").write_text(config_json)
        
        build_job.build_logs.append("Generated build files successfully")
    
    def _generate_env_vars(self, env_vars: Dict[str, str]) -> str:
        """Generate ENV statements for Dockerfile"""
        return "\\n".join([f"ENV {key}={value}" for key, value in env_vars.items()])
    
    def _generate_main_py(self, build_job: BuildJob) -> str:
        """Generate the main application file"""
        spec = build_job.build_spec
        
        return f'''
import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

# Load configuration
with open("config.json", "r") as f:
    config = json.load(f)

app = FastAPI(title=config["name"], version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Main chat endpoint"""
    try:
        response = openai.ChatCompletion.create(
            model="{spec['model']}",
            messages=[
                {{"role": "system", "content": "{build_job.chatbot_config.get('description', 'You are a helpful AI assistant.')}"}},
                {{"role": "user", "content": message.message}}
            ],
            max_tokens=int(os.getenv("MAX_TOKENS", "2048")),
            temperature=float(os.getenv("TEMPERATURE", "0.7"))
        )
        
        bot_response = response.choices[0].message.content
        
        return ChatResponse(
            response=bot_response,
            session_id=message.session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{"status": "healthy", "chatbot": config["name"]}}

@app.get("/info")
async def chatbot_info():
    """Get chatbot information"""
    return {{
        "name": config["name"],
        "description": config.get("description", ""),
        "personality": config.get("personality_config", {{}}).get("personality", "helpful"),
        "features": {spec['features']},
        "status": "running"
    }}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port={spec['ports']['api']},
        reload=False
    )
'''
    
    async def _build_docker_image(self, build_job: BuildJob, build_context: Path, image_tag: str):
        """Build Docker image"""
        try:
            build_job.build_logs.append(f"Building Docker image: {image_tag}")
            
            # Build image using Docker API
            image, build_logs = self.docker_client.images.build(
                path=str(build_context),
                tag=image_tag,
                rm=True,
                pull=True
            )
            
            # Capture build logs
            for log in build_logs:
                if 'stream' in log:
                    build_job.build_logs.append(log['stream'].strip())
            
            build_job.build_logs.append(f"Image built successfully: {image.id}")
            return image
            
        except docker.errors.BuildError as e:
            build_job.error_message = f"Docker build failed: {str(e)}"
            for log in e.build_log:
                if 'stream' in log:
                    build_job.build_logs.append(log['stream'].strip())
            return None
        except Exception as e:
            build_job.error_message = f"Build error: {str(e)}"
            return None
    
    async def _test_chatbot(self, build_job: BuildJob, image_tag: str) -> bool:
        """Test the built chatbot"""
        try:
            build_job.build_logs.append("Starting chatbot tests...")
            
            # Start test container
            container = self.docker_client.containers.run(
                image_tag,
                detach=True,
                ports={'8000/tcp': None, '8001/tcp': None},
                network=self.network_name,
                name=f"test-{build_job.id}"
            )
            
            build_job.container_id = container.id
            
            # Wait for container to start
            await asyncio.sleep(10)
            
            # Get container port mappings
            container.reload()
            ports = container.attrs['NetworkSettings']['Ports']
            api_port = ports['8000/tcp'][0]['HostPort']
            health_port = ports['8001/tcp'][0]['HostPort']
            
            # Test health endpoint
            import aiohttp
            async with aiohttp.ClientSession() as session:
                health_url = f"http://localhost:{health_port}/health"
                async with session.get(health_url) as response:
                    if response.status != 200:
                        raise Exception("Health check failed")
                
                # Test chat endpoint
                chat_url = f"http://localhost:{api_port}/chat"
                test_message = {"message": "Hello, this is a test message"}
                async with session.post(chat_url, json=test_message) as response:
                    if response.status != 200:
                        raise Exception("Chat endpoint test failed")
                    
                    result = await response.json()
                    if not result.get('response'):
                        raise Exception("No response from chatbot")
            
            build_job.build_logs.append("All tests passed successfully")
            
            # Stop test container
            container.stop()
            container.remove()
            
            return True
            
        except Exception as e:
            build_job.build_logs.append(f"Test failed: {str(e)}")
            # Clean up test container if it exists
            if build_job.container_id:
                try:
                    container = self.docker_client.containers.get(build_job.container_id)
                    container.stop()
                    container.remove()
                except:
                    pass
            return False
    
    async def _deploy_chatbot(self, build_job: BuildJob, image_tag: str) -> bool:
        """Deploy the chatbot to production"""
        try:
            build_job.build_logs.append("Deploying chatbot...")
            
            # Stop existing container if it exists
            container_name = f"chatbot-{build_job.project_id}"
            try:
                existing = self.docker_client.containers.get(container_name)
                existing.stop()
                existing.remove()
                build_job.build_logs.append("Stopped existing container")
            except docker.errors.NotFound:
                pass
            
            # Start production container
            container = self.docker_client.containers.run(
                image_tag,
                detach=True,
                ports={'8000/tcp': None},
                network=self.network_name,
                name=container_name,
                restart_policy={"Name": "unless-stopped"},
                environment={
                    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
                    'ENVIRONMENT': 'production'
                }
            )
            
            build_job.container_id = container.id
            
            # Get assigned port
            container.reload()
            ports = container.attrs['NetworkSettings']['Ports']
            api_port = ports['8000/tcp'][0]['HostPort']
            
            # Update database with deployment info
            await self._update_project_deployment(
                build_job.project_id, 
                container_name, 
                api_port,
                f"http://localhost:{api_port}"
            )
            
            build_job.build_logs.append(f"Chatbot deployed successfully on port {api_port}")
            return True
            
        except Exception as e:
            build_job.build_logs.append(f"Deployment failed: {str(e)}")
            return False
    
    async def _update_project_status(self, project_id: int, status: str, progress: int):
        """Update project status in database"""
        try:
            async with get_db() as db:
                await db.execute(
                    update(Project)
                    .where(Project.id == project_id)
                    .values(status=status, progress=progress, updated_at=datetime.utcnow())
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to update project status: {str(e)}")
    
    async def _update_project_deployment(self, project_id: int, container_name: str, port: str, url: str):
        """Update project with deployment information"""
        try:
            deployment_info = {
                "container_name": container_name,
                "port": port,
                "url": url,
                "deployed_at": datetime.utcnow().isoformat()
            }
            
            async with get_db() as db:
                await db.execute(
                    update(Project)
                    .where(Project.id == project_id)
                    .values(
                        deployment_info=deployment_info,
                        updated_at=datetime.utcnow()
                    )
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to update deployment info: {str(e)}")
    
    def get_build_status(self, build_id: str) -> Optional[Dict[str, Any]]:
        """Get build status by build ID"""
        if build_id in self.active_builds:
            return asdict(self.active_builds[build_id])
        elif build_id in self.completed_builds:
            return asdict(self.completed_builds[build_id])
        return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        return {
            "queue_size": self.build_queue.qsize(),
            "active_builds": len(self.active_builds),
            "completed_builds": len(self.completed_builds),
            "max_concurrent": self.max_concurrent_builds
        }

# Global build manager instance
build_manager = DockerBuildManager()