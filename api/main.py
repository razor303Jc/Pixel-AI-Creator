from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our core modules
from core.config import settings
from core.database import init_db
from services.web_analyzer import WebAnalyzer
from services.ai_generator import AIAssistantGenerator
from services.client_manager import ClientManager
from services.razorflow_integration import RazorflowIntegration
from services.template_manager import TemplateManager
from models.client import (
    ClientCreate,
    ClientResponse,
    ProjectCreate,
    ProjectResponse,
)
from routes.embeddings import router as embeddings_router
from routes.clients import router as clients_router
from routes.chatbots import router as chatbots_router
from routes.conversations import router as conversations_router
from routes.analytics_clean import router as analytics_router
from auth.routes import router as auth_router

# Initialize FastAPI app
app = FastAPI(
    title="Pixel AI Creator",
    description="AI platform that creates custom AI assistants for clients",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
web_analyzer = WebAnalyzer()
ai_generator = AIAssistantGenerator()
client_manager = ClientManager()
razorflow_integration = RazorflowIntegration()
template_manager = TemplateManager()

# Include routers with /api prefix
app.include_router(embeddings_router, prefix="/api")
app.include_router(clients_router, prefix="/api")
app.include_router(chatbots_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(analytics_router)
app.include_router(auth_router, prefix="/api")

# Import and include AI conversation router
from routes.ai_conversation import router as ai_conversation_router

app.include_router(ai_conversation_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    await init_db()
    print("🤖 Pixel AI Creator is online!")


@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Pixel AI Creator!",
        "version": "1.0.0",
        "status": "online",
        "description": "AI platform that creates custom AI assistants",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "pixel-ai-creator"}


# ===== CLIENT MANAGEMENT ENDPOINTS =====


@app.post("/api/clients", response_model=ClientResponse)
async def create_client(client: ClientCreate):
    """Create a new client"""
    try:
        return await client_manager.create_client(client)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/clients")
async def get_clients():
    """Get all clients"""
    return await client_manager.get_all_clients()


@app.get("/api/clients/{client_id}")
async def get_client(client_id: int):
    """Get specific client by ID"""
    client = await client_manager.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


# ===== WEB ANALYSIS ENDPOINTS =====


@app.post("/api/analyze/website")
async def analyze_website(background_tasks: BackgroundTasks, url: str, client_id: int):
    """Analyze a client's website"""
    try:
        # Start analysis in background
        background_tasks.add_task(web_analyzer.analyze_website, url, client_id)
        return {
            "message": "Website analysis started",
            "url": url,
            "client_id": client_id,
            "status": "processing",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/analyze/social-media")
async def analyze_social_media(
    background_tasks: BackgroundTasks, platform: str, handle: str, client_id: int
):
    """Analyze client's social media presence"""
    try:
        background_tasks.add_task(
            web_analyzer.analyze_social_media, platform, handle, client_id
        )
        return {
            "message": f"Social media analysis started for {platform}",
            "handle": handle,
            "platform": platform,
            "client_id": client_id,
            "status": "processing",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== AI GENERATION ENDPOINTS =====


@app.post("/api/generate/assistant")
async def generate_ai_assistant(
    background_tasks: BackgroundTasks,
    client_id: int,
    assistant_type: str = "chatbot",
    complexity: str = "basic",
):
    """Generate a custom AI assistant for the client"""
    try:
        background_tasks.add_task(
            ai_generator.generate_assistant, client_id, assistant_type, complexity
        )
        return {
            "message": "AI assistant generation started",
            "client_id": client_id,
            "type": assistant_type,
            "complexity": complexity,
            "status": "generating",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/generate/status/{project_id}")
async def get_generation_status(project_id: int):
    """Get status of AI assistant generation"""
    try:
        status = await ai_generator.get_generation_status(project_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== PROJECT MANAGEMENT =====


@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate):
    """Create a new AI assistant project"""
    try:
        return await client_manager.create_project(project)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/projects/{client_id}")
async def get_client_projects(client_id: int):
    """Get all projects for a client"""
    return await client_manager.get_client_projects(client_id)


# ===== Q&A SESSION ENDPOINTS =====


@app.post("/api/qa/session")
async def create_qa_session(client_id: int):
    """Start a Q&A session with a client"""
    try:
        session = await client_manager.create_qa_session(client_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/qa/question")
async def ask_question(session_id: int, question: str, answer: str):
    """Record a Q&A pair in the session"""
    try:
        return await client_manager.record_qa(session_id, question, answer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== PIXEL AI STATUS =====


@app.get("/api/pixel/status")
async def pixel_status():
    """Get Pixel AI's current status and capabilities"""
    return {
        "pixel_status": "online",
        "capabilities": [
            "Website Analysis",
            "Social Media Scraping",
            "Client Q&A Sessions",
            "AI Assistant Generation",
            "Custom Chatbot Creation",
            "Business Logic Implementation",
        ],
        "active_projects": await client_manager.get_active_projects_count(),
        "total_clients": await client_manager.get_total_clients_count(),
    }


# ===== RAZORFLOW-AI INTEGRATION ENDPOINTS =====


@app.post("/api/razorflow/queue-build")
async def queue_client_build(
    client_id: int,
    template_type: str,
    priority: str = "normal",
    custom_requirements: dict = {},
):
    """Queue a new client build for automated processing"""
    try:
        result = await razorflow_integration.queue_client_build(
            client_id=client_id,
            template_type=template_type,
            priority=priority,
            custom_requirements=custom_requirements,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/razorflow/build-status/{build_id}")
async def get_build_status(build_id: str):
    """Get current status of a build"""
    try:
        return await razorflow_integration.get_build_status(build_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/razorflow/deploy-default-suite")
async def deploy_default_suite(client_id: int):
    """Deploy the complete default assistant suite for a client"""
    try:
        result = await razorflow_integration.deploy_default_assistant_suite(
            client_id=client_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/templates")
async def list_templates():
    """List all available AI assistant templates"""
    try:
        return await template_manager.list_available_templates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/templates/category/{category}")
async def get_templates_by_category(category: str):
    """Get templates filtered by category"""
    try:
        return await template_manager.get_templates_by_category(category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/templates/industry/{industry}")
async def get_templates_by_industry(industry: str):
    """Get templates suitable for specific industry"""
    try:
        return await template_manager.get_templates_by_industry(industry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/templates/{template_id}")
async def get_template_details(template_id: str):
    """Get detailed template configuration"""
    try:
        return await template_manager.load_template(template_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/templates/custom")
async def create_custom_template(
    base_template_id: str, template_name: str, customizations: dict
):
    """Create a custom template based on existing template"""
    try:
        result = await template_manager.create_custom_template(
            base_template_id=base_template_id,
            customizations=customizations,
            template_name=template_name,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/templates/validate")
async def validate_template(template_data: dict):
    """Validate template structure and configuration"""
    try:
        return await template_manager.validate_template(template_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
    )
