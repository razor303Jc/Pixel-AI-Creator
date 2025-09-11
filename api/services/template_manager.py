"""
Template Manager Service
Handles template loading, customization, and management for AI assistant generation
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from core.config import settings
import structlog

logger = structlog.get_logger()


class TemplateManager:
    """Service for managing AI assistant templates"""

    def __init__(self):
        self.templates_dir = Path(settings.templates_dir)
        self._template_cache = {}

    async def load_template(self, template_id: str) -> Dict[str, Any]:
        """Load template configuration by ID"""

        if template_id in self._template_cache:
            return self._template_cache[template_id]

        template_path = self._find_template_file(template_id)

        if not template_path:
            raise FileNotFoundError(f"Template not found: {template_id}")

        with open(template_path, "r") as f:
            template_data = json.load(f)

        # Cache the template
        self._template_cache[template_id] = template_data

        return template_data

    async def list_available_templates(self) -> List[Dict[str, Any]]:
        """List all available templates with metadata"""

        templates = []

        for category_dir in self.templates_dir.iterdir():
            if category_dir.is_dir() and category_dir.name != "__pycache__":
                for template_file in category_dir.glob("*.json"):
                    try:
                        with open(template_file, "r") as f:
                            template_data = json.load(f)

                        templates.append(
                            {
                                "template_id": template_data.get("template_id"),
                                "name": template_data.get("name"),
                                "description": template_data.get("description"),
                                "category": template_data.get("category"),
                                "complexity": template_data.get("complexity"),
                                "estimated_build_time": template_data.get(
                                    "estimated_build_time"
                                ),
                                "target_industries": template_data.get(
                                    "target_industries", []
                                ),
                                "base_price": template_data.get(
                                    "pricing_model", {}
                                ).get("base_price"),
                            }
                        )
                    except Exception as e:
                        logger.warning(
                            "Failed to load template",
                            file=str(template_file),
                            error=str(e),
                        )

        return templates

    async def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get templates filtered by category"""

        all_templates = await self.list_available_templates()
        return [t for t in all_templates if t.get("category") == category]

    async def get_templates_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """Get templates suitable for specific industry"""

        all_templates = await self.list_available_templates()
        return [t for t in all_templates if industry in t.get("target_industries", [])]

    async def create_custom_template(
        self,
        base_template_id: str,
        customizations: Dict[str, Any],
        template_name: str,
    ) -> Dict[str, Any]:
        """Create a custom template based on existing template"""

        # Load base template
        base_template = await self.load_template(base_template_id)

        # Apply customizations
        custom_template = self._apply_customizations(base_template, customizations)

        # Generate new template ID
        custom_template["template_id"] = (
            f"custom_{template_name.lower().replace(' ', '_')}"
        )
        custom_template["name"] = template_name
        custom_template["is_custom"] = True
        custom_template["base_template"] = base_template_id

        return custom_template

    async def validate_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template structure and configuration"""

        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        # Required fields
        required_fields = [
            "template_id",
            "name",
            "description",
            "category",
            "personality",
            "capabilities",
            "conversation_flows",
        ]

        for field in required_fields:
            if field not in template_data:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["valid"] = False

        # Validate personality structure
        if "personality" in template_data:
            personality_fields = ["tone", "communication_style", "expertise_level"]
            for field in personality_fields:
                if field not in template_data["personality"]:
                    validation_result["warnings"].append(
                        f"Missing personality field: {field}"
                    )

        # Validate pricing model
        if "pricing_model" in template_data:
            if "base_price" not in template_data["pricing_model"]:
                validation_result["warnings"].append(
                    "Missing base_price in pricing_model"
                )

        return validation_result

    def _find_template_file(self, template_id: str) -> Optional[Path]:
        """Find template file by ID"""

        for category_dir in self.templates_dir.iterdir():
            if category_dir.is_dir():
                for template_file in category_dir.glob("*.json"):
                    try:
                        with open(template_file, "r") as f:
                            template_data = json.load(f)

                        if template_data.get("template_id") == template_id:
                            return template_file
                    except Exception:
                        continue

        return None

    def _apply_customizations(
        self,
        base_template: Dict[str, Any],
        customizations: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply customizations to base template"""

        custom_template = base_template.copy()

        # Apply personality customizations
        if "personality" in customizations:
            custom_template["personality"].update(customizations["personality"])

        # Apply capability customizations
        if "capabilities" in customizations:
            custom_template["capabilities"].update(customizations["capabilities"])

        # Apply conversation flow customizations
        if "conversation_flows" in customizations:
            custom_template["conversation_flows"].update(
                customizations["conversation_flows"]
            )

        # Apply pricing customizations
        if "pricing_model" in customizations:
            custom_template["pricing_model"].update(customizations["pricing_model"])

        return custom_template
