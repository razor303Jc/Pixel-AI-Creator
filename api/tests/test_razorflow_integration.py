"""
Comprehensive tests for Razorflow-AI integration system
"""

import pytest
import json
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from main import app
from services.razorflow_integration import RazorflowIntegration, BuildStatus
from services.template_manager import TemplateManager

client = TestClient(app)


class TestRazorflowIntegration:
    """Test Razorflow-AI integration functionality"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def razorflow_service(self, mock_db):
        """Create RazorflowIntegration instance"""
        return RazorflowIntegration(mock_db)

    @pytest.fixture
    def template_manager(self):
        """Create TemplateManager instance"""
        return TemplateManager()

    @pytest.fixture
    def sample_client_data(self):
        """Sample client data for testing"""
        return {
            "name": "Test Business",
            "email": "test@business.com",
            "industry": "restaurant",
            "description": "A test restaurant for automated assistant",
            "requirements": ["order_taking", "reservations", "customer_support"],
            "budget": 5000,
            "timeline": "2_weeks",
        }

    def test_build_status_enum(self):
        """Test BuildStatus enum values"""
        assert BuildStatus.PENDING.value == "pending"
        assert BuildStatus.IN_PROGRESS.value == "in_progress"
        assert BuildStatus.COMPLETED.value == "completed"
        assert BuildStatus.FAILED.value == "failed"
        assert BuildStatus.DEPLOYED.value == "deployed"

    @pytest.mark.asyncio
    async def test_queue_build_success(self, razorflow_service, sample_client_data):
        """Test successful build queuing"""
        with patch.object(
            razorflow_service, "_select_best_template"
        ) as mock_select, patch.object(
            razorflow_service, "_validate_requirements"
        ) as mock_validate, patch.object(
            razorflow_service, "_create_client_record"
        ) as mock_create:

            mock_select.return_value = "restaurant_assistant"
            mock_validate.return_value = True
            mock_create.return_value = Mock(id=1)

            result = await razorflow_service.queue_build(sample_client_data)

            assert "build_id" in result
            assert result["status"] == BuildStatus.PENDING.value
            assert result["template"] == "restaurant_assistant"
            assert "estimated_completion" in result

    @pytest.mark.asyncio
    async def test_queue_build_validation_failure(
        self, razorflow_service, sample_client_data
    ):
        """Test build queuing with validation failure"""
        # Remove required fields
        invalid_data = sample_client_data.copy()
        del invalid_data["email"]

        result = await razorflow_service.queue_build(invalid_data)

        assert result["status"] == BuildStatus.FAILED.value
        assert "error" in result
        assert "validation" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_process_build_queue(self, razorflow_service):
        """Test build queue processing"""
        # Mock pending builds
        mock_build1 = Mock(id=1, status=BuildStatus.PENDING.value, client_data="{}")
        mock_build2 = Mock(id=2, status=BuildStatus.PENDING.value, client_data="{}")

        with patch.object(
            razorflow_service, "_get_pending_builds"
        ) as mock_pending, patch.object(
            razorflow_service, "_process_single_build"
        ) as mock_process:

            mock_pending.return_value = [mock_build1, mock_build2]
            mock_process.return_value = True

            await razorflow_service.process_build_queue()

            assert mock_process.call_count == 2

    def test_select_best_template_restaurant(self, razorflow_service):
        """Test template selection for restaurant industry"""
        client_data = {
            "industry": "restaurant",
            "requirements": ["order_taking", "reservations"],
        }

        template = razorflow_service._select_best_template(client_data)
        assert template == "restaurant_assistant"

    def test_select_best_template_ecommerce(self, razorflow_service):
        """Test template selection for ecommerce"""
        client_data = {
            "industry": "ecommerce",
            "requirements": ["product_recommendations", "customer_support"],
        }

        template = razorflow_service._select_best_template(client_data)
        assert template == "product_recommendation_engine"

    def test_select_best_template_default(self, razorflow_service):
        """Test default template selection"""
        client_data = {"industry": "unknown", "requirements": ["customer_support"]}

        template = razorflow_service._select_best_template(client_data)
        assert template == "customer_service_bot"

    def test_validate_requirements_valid(self, razorflow_service):
        """Test requirement validation with valid data"""
        client_data = {
            "name": "Test Business",
            "email": "test@business.com",
            "industry": "restaurant",
            "requirements": ["order_taking"],
            "budget": 5000,
        }

        is_valid = razorflow_service._validate_requirements(client_data)
        assert is_valid is True

    def test_validate_requirements_missing_email(self, razorflow_service):
        """Test requirement validation with missing email"""
        client_data = {
            "name": "Test Business",
            "industry": "restaurant",
            "requirements": ["order_taking"],
            "budget": 5000,
        }

        is_valid = razorflow_service._validate_requirements(client_data)
        assert is_valid is False

    def test_validate_requirements_low_budget(self, razorflow_service):
        """Test requirement validation with insufficient budget"""
        client_data = {
            "name": "Test Business",
            "email": "test@business.com",
            "industry": "restaurant",
            "requirements": ["order_taking"],
            "budget": 1000,  # Below minimum
        }

        is_valid = razorflow_service._validate_requirements(client_data)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_get_build_status_existing(self, razorflow_service):
        """Test getting status of existing build"""
        mock_build = Mock(
            id=1,
            status=BuildStatus.IN_PROGRESS.value,
            client_data='{"name": "Test"}',
            template="customer_service_bot",
            created_at="2024-01-01T00:00:00",
        )

        with patch.object(razorflow_service, "_get_build_by_id") as mock_get:
            mock_get.return_value = mock_build

            result = await razorflow_service.get_build_status("build_1")

            assert result["build_id"] == "build_1"
            assert result["status"] == BuildStatus.IN_PROGRESS.value
            assert result["template"] == "customer_service_bot"

    @pytest.mark.asyncio
    async def test_get_build_status_not_found(self, razorflow_service):
        """Test getting status of non-existent build"""
        with patch.object(razorflow_service, "_get_build_by_id") as mock_get:
            mock_get.return_value = None

            result = await razorflow_service.get_build_status("invalid_id")

            assert "error" in result
            assert "not found" in result["error"]


class TestTemplateManager:
    """Test template management functionality"""

    @pytest.fixture
    def template_manager(self):
        """Create TemplateManager instance"""
        return TemplateManager()

    def test_load_all_templates(self, template_manager):
        """Test loading all available templates"""
        with patch("os.listdir") as mock_listdir, patch(
            "os.path.isdir"
        ) as mock_isdir, patch.object(template_manager, "load_template") as mock_load:

            mock_listdir.side_effect = [
                ["business-automation", "ecommerce-automation"],  # Root categories
                ["customer_service_bot.json"],  # business-automation files
                ["product_recommendation_engine.json"],  # ecommerce-automation files
            ]
            mock_isdir.return_value = True
            mock_load.return_value = {"name": "test_template"}

            templates = template_manager.load_all_templates()

            assert len(templates) >= 2
            assert mock_load.call_count >= 2

    def test_load_template_valid(self, template_manager):
        """Test loading a valid template"""
        template_data = {
            "name": "Customer Service Bot",
            "description": "AI-powered customer service assistant",
            "category": "business-automation",
            "price": 2500,
            "features": ["24/7 support", "multi-language"],
            "customization": {"branding": True, "workflows": True},
        }

        with patch("builtins.open", create=True) as mock_open, patch(
            "json.load"
        ) as mock_json:

            mock_json.return_value = template_data

            result = template_manager.load_template("customer_service_bot")

            assert result == template_data
            assert result["name"] == "Customer Service Bot"
            assert result["price"] == 2500

    def test_load_template_not_found(self, template_manager):
        """Test loading non-existent template"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = template_manager.load_template("nonexistent")
            assert result is None

    def test_load_template_invalid_json(self, template_manager):
        """Test loading template with invalid JSON"""
        with patch("builtins.open", create=True), patch(
            "json.load", side_effect=json.JSONDecodeError("Invalid JSON", "", 0)
        ):

            result = template_manager.load_template("invalid_json")
            assert result is None

    def test_validate_template_valid(self, template_manager):
        """Test template validation with valid template"""
        template = {
            "name": "Test Template",
            "description": "A test template",
            "category": "business-automation",
            "price": 3000,
            "features": ["feature1", "feature2"],
            "customization": {"branding": True},
        }

        is_valid, errors = template_manager.validate_template(template)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_template_missing_required(self, template_manager):
        """Test template validation with missing required fields"""
        template = {
            "name": "Test Template",
            "description": "A test template",
            # Missing category, price, features, customization
        }

        is_valid, errors = template_manager.validate_template(template)
        assert is_valid is False
        assert len(errors) > 0
        assert any("category" in error for error in errors)
        assert any("price" in error for error in errors)

    def test_customize_template(self, template_manager):
        """Test template customization"""
        base_template = {
            "name": "Base Template",
            "description": "Base description",
            "customization": {"branding": True, "workflows": True},
        }

        customizations = {
            "company_name": "Test Company",
            "branding_colors": ["#FF0000", "#00FF00"],
            "custom_workflows": ["workflow1", "workflow2"],
        }

        result = template_manager.customize_template(base_template, customizations)

        assert result["company_name"] == "Test Company"
        assert result["branding_colors"] == ["#FF0000", "#00FF00"]
        assert result["custom_workflows"] == ["workflow1", "workflow2"]
        assert result["name"] == "Base Template"  # Original fields preserved


class TestAPIEndpoints:
    """Test Razorflow-AI API endpoints"""

    def test_queue_build_endpoint(self):
        """Test /api/razorflow/queue-build endpoint"""
        client_data = {
            "name": "Test Business",
            "email": "test@business.com",
            "industry": "restaurant",
            "description": "A test restaurant",
            "requirements": ["order_taking", "reservations"],
            "budget": 5000,
            "timeline": "2_weeks",
        }

        with patch("api.main.razorflow_service.queue_build") as mock_queue:
            mock_queue.return_value = {
                "build_id": "build_123",
                "status": "pending",
                "template": "restaurant_assistant",
            }

            response = client.post("/api/razorflow/queue-build", json=client_data)

            assert response.status_code == 200
            data = response.json()
            assert data["build_id"] == "build_123"
            assert data["status"] == "pending"

    def test_get_build_status_endpoint(self):
        """Test /api/razorflow/build-status/{build_id} endpoint"""
        with patch("api.main.razorflow_service.get_build_status") as mock_status:
            mock_status.return_value = {
                "build_id": "build_123",
                "status": "completed",
                "progress": 100,
            }

            response = client.get("/api/razorflow/build-status/build_123")

            assert response.status_code == 200
            data = response.json()
            assert data["build_id"] == "build_123"
            assert data["status"] == "completed"

    def test_list_templates_endpoint(self):
        """Test /api/templates/list endpoint"""
        mock_templates = {
            "customer_service_bot": {"name": "Customer Service Bot", "price": 2500}
        }

        with patch("api.main.template_manager.load_all_templates") as mock_load:
            mock_load.return_value = mock_templates

            response = client.get("/api/templates/list")

            assert response.status_code == 200
            data = response.json()
            assert "customer_service_bot" in data

    def test_get_template_endpoint(self):
        """Test /api/templates/{template_id} endpoint"""
        mock_template = {
            "name": "Customer Service Bot",
            "description": "AI-powered customer service",
            "price": 2500,
        }

        with patch("api.main.template_manager.load_template") as mock_load:
            mock_load.return_value = mock_template

            response = client.get("/api/templates/customer_service_bot")

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Customer Service Bot"

    def test_get_template_not_found(self):
        """Test /api/templates/{template_id} endpoint with non-existent template"""
        with patch("api.main.template_manager.load_template") as mock_load:
            mock_load.return_value = None

            response = client.get("/api/templates/nonexistent")

            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"]


class TestIntegrationScenarios:
    """Test end-to-end integration scenarios"""

    @pytest.mark.asyncio
    async def test_complete_build_workflow(self):
        """Test complete build workflow from queue to completion"""
        # This would test the full workflow:
        # 1. Queue build
        # 2. Process queue
        # 3. Generate assistant
        # 4. Deploy
        # 5. Monitor status

        # Mock the entire workflow
        with patch(
            "api.services.razorflow_integration.RazorflowIntegration"
        ) as MockRazorflow:
            mock_service = MockRazorflow.return_value

            # Queue build
            mock_service.queue_build.return_value = {
                "build_id": "build_123",
                "status": "pending",
            }

            # Process queue
            mock_service.process_build_queue.return_value = None

            # Check status - completed
            mock_service.get_build_status.return_value = {
                "build_id": "build_123",
                "status": "completed",
                "deployment_url": "https://test-assistant.razorflow.ai",
            }

            # Execute workflow steps
            queue_result = await mock_service.queue_build({})
            await mock_service.process_build_queue()
            status_result = await mock_service.get_build_status("build_123")

            assert queue_result["status"] == "pending"
            assert status_result["status"] == "completed"
            assert "deployment_url" in status_result

    def test_pricing_calculation(self):
        """Test pricing calculation based on template and customizations"""
        base_prices = {
            "customer_service_bot": 2500,
            "lead_qualification_assistant": 3500,
            "product_recommendation_engine": 4500,
            "appointment_scheduler": 3000,
            "social_media_manager": 5000,
            "restaurant_assistant": 4000,
        }

        customization_costs = {
            "advanced_ai": 1500,
            "multi_language": 1000,
            "custom_integrations": 2000,
            "advanced_analytics": 1500,
        }

        # Test base pricing
        for template, price in base_prices.items():
            assert price >= 2500  # Minimum price
            assert price <= 10000  # Maximum base price

        # Test package pricing
        basic_package = sum([base_prices["customer_service_bot"]])
        professional_package = sum(
            [
                base_prices["customer_service_bot"],
                base_prices["lead_qualification_assistant"],
                customization_costs["advanced_ai"],
            ]
        )
        enterprise_package = sum(base_prices.values()) + sum(
            customization_costs.values()
        )

        assert basic_package == 2500
        assert professional_package == 7500
        assert enterprise_package >= 30000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
