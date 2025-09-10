-- Initialize Pixel AI Creator Database
-- This script sets up the initial database structure

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS pixel_ai;

-- Create user if it doesn't exist  
CREATE USER IF NOT EXISTS pixel_user WITH PASSWORD 'pixel_secure_2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE pixel_ai TO pixel_user;

-- Connect to the database
\c pixel_ai;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial admin/demo data (optional)
-- This will be handled by SQLAlchemy models, but we can add seed data here

-- Example: Insert demo client data
-- INSERT INTO clients (name, email, company, website, industry, description, created_at, updated_at) 
-- VALUES 
-- ('Demo Restaurant', 'demo@restaurant.com', 'Pizza Palace', 'https://pizzapalace.com', 'Food & Beverage', 'A local pizzeria looking to automate customer service', NOW(), NOW()),
-- ('Tech Startup', 'demo@techstartup.com', 'InnovateTech', 'https://innovatetech.io', 'Technology', 'SaaS company needing AI customer support', NOW(), NOW());

COMMIT;
