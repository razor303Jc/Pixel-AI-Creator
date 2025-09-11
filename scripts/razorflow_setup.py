#!/usr/bin/env python3
"""
Razorflow-AI Default Assistant Suite Setup
Initializes the complete default AI assistant ecosystem for automated client deployment
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add the API directory to the path
sys.path.append(str(Path(__file__).parent.parent / "api"))

from services.razorflow_integration import RazorflowIntegration
from services.template_manager import TemplateManager
from services.client_manager import ClientManager
from core.database import init_db


class RazorflowSetup:
    """Setup manager for Razorflow-AI default assistant suite"""

    def __init__(self):
        self.razorflow = RazorflowIntegration()
        self.template_manager = TemplateManager()
        self.client_manager = ClientManager()

        # Default assistant configurations
        self.default_assistants = {
            "core_business_suite": [
                {
                    "template_id": "customer_service_bot_v1",
                    "priority": "high",
                    "auto_deploy": True,
                    "description": "24/7 customer support automation",
                },
                {
                    "template_id": "lead_qualification_assistant_v1",
                    "priority": "high",
                    "auto_deploy": True,
                    "description": "Automated sales lead qualification",
                },
                {
                    "template_id": "appointment_scheduler_v1",
                    "priority": "medium",
                    "auto_deploy": True,
                    "description": "Smart scheduling and calendar management",
                },
            ],
            "ecommerce_suite": [
                {
                    "template_id": "product_recommendation_engine_v1",
                    "priority": "high",
                    "auto_deploy": False,  # Requires e-commerce setup
                    "description": "AI-powered shopping assistant",
                }
            ],
            "marketing_suite": [
                {
                    "template_id": "social_media_manager_v1",
                    "priority": "medium",
                    "auto_deploy": False,  # Requires social media accounts
                    "description": "Automated social media management",
                }
            ],
            "industry_specific": [
                {
                    "template_id": "restaurant_assistant_v1",
                    "priority": "medium",
                    "auto_deploy": False,  # Industry-specific
                    "description": "Restaurant orders and reservations",
                }
            ],
        }

    async def initialize_razorflow_system(self) -> Dict[str, Any]:
        """Initialize the complete Razorflow-AI system"""

        print("🚀 Initializing Razorflow-AI Default Assistant Suite...")

        setup_results = {
            "razorflow_status": "initializing",
            "templates_validated": [],
            "system_health": {},
            "default_assistants": {},
            "ready_for_deployment": False,
        }

        try:
            # Step 1: Validate all templates
            print("📋 Step 1: Validating assistant templates...")
            template_validation = await self._validate_all_templates()
            setup_results["templates_validated"] = template_validation

            # Step 2: System health check
            print("🔍 Step 2: Running system health checks...")
            health_check = await self._run_system_health_check()
            setup_results["system_health"] = health_check

            # Step 3: Initialize default assistant configurations
            print("🤖 Step 3: Setting up default assistant configurations...")
            assistant_setup = await self._setup_default_assistants()
            setup_results["default_assistants"] = assistant_setup

            # Step 4: Test queue system
            print("⚡ Step 4: Testing build queue system...")
            queue_test = await self._test_queue_system()
            setup_results["queue_test"] = queue_test

            # Final validation
            setup_results["ready_for_deployment"] = (
                template_validation["all_valid"]
                and health_check["system_ready"]
                and assistant_setup["setup_complete"]
                and queue_test["queue_operational"]
            )

            setup_results["razorflow_status"] = (
                "ready" if setup_results["ready_for_deployment"] else "needs_attention"
            )

            print(
                f"✅ Razorflow-AI Setup Complete! Status: {setup_results['razorflow_status']}"
            )
            return setup_results

        except Exception as e:
            print(f"❌ Setup failed: {str(e)}")
            setup_results["razorflow_status"] = "failed"
            setup_results["error"] = str(e)
            return setup_results

    async def create_demo_client_deployment(
        self, client_name: str = "Demo Client"
    ) -> Dict[str, Any]:
        """Create a demo client and deploy the core business suite"""

        print(f"🎯 Creating demo deployment for: {client_name}")

        try:
            # Create demo client
            from models.client import ClientCreate

            demo_client = ClientCreate(
                name=client_name,
                email=f"{client_name.lower().replace(' ', '.')}@demo.razorflow.ai",
                company=f"{client_name} Corp",
                website="https://demo.razorflow.ai",
                industry="technology",
                description="Demo client for Razorflow-AI assistant suite testing",
            )

            client_record = await self.client_manager.create_client(demo_client)
            client_id = client_record.id

            # Deploy core business suite
            deployment_result = await self.razorflow.deploy_default_assistant_suite(
                client_id
            )

            print(f"✅ Demo deployment initiated for client ID: {client_id}")
            return {
                "client_id": client_id,
                "client_name": client_name,
                "deployment_status": "initiated",
                "deployment_details": deployment_result,
            }

        except Exception as e:
            print(f"❌ Demo deployment failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def _validate_all_templates(self) -> Dict[str, Any]:
        """Validate all template files"""

        validation_results = {
            "total_templates": 0,
            "valid_templates": 0,
            "invalid_templates": 0,
            "validation_errors": [],
            "all_valid": True,
        }

        try:
            templates = await self.template_manager.list_available_templates()
            validation_results["total_templates"] = len(templates)

            for template in templates:
                template_id = template.get("template_id")
                if template_id:
                    try:
                        template_data = await self.template_manager.load_template(
                            template_id
                        )
                        validation = await self.template_manager.validate_template(
                            template_data
                        )

                        if validation["valid"]:
                            validation_results["valid_templates"] += 1
                        else:
                            validation_results["invalid_templates"] += 1
                            validation_results["validation_errors"].append(
                                {
                                    "template_id": template_id,
                                    "errors": validation["errors"],
                                }
                            )
                            validation_results["all_valid"] = False

                    except Exception as e:
                        validation_results["invalid_templates"] += 1
                        validation_results["validation_errors"].append(
                            {"template_id": template_id, "error": str(e)}
                        )
                        validation_results["all_valid"] = False

            print(
                f"   📊 Templates: {validation_results['valid_templates']}/{validation_results['total_templates']} valid"
            )
            return validation_results

        except Exception as e:
            validation_results["all_valid"] = False
            validation_results["validation_errors"].append({"system_error": str(e)})
            return validation_results

    async def _run_system_health_check(self) -> Dict[str, Any]:
        """Run comprehensive system health checks"""

        health_status = {
            "database_connection": False,
            "template_directory": False,
            "output_directory": False,
            "queue_system": False,
            "ai_service": False,
            "system_ready": False,
        }

        try:
            # Check database connection
            try:
                await init_db()
                health_status["database_connection"] = True
                print("   ✅ Database connection: OK")
            except Exception as e:
                print(f"   ❌ Database connection: FAILED - {str(e)}")

            # Check template directory
            templates_dir = Path("templates")
            if templates_dir.exists() and any(templates_dir.iterdir()):
                health_status["template_directory"] = True
                print("   ✅ Template directory: OK")
            else:
                print("   ❌ Template directory: MISSING or EMPTY")

            # Check output directory
            output_dir = Path("generated-bots")
            if output_dir.exists():
                health_status["output_directory"] = True
                print("   ✅ Output directory: OK")
            else:
                print("   ❌ Output directory: MISSING")

            # Check queue system
            try:
                # Test queue initialization
                queue_status = {
                    "max_concurrent": self.razorflow.max_concurrent_builds,
                    "active_builds": len(self.razorflow.active_builds),
                    "queued_builds": len(self.razorflow.build_queue),
                }
                health_status["queue_system"] = True
                print("   ✅ Queue system: OK")
            except Exception as e:
                print(f"   ❌ Queue system: FAILED - {str(e)}")

            # Check AI service
            try:
                # Test OpenAI connection (basic check)
                if hasattr(self.razorflow, "openai_client"):
                    health_status["ai_service"] = True
                    print("   ✅ AI service: OK")
                else:
                    print("   ❌ AI service: NOT CONFIGURED")
            except Exception as e:
                print(f"   ❌ AI service: FAILED - {str(e)}")

            # Overall system readiness
            health_status["system_ready"] = all(
                [
                    health_status["database_connection"],
                    health_status["template_directory"],
                    health_status["output_directory"],
                    health_status["queue_system"],
                    health_status["ai_service"],
                ]
            )

            return health_status

        except Exception as e:
            print(f"   ❌ Health check failed: {str(e)}")
            return health_status

    async def _setup_default_assistants(self) -> Dict[str, Any]:
        """Setup default assistant configurations"""

        setup_status = {
            "assistants_configured": 0,
            "total_assistants": 0,
            "configuration_errors": [],
            "setup_complete": False,
        }

        try:
            total_assistants = sum(
                len(suite) for suite in self.default_assistants.values()
            )
            setup_status["total_assistants"] = total_assistants

            for suite_name, assistants in self.default_assistants.items():
                print(f"   🔧 Configuring {suite_name}...")

                for assistant in assistants:
                    try:
                        template_id = assistant["template_id"]
                        # Verify template exists
                        template_data = await self.template_manager.load_template(
                            template_id
                        )

                        if template_data:
                            setup_status["assistants_configured"] += 1
                            print(f"      ✅ {assistant['description']}")
                        else:
                            setup_status["configuration_errors"].append(
                                {
                                    "assistant": template_id,
                                    "error": "Template not found",
                                }
                            )
                            print(
                                f"      ❌ {assistant['description']} - Template not found"
                            )

                    except Exception as e:
                        setup_status["configuration_errors"].append(
                            {
                                "assistant": assistant.get("template_id", "unknown"),
                                "error": str(e),
                            }
                        )
                        print(
                            f"      ❌ {assistant.get('description', 'Unknown')} - {str(e)}"
                        )

            setup_status["setup_complete"] = (
                setup_status["assistants_configured"]
                == setup_status["total_assistants"]
            )

            print(
                f"   📊 Assistant setup: {setup_status['assistants_configured']}/{setup_status['total_assistants']} configured"
            )
            return setup_status

        except Exception as e:
            setup_status["configuration_errors"].append({"system_error": str(e)})
            return setup_status

    async def _test_queue_system(self) -> Dict[str, Any]:
        """Test the build queue system"""

        queue_test = {
            "queue_initialized": False,
            "concurrent_limit": 0,
            "queue_operational": False,
            "test_results": [],
        }

        try:
            # Test queue initialization
            if hasattr(self.razorflow, "build_queue"):
                queue_test["queue_initialized"] = True
                queue_test["concurrent_limit"] = self.razorflow.max_concurrent_builds

                # Test queue functionality (without actual builds)
                test_build_config = {
                    "build_id": "test_build_001",
                    "client_id": 9999,
                    "template_type": "customer_service_bot",
                    "priority": "normal",
                    "status": "test",
                }

                # Test adding to queue
                try:
                    initial_queue_size = len(self.razorflow.build_queue)
                    self.razorflow._add_to_queue(test_build_config)
                    new_queue_size = len(self.razorflow.build_queue)

                    if new_queue_size == initial_queue_size + 1:
                        queue_test["test_results"].append("✅ Queue add: PASSED")

                        # Remove test build
                        self.razorflow.build_queue.pop()
                        queue_test["queue_operational"] = True
                    else:
                        queue_test["test_results"].append("❌ Queue add: FAILED")

                except Exception as e:
                    queue_test["test_results"].append(f"❌ Queue test: {str(e)}")

            print(
                f"   ⚡ Queue system: {'OPERATIONAL' if queue_test['queue_operational'] else 'FAILED'}"
            )
            return queue_test

        except Exception as e:
            queue_test["test_results"].append(f"❌ Queue system error: {str(e)}")
            return queue_test

    def print_setup_summary(self, setup_results: Dict[str, Any]):
        """Print a comprehensive setup summary"""

        print("\n" + "=" * 60)
        print("🤖 RAZORFLOW-AI SETUP SUMMARY")
        print("=" * 60)

        print(f"Overall Status: {setup_results['razorflow_status'].upper()}")

        if setup_results.get("templates_validated"):
            tv = setup_results["templates_validated"]
            print(f"Templates: {tv['valid_templates']}/{tv['total_templates']} valid")

        if setup_results.get("system_health"):
            sh = setup_results["system_health"]
            print(
                f"System Health: {'✅ READY' if sh['system_ready'] else '❌ NEEDS ATTENTION'}"
            )

        if setup_results.get("default_assistants"):
            da = setup_results["default_assistants"]
            print(
                f"Default Assistants: {da['assistants_configured']}/{da['total_assistants']} configured"
            )

        print(
            f"Ready for Deployment: {'✅ YES' if setup_results['ready_for_deployment'] else '❌ NO'}"
        )

        if setup_results["ready_for_deployment"]:
            print("\n🚀 Razorflow-AI is ready for client deployments!")
            print("   Use: python scripts/razorflow_setup.py --demo")
            print("   Or deploy via API: POST /api/razorflow/deploy-default-suite")
        else:
            print("\n⚠️  Please resolve issues before deploying to clients.")

        print("=" * 60)


async def main():
    """Main setup function"""

    setup = RazorflowSetup()

    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Create demo deployment
        demo_result = await setup.create_demo_client_deployment()
        print(f"\n🎯 Demo Result: {demo_result}")
    else:
        # Run full setup
        setup_results = await setup.initialize_razorflow_system()
        setup.print_setup_summary(setup_results)


if __name__ == "__main__":
    asyncio.run(main())
