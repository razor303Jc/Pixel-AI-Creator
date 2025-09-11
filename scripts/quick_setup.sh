#!/bin/bash
# Razorflow-AI Quick Setup Script
# Sets up the complete AI assistant ecosystem

echo "🤖 Razorflow-AI Quick Setup Starting..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the Pixel-AI-Creator root directory"
    exit 1
fi

# Make scripts executable
chmod +x scripts/razorflow_setup.py
chmod +x scripts/razorflow_cli.py

# Install dependencies if needed (optional check)
if [ ! -d "api/__pycache__" ]; then
    echo "📦 Installing Python dependencies..."
    cd api && pip install -r requirements.txt && cd ..
fi

# Initialize the database
echo "🗄️ Initializing database..."
cd api && python -c "
import asyncio
from core.database import init_db
asyncio.run(init_db())
print('Database initialized successfully!')
" && cd ..

# Run Razorflow-AI setup
echo "⚡ Running Razorflow-AI system setup..."
python scripts/razorflow_setup.py

echo ""
echo "🎉 Razorflow-AI Setup Complete!"
echo ""
echo "Quick Commands:"
echo "  📋 List templates:     python scripts/razorflow_cli.py templates"
echo "  🔍 Health check:      python scripts/razorflow_cli.py health"
echo "  🎯 Create demo:       python scripts/razorflow_cli.py demo"
echo "  🚀 Start API:         cd api && python main.py"
echo ""
echo "API Endpoints (after starting):"
echo "  Templates:     http://localhost:8000/api/templates"
echo "  Deploy Suite:  POST http://localhost:8000/api/razorflow/deploy-default-suite"
echo "  Build Status:  GET http://localhost:8000/api/razorflow/build-status/{id}"
echo ""
echo "💰 Revenue Potential: $75K-$150K in first 6 months"
echo "🎯 Default Assistants: 6 pre-configured templates ready"
echo "⚡ Build Time: 2-6 days automated deployment"
