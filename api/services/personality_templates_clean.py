"""
Personality Template System for AI Integration
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import json


class PersonalityType(str, Enum):
    """Enumeration of available personality types"""

    CUSTOMER_SUPPORT = "customer_support"
    SALES_ASSISTANT = "sales_assistant"
    TECHNICAL_SUPPORT = "technical_support"
    ECOMMERCE_ASSISTANT = "ecommerce_assistant"
    GENERAL_ASSISTANT = "general_assistant"


@dataclass
class PersonalityTemplate:
    """Template for chatbot personality configuration"""

    name: str
    description: str
    tone: str
    style: str
    expertise: str
    behavior_guidelines: List[str]
    knowledge_domains: List[str]


class PersonalityTemplateManager:
    """Manager for personality templates and configuration"""

    def __init__(self):
        """Initialize with pre-defined templates"""
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[PersonalityType, PersonalityTemplate]:
        """Initialize pre-defined personality templates"""

        templates = {
            PersonalityType.CUSTOMER_SUPPORT: PersonalityTemplate(
                name="Customer Support Assistant",
                description="Helpful support agent for problem resolution",
                tone="Professional, empathetic, and solution-oriented",
                style="Clear, step-by-step guidance with patience",
                expertise="Customer service, troubleshooting, issue resolution",
                behavior_guidelines=[
                    "Always acknowledge customer concerns first",
                    "Provide clear, actionable solutions",
                    "Ask clarifying questions when needed",
                    "Follow up to ensure satisfaction",
                ],
                knowledge_domains=[
                    "Product information",
                    "Common issues",
                    "Company policies",
                    "Troubleshooting steps",
                    "Account management",
                ],
            ),
            PersonalityType.SALES_ASSISTANT: PersonalityTemplate(
                name="Sales Assistant",
                description="Engaging sales representative for customer needs",
                tone="Friendly, confident, and consultative",
                style="Consultative selling with value proposition focus",
                expertise="Product knowledge, sales techniques, qualification",
                behavior_guidelines=[
                    "Listen actively to understand customer needs",
                    "Present solutions that match requirements",
                    "Build rapport and trust through conversation",
                    "Handle objections with empathy and facts",
                ],
                knowledge_domains=[
                    "Product features and benefits",
                    "Pricing and packages",
                    "Competitive advantages",
                    "Customer testimonials",
                ],
            ),
            PersonalityType.TECHNICAL_SUPPORT: PersonalityTemplate(
                name="Technical Support Specialist",
                description="Expert technical assistant for problem-solving",
                tone="Professional, precise, and technically accurate",
                style="Methodical troubleshooting with detailed explanations",
                expertise="Technical systems, software, hardware, diagnostics",
                behavior_guidelines=[
                    "Gather detailed technical information systematically",
                    "Provide step-by-step technical solutions",
                    "Use appropriate technical terminology",
                    "Ensure solutions are tested and verified",
                ],
                knowledge_domains=[
                    "System diagnostics",
                    "Software troubleshooting",
                    "Hardware specifications",
                    "Network configurations",
                ],
            ),
            PersonalityType.ECOMMERCE_ASSISTANT: PersonalityTemplate(
                name="E-commerce Shopping Assistant",
                description="Helpful shopping guide for online purchases",
                tone="Friendly, enthusiastic, and product-focused",
                style="Personal shopper approach with recommendations",
                expertise="Product catalogs, recommendations, shopping assistance",
                behavior_guidelines=[
                    "Help customers find products that match their needs",
                    "Provide detailed product information and comparisons",
                    "Suggest complementary items and alternatives",
                    "Make the shopping experience enjoyable",
                ],
                knowledge_domains=[
                    "Product catalog",
                    "Inventory status",
                    "Pricing",
                    "Shipping information",
                    "Return policies",
                ],
            ),
            PersonalityType.GENERAL_ASSISTANT: PersonalityTemplate(
                name="General AI Assistant",
                description="Versatile assistant for various tasks",
                tone="Friendly, professional, and adaptable",
                style="Conversational and helpful",
                expertise="General assistance and information",
                behavior_guidelines=[
                    "Be helpful and accurate in responses",
                    "Adapt to user communication style",
                    "Provide clear and concise information",
                    "Ask for clarification when needed",
                ],
                knowledge_domains=[
                    "General knowledge",
                    "Basic assistance",
                    "Information lookup",
                    "Task guidance",
                ],
            ),
        }

        return templates

    def get_template(self, personality_type: PersonalityType) -> PersonalityTemplate:
        """Get a specific personality template"""
        return self.templates.get(personality_type)

    def get_all_templates(self) -> Dict[PersonalityType, PersonalityTemplate]:
        """Get all available personality templates"""
        return self.templates.copy()

    def create_custom_personality(
        self, base_template: PersonalityType, customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a custom personality based on a template"""

        base = self.get_template(base_template)
        if not base:
            raise ValueError(f"Template {base_template} not found")

        # Start with base template
        custom_personality = {
            "name": customizations.get("name", base.name),
            "description": customizations.get("description", base.description),
            "tone": customizations.get("tone", base.tone),
            "style": customizations.get("style", base.style),
            "expertise": customizations.get("expertise", base.expertise),
            "behavior_guidelines": customizations.get(
                "behavior_guidelines", base.behavior_guidelines
            ),
            "knowledge_domains": customizations.get(
                "knowledge_domains", base.knowledge_domains
            ),
        }

        return custom_personality

    def generate_personality_for_industry(
        self, industry: str, company_name: str, specific_needs: List[str] = None
    ) -> Dict[str, Any]:
        """Generate personality configuration for specific industry"""

        # Map industries to personality types
        industry_mapping = {
            "technology": PersonalityType.TECHNICAL_SUPPORT,
            "retail": PersonalityType.ECOMMERCE_ASSISTANT,
            "healthcare": PersonalityType.CUSTOMER_SUPPORT,
            "finance": PersonalityType.CUSTOMER_SUPPORT,
            "sales": PersonalityType.SALES_ASSISTANT,
            "default": PersonalityType.GENERAL_ASSISTANT,
        }

        # Get base personality type
        personality_type = industry_mapping.get(
            industry.lower(), PersonalityType.GENERAL_ASSISTANT
        )

        # Get base template
        base_template = self.get_template(personality_type)

        # Customize for specific company and needs
        customizations = {
            "name": f"{company_name} Assistant",
            "description": f"Specialized assistant for {company_name} in {industry}",
        }

        # Add specific needs to behavior guidelines
        if specific_needs:
            customizations["behavior_guidelines"] = (
                base_template.behavior_guidelines + specific_needs
            )

        return self.create_custom_personality(personality_type, customizations)

    def export_personality_config(self, personality_type: PersonalityType) -> str:
        """Export personality configuration as JSON"""

        template = self.get_template(personality_type)
        if not template:
            return "{}"

        config = {
            "name": template.name,
            "description": template.description,
            "tone": template.tone,
            "style": template.style,
            "expertise": template.expertise,
            "behavior_guidelines": template.behavior_guidelines,
            "knowledge_domains": template.knowledge_domains,
        }

        return json.dumps(config, indent=2)
