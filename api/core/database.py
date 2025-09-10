from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from core.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug
)

# Create session factory
async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# ===== DATABASE MODELS =====

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    company = Column(String)
    website = Column(String)
    phone = Column(String)
    industry = Column(String)
    description = Column(Text)
    
    # Social media handles
    twitter_handle = Column(String)
    instagram_handle = Column(String)
    linkedin_profile = Column(String)
    
    # Analysis data
    website_analysis = Column(JSON)
    social_media_analysis = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="client")
    qa_sessions = relationship("QASession", back_populates="client")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Project details
    name = Column(String, nullable=False)
    description = Column(Text)
    assistant_type = Column(String)  # chatbot, voice_assistant, automation_bot
    complexity = Column(String)      # basic, advanced, enterprise
    
    # Generation status
    status = Column(String, default="pending")  # pending, analyzing, generating, completed, failed
    progress = Column(Integer, default=0)
    
    # Generated content
    generated_code = Column(Text)
    deployment_config = Column(JSON)
    personality_config = Column(JSON)
    
    # Business logic
    business_rules = Column(JSON)
    training_data = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    client = relationship("Client", back_populates="projects")

class QASession(Base):
    __tablename__ = "qa_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Session details
    session_name = Column(String)
    status = Column(String, default="active")  # active, completed
    
    # Q&A data
    questions_answers = Column(JSON, default=list)
    insights = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    client = relationship("Client", back_populates="qa_sessions")

class WebAnalysis(Base):
    __tablename__ = "web_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Analysis target
    url = Column(String, nullable=False)
    analysis_type = Column(String)  # website, social_media
    platform = Column(String)       # for social media: twitter, instagram, linkedin
    
    # Analysis results
    content_summary = Column(Text)
    key_features = Column(JSON)
    business_insights = Column(JSON)
    personality_traits = Column(JSON)
    target_audience = Column(JSON)
    
    # Technical data
    page_structure = Column(JSON)
    technologies_used = Column(JSON)
    seo_analysis = Column(JSON)
    
    # Metadata
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")

# ===== DATABASE INITIALIZATION =====

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency to get database session"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
