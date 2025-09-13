# 🚀 POST VSCODE CRASH RECOVERY GUIDE
## Pixel AI Creator - Complete Setup After Fresh Clone

### 📋 **Quick Start Checklist**

After VSCode crash, follow these steps for complete recovery:

#### ✅ **1. Fresh Clone & Basic Setup**
```bash
# Clone the repository
git clone https://github.com/razor303Jc/Pixel-AI-Creator.git
cd Pixel-AI-Creator

# Choose your branch
git checkout playwright-ui-tests  # For latest test work
# OR
git checkout dev                  # For clean base

# Run automated setup
chmod +x POST_CLONE_SETUP.sh
./POST_CLONE_SETUP.sh
```

#### ✅ **2. Manual Configuration Files**
The setup script creates these automatically, but you can also copy manually:

```bash
# Essential config files
cp ENHANCED_GITIGNORE.template .gitignore
cp VSCODE_SETTINGS.template .vscode/settings.json  
cp PRETTIERRC.template .prettierrc
cp EDITORCONFIG.template .editorconfig
cp DOCKER_COMPOSE_OVERRIDE.template docker-compose.override.yml
```

#### ✅ **3. Environment Setup**
```bash
# Update .env file with your keys
nano .env

# Essential variables to set:
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
SECRET_KEY=your-secret-key
```

#### ✅ **4. Python Environment**
```bash
# Create and activate virtual environment
python3 -m venv api_venv
source api_venv/bin/activate

# Install dependencies
pip install -r api/requirements.txt
pip install -r requirements-test.txt
```

#### ✅ **5. Node.js Dependencies**
```bash
# Frontend dependencies
cd frontend && npm install && cd ..

# Test dependencies (if tests/package.json exists)
cd tests && npm install && cd ..

# Playwright setup
npx playwright install
```

#### ✅ **6. Docker Services**
```bash
# Start all services
docker-compose up -d

# Check services are running
curl http://localhost:3002  # Frontend
curl http://localhost:8002  # Backend API
```

---

### 🔧 **Configuration Files Overview**

#### **📄 .gitignore (Enhanced)**
- Comprehensive Python/Node.js ignores
- AI/ML specific exclusions
- Security-focused (API keys, secrets)
- Development tool exclusions
- Docker and environment files

#### **⚙️ VSCode Settings**
- Python environment: `./api_venv/bin/python`
- Formatting: Black (Python), Prettier (JS/TS)
- Testing: Pytest, Playwright integration
- Git integration and auto-fetch
- Terminal: ZSH with custom settings

#### **🎨 Prettier Config**
- Line width: 88 (matches Black)
- Single quotes, trailing commas
- 2-space indentation (JS/TS)
- Custom overrides for MD, JSON, YAML

#### **📝 EditorConfig**
- UTF-8 encoding, LF line endings
- Python: 4 spaces, 88 char limit
- JS/TS/JSON: 2 spaces
- Markdown: 80 char limit
- Trim whitespace, final newlines

#### **🐳 Docker Override**
- Development environment settings
- Hot reload for frontend/backend
- PostgreSQL database for testing
- Redis for caching
- Nginx for local SSL

---

### 🧪 **Testing Setup**

#### **Playwright Configuration**
```bash
# Run comprehensive UI tests
npx playwright test --headed --reporter=list

# Specific test files
npx playwright test tests/test_frontend_complete_qa.spec.js --headed

# Debug mode
npx playwright test --debug
```

#### **Python Testing**
```bash
# Activate environment
source api_venv/bin/activate

# Run API tests
pytest api/tests/

# Run with coverage
pytest --cov=api api/tests/
```

---

### 🚀 **Development Workflow**

#### **Start Development Servers**
```bash
# Option 1: Docker (recommended)
docker-compose up -d

# Option 2: Manual
# Terminal 1 - Backend
source api_venv/bin/activate
python api/main.py

# Terminal 2 - Frontend  
cd frontend
npm start
```

#### **Running Tests**
```bash
# UI Tests (Playwright)
npx playwright test --headed

# API Tests (Pytest)
source api_venv/bin/activate
pytest

# Full test suite
./scripts/run_all_tests.sh
```

#### **Code Quality**
```bash
# Python formatting
black api/
isort api/

# JavaScript formatting  
npx prettier --write frontend/src/

# Linting
flake8 api/
npx eslint frontend/src/
```

---

### 📁 **Directory Structure**

```
Pixel-AI-Creator/
├── .vscode/               # VSCode configuration
├── api/                   # FastAPI backend
│   ├── main.py           # Application entry
│   ├── requirements.txt  # Python dependencies
│   └── tests/            # Backend tests
├── frontend/             # React frontend
│   ├── src/              # Source code
│   ├── package.json      # Node dependencies
│   └── public/           # Static assets
├── tests/                # Playwright E2E tests
├── logs/                 # Application logs
├── test-reports/         # Test results
├── docker/               # Docker configurations
├── scripts/              # Utility scripts
├── .env                  # Environment variables
├── docker-compose.yml    # Docker services
└── POST_CLONE_SETUP.sh   # This setup script
```

---

### 🔍 **Troubleshooting**

#### **Common Issues & Solutions**

**🐛 File Writing Issues (VSCode Crash)**
```bash
# Solution: Fresh clone
rm -rf Pixel-AI-Creator
git clone https://github.com/razor303Jc/Pixel-AI-Creator.git
```

**🐛 Python Environment Issues**
```bash
# Recreate virtual environment
rm -rf api_venv
python3 -m venv api_venv
source api_venv/bin/activate
pip install -r api/requirements.txt
```

**🐛 Node Dependencies Issues**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**🐛 Docker Issues**
```bash
# Reset Docker state
docker-compose down
docker system prune -f
docker-compose up -d
```

**🐛 Port Conflicts**
```bash
# Check what's using ports
lsof -i :3002  # Frontend
lsof -i :8002  # Backend

# Kill processes if needed
kill -9 $(lsof -t -i:3002)
```

---

### 🎯 **Next Steps**

1. **✅ Complete setup** using this guide
2. **🧪 Run test suite** to verify everything works
3. **💬 Create chat tests** for UI interaction testing
4. **🚀 Continue development** with clean environment

#### **Verification Commands**
```bash
# Check all services
curl http://localhost:3002 | grep -i title  # Should show "Pixel AI Creator"
curl http://localhost:8002 | head -1        # Should show welcome JSON

# Run basic tests
npx playwright test tests/test_frontend_complete_qa.spec.js --headed
```

---

### 📞 **Support**

If you encounter issues:
1. Check logs: `tail -f logs/app.log`
2. Verify environment: `source api_venv/bin/activate && python --version`
3. Test services: Run verification commands above
4. Fresh restart: `docker-compose restart`

**🎉 You're ready to continue development!**
