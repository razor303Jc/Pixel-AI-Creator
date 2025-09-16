# 🏗️ PIXEL AI CREATOR - BUILD PROCESS ARCHITECTURE

## 📋 Overview

This document outlines the comprehensive build process for Pixel AI Creator, covering the end-to-end flow from assistant creation to deployment.

## 🎯 Build Process Flow

### Phase 1: Data Collection & Validation

```
User Input → Form Validation → Template Selection → Database Storage
```

### Phase 2: Code Generation

```
Template Engine → Variable Substitution → Code Assembly → File Generation
```

### Phase 3: Container Build

```
Docker Build → Image Creation → Testing → Registry Push
```

### Phase 4: Deployment

```
Container Orchestration → Service Deployment → Health Checks → Status Update
```

## 🗃️ Database Schema Analysis

### Current Tables:

- **projects**: Store assistant/chatbot configurations
- **templates**: Store code templates and configurations
- **clients**: Store client information
- **users**: Store user authentication data

### Required Extensions:

```sql
-- Build queue table
CREATE TABLE builds (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    status VARCHAR(50) DEFAULT 'queued',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    build_logs TEXT[],
    container_id VARCHAR(100),
    image_name VARCHAR(200),
    deployment_url VARCHAR(500),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Build artifacts table
CREATE TABLE build_artifacts (
    id SERIAL PRIMARY KEY,
    build_id INTEGER REFERENCES builds(id),
    artifact_type VARCHAR(50), -- 'dockerfile', 'source_code', 'config'
    file_path VARCHAR(500),
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Template System Architecture

### Template Structure:

```
build-templates/
├── Dockerfile.template          # Container definition
├── main.py.template            # FastAPI application
├── requirements.txt.template   # Python dependencies
├── config/
│   ├── settings.py.template    # App configuration
│   └── prompts.py.template     # AI prompts
└── deployment/
    ├── docker-compose.yml.template
    └── nginx.conf.template
```

### Template Variables:

```python
TEMPLATE_VARIABLES = {
    # Project metadata
    'CHATBOT_NAME': project.name,
    'CHATBOT_DESCRIPTION': project.description,
    'PROJECT_ID': project.id,

    # Personality configuration
    'PERSONALITY_TONE': project.personality_config.tone,
    'PERSONALITY_STYLE': project.personality_config.style,
    'SYSTEM_PROMPT': project.personality_config.system_prompt,

    # Business rules
    'BUSINESS_RULES': project.business_rules,
    'TRAINING_DATA': project.training_data,

    # Technical configuration
    'API_ENDPOINTS': project.deployment_config.endpoints,
    'ENVIRONMENT_VARS': project.deployment_config.env_vars,
    'DEPENDENCIES': project.deployment_config.dependencies
}
```

## 🐳 Docker-in-Docker Build System

### Build Container Setup:

```dockerfile
# Builder container with Docker-in-Docker capability
FROM docker:24-dind

# Install Python for build scripts
RUN apk add --no-cache python3 py3-pip

# Install build dependencies
RUN pip3 install jinja2 pyyaml requests

# Copy build scripts
COPY build-scripts/ /usr/local/bin/
COPY build-templates/ /templates/

# Set up volume mounts
VOLUME ["/var/lib/docker", "/builds", "/artifacts"]

ENTRYPOINT ["build-assistant.py"]
```

### Build Script Architecture:

```python
# build-assistant.py
import os
import docker
import jinja2
from pathlib import Path

class AssistantBuilder:
    def __init__(self, project_id):
        self.project_id = project_id
        self.docker_client = docker.from_env()
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('/templates')
        )

    def build_flow(self):
        """Complete build flow"""
        try:
            # 1. Fetch project data from database
            project_data = self.fetch_project_data()

            # 2. Generate code from templates
            generated_files = self.generate_code(project_data)

            # 3. Build Docker image
            image = self.build_docker_image(generated_files)

            # 4. Test container
            test_results = self.test_container(image)

            # 5. Deploy to registry
            deployment_info = self.deploy_container(image)

            # 6. Update build status
            self.update_build_status('completed', deployment_info)

            return deployment_info

        except Exception as e:
            self.update_build_status('failed', {'error': str(e)})
            raise
```

## 🚀 Celery Build Queue Integration

### Task Definition:

```python
# tasks/build_tasks.py
from celery import Celery
from .builder import AssistantBuilder

app = Celery('pixel_ai_builder')

@app.task(bind=True)
def build_assistant_task(self, project_id):
    """Celery task for building assistants"""

    # Update status to 'building'
    self.update_state(
        state='BUILDING',
        meta={'project_id': project_id, 'status': 'Building container...'}
    )

    try:
        builder = AssistantBuilder(project_id)
        result = builder.build_flow()

        return {
            'status': 'completed',
            'project_id': project_id,
            'deployment_url': result['url'],
            'container_id': result['container_id']
        }

    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'project_id': project_id, 'error': str(e)}
        )
        raise
```

### Queue Configuration:

```python
# celery_config.py
CELERY_CONFIG = {
    'broker_url': 'redis://pixel-redis:6379/0',
    'result_backend': 'redis://pixel-redis:6379/0',
    'task_serializer': 'json',
    'result_serializer': 'json',
    'task_routes': {
        'tasks.build_tasks.build_assistant_task': {'queue': 'builds'},
    },
    'worker_prefetch_multiplier': 1,
    'task_acks_late': True,
}
```

## 📊 Build Status API Enhancement

### Enhanced Build Routes:

```python
# api/routes/builds.py
from fastapi import APIRouter, Depends, HTTPException
from .auth import get_current_user
from .database import get_db
from .tasks import build_assistant_task

router = APIRouter()

@router.post("/builds/trigger/{project_id}")
async def trigger_build(
    project_id: int,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Trigger a new build for a project"""

    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.client_id == user.client_id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Create build record
    build = Build(
        project_id=project_id,
        status='queued',
        created_at=datetime.utcnow()
    )
    db.add(build)
    db.commit()

    # Queue build task
    task = build_assistant_task.delay(project_id)

    return {
        "build_id": build.id,
        "task_id": task.id,
        "status": "queued",
        "message": "Build has been queued"
    }

@router.get("/builds/status/{build_id}")
async def get_build_status(
    build_id: int,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get detailed build status"""

    build = db.query(Build).filter(Build.id == build_id).first()
    if not build:
        raise HTTPException(404, "Build not found")

    # Get task status from Celery
    task_status = None
    if build.task_id:
        task = build_assistant_task.AsyncResult(build.task_id)
        task_status = {
            'state': task.state,
            'info': task.info
        }

    return {
        "build_id": build.id,
        "project_id": build.project_id,
        "status": build.status,
        "started_at": build.started_at,
        "completed_at": build.completed_at,
        "logs": build.build_logs,
        "task_status": task_status,
        "deployment_url": build.deployment_url
    }
```

## 🔄 Real-time Status Updates

### WebSocket Integration:

```python
# websocket/build_updates.py
from fastapi import WebSocket
import json

class BuildStatusManager:
    def __init__(self):
        self.connections = {}

    async def connect(self, websocket: WebSocket, build_id: int):
        await websocket.accept()
        if build_id not in self.connections:
            self.connections[build_id] = []
        self.connections[build_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, build_id: int):
        if build_id in self.connections:
            self.connections[build_id].remove(websocket)

    async def broadcast_update(self, build_id: int, update: dict):
        if build_id in self.connections:
            message = json.dumps(update)
            for connection in self.connections[build_id]:
                await connection.send_text(message)

build_manager = BuildStatusManager()
```

## 🚢 Deployment Strategy

### Container Registry:

```yaml
# docker-compose.override.yml for development
services:
  registry:
    image: registry:2
    ports:
      - "5000:5000"
    volumes:
      - ./registry-data:/var/lib/registry

  pixel-api:
    environment:
      - DOCKER_REGISTRY_URL=http://registry:5000
      - BUILD_STORAGE_PATH=/app/builds
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./builds:/app/builds
```

### Production Deployment:

```yaml
# k8s/build-system.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pixel-builder
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pixel-builder
  template:
    spec:
      containers:
        - name: builder
          image: pixel-ai/builder:latest
          env:
            - name: DOCKER_HOST
              value: "tcp://docker-dind:2376"
          volumeMounts:
            - name: builds
              mountPath: /builds
        - name: docker-dind
          image: docker:24-dind
          securityContext:
            privileged: true
```

## 📈 Monitoring & Metrics

### Build Metrics:

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Metrics definitions
BUILD_COUNTER = Counter('builds_total', 'Total builds', ['status'])
BUILD_DURATION = Histogram('build_duration_seconds', 'Build duration')
ACTIVE_BUILDS = Gauge('active_builds', 'Currently active builds')

def track_build_metrics(build_id, status, duration=None):
    BUILD_COUNTER.labels(status=status).inc()
    if duration:
        BUILD_DURATION.observe(duration)
    if status == 'building':
        ACTIVE_BUILDS.inc()
    elif status in ['completed', 'failed']:
        ACTIVE_BUILDS.dec()
```

## 🧪 Testing Strategy

### Build System Tests:

1. **Unit Tests**: Template generation, Docker operations
2. **Integration Tests**: End-to-end build flow
3. **Performance Tests**: Build time optimization
4. **Load Tests**: Multiple concurrent builds

### Test Implementation:

```javascript
// Enhanced Playwright test
test("Complete Build Flow", async ({ page }) => {
  // 1. Create assistant
  const projectId = await createAssistant(page);

  // 2. Trigger build
  const buildId = await triggerBuild(page, projectId);

  // 3. Monitor build progress
  await monitorBuildProgress(page, buildId);

  // 4. Verify deployment
  await verifyDeployment(page, buildId);
});
```

## 🎯 Implementation Roadmap

### Phase 1: Foundation (Week 1)

- [ ] Database schema updates
- [ ] Enhanced API routes
- [ ] Basic template engine

### Phase 2: Build System (Week 2)

- [ ] Docker-in-Docker setup
- [ ] Build queue integration
- [ ] Container registry setup

### Phase 3: Monitoring (Week 3)

- [ ] Real-time status updates
- [ ] WebSocket integration
- [ ] Metrics and logging

### Phase 4: Production (Week 4)

- [ ] Security hardening
- [ ] Performance optimization
- [ ] Comprehensive testing

---

_This architecture provides a robust, scalable build system for Pixel AI Creator with comprehensive monitoring, testing, and deployment capabilities._
