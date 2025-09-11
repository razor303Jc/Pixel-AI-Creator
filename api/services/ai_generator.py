import asyncio
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from openai import AsyncOpenAI
from core.config import settings
from core.database import async_session, Project, Client, WebAnalysis
from sqlalchemy import select, update
import structlog

logger = structlog.get_logger()


class AIAssistantGenerator:
    """Service for generating custom AI assistants based on client analysis"""

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.templates_dir = Path(settings.templates_dir)
        self.output_dir = Path(settings.generated_bots_dir)

    async def generate_assistant(
        self, client_id: int, assistant_type: str, complexity: str
    ) -> Dict[str, Any]:
        """Generate a custom AI assistant for the client"""
        logger.info(
            "Starting AI assistant generation",
            client_id=client_id,
            type=assistant_type,
            complexity=complexity,
        )

        try:
            # Create project record
            project = await self._create_project_record(
                client_id, assistant_type, complexity
            )

            # Get client data and analysis
            client_data = await self._get_client_context(client_id)

            # Generate assistant components
            await self._update_project_status(project.id, "analyzing", 10)
            personality = await self._generate_personality(client_data, assistant_type)

            await self._update_project_status(project.id, "generating", 30)
            conversation_flows = await self._generate_conversation_flows(
                client_data, personality
            )

            await self._update_project_status(project.id, "coding", 50)
            code = await self._generate_code(
                client_data, personality, conversation_flows, assistant_type, complexity
            )

            await self._update_project_status(project.id, "configuring", 70)
            deployment_config = await self._generate_deployment_config(
                client_data, assistant_type
            )

            await self._update_project_status(project.id, "finalizing", 90)
            training_data = await self._generate_training_data(
                client_data, conversation_flows
            )

            # Save generated assistant
            await self._save_generated_assistant(
                project.id,
                {
                    "code": code,
                    "personality": personality,
                    "deployment_config": deployment_config,
                    "training_data": training_data,
                    "conversation_flows": conversation_flows,
                },
            )

            await self._update_project_status(project.id, "completed", 100)

            logger.info("AI assistant generation completed", project_id=project.id)
            return {"project_id": project.id, "status": "completed"}

        except Exception as e:
            logger.error("AI assistant generation failed", error=str(e))
            if "project" in locals():
                await self._update_project_status(project.id, "failed", 0)
            raise

    async def get_generation_status(self, project_id: int) -> Dict[str, Any]:
        """Get the status of AI assistant generation"""
        async with async_session() as session:
            result = await session.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()

            if not project:
                raise ValueError("Project not found")

            return {
                "project_id": project_id,
                "status": project.status,
                "progress": project.progress,
                "created_at": project.created_at,
                "completed_at": project.completed_at,
                "assistant_type": project.assistant_type,
                "complexity": project.complexity,
            }

    async def _create_project_record(
        self, client_id: int, assistant_type: str, complexity: str
    ) -> Project:
        """Create a new project record"""
        async with async_session() as session:
            project = Project(
                client_id=client_id,
                name=f"{assistant_type.title()} Assistant",
                assistant_type=assistant_type,
                complexity=complexity,
                status="pending",
                progress=0,
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            return project

    async def _get_client_context(self, client_id: int) -> Dict[str, Any]:
        """Get all client data and analysis for context"""
        async with async_session() as session:
            # Get client info
            client_result = await session.execute(
                select(Client).where(Client.id == client_id)
            )
            client = client_result.scalar_one_or_none()

            # Get web analysis
            analysis_result = await session.execute(
                select(WebAnalysis).where(WebAnalysis.client_id == client_id)
            )
            analyses = analysis_result.scalars().all()

            return {
                "client": {
                    "name": client.name,
                    "company": client.company,
                    "industry": client.industry,
                    "website": client.website,
                    "description": client.description,
                    "website_analysis": client.website_analysis,
                    "social_media_analysis": client.social_media_analysis,
                },
                "analyses": [
                    {
                        "type": analysis.analysis_type,
                        "platform": analysis.platform,
                        "business_insights": analysis.business_insights,
                        "personality_traits": analysis.personality_traits,
                        "target_audience": analysis.target_audience,
                    }
                    for analysis in analyses
                ],
            }

    async def _generate_personality(
        self, client_data: Dict[str, Any], assistant_type: str
    ) -> Dict[str, Any]:
        """Generate AI assistant personality based on client analysis"""
        prompt = f"""
        Based on the following client data, generate a detailed personality profile for their AI {assistant_type}:

        Client Data: {json.dumps(client_data, indent=2)}

        Generate a personality that includes:
        1. Communication style (formal/casual, friendly/professional, etc.)
        2. Tone of voice
        3. Key personality traits
        4. Response patterns
        5. Conversation style
        6. Brand alignment
        7. Do's and Don'ts

        Return as JSON with these exact keys: communication_style, tone, traits, response_patterns, conversation_style, brand_alignment, guidelines
        """

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI personality designer. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        return json.loads(response.choices[0].message.content)

    async def _generate_conversation_flows(
        self, client_data: Dict[str, Any], personality: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate conversation flows and scenarios"""
        prompt = f"""
        Create conversation flows for this AI assistant:

        Client Data: {json.dumps(client_data, indent=2)}
        Personality: {json.dumps(personality, indent=2)}

        Generate:
        1. Welcome message and introduction
        2. Main conversation flows (at least 5)
        3. FAQ responses (at least 10)
        4. Escalation procedures
        5. Fallback responses
        6. Business-specific scenarios

        Return as JSON with keys: welcome_message, main_flows, faqs, escalation, fallbacks, business_scenarios
        """

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert conversational AI designer. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )

        return json.loads(response.choices[0].message.content)

    async def _generate_code(
        self,
        client_data: Dict[str, Any],
        personality: Dict[str, Any],
        flows: Dict[str, Any],
        assistant_type: str,
        complexity: str,
    ) -> str:
        """Generate the actual AI assistant code"""

        if assistant_type == "chatbot":
            return await self._generate_chatbot_code(
                client_data, personality, flows, complexity
            )
        elif assistant_type == "voice_assistant":
            return await self._generate_voice_assistant_code(
                client_data, personality, flows, complexity
            )
        elif assistant_type == "automation_bot":
            return await self._generate_automation_bot_code(
                client_data, personality, flows, complexity
            )
        else:
            raise ValueError(f"Unknown assistant type: {assistant_type}")

    async def _generate_chatbot_code(
        self,
        client_data: Dict[str, Any],
        personality: Dict[str, Any],
        flows: Dict[str, Any],
        complexity: str,
    ) -> str:
        """Generate chatbot implementation code"""

        template = f"""
# Generated AI Chatbot for {client_data['client']['company']}
# Generated on: {datetime.now().isoformat()}

from typing import Dict, Any, List
import openai
import json

class {client_data['client']['company'].replace(' ', '')}Chatbot:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.personality = {json.dumps(personality, indent=8)}
        self.conversation_flows = {json.dumps(flows, indent=8)}
        self.context = []
        
    async def respond(self, message: str, user_context: Dict[str, Any] = None) -> str:
        \"\"\"Generate response to user message\"\"\"
        
        # Build context
        system_prompt = self._build_system_prompt()
        
        # Add user message to context
        self.context.append({{"role": "user", "content": message}})
        
        # Generate response
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {{"role": "system", "content": system_prompt}},
                *self.context[-10:]  # Keep last 10 messages for context
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        assistant_response = response.choices[0].message.content
        self.context.append({{"role": "assistant", "content": assistant_response}})
        
        return assistant_response
    
    def _build_system_prompt(self) -> str:
        \"\"\"Build system prompt from personality and business context\"\"\"
        return f\"\"\"
        You are an AI assistant for {client_data['client']['company']}.
        
        Company: {client_data['client']['company']}
        Industry: {client_data['client']['industry']}
        Website: {client_data['client']['website']}
        
        Personality:
        - Communication Style: {personality.get('communication_style', 'Professional')}
        - Tone: {personality.get('tone', 'Friendly and helpful')}
        - Key Traits: {', '.join(personality.get('traits', []))}
        
        Your role is to:
        1. Help customers with inquiries about our business
        2. Provide information about our products/services
        3. Guide users through our processes
        4. Escalate complex issues to human staff when needed
        
        Always maintain the specified personality and tone.
        Use the conversation flows as guidance for common scenarios.
        \"\"\"
        
    def get_welcome_message(self) -> str:
        \"\"\"Return welcome message\"\"\"
        return self.conversation_flows.get('welcome_message', 
            f"Hello! I'm the AI assistant for {client_data['client']['company']}. How can I help you today?")
    
    def reset_context(self):
        \"\"\"Reset conversation context\"\"\"
        self.context = []

# Example usage:
# chatbot = {client_data['client']['company'].replace(' ', '')}Chatbot(api_key="your-api-key")
# response = await chatbot.respond("Hello, I need help with...")
"""

        return template

    async def _generate_deployment_config(
        self, client_data: Dict[str, Any], assistant_type: str
    ) -> Dict[str, Any]:
        """Generate deployment configuration"""

        company_name = client_data["client"]["company"].replace(" ", "").lower()

        return {
            "container_name": f"{company_name}-ai-assistant",
            "image_name": f"pixel-ai/{company_name}-{assistant_type}",
            "environment_variables": {
                "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                "COMPANY_NAME": client_data["client"]["company"],
                "WEBSITE_URL": client_data["client"]["website"],
                "ASSISTANT_TYPE": assistant_type,
            },
            "docker_compose": {
                "version": "3.8",
                "services": {
                    f"{company_name}-assistant": {
                        "build": ".",
                        "ports": ["8080:8080"],
                        "environment": [
                            "OPENAI_API_KEY=${OPENAI_API_KEY}",
                            f"COMPANY_NAME={client_data['client']['company']}",
                            f"WEBSITE_URL={client_data['client']['website']}",
                        ],
                        "restart": "unless-stopped",
                    }
                },
            },
            "deployment_instructions": [
                "1. Build the Docker image",
                "2. Set environment variables",
                "3. Deploy to cloud platform",
                "4. Configure domain and SSL",
                "5. Test all conversation flows",
                "6. Monitor performance and usage",
            ],
        }

    async def _generate_training_data(
        self, client_data: Dict[str, Any], flows: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate training data for fine-tuning"""

        return {
            "faq_pairs": flows.get("faqs", []),
            "business_context": {
                "company": client_data["client"]["company"],
                "industry": client_data["client"]["industry"],
                "services": "Extracted from website analysis",
                "target_customers": "Based on analysis",
            },
            "conversation_examples": [
                {
                    "input": "What are your business hours?",
                    "output": "Our business hours are Monday-Friday 9AM-6PM. We're closed on weekends.",
                },
                {
                    "input": "How can I contact you?",
                    "output": f"You can reach us through our website at {client_data['client']['website']} or email us directly.",
                },
            ],
            "personality_examples": [
                {
                    "scenario": "Customer complaint",
                    "response_style": "Empathetic, solution-focused, professional",
                },
                {
                    "scenario": "Product inquiry",
                    "response_style": "Informative, helpful, encouraging",
                },
            ],
        }

    async def _save_generated_assistant(
        self, project_id: int, generated_content: Dict[str, Any]
    ):
        """Save the generated assistant to database and files"""

        # Save to database
        async with async_session() as session:
            stmt = (
                update(Project)
                .where(Project.id == project_id)
                .values(
                    generated_code=generated_content["code"],
                    deployment_config=generated_content["deployment_config"],
                    personality_config=generated_content["personality"],
                    training_data=generated_content["training_data"],
                    business_rules=generated_content["conversation_flows"],
                )
            )
            await session.execute(stmt)
            await session.commit()

        # Save to files
        project_dir = self.output_dir / f"project_{project_id}"
        project_dir.mkdir(parents=True, exist_ok=True)

        # Save code
        with open(project_dir / "assistant.py", "w") as f:
            f.write(generated_content["code"])

        # Save configurations
        with open(project_dir / "config.json", "w") as f:
            json.dump(
                {
                    "personality": generated_content["personality"],
                    "deployment": generated_content["deployment_config"],
                    "training_data": generated_content["training_data"],
                    "conversation_flows": generated_content["conversation_flows"],
                },
                f,
                indent=2,
            )

        # Save Docker files
        await self._generate_docker_files(
            project_dir, generated_content["deployment_config"]
        )

    async def _generate_docker_files(
        self, project_dir: Path, deployment_config: Dict[str, Any]
    ):
        """Generate Docker files for deployment"""

        # Dockerfile
        dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
"""

        with open(project_dir / "Dockerfile", "w") as f:
            f.write(dockerfile_content)

        # requirements.txt
        requirements_content = """
openai==1.3.7
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
"""

        with open(project_dir / "requirements.txt", "w") as f:
            f.write(requirements_content)

        # docker-compose.yml
        with open(project_dir / "docker-compose.yml", "w") as f:
            json.dump(deployment_config["docker_compose"], f, indent=2)

    async def _update_project_status(self, project_id: int, status: str, progress: int):
        """Update project status and progress"""
        async with async_session() as session:
            stmt = (
                update(Project)
                .where(Project.id == project_id)
                .values(
                    status=status,
                    progress=progress,
                    completed_at=datetime.utcnow() if status == "completed" else None,
                )
            )
            await session.execute(stmt)
            await session.commit()

    async def _generate_voice_assistant_code(
        self,
        client_data: Dict[str, Any],
        personality: Dict[str, Any],
        flows: Dict[str, Any],
        complexity: str,
    ) -> str:
        """Generate voice assistant code (placeholder)"""
        return f"# Voice Assistant for {client_data['client']['company']} - Coming Soon"

    async def _generate_automation_bot_code(
        self,
        client_data: Dict[str, Any],
        personality: Dict[str, Any],
        flows: Dict[str, Any],
        complexity: str,
    ) -> str:
        """Generate automation bot code (placeholder)"""
        return f"# Automation Bot for {client_data['client']['company']} - Coming Soon"
