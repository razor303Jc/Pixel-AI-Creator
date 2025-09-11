from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List, Any
from datetime import datetime

# ===== CLIENT MODELS =====


class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    
    # Social media handles
    twitter_handle: Optional[str] = None
    instagram_handle: Optional[str] = None
    linkedin_profile: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    
    # Social media handles
    twitter_handle: Optional[str] = None
    instagram_handle: Optional[str] = None
    linkedin_profile: Optional[str] = None


class ClientStatus(BaseModel):
    status: str  # active, inactive, suspended, pending


class ClientResponse(BaseModel):
    id: int
    name: str
    email: str
    company: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"
    
    # Social media handles
    twitter_handle: Optional[str] = None
    instagram_handle: Optional[str] = None
    linkedin_profile: Optional[str] = None
    
    # Analysis data
    website_analysis: Optional[Dict[str, Any]] = None
    social_media_analysis: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== PROJECT MODELS =====


class ProjectCreate(BaseModel):
    client_id: int
    name: str
    description: Optional[str] = None
    assistant_type: str = "chatbot"  # chatbot, voice_assistant, automation_bot
    complexity: str = "basic"        # basic, advanced, enterprise


class ProjectResponse(BaseModel):
    id: int
    client_id: int
    name: str
    description: Optional[str] = None
    assistant_type: str
    complexity: str
    
    # Generation status
    status: str
    progress: int
    
    # Generated content
    generated_code: Optional[str] = None
    deployment_config: Optional[Dict[str, Any]] = None
    personality_config: Optional[Dict[str, Any]] = None
    
    # Business logic
    business_rules: Optional[Dict[str, Any]] = None
    training_data: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== QA SESSION MODELS =====


class QASessionCreate(BaseModel):
    client_id: int
    project_id: Optional[int] = None


class QASessionResponse(BaseModel):
    id: int
    client_id: int
    project_id: Optional[int] = None
    
    # Questions and answers
    questions: List[str] = []
    answers: List[str] = []
    
    # Session metadata
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class QARecord(BaseModel):
    question: str
    answer: str
    confidence: float


# ===== ANALYSIS MODELS =====


class WebAnalysisRequest(BaseModel):
    url: str


class SocialMediaAnalysisRequest(BaseModel):
    platform: str
    handle: str


class AnalysisResponse(BaseModel):
    # Website analysis
    content_categories: Optional[Dict[str, Any]] = None
    color_scheme: Optional[Dict[str, Any]] = None
    brand_identity: Optional[Dict[str, Any]] = None
    
    # Social media analysis
    post_themes: Optional[Dict[str, Any]] = None
    engagement_patterns: Optional[Dict[str, Any]] = None
    personality_traits: Optional[Dict[str, Any]] = None
    target_audience: Optional[Dict[str, Any]] = None
    
    # Technical data
    page_structure: Optional[Dict[str, Any]] = None
    technologies_used: Optional[Dict[str, Any]] = None
    seo_analysis: Optional[Dict[str, Any]] = None
    
    # Metadata
    analyzed_at: datetime
    status: str
    
    class Config:
        from_attributes = True


# ===== AI GENERATION MODELS =====


class AIGenerationRequest(BaseModel):
    client_id: int
    assistant_type: str = "chatbot"
    complexity: str = "basic"
    custom_requirements: Optional[str] = None


class AIGenerationStatus(BaseModel):
    project_id: int
    status: str
    progress: int
    current_stage: str
    estimated_completion: Optional[datetime] = None
    logs: List[str] = []
