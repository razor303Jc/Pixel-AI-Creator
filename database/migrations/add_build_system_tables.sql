-- 🏗️ BUILD SYSTEM DATABASE MIGRATION
-- Adds tables required for comprehensive build flow functionality

-- Create builds table for tracking build jobs
CREATE TABLE IF NOT EXISTS builds (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'queued' CHECK (status IN ('queued', 'building', 'completed', 'failed', 'cancelled')),
    
    -- Timing information
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Build metadata
    build_logs TEXT[] DEFAULT '{}',
    error_message TEXT,
    
    -- Container information
    container_id VARCHAR(100),
    image_name VARCHAR(200),
    image_tag VARCHAR(50) DEFAULT 'latest',
    
    -- Deployment information
    deployment_url VARCHAR(500),
    deployment_status VARCHAR(50) DEFAULT 'pending',
    
    -- Build configuration
    build_config JSONB DEFAULT '{}',
    
    -- Progress tracking
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    
    -- Task management
    task_id VARCHAR(100),  -- Celery task ID
    
    UNIQUE(project_id, created_at)
);

-- Create build artifacts table for storing generated files
CREATE TABLE IF NOT EXISTS build_artifacts (
    id SERIAL PRIMARY KEY,
    build_id INTEGER REFERENCES builds(id) ON DELETE CASCADE,
    artifact_type VARCHAR(50) NOT NULL, -- 'dockerfile', 'source_code', 'config', 'logs'
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    content_hash VARCHAR(64), -- SHA256 hash for integrity
    content TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create build templates table for storing reusable build configurations
CREATE TABLE IF NOT EXISTS build_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL, -- 'dockerfile', 'source', 'config'
    template_content TEXT NOT NULL,
    variables JSONB DEFAULT '{}', -- Template variable definitions
    is_public BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    usage_count INTEGER DEFAULT 0
);

-- Create deployment environments table
CREATE TABLE IF NOT EXISTS deployment_environments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'development', 'staging', 'production'
    config JSONB NOT NULL, -- Environment-specific configuration
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create build logs table for detailed logging
CREATE TABLE IF NOT EXISTS build_logs (
    id SERIAL PRIMARY KEY,
    build_id INTEGER REFERENCES builds(id) ON DELETE CASCADE,
    log_level VARCHAR(20) DEFAULT 'INFO', -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    message TEXT NOT NULL,
    step VARCHAR(100), -- Build step name
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_builds_project_id ON builds(project_id);
CREATE INDEX IF NOT EXISTS idx_builds_status ON builds(status);
CREATE INDEX IF NOT EXISTS idx_builds_created_at ON builds(created_at);
CREATE INDEX IF NOT EXISTS idx_builds_user_id ON builds(user_id);
CREATE INDEX IF NOT EXISTS idx_build_artifacts_build_id ON build_artifacts(build_id);
CREATE INDEX IF NOT EXISTS idx_build_artifacts_type ON build_artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_build_logs_build_id ON build_logs(build_id);
CREATE INDEX IF NOT EXISTS idx_build_logs_level ON build_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_build_templates_type ON build_templates(template_type);

-- Add updated_at trigger for builds table
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create updated_at column and trigger for builds table
ALTER TABLE builds ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
CREATE TRIGGER update_builds_updated_at BEFORE UPDATE ON builds 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample build templates
INSERT INTO build_templates (name, description, template_type, template_content, variables, is_public) VALUES
(
    'FastAPI Assistant Base',
    'Basic FastAPI application template for AI assistants',
    'source',
    'from fastapi import FastAPI\napp = FastAPI(title="{{CHATBOT_NAME}}")\n\n@app.get("/")\ndef root():\n    return {"message": "{{CHATBOT_DESCRIPTION}}"}',
    '{"CHATBOT_NAME": "string", "CHATBOT_DESCRIPTION": "string"}',
    true
),
(
    'Standard Dockerfile',
    'Production-ready Dockerfile for Python AI assistants',
    'dockerfile',
    'FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nEXPOSE {{PORT}}\nCMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{{PORT}}"]',
    '{"PORT": "8000"}',
    true
),
(
    'Basic Requirements',
    'Standard Python requirements for AI assistants',
    'config',
    'fastapi==0.104.1\nuvicorn==0.24.0\nopenai==1.3.0\npydantic==2.5.0\npython-dotenv==1.0.0',
    '{}',
    true
) ON CONFLICT DO NOTHING;

-- Insert sample deployment environment
INSERT INTO deployment_environments (name, type, config) VALUES
(
    'Development',
    'development',
    '{"registry": "localhost:5000", "namespace": "pixel-ai-dev", "resources": {"cpu": "0.5", "memory": "512Mi"}}'
),
(
    'Production',
    'production', 
    '{"registry": "ghcr.io", "namespace": "pixel-ai-prod", "resources": {"cpu": "1", "memory": "1Gi"}}'
) ON CONFLICT DO NOTHING;

-- Create a view for build status overview
CREATE OR REPLACE VIEW build_status_overview AS
SELECT 
    b.id,
    b.project_id,
    p.name as project_name,
    u.email as user_email,
    b.status,
    b.progress,
    b.created_at,
    b.started_at,
    b.completed_at,
    b.deployment_url,
    CASE 
        WHEN b.completed_at IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (b.completed_at - b.created_at))
        WHEN b.started_at IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (NOW() - b.started_at))
        ELSE NULL
    END as duration_seconds,
    COUNT(bl.id) as log_count,
    COUNT(ba.id) as artifact_count
FROM builds b
LEFT JOIN projects p ON b.project_id = p.id
LEFT JOIN users u ON b.user_id = u.id
LEFT JOIN build_logs bl ON b.id = bl.build_id
LEFT JOIN build_artifacts ba ON b.id = ba.build_id
GROUP BY b.id, p.name, u.email;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON builds TO pixel_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON build_artifacts TO pixel_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON build_templates TO pixel_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON deployment_environments TO pixel_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON build_logs TO pixel_user;
-- GRANT SELECT ON build_status_overview TO pixel_user;

-- Add comments for documentation
COMMENT ON TABLE builds IS 'Tracks build jobs for AI assistant projects';
COMMENT ON TABLE build_artifacts IS 'Stores generated files and artifacts from builds';
COMMENT ON TABLE build_templates IS 'Reusable templates for build configurations';
COMMENT ON TABLE deployment_environments IS 'Environment configurations for deployments';
COMMENT ON TABLE build_logs IS 'Detailed logs for build processes';
COMMENT ON VIEW build_status_overview IS 'Comprehensive view of build status with project details';

-- Success message
SELECT 'Build system database migration completed successfully!' as message;