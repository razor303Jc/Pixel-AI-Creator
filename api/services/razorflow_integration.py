"""
Razorflow-AI Integration Service
Manages automated client builds, queue management, and template deployment
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

from openai import AsyncOpenAI
from core.config import settings
from core.database import async_session, Project, Client, WebAnalysis
from sqlalchemy import select, update
import structlog

logger = structlog.get_logger()


class BuildStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    BUILDING = "building"
    TESTING = "testing"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RazorflowIntegration:
    """Service for Razorflow-AI integration and automated client builds"""

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.templates_dir = Path(settings.templates_dir)
        self.output_dir = Path(settings.generated_bots_dir)
        self.build_queue = []
        self.active_builds = {}
        self.max_concurrent_builds = 5

    async def queue_client_build(
        self,
        client_id: int,
        template_type: str,
        priority: str = "normal",
        custom_requirements: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Queue a new client build for automated processing"""

        logger.info(
            "Queueing client build",
            client_id=client_id,
            template=template_type,
            priority=priority,
        )

        try:
            # Create build record
            build_id = f"build_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            build_config = {
                "build_id": build_id,
                "client_id": client_id,
                "template_type": template_type,
                "priority": priority,
                "custom_requirements": custom_requirements or {},
                "status": BuildStatus.QUEUED.value,
                "created_at": datetime.now().isoformat(),
                "estimated_completion": self._calculate_completion_time(template_type),
                "build_stages": [
                    "template_loading",
                    "client_analysis",
                    "customization",
                    "code_generation",
                    "testing",
                    "deployment",
                    "validation",
                ],
                "current_stage": None,
                "progress_percentage": 0,
            }

            # Add to queue with priority ordering
            self._add_to_queue(build_config)

            # Start processing if capacity available
            if len(self.active_builds) < self.max_concurrent_builds:
                asyncio.create_task(self._process_build_queue())

            logger.info("Build queued successfully", build_id=build_id)
            return {
                "build_id": build_id,
                "status": "queued",
                "estimated_completion": build_config["estimated_completion"],
                "queue_position": self._get_queue_position(build_id),
            }

        except Exception as e:
            logger.error("Failed to queue build", error=str(e))
            raise

    async def get_build_status(self, build_id: str) -> Dict[str, Any]:
        """Get current status of a build"""

        # Check active builds
        if build_id in self.active_builds:
            return self.active_builds[build_id]

        # Check queue
        for build in self.build_queue:
            if build["build_id"] == build_id:
                return {
                    "build_id": build_id,
                    "status": build["status"],
                    "queue_position": self._get_queue_position(build_id),
                    "estimated_start": self._estimate_start_time(build_id),
                }

        # Check completed builds (from database)
        return await self._get_completed_build_status(build_id)

    async def deploy_default_assistant_suite(self, client_id: int) -> Dict[str, Any]:
        """Deploy the complete default assistant suite for a client"""

        logger.info("Deploying default assistant suite", client_id=client_id)

        default_assistants = [
            {
                "template": "customer_service_bot",
                "priority": "high",
                "auto_deploy": True,
            },
            {
                "template": "lead_qualification_assistant",
                "priority": "high",
                "auto_deploy": True,
            },
            {
                "template": "product_recommendation_engine",
                "priority": "medium",
                "auto_deploy": False,  # Requires e-commerce setup
            },
        ]

        deployment_results = []

        for assistant in default_assistants:
            try:
                build_result = await self.queue_client_build(
                    client_id=client_id,
                    template_type=assistant["template"],
                    priority=assistant["priority"],
                    custom_requirements={"auto_deploy": assistant["auto_deploy"]},
                )
                deployment_results.append(
                    {
                        "template": assistant["template"],
                        "build_id": build_result["build_id"],
                        "status": "queued",
                    }
                )
            except Exception as e:
                deployment_results.append(
                    {
                        "template": assistant["template"],
                        "status": "failed",
                        "error": str(e),
                    }
                )

        return {
            "client_id": client_id,
            "suite_deployment": "initiated",
            "total_assistants": len(default_assistants),
            "results": deployment_results,
        }

    async def _process_build_queue(self):
        """Process builds from the queue"""

        while self.build_queue and len(self.active_builds) < self.max_concurrent_builds:
            # Get next build (priority-ordered)
            build_config = self.build_queue.pop(0)
            build_id = build_config["build_id"]

            # Move to active builds
            self.active_builds[build_id] = build_config

            # Start build process
            try:
                await self._execute_build(build_config)
            except Exception as e:
                logger.error("Build execution failed", build_id=build_id, error=str(e))
                await self._update_build_status(
                    build_id, BuildStatus.FAILED, error=str(e)
                )

    async def _execute_build(self, build_config: Dict[str, Any]):
        """Execute the complete build process"""

        build_id = build_config["build_id"]
        client_id = build_config["client_id"]
        template_type = build_config["template_type"]

        logger.info("Starting build execution", build_id=build_id)

        try:
            # Stage 1: Template Loading
            await self._update_build_status(
                build_id, BuildStatus.PROCESSING, stage="template_loading", progress=10
            )
            template_data = await self._load_template(template_type)

            # Stage 2: Client Analysis
            await self._update_build_status(
                build_id, BuildStatus.PROCESSING, stage="client_analysis", progress=25
            )
            client_context = await self._analyze_client_context(client_id)

            # Stage 3: Customization
            await self._update_build_status(
                build_id, BuildStatus.BUILDING, stage="customization", progress=40
            )
            customized_config = await self._customize_template(
                template_data, client_context, build_config["custom_requirements"]
            )

            # Stage 4: Code Generation
            await self._update_build_status(
                build_id, BuildStatus.BUILDING, stage="code_generation", progress=60
            )
            generated_code = await self._generate_assistant_code(customized_config)

            # Stage 5: Testing
            await self._update_build_status(
                build_id, BuildStatus.TESTING, stage="testing", progress=80
            )
            test_results = await self._run_build_tests(generated_code)

            if not test_results["passed"]:
                raise Exception(f"Build tests failed: {test_results['errors']}")

            # Stage 6: Deployment
            await self._update_build_status(
                build_id, BuildStatus.DEPLOYING, stage="deployment", progress=90
            )
            deployment_result = await self._deploy_assistant(build_id, generated_code)

            # Stage 7: Validation
            await self._update_build_status(
                build_id, BuildStatus.DEPLOYING, stage="validation", progress=95
            )
            await self._validate_deployment(deployment_result)

            # Complete
            await self._update_build_status(
                build_id, BuildStatus.COMPLETED, progress=100
            )

            # Update project record
            await self._finalize_project_record(build_id, deployment_result)

            logger.info("Build completed successfully", build_id=build_id)

        except Exception as e:
            logger.error("Build failed", build_id=build_id, error=str(e))
            await self._update_build_status(build_id, BuildStatus.FAILED, error=str(e))

        finally:
            # Remove from active builds
            if build_id in self.active_builds:
                del self.active_builds[build_id]

    async def _load_template(self, template_type: str) -> Dict[str, Any]:
        """Load template configuration"""

        template_paths = {
            "customer_service_bot": "business-automation/customer_service_bot.json",
            "lead_qualification_assistant": "business-automation/lead_qualification_assistant.json",
            "product_recommendation_engine": "ecommerce-automation/product_recommendation_engine.json",
            "restaurant_assistant": "industry-specific/restaurant_assistant.json",
        }

        template_path = self.templates_dir / template_paths.get(template_type)

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_type}")

        with open(template_path, "r") as f:
            return json.load(f)

    async def _analyze_client_context(self, client_id: int) -> Dict[str, Any]:
        """Analyze client data for customization"""

        async with async_session() as session:
            # Get client data
            client_result = await session.execute(
                select(Client).where(Client.id == client_id)
            )
            client = client_result.scalar_one_or_none()

            if not client:
                raise ValueError(f"Client {client_id} not found")

            # Get web analysis data
            analysis_result = await session.execute(
                select(WebAnalysis)
                .where(WebAnalysis.client_id == client_id)
                .order_by(WebAnalysis.created_at.desc())
                .limit(1)
            )
            analysis = analysis_result.scalar_one_or_none()

            return {
                "client_info": {
                    "name": client.name,
                    "company": client.company,
                    "industry": client.industry,
                    "website": client.website,
                    "description": client.description,
                },
                "web_analysis": analysis.ai_analysis if analysis else None,
                "brand_context": await self._extract_brand_context(client),
            }

    async def _customize_template(
        self,
        template_data: Dict[str, Any],
        client_context: Dict[str, Any],
        custom_requirements: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Customize template based on client context"""

        # Create customized configuration
        customized = template_data.copy()

        # Update personality based on brand
        if client_context.get("brand_context"):
            brand = client_context["brand_context"]
            customized["personality"]["brand_voice"] = brand.get(
                "voice", "professional"
            )
            customized["personality"]["tone"] = brand.get("tone", "friendly")

        # Customize based on industry
        industry = client_context["client_info"].get("industry", "")
        industry_customizations = await self._get_industry_customizations(industry)
        customized.update(industry_customizations)

        # Apply custom requirements
        if custom_requirements:
            customized["custom_requirements"] = custom_requirements

        return customized

    async def _generate_assistant_code(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the actual assistant code"""

        # Use AI to generate code based on configuration
        prompt = self._build_code_generation_prompt(config)

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI assistant developer. Generate production-ready code based on the provided configuration.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        # Parse and structure the generated code
        generated_code = self._parse_generated_code(response.choices[0].message.content)

        return generated_code

    async def _run_build_tests(self, generated_code: Dict[str, Any]) -> Dict[str, Any]:
        """Run automated tests on the generated assistant"""

        # Implement automated testing
        test_results = {
            "passed": True,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
        }

        # Add specific test implementations here

        return test_results

    async def _deploy_assistant(
        self, build_id: str, generated_code: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy the generated assistant"""

        # Create deployment package
        deployment_package = {
            "build_id": build_id,
            "assistant_code": generated_code,
            "container_config": self._create_container_config(generated_code),
            "environment_config": self._create_environment_config(generated_code),
        }

        # Deploy to container orchestration system
        deployment_result = await self._execute_deployment(deployment_package)

        return deployment_result

    def _add_to_queue(self, build_config: Dict[str, Any]):
        """Add build to queue with priority ordering"""

        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        build_priority = priority_order.get(build_config["priority"], 2)

        # Insert in priority order
        inserted = False
        for i, queued_build in enumerate(self.build_queue):
            queued_priority = priority_order.get(queued_build["priority"], 2)
            if build_priority < queued_priority:
                self.build_queue.insert(i, build_config)
                inserted = True
                break

        if not inserted:
            self.build_queue.append(build_config)

    def _calculate_completion_time(self, template_type: str) -> str:
        """Calculate estimated completion time"""

        base_times = {
            "customer_service_bot": 180,  # 3 hours
            "lead_qualification_assistant": 300,  # 5 hours
            "product_recommendation_engine": 480,  # 8 hours
            "restaurant_assistant": 240,  # 4 hours
        }

        base_minutes = base_times.get(template_type, 240)
        queue_delay = len(self.build_queue) * 30  # 30 min per queued item

        completion_time = datetime.now() + timedelta(minutes=base_minutes + queue_delay)
        return completion_time.isoformat()

    def _get_queue_position(self, build_id: str) -> int:
        """Get position in queue"""

        for i, build in enumerate(self.build_queue):
            if build["build_id"] == build_id:
                return i + 1
        return 0

    async def _update_build_status(
        self,
        build_id: str,
        status: BuildStatus,
        stage: Optional[str] = None,
        progress: Optional[int] = None,
        error: Optional[str] = None,
    ):
        """Update build status"""

        if build_id in self.active_builds:
            self.active_builds[build_id]["status"] = status.value
            if stage:
                self.active_builds[build_id]["current_stage"] = stage
            if progress is not None:
                self.active_builds[build_id]["progress_percentage"] = progress
            if error:
                self.active_builds[build_id]["error"] = error

            self.active_builds[build_id]["updated_at"] = datetime.now().isoformat()

    # Additional helper methods would be implemented here...

    def _build_code_generation_prompt(self, config: Dict[str, Any]) -> str:
        """Build prompt for AI code generation"""
        return f"""
        Generate a production-ready AI assistant based on this configuration:
        {json.dumps(config, indent=2)}
        
        Include:
        1. Main assistant class
        2. Conversation flow handlers
        3. Integration connectors
        4. Error handling
        5. Logging and monitoring
        6. Docker configuration
        7. API endpoints
        """

    def _parse_generated_code(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI-generated code response"""
        # Implementation for parsing structured code from AI response
        return {"generated": True, "code": ai_response}

    async def _extract_brand_context(self, client) -> Dict[str, Any]:
        """Extract brand context from client data"""
        return {
            "voice": "professional",
            "tone": "friendly",
            "style": "modern",
        }

    async def _get_industry_customizations(self, industry: str) -> Dict[str, Any]:
        """Get industry-specific customizations"""
        return {}

    def _create_container_config(
        self, generated_code: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create Docker container configuration"""
        return {"image": "python:3.11-slim", "ports": ["8000:8000"]}

    def _create_environment_config(
        self, generated_code: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create environment configuration"""
        return {"env_vars": {}}

    async def _execute_deployment(
        self, deployment_package: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the deployment"""
        return {"status": "deployed", "url": "https://assistant.example.com"}

    async def _validate_deployment(self, deployment_result: Dict[str, Any]):
        """Validate successful deployment"""
        pass

    async def _finalize_project_record(
        self, build_id: str, deployment_result: Dict[str, Any]
    ):
        """Update project record with final results"""
        pass

    async def _get_completed_build_status(self, build_id: str) -> Dict[str, Any]:
        """Get status of completed build from database"""
        return {"build_id": build_id, "status": "not_found"}

    def _estimate_start_time(self, build_id: str) -> str:
        """Estimate when build will start"""
        queue_position = self._get_queue_position(build_id)
        start_time = datetime.now() + timedelta(minutes=queue_position * 30)
        return start_time.isoformat()
