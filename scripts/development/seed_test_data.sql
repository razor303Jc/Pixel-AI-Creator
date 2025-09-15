-- RazorFlow Test User Seed Script
-- Creates test data for user: jc@razorflow-ai.com

-- Create the test user if not exists
INSERT INTO users (
    email, password_hash, first_name, last_name, company_name, phone,
    role, is_active, is_verified, openai_api_key, preferred_language, timezone
) VALUES (
    'jc@razorflow-ai.com',
    '$2b$12$LQv3c1yqBwEHxPuNYuR1zOsQsC/G8n/k.7GZz8L9nOp.8XmZ7FeRe', -- Password123!
    'Razor303',
    'JC', 
    'RazorFlow-AI',
    '+1-555-0123',
    'admin',
    true,
    true,
    'sk-test-razorflow-key',
    'en',
    'America/New_York'
) ON CONFLICT (email) DO NOTHING;

-- Get the user ID for relationships
DO $$
DECLARE
    user_id_var INTEGER;
    client_id_var INTEGER;
BEGIN
    -- Get user ID
    SELECT id INTO user_id_var FROM users WHERE email = 'jc@razorflow-ai.com';
    
    -- Create test client
    INSERT INTO clients (
        name, email, company, website, phone, industry, description,
        status, priority_level, monthly_budget, user_id
    ) VALUES (
        'RazorFlow Tech Solutions',
        'contact@razorflow-tech.com',
        'RazorFlow Tech Solutions',
        'https://razorflow-tech.com',
        '+1-555-0101',
        'Technology',
        'Leading AI and automation solutions provider',
        'active',
        'vip',
        15000.00,
        user_id_var
    ) ON CONFLICT (email) DO NOTHING
    RETURNING id INTO client_id_var;
    
    -- If no returning value (conflict), get existing client ID
    IF client_id_var IS NULL THEN
        SELECT id INTO client_id_var FROM clients WHERE email = 'contact@razorflow-tech.com';
    END IF;
    
    -- Create sample chatbot project
    INSERT INTO chatbots (
        name, description, project_type, complexity, status, 
        personality_type, system_prompt, progress_percentage,
        user_id, client_id, is_deployed
    ) VALUES (
        'Executive Assistant Bot',
        'Personal assistant for executive management with MCP integration',
        'chatbot',
        'advanced',
        'completed',
        'professional',
        'You are a professional executive assistant with MCP server access.',
        100,
        user_id_var,
        client_id_var,
        true
    ) ON CONFLICT DO NOTHING;
    
END $$;

-- Create templates table if it doesn't exist
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
    tags TEXT[],
    scope VARCHAR(50) DEFAULT 'general',
    training_qa JSONB,
    tools JSONB,
    integrations JSONB,
    user_id INTEGER REFERENCES users(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
CREATE INDEX IF NOT EXISTS idx_templates_public ON templates(is_public);
CREATE INDEX IF NOT EXISTS idx_templates_user ON templates(user_id);
CREATE INDEX IF NOT EXISTS idx_templates_tags ON templates USING GIN(tags);

-- Insert enhanced templates
DO $$
DECLARE
    user_id_var INTEGER;
BEGIN
    SELECT id INTO user_id_var FROM users WHERE email = 'jc@razorflow-ai.com';
    
    -- Executive Personal Assistant Template
    INSERT INTO templates (
        name, description, category, personality, instructions,
        is_public, tags, scope, training_qa, tools, author, user_id
    ) VALUES (
        'Executive Personal Assistant (MCP)',
        'AI assistant with MCP server integration for calendar, email, and file management',
        'PA',
        'professional',
        'You are an executive personal assistant with access to calendar management, email handling, and file organization. Use MCP server tools to efficiently manage schedules, communications, and documents.',
        true,
        ARRAY['personal-assistant', 'mcp', 'calendar', 'email', 'productivity'],
        'specialized',
        '[
            {"question": "How do I schedule a meeting?", "answer": "I can access your calendar through the MCP calendar server and create meetings with automatic conflict detection."},
            {"question": "Can you manage my emails?", "answer": "Yes, I can read, compose, send, and organize your emails using the email MCP server integration."}
        ]'::jsonb,
        '{
            "calendar": {"enabled": true, "apiKey": "mcp://calendar-server"},
            "email": {"enabled": true, "apiKey": "mcp://email-server"},
            "file-system": {"enabled": true}
        }'::jsonb,
        'Razor303 JC',
        user_id_var
    ) ON CONFLICT (name) DO NOTHING;
    
    -- Financial Advisor Template
    INSERT INTO templates (
        name, description, category, personality, instructions,
        is_public, tags, scope, training_qa, tools, author, user_id
    ) VALUES (
        'Financial Advisor (MCP Enhanced)',
        'Comprehensive financial advisory with market data and portfolio analysis via MCP',
        'Finance',
        'analytical',
        'You are a professional financial advisor with access to real-time market data, portfolio analysis tools, and financial planning resources through MCP servers.',
        true,
        ARRAY['finance', 'investment', 'mcp', 'market-data', 'portfolio'],
        'expert',
        '[
            {"question": "What is my portfolio performance?", "answer": "I can analyze your portfolio using real-time market data through the financial MCP server."},
            {"question": "Should I invest in tech stocks?", "answer": "Let me analyze current market conditions and your risk profile using market data integration."}
        ]'::jsonb,
        '{
            "web-search": {"enabled": true, "apiKey": "search_api_key_here"},
            "api-client": {"enabled": true, "apiKey": "financial_api_key_here"},
            "database": {"enabled": true, "config": {"host": "localhost", "port": "5432", "database": "financial_data"}}
        }'::jsonb,
        'Razor303 JC',
        user_id_var
    ) ON CONFLICT (name) DO NOTHING;
    
    -- E-commerce Support Template
    INSERT INTO templates (
        name, description, category, personality, instructions,
        is_public, tags, scope, training_qa, tools, author, user_id
    ) VALUES (
        'E-commerce Support Specialist',
        'Customer support for online stores with order tracking and inventory management',
        'Customer Support',
        'helpful',
        'You are an e-commerce customer support specialist with access to order management, inventory systems, and customer databases.',
        true,
        ARRAY['ecommerce', 'customer-support', 'orders', 'inventory'],
        'specialized',
        '[
            {"question": "Where is my order?", "answer": "I can track your order status using our integrated order management system."},
            {"question": "Is this item in stock?", "answer": "Let me check our current inventory levels through the inventory management integration."}
        ]'::jsonb,
        '{
            "api-client": {"enabled": true, "apiKey": "ecommerce_api_key"},
            "email": {"enabled": true, "apiKey": "support_email_api"},
            "web-search": {"enabled": true, "apiKey": "product_search_api"}
        }'::jsonb,
        'Razor303 JC',
        user_id_var
    ) ON CONFLICT (name) DO NOTHING;
    
END $$;

-- Verify the data
SELECT 'Users created:', COUNT(*) FROM users WHERE email LIKE '%razorflow%';
SELECT 'Clients created:', COUNT(*) FROM clients WHERE company LIKE '%RazorFlow%';
SELECT 'Templates created:', COUNT(*) FROM templates WHERE author = 'Razor303 JC';
SELECT 'Projects created:', COUNT(*) FROM chatbots WHERE name LIKE '%Assistant%';