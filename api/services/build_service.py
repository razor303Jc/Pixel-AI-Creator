"""
Docker Build Service for Pixel AI Creator
Handles template substitution and Docker image building
"""

import os
import shutil
import tempfile
import logging
import json
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import asyncio
import aiofiles

logger = logging.getLogger(__name__)

class BuildService:
    def __init__(self, build_templates_dir: str, output_dir: str):
        self.build_templates_dir = Path(build_templates_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    async def build_assistant(self, build_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build a complete AI assistant Docker image"""
        try:
            build_id = build_config.get("build_id", f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            assistant_name = build_config["assistant_name"].lower().replace(" ", "-")
            
            logger.info(f"Starting build {build_id} for assistant: {assistant_name}")
            
            # Create temporary build directory
            with tempfile.TemporaryDirectory() as temp_dir:
                build_dir = Path(temp_dir) / f"{assistant_name}-{build_id}"
                build_dir.mkdir(exist_ok=True)
                
                # Step 1: Copy and process templates
                await self._process_templates(build_dir, build_config)
                
                # Step 2: Create Docker image
                image_tag = await self._build_docker_image(build_dir, assistant_name, build_id)
                
                # Step 3: Save build artifacts
                artifacts_dir = self.output_dir / build_id
                artifacts_dir.mkdir(exist_ok=True)
                
                # Copy processed files to artifacts
                shutil.copytree(build_dir, artifacts_dir / "source", dirs_exist_ok=True)
                
                # Save build metadata
                build_metadata = {
                    "build_id": build_id,
                    "assistant_name": assistant_name,
                    "image_tag": image_tag,
                    "build_time": datetime.now().isoformat(),
                    "config": build_config,
                    "status": "completed"
                }
                
                async with aiofiles.open(artifacts_dir / "build_metadata.json", "w") as f:
                    await f.write(json.dumps(build_metadata, indent=2))
                
                logger.info(f"Build {build_id} completed successfully")
                return build_metadata
                
        except Exception as e:
            logger.error(f"Build {build_id} failed: {str(e)}")
            error_metadata = {
                "build_id": build_id,
                "status": "failed",
                "error": str(e),
                "build_time": datetime.now().isoformat()
            }
            return error_metadata
    
    async def _process_templates(self, build_dir: Path, config: Dict[str, Any]):
        """Process template files with variable substitution"""
        logger.info("Processing templates...")
        
        # Copy all template files
        for template_file in self.build_templates_dir.rglob("*"):
            if template_file.is_file():
                relative_path = template_file.relative_to(self.build_templates_dir)
                target_path = build_dir / relative_path
                
                # Remove .template extension if present
                if target_path.name.endswith('.template'):
                    target_path = target_path.with_name(target_path.name[:-9])
                
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Process file content
                if template_file.suffix in ['.py', '.txt', '.md', '.yml', '.yaml', '.json', '.sh', '.template']:
                    await self._process_template_file(template_file, target_path, config)
                else:
                    # Copy binary files as-is
                    shutil.copy2(template_file, target_path)
        
        # Create additional required directories
        (build_dir / "static").mkdir(exist_ok=True)
        (build_dir / "logs").mkdir(exist_ok=True)
        
        logger.info("Template processing completed")
    
    async def _process_template_file(self, template_path: Path, target_path: Path, config: Dict[str, Any]):
        """Process a single template file"""
        async with aiofiles.open(template_path, "r", encoding="utf-8") as f:
            content = await f.read()
        
        # Prepare template variables
        template_vars = self._prepare_template_variables(config)
        
        # Replace template variables
        for key, value in template_vars.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        async with aiofiles.open(target_path, "w", encoding="utf-8") as f:
            await f.write(content)
    
    def _prepare_template_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare template variables from build configuration"""
        variables = {
            # Basic info
            "CHATBOT_NAME": config.get("assistant_name", "AI Assistant"),
            "CHATBOT_DESCRIPTION": config.get("description", "AI Assistant created with Pixel AI Creator"),
            "PROJECT_ID": config.get("project_id", 1),
            
            # Client info
            "CLIENT_ID": config.get("client_id", "null"),
            "CLIENT_NAME": config.get("client_name", "Default Client"),
            "CLIENT_COMPANY": config.get("client_company", "Pixel AI"),
            
            # Personality configuration
            "PERSONALITY_TONE": config.get("personality", {}).get("tone", "professional"),
            "PERSONALITY_STYLE": config.get("personality", {}).get("style", "helpful"),
            "SYSTEM_PROMPT": config.get("personality", {}).get("system_prompt", "You are a helpful AI assistant."),
            "TEMPERATURE": config.get("ai_config", {}).get("temperature", 0.7),
            "MAX_TOKENS": config.get("ai_config", {}).get("max_tokens", 1000),
            
            # Feature flags
            "ENABLE_FILE_UPLOAD": str(config.get("features", {}).get("file_upload", False)).lower(),
            "ENABLE_VOICE_CHAT": str(config.get("features", {}).get("voice_chat", False)).lower(),
            "ENABLE_CUSTOM_PROMPTS": str(config.get("features", {}).get("custom_prompts", True)).lower(),
            
            # Security
            "SECRET_KEY": config.get("secret_key", f"secret_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            
            # Template selection
            "TEMPLATE_TYPE": config.get("template", "basic"),
        }
        
        return variables
    
    async def _build_docker_image(self, build_dir: Path, assistant_name: str, build_id: str) -> str:
        """Build Docker image from processed templates"""
        image_tag = f"{assistant_name}:{build_id}"
        logger.info(f"Building Docker image: {image_tag}")
        
        try:
            # Build the Docker image
            cmd = [
                "docker", "build",
                "-t", image_tag,
                "-f", str(build_dir / "Dockerfile"),
                str(build_dir)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=build_dir
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = f"Docker build failed: {stderr.decode()}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            logger.info(f"Docker image {image_tag} built successfully")
            return image_tag
            
        except Exception as e:
            logger.error(f"Error building Docker image: {str(e)}")
            raise
    
    async def get_build_logs(self, build_id: str) -> Optional[str]:
        """Get build logs for a specific build"""
        build_dir = self.output_dir / build_id
        log_file = build_dir / "build.log"
        
        if log_file.exists():
            async with aiofiles.open(log_file, "r") as f:
                return await f.read()
        return None
    
    async def get_build_metadata(self, build_id: str) -> Optional[Dict[str, Any]]:
        """Get build metadata for a specific build"""
        build_dir = self.output_dir / build_id
        metadata_file = build_dir / "build_metadata.json"
        
        if metadata_file.exists():
            async with aiofiles.open(metadata_file, "r") as f:
                content = await f.read()
                return json.loads(content)
        return None
    
    async def list_builds(self) -> List[Dict[str, Any]]:
        """List all builds"""
        builds = []
        
        for build_dir in self.output_dir.iterdir():
            if build_dir.is_dir():
                metadata = await self.get_build_metadata(build_dir.name)
                if metadata:
                    builds.append(metadata)
        
        return sorted(builds, key=lambda x: x.get("build_time", ""), reverse=True)
    
    async def cleanup_build(self, build_id: str) -> bool:
        """Clean up build artifacts"""
        build_dir = self.output_dir / build_id
        
        if build_dir.exists():
            shutil.rmtree(build_dir)
            logger.info(f"Cleaned up build {build_id}")
            return True
        
        return False

# Build queue manager
class BuildQueueManager:
    def __init__(self, build_service: BuildService):
        self.build_service = build_service
        self.queue = asyncio.Queue()
        self.active_builds = {}
        self.build_history = []
        
    async def queue_build(self, build_config: Dict[str, Any]) -> str:
        """Queue a new build"""
        build_id = f"build_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        build_config["build_id"] = build_id
        
        await self.queue.put(build_config)
        self.active_builds[build_id] = {
            "status": "queued",
            "queued_at": datetime.now().isoformat(),
            "config": build_config
        }
        
        logger.info(f"Build {build_id} queued")
        return build_id
    
    async def process_builds(self):
        """Process builds from the queue"""
        while True:
            try:
                build_config = await self.queue.get()
                build_id = build_config["build_id"]
                
                # Update status
                self.active_builds[build_id]["status"] = "building"
                self.active_builds[build_id]["started_at"] = datetime.now().isoformat()
                
                # Process the build
                result = await self.build_service.build_assistant(build_config)
                
                # Update status
                self.active_builds[build_id]["status"] = result["status"]
                self.active_builds[build_id]["completed_at"] = datetime.now().isoformat()
                self.active_builds[build_id]["result"] = result
                
                # Move to history
                self.build_history.append(self.active_builds[build_id])
                del self.active_builds[build_id]
                
                logger.info(f"Build {build_id} completed with status: {result['status']}")
                
            except Exception as e:
                logger.error(f"Error processing build queue: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def get_build_status(self, build_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific build"""
        if build_id in self.active_builds:
            return self.active_builds[build_id]
        
        for build in self.build_history:
            if build["config"]["build_id"] == build_id:
                return build
        
        return None
    
    def get_all_builds(self) -> List[Dict[str, Any]]:
        """Get all builds (active and completed)"""
        all_builds = list(self.active_builds.values())
        all_builds.extend(self.build_history)
        return sorted(all_builds, key=lambda x: x.get("queued_at", ""), reverse=True)