# Pixel-AI-Creator Directory Structure

This document describes the organized directory structure of the Pixel-AI-Creator project after cleanup.

## 📁 Root Directory Structure

```
Pixel-AI-Creator/
├── 📄 README.md                    # Main project documentation
├── 📄 .env.example                 # Environment template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 docker-compose*.yml          # Docker orchestration files
├── 📄 playwright.config.js         # End-to-end test configuration
├── 📄 pytest.ini                   # Python test configuration
├── 📄 requirements-test.txt        # Test dependencies
│
├── 📁 api/                         # FastAPI backend application
│   ├── routes/                     # API endpoint definitions
│   ├── services/                   # Business logic services
│   ├── models/                     # Database models
│   ├── core/                       # Core configuration
│   └── ...
│
├── 📁 frontend/                    # React TypeScript frontend
│   ├── src/                        # Source code
│   ├── public/                     # Static assets
│   ├── package.json                # NPM dependencies
│   └── ...
│
├── 📁 docs/                        # Documentation
│   ├── development/                # Development documentation
│   │   ├── APP_REVIEW_COMPREHENSIVE.md
│   │   ├── DEVELOPMENT_PROGRESS_SUMMARY.md
│   │   └── TODO_CRITICAL_DEVELOPMENT.md
│   ├── reports/                    # Status and completion reports
│   │   ├── AUTHENTICATION_SYSTEM_COMPLETE.md
│   │   ├── FILE_UPLOAD_SYSTEM_COMPLETION_REPORT.md
│   │   ├── FRONTEND_BACKEND_INTEGRATION_SUCCESS.md
│   │   ├── TEST_REPORT_COMPREHENSIVE.md
│   │   └── ...
│   └── status-reports/             # Legacy status reports
│
├── 📁 tests/                       # Test suite
│   ├── integration/                # Integration tests
│   │   ├── test_file_upload_system.py
│   │   ├── test_ai_integration.py
│   │   ├── test_auth.py
│   │   └── ...
│   ├── system/                     # System-level tests
│   │   ├── final_system_report.py
│   │   └── system_validation_report.json
│   ├── unit/                       # Unit tests
│   ├── test_document.txt           # Test artifacts
│   └── test_upload.html            # Test HTML pages
│
├── 📁 scripts/                     # Utility scripts
│   ├── development/                # Development utilities
│   │   ├── create_test_users.py
│   │   ├── database_management_status_report.py
│   │   ├── reset_database.py
│   │   ├── dev.sh
│   │   ├── start-dev.sh
│   │   └── cleanup_root.sh
│   └── testing/                    # Test runner scripts
│       ├── run_comprehensive_qa_tests.sh
│       ├── quick_ai_validation.py
│       ├── minimal_ai_test.py
│       └── ...
│
├── 📁 docker/                      # Docker configuration
├── 📁 backups/                     # Database backups
├── 📁 logs/                        # Application logs
├── 📁 templates/                   # Template files
├── 📁 generated-bots/              # Generated chatbot configurations
├── 📁 test-reports/                # Test output reports
└── 📁 test-results/                # Test result artifacts
```

## 📂 Directory Purposes

### `/api/` - Backend Application

- FastAPI-based REST API
- Database models and migrations
- Business logic services
- Authentication and authorization
- Document processing and vector storage

### `/frontend/` - Frontend Application

- React 18 with TypeScript
- Bootstrap UI components
- Authentication integration
- File upload interfaces
- Dashboard and analytics

### `/docs/` - Documentation Hub

- **`development/`**: Active development documentation
- **`reports/`**: Completion and status reports
- **`status-reports/`**: Legacy status tracking

### `/tests/` - Comprehensive Test Suite

- **`integration/`**: API and service integration tests
- **`system/`**: End-to-end system validation
- **`unit/`**: Component-level unit tests
- Test artifacts and fixtures

### `/scripts/` - Automation Scripts

- **`development/`**: Database setup, user creation, environment scripts
- **`testing/`**: Test runners, validation scripts, QA automation

### Root Configuration Files

- **Docker**: Multi-environment container orchestration
- **Testing**: Pytest and Playwright configurations
- **Environment**: Template and example configurations
- **Dependencies**: Test requirements and package definitions

## 🚀 Benefits of This Structure

### ✅ **Improved Organization**

- Clear separation of concerns
- Logical grouping of related files
- Easy navigation and discovery

### ✅ **Development Efficiency**

- Faster file location
- Reduced cognitive overhead
- Better IDE integration

### ✅ **Team Collaboration**

- Standardized structure
- Clear ownership boundaries
- Predictable file locations

### ✅ **Maintenance**

- Easier cleanup and refactoring
- Better version control organization
- Simplified deployment processes

## 🔧 Usage Guidelines

### Adding New Files

- **Documentation**: Add to appropriate `/docs/` subdirectory
- **Tests**: Place in relevant `/tests/` category
- **Scripts**: Categorize in `/scripts/` by purpose
- **Configuration**: Keep in root only if project-wide

### File Naming Conventions

- Use descriptive, lowercase names with underscores
- Include purpose prefix for clarity (e.g., `test_`, `script_`)
- Group related files with common prefixes

### Regular Maintenance

- Review and reorganize quarterly
- Remove obsolete files and documentation
- Update this directory structure document as needed

---

_This organized structure supports efficient development, testing, and maintenance of the Pixel-AI-Creator platform._
