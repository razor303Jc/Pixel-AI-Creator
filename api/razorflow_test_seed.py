#!/usr/bin/env python3
"""
RazorFlow Test User Seed Script

Creates comprehensive test data including:
- Razor303 (jc) test user at RazorFlow-AI
- Sample clients and projects
- Enhanced template collection with MCP integrations
- Realistic test data for human-like workflow testing
"""

import asyncio
import sys
import json

# Add the API directory to Python path
sys.path.insert(0, "/home/jc/Documents/ChatBot-Project/Pixel-AI-Creator/api")

from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy import select, text
from models.database_schema import (
    User, Client, Chatbot,
    UserRole, ChatbotType, ChatbotComplexity, ChatbotStatus
)
from core.config import settings
from auth.jwt import hash_password


# Enhanced Template Collection with MCP Integration
ENHANCED_TEMPLATES = [
    {
        "name": "Executive Personal Assistant (MCP)",
        "description": "AI assistant with MCP server integration for calendar, email, and file management",
        "category": "PA",
        "personality": "professional",
        "instructions": "You are an executive personal assistant with access to calendar management, email handling, and file organization. Use MCP server tools to efficiently manage schedules, communications, and documents.",
        "is_public": True,
        "tags": ["personal-assistant", "mcp", "calendar", "email", "productivity"],
        "scope": "specialized",
        "training_qa": [
            {"question": "How do I schedule a meeting?", "answer": "I can access your calendar through the MCP calendar server and create meetings with automatic conflict detection and attendee notifications."},
            {"question": "Can you manage my emails?", "answer": "Yes, I can read, compose, send, and organize your emails using the email MCP server integration."}
        ],
        "tools": {
            "calendar": {"enabled": True, "apiKey": "mcp://calendar-server"},
            "email": {"enabled": True, "apiKey": "mcp://email-server"},
            "file-system": {"enabled": True}
        }
    },
    {
        "name": "Financial Advisor (MCP Enhanced)",
        "description": "Comprehensive financial advisory with market data and portfolio analysis via MCP",
        "category": "Finance",
        "personality": "analytical",
        "instructions": "You are a professional financial advisor with access to real-time market data, portfolio analysis tools, and financial planning resources through MCP servers.",
        "is_public": True,
        "tags": ["finance", "investment", "mcp", "market-data", "portfolio"],
        "scope": "expert",
        "training_qa": [
            {"question": "What's my portfolio performance?", "answer": "I can analyze your portfolio using real-time market data through the financial MCP server and provide comprehensive performance metrics."},
            {"question": "Should I invest in tech stocks?", "answer": "Let me analyze current market conditions and your risk profile using the market data MCP integration to provide personalized investment advice."}
        ],
        "tools": {
            "web-search": {"enabled": True, "apiKey": "search_api_key_here"},
            "api-client": {"enabled": True, "apiKey": "financial_api_key_here"},
            "database": {"enabled": True, "config": {"host": "localhost", "port": "5432", "database": "financial_data"}}
        }
    },
    {
        "name": "Healthcare Assistant (HIPAA Compliant)",
        "description": "Medical assistant with patient management and appointment scheduling capabilities",
        "category": "Healthcare",
        "personality": "empathetic",
        "instructions": "You are a healthcare assistant specializing in patient communication, appointment management, and basic medical information. Always maintain HIPAA compliance.",
        "is_public": False,
        "tags": ["healthcare", "appointments", "patient-care", "hipaa"],
        "scope": "domain-specific",
        "training_qa": [
            {"question": "How do I schedule a medical appointment?", "answer": "I can help you schedule appointments while ensuring all patient information remains secure and HIPAA compliant."},
            {"question": "What are the clinic hours?", "answer": "I have access to current clinic schedules and can provide accurate availability information."}
        ],
        "tools": {
            "calendar": {"enabled": True, "apiKey": "medical_calendar_api"},
            "email": {"enabled": True, "apiKey": "secure_email_api"}
        }
    },
    {
        "name": "E-commerce Support Specialist",
        "description": "Customer support for online stores with order tracking and inventory management",
        "category": "Customer Support",
        "personality": "helpful",
        "instructions": "You are an e-commerce customer support specialist with access to order management, inventory systems, and customer databases.",
        "is_public": True,
        "tags": ["ecommerce", "customer-support", "orders", "inventory"],
        "scope": "specialized",
        "training_qa": [
            {"question": "Where is my order?", "answer": "I can track your order status using our integrated order management system and provide real-time updates."},
            {"question": "Is this item in stock?", "answer": "Let me check our current inventory levels through the inventory management integration."}
        ],
        "tools": {
            "api-client": {"enabled": True, "apiKey": "ecommerce_api_key"},
            "email": {"enabled": True, "apiKey": "support_email_api"},
            "web-search": {"enabled": True, "apiKey": "product_search_api"}
        }
    },
    {
        "name": "Real Estate Agent Assistant",
        "description": "Property search and client management for real estate professionals",
        "category": "Real Estate",
        "personality": "enthusiastic",
        "instructions": "You are a real estate assistant helping agents with property searches, client communications, and market analysis.",
        "is_public": True,
        "tags": ["real-estate", "property", "mls", "clients"],
        "scope": "specialized",
        "training_qa": [
            {"question": "Find properties under $500k", "answer": "I can search MLS data and property databases to find suitable properties within your budget range."},
            {"question": "Schedule property viewing", "answer": "I can coordinate property viewings and manage your showing schedule."}
        ],
        "tools": {
            "maps": {"enabled": True, "apiKey": "maps_api_key"},
            "calendar": {"enabled": True, "apiKey": "realtor_calendar_api"},
            "api-client": {"enabled": True, "apiKey": "mls_api_key"}
        }
    },
    {
        "name": "Travel Concierge (Global)",
        "description": "Comprehensive travel planning with booking capabilities and local recommendations",
        "category": "Travel",
        "personality": "adventurous",
        "instructions": "You are a travel concierge with access to booking systems, weather data, and local information to create perfect travel experiences.",
        "is_public": True,
        "tags": ["travel", "booking", "weather", "recommendations"],
        "scope": "general",
        "training_qa": [
            {"question": "Plan a trip to Tokyo", "answer": "I can create a comprehensive Tokyo itinerary using weather data, local recommendations, and booking integrations."},
            {"question": "What's the weather like in Paris?", "answer": "I can provide current and forecast weather conditions for Paris using integrated weather services."}
        ],
        "tools": {
            "weather": {"enabled": True, "apiKey": "weather_api_key"},
            "maps": {"enabled": True, "apiKey": "travel_maps_api"},
            "translation": {"enabled": True, "apiKey": "translation_api"},
            "web-search": {"enabled": True, "apiKey": "travel_search_api"}
        }
    }
]


async def create_template_table():
    """Create templates table if it doesn't exist"""
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS templates (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100) NOT NULL,
                personality VARCHAR(50) NOT NULL,
                instructions TEXT,
                is_public BOOLEAN DEFAULT FALSE,
                is_favorite BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                usage_count INTEGER DEFAULT 0,
                author VARCHAR(255),
                tags TEXT[], -- PostgreSQL array type
                scope VARCHAR(50) DEFAULT 'general',
                training_qa JSONB,
                tools JSONB,
                integrations JSONB,
                user_id INTEGER REFERENCES users(id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
            CREATE INDEX IF NOT EXISTS idx_templates_public ON templates(is_public);
            CREATE INDEX IF NOT EXISTS idx_templates_user ON templates(user_id);
            CREATE INDEX IF NOT EXISTS idx_templates_tags ON templates USING GIN(tags);
        """))
    
    await engine.dispose()


async def seed_razorflow_test_data():
    """Create comprehensive test data for RazorFlow testing"""
    
    print("🚀 Starting RazorFlow Test Data Seeding...")
    print("=" * 60)
    
    # Create engine and session
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )
    
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        # Create templates table first
        await create_template_table()
        print("✅ Templates table created/verified")
        
        async with async_session() as session:
            # 1. Create test user: Razor303 (jc) at RazorFlow-AI
            print("\n👤 Creating primary test user...")
            
            existing_user = await session.execute(
                select(User).where(User.email == "jc@razorflow-ai.com")
            )
            user = existing_user.scalar_one_or_none()
            
            if not user:
                user = User(
                    email="jc@razorflow-ai.com",
                    password_hash=hash_password("Password123!"),
                    first_name="Razor303",
                    last_name="JC",
                    company_name="RazorFlow-AI",
                    phone="+1-555-0123",
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True,
                    openai_api_key="sk-test-razorflow-key",
                    preferred_language="en",
                    timezone="America/New_York"
                )
                session.add(user)
                await session.flush()  # Get the ID
                print(f"✅ Created user: {user.email} (ID: {user.id})")
            else:
                print(f"⚠️  User {user.email} already exists (ID: {user.id})")
            
            # 2. Create additional test users
            print("\n👥 Creating additional test users...")
            
            additional_users = [
                {
                    "email": "admin@razorflow-ai.com",
                    "password": "AdminPass123!",
                    "first_name": "Admin",
                    "last_name": "User",
                    "company_name": "RazorFlow-AI",
                    "role": UserRole.ADMIN
                },
                {
                    "email": "client@razorflow-ai.com", 
                    "password": "ClientPass123!",
                    "first_name": "Test",
                    "last_name": "Client",
                    "company_name": "Client Corp",
                    "role": UserRole.CLIENT
                }
            ]
            
            for user_data in additional_users:
                existing = await session.execute(
                    select(User).where(User.email == user_data["email"])
                )
                if not existing.scalar_one_or_none():
                    new_user = User(
                        email=user_data["email"],
                        password_hash=hash_password(user_data["password"]),
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        company_name=user_data["company_name"],
                        role=user_data["role"],
                        is_active=True,
                        is_verified=True
                    )
                    session.add(new_user)
                    print(f"✅ Created user: {user_data['email']}")
                else:
                    print(f"⚠️  User {user_data['email']} already exists")
            
            await session.flush()
            
            # 3. Create test clients
            print("\n🏢 Creating test clients...")
            
            test_clients = [
                {
                    "name": "RazorFlow Tech Solutions",
                    "email": "contact@razorflow-tech.com",
                    "company": "RazorFlow Tech Solutions",
                    "website": "https://razorflow-tech.com",
                    "phone": "+1-555-0101",
                    "industry": "Technology",
                    "description": "Leading AI and automation solutions provider",
                    "status": "active",
                    "priority_level": "vip",
                    "monthly_budget": 15000.00
                },
                {
                    "name": "Digital Marketing Pro",
                    "email": "hello@digitalmarketingpro.com",
                    "company": "Digital Marketing Pro",
                    "website": "https://digitalmarketingpro.com",
                    "phone": "+1-555-0102",
                    "industry": "Marketing",
                    "description": "Full-service digital marketing agency",
                    "status": "active",
                    "priority_level": "high",
                    "monthly_budget": 8500.00
                },
                {
                    "name": "HealthTech Innovations",
                    "email": "info@healthtech-innovations.com",
                    "company": "HealthTech Innovations",
                    "website": "https://healthtech-innovations.com",
                    "phone": "+1-555-0103",
                    "industry": "Healthcare",
                    "description": "Healthcare technology and patient management solutions",
                    "status": "active",
                    "priority_level": "high",
                    "monthly_budget": 12000.00
                }
            ]
            
            for client_data in test_clients:
                existing_client = await session.execute(
                    select(Client).where(Client.email == client_data["email"])
                )
                if not existing_client.scalar_one_or_none():
                    client = Client(
                        name=client_data["name"],
                        email=client_data["email"],
                        company=client_data["company"],
                        website=client_data["website"],
                        phone=client_data["phone"],
                        industry=client_data["industry"],
                        description=client_data["description"],
                        status=client_data["status"],
                        priority_level=client_data["priority_level"],
                        monthly_budget=client_data["monthly_budget"],
                        user_id=user.id
                    )
                    session.add(client)
                    print(f"✅ Created client: {client_data['name']}")
                else:
                    print(f"⚠️  Client {client_data['email']} already exists")
            
            await session.flush()
            
            # 4. Create enhanced templates with MCP integration
            print("\n📝 Creating enhanced templates...")
            
            for template_data in ENHANCED_TEMPLATES:
                # Check if template exists
                existing_template = await session.execute(
                    text("SELECT id FROM templates WHERE name = :name"),
                    {"name": template_data["name"]}
                )
                if not existing_template.scalar_one_or_none():
                    await session.execute(
                        text("""
                            INSERT INTO templates (
                                name, description, category, personality, instructions,
                                is_public, tags, scope, training_qa, tools, author, user_id
                            ) VALUES (
                                :name, :description, :category, :personality, :instructions,
                                :is_public, :tags, :scope, :training_qa, :tools, :author, :user_id
                            )
                        """),
                        {
                            "name": template_data["name"],
                            "description": template_data["description"],
                            "category": template_data["category"],
                            "personality": template_data["personality"],
                            "instructions": template_data["instructions"],
                            "is_public": template_data["is_public"],
                            "tags": template_data["tags"],
                            "scope": template_data["scope"],
                            "training_qa": json.dumps(template_data["training_qa"]),
                            "tools": json.dumps(template_data["tools"]),
                            "author": "Razor303 JC",
                            "user_id": user.id
                        }
                    )
                    print(f"✅ Created template: {template_data['name']}")
                else:
                    print(f"⚠️  Template {template_data['name']} already exists")
            
            # 5. Create sample chatbots/projects
            print("\n🤖 Creating sample projects...")
            
            # Get first client for projects
            first_client = await session.execute(
                select(Client).where(Client.user_id == user.id).limit(1)
            )
            client = first_client.scalar_one_or_none()
            
            if client:
                sample_projects = [
                    {
                        "name": "Executive Assistant Bot",
                        "description": "Personal assistant for executive management",
                        "project_type": ChatbotType.CHATBOT,
                        "complexity": ChatbotComplexity.ADVANCED,
                        "status": ChatbotStatus.COMPLETED,
                        "personality_type": "professional",
                        "system_prompt": "You are a professional executive assistant.",
                        "progress_percentage": 100
                    },
                    {
                        "name": "Customer Support Bot",
                        "description": "24/7 customer support automation",
                        "project_type": ChatbotType.CHATBOT,
                        "complexity": ChatbotComplexity.ENTERPRISE,
                        "status": ChatbotStatus.DEPLOYED,
                        "personality_type": "helpful",
                        "system_prompt": "You are a helpful customer support agent.",
                        "progress_percentage": 100
                    }
                ]
                
                for project_data in sample_projects:
                    existing_bot = await session.execute(
                        select(Chatbot).where(
                            Chatbot.name == project_data["name"],
                            Chatbot.user_id == user.id
                        )
                    )
                    if not existing_bot.scalar_one_or_none():
                        chatbot = Chatbot(
                            name=project_data["name"],
                            description=project_data["description"],
                            project_type=project_data["project_type"],
                            complexity=project_data["complexity"],
                            status=project_data["status"],
                            personality_type=project_data["personality_type"],
                            system_prompt=project_data["system_prompt"],
                            progress_percentage=project_data["progress_percentage"],
                            user_id=user.id,
                            client_id=client.id,
                            is_deployed=project_data["status"] == ChatbotStatus.DEPLOYED
                        )
                        session.add(chatbot)
                        print(f"✅ Created project: {project_data['name']}")
                    else:
                        print(f"⚠️  Project {project_data['name']} already exists")
            
            # Commit all changes
            await session.commit()
            
            print("\n🎉 RazorFlow Test Data Seeding Complete!")
            print("=" * 60)
            print("\n📋 Test Credentials:")
            print(f"Primary User: jc@razorflow-ai.com / Password123!")
            print(f"Admin User: admin@razorflow-ai.com / AdminPass123!")
            print(f"Client User: client@razorflow-ai.com / ClientPass123!")
            
            print("\n🌐 Frontend Access:")
            print(f"URL: http://localhost:3002")
            print(f"Login with any of the above credentials")
            
            print("\n🧪 Test Data Summary:")
            print(f"✅ {len(additional_users) + 1} Users created")
            print(f"✅ {len(test_clients)} Clients created")
            print(f"✅ {len(ENHANCED_TEMPLATES)} Enhanced Templates created")
            print(f"✅ Sample projects and chatbots created")
            
            print("\n🚀 Ready for human-like workflow testing!")
            
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_razorflow_test_data())