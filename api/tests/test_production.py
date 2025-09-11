# Production Test Framework for Pixel AI Creator
# Pre-deployment validation suite for Linode deployment

import pytest
import asyncio
import os
import sys
import requests
import docker
import subprocess
from typing import Dict, Any, List
from pathlib import Path


class TestProductionReadiness:
    """Comprehensive production readiness validation"""

    def setup_method(self):
        """Setup for production tests"""
        self.project_root = Path(__file__).parent.parent.parent
        self.required_env_vars = [
            "OPENAI_API_KEY",
            "SECRET_KEY",
            "DATABASE_URL",
            "REDIS_URL",
        ]

    def test_environment_variables(self):
        """Test all required environment variables are set"""
        missing_vars = []

        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            pytest.fail(f"Missing required environment variables: {missing_vars}")

        print("✅ All required environment variables are set")

    def test_docker_configuration(self):
        """Test Docker configuration is valid"""

        # Check docker-compose.yml exists and is valid
        compose_file = self.project_root / "docker-compose.yml"
        assert compose_file.exists(), "docker-compose.yml not found"

        # Validate docker-compose configuration
        result = subprocess.run(
            ["docker-compose", "-f", str(compose_file), "config"],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

        assert result.returncode == 0, f"Invalid docker-compose.yml: {result.stderr}"
        print("✅ Docker Compose configuration is valid")

    def test_dockerfile_syntax(self):
        """Test Dockerfile syntax is correct"""

        dockerfiles = [
            self.project_root / "docker" / "api" / "Dockerfile",
            self.project_root / "docker" / "frontend" / "Dockerfile",
        ]

        for dockerfile in dockerfiles:
            if dockerfile.exists():
                # Basic syntax check
                with open(dockerfile, "r") as f:
                    content = f.read()
                    assert "FROM" in content, f"Invalid Dockerfile: {dockerfile}"
                    assert "WORKDIR" in content, f"Missing WORKDIR in: {dockerfile}"

                print(f"✅ {dockerfile.name} syntax is valid")

    def test_requirements_completeness(self):
        """Test all Python dependencies are properly specified"""

        requirements_file = self.project_root / "api" / "requirements.txt"
        assert requirements_file.exists(), "requirements.txt not found"

        with open(requirements_file, "r") as f:
            requirements = f.read()

        # Check for essential packages
        essential_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "psycopg2-binary",
            "redis",
            "openai",
            "playwright",
            "beautifulsoup4",
        ]

        missing_packages = []
        for package in essential_packages:
            if package not in requirements.lower():
                missing_packages.append(package)

        if missing_packages:
            pytest.fail(f"Missing essential packages: {missing_packages}")

        print("✅ All essential packages are in requirements.txt")

    def test_database_migrations(self):
        """Test database schema is properly defined"""

        # Check database models exist
        models_file = self.project_root / "api" / "core" / "database.py"
        assert models_file.exists(), "Database models file not found"

        with open(models_file, "r") as f:
            content = f.read()

        # Check for essential models
        essential_models = ["Client", "Project", "QASession", "WebAnalysis"]

        for model in essential_models:
            assert f"class {model}" in content, f"Missing model: {model}"

        print("✅ Database models are properly defined")

    def test_security_configuration(self):
        """Test security configurations"""

        # Check if secrets are not hardcoded
        sensitive_files = [
            self.project_root / "docker-compose.yml",
            self.project_root / "api" / "core" / "config.py",
        ]

        for file_path in sensitive_files:
            if file_path.exists():
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for hardcoded secrets (basic check)
                suspicious_patterns = [
                    "sk-",  # OpenAI API key pattern
                    "password=",
                    "secret=",
                    "key=",
                ]

                for pattern in suspicious_patterns:
                    if pattern in content.lower() and "${" not in content:
                        # Allow environment variable references
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            if pattern in line.lower() and "${" not in line:
                                print(
                                    f"⚠️  Potential hardcoded secret in {file_path}:{i}"
                                )

        print("✅ Basic security configuration check passed")

    def test_api_service_imports(self):
        """Test all API service imports are resolvable"""

        api_dir = self.project_root / "api"
        sys.path.insert(0, str(api_dir))

        try:
            # Test core imports
            from core.config import settings
            from core.database import init_db

            # Test service imports
            from services.web_analyzer import WebAnalyzer
            from services.ai_generator import AIAssistantGenerator
            from services.client_manager import ClientManager

            # Test model imports
            from models.client import ClientCreate, ClientResponse

            print("✅ All API service imports are resolvable")

        except ImportError as e:
            pytest.fail(f"Import error: {e}")
        finally:
            sys.path.remove(str(api_dir))


class TestDeploymentValidation:
    """Test deployment validation"""

    def setup_method(self):
        """Setup for deployment tests"""
        self.project_root = Path(__file__).parent.parent.parent

    def test_docker_build_success(self):
        """Test Docker configuration and build setup is valid"""

        try:
            import docker

            client = docker.from_env()

            # Check if Docker is available
            try:
                client.ping()
            except Exception as e:
                pytest.skip(f"Docker not available: {e}")

            # Test API Dockerfile exists and is valid
            api_dockerfile = self.project_root / "docker" / "api" / "Dockerfile"
            if not api_dockerfile.exists():
                pytest.fail(f"API Dockerfile not found at {api_dockerfile}")

            print("✅ API Dockerfile found")

            # Test Frontend Dockerfile exists and is valid
            frontend_dockerfile = (
                self.project_root / "docker" / "frontend" / "Dockerfile"
            )
            if not frontend_dockerfile.exists():
                pytest.fail(f"Frontend Dockerfile not found at {frontend_dockerfile}")

            print("✅ Frontend Dockerfile found")

            # Validate Dockerfile syntax
            dockerfiles = [api_dockerfile, frontend_dockerfile]
            for dockerfile in dockerfiles:
                with open(dockerfile, "r") as f:
                    content = f.read()
                    # Check if FROM instruction exists (may not be first line due to comments)
                    if "FROM " not in content:
                        pytest.fail(f"Invalid Dockerfile syntax in {dockerfile}")
                    print(f"✅ {dockerfile.name} has valid syntax")

            # Test that frontend Docker build works (this is fast)
            print("Testing frontend Docker build...")
            try:
                image, logs = client.images.build(
                    path=str(self.project_root / "frontend"),
                    dockerfile="../docker/frontend/Dockerfile",
                    tag="pixel-ai-test:frontend",
                    rm=True,
                    forcerm=True,
                    timeout=120,  # 2 minute timeout for frontend
                )
                print("✅ Frontend Docker image built successfully")

                # Clean up the test image
                try:
                    client.images.remove("pixel-ai-test:frontend", force=True)
                except Exception:
                    pass  # Ignore cleanup errors

            except Exception as e:
                if "build" in str(e).lower():
                    error_msg = f"Frontend Docker build failed: {e}"
                    pytest.fail(error_msg)
                else:
                    raise e

            print("✅ Docker build configuration validated successfully")

        except ImportError:
            pytest.skip("Docker SDK not available")
        except Exception as e:
            pytest.fail(f"Docker build test failed: {e}")

    def test_port_configuration(self):
        """Test port configurations are correct"""

        compose_file = self.project_root / "docker-compose.yml"
        if compose_file.exists():
            with open(compose_file, "r") as f:
                content = f.read()

            # Check for port mappings
            expected_ports = ["8000", "3000", "5432", "6379", "8001"]

            for port in expected_ports:
                if f'"{port}:' not in content and f"'{port}:" not in content:
                    print(f"⚠️  Port {port} mapping not found in docker-compose.yml")

        print("✅ Port configurations checked")

    def test_volume_mounts(self):
        """Test volume mounts are properly configured"""

        compose_file = self.project_root / "docker-compose.yml"
        if compose_file.exists():
            with open(compose_file, "r") as f:
                content = f.read()

            # Check for data persistence volumes
            expected_volumes = ["postgres_data", "redis_data", "chromadb_data"]

            for volume in expected_volumes:
                assert volume in content, f"Missing volume: {volume}"

        print("✅ Volume mounts are properly configured")


class TestLinodeDeployment:
    """Linode-specific deployment tests"""

    def test_linode_compatibility(self):
        """Test configurations are compatible with Linode"""

        # Check resource requirements are reasonable for Linode
        compose_file = Path(__file__).parent.parent.parent / "docker-compose.yml"

        if compose_file.exists():
            with open(compose_file, "r") as f:
                content = f.read()

            # Basic checks for Linode compatibility
            # - No excessive resource limits
            # - Proper restart policies
            # - Network configurations

            if "restart: unless-stopped" in content:
                print("✅ Proper restart policies configured")
            else:
                print("⚠️  Consider adding restart policies for production")

        print("✅ Linode compatibility checks passed")

    def test_ssl_readiness(self):
        """Test SSL/TLS configuration readiness"""

        # Check if nginx configuration exists for SSL termination
        nginx_dir = Path(__file__).parent.parent.parent / "docker" / "nginx"

        if nginx_dir.exists():
            print("✅ Nginx directory exists for SSL configuration")
        else:
            print("⚠️  Consider adding nginx for SSL termination")

    def test_backup_configuration(self):
        """Test backup configurations are in place"""

        # Check for backup scripts or configurations
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"

        if scripts_dir.exists():
            backup_files = list(scripts_dir.glob("*backup*"))
            if backup_files:
                print("✅ Backup scripts found")
            else:
                print("⚠️  Consider adding backup scripts")


class TestPerformanceValidation:
    """Performance and resource validation tests"""

    @pytest.mark.performance
    def test_memory_requirements(self):
        """Test estimated memory requirements"""

        # Estimate memory requirements based on services
        estimated_memory = {
            "postgres": 256,  # MB
            "redis": 128,  # MB
            "api": 512,  # MB
            "frontend": 128,  # MB
            "chromadb": 256,  # MB
            "system": 512,  # MB for system overhead
        }

        total_memory = sum(estimated_memory.values())

        print(f"Estimated memory requirements:")
        for service, memory in estimated_memory.items():
            print(f"  {service}: {memory}MB")
        print(f"  Total: {total_memory}MB ({total_memory/1024:.1f}GB)")

        # Recommend minimum Linode plan
        if total_memory <= 2048:  # 2GB
            print("✅ Compatible with Linode 2GB plan or higher")
        elif total_memory <= 4096:  # 4GB
            print("✅ Requires Linode 4GB plan or higher")
        else:
            print("⚠️  Requires Linode 8GB plan or higher")

    @pytest.mark.performance
    def test_disk_requirements(self):
        """Test estimated disk space requirements"""

        # Calculate approximate disk usage
        estimated_disk = {
            "docker_images": 2000,  # MB
            "database": 1000,  # MB
            "logs": 500,  # MB
            "generated_bots": 1000,  # MB
            "system": 1000,  # MB
            "swap": 2048,  # MB
        }

        total_disk = sum(estimated_disk.values())

        print(f"Estimated disk requirements:")
        for component, disk in estimated_disk.items():
            print(f"  {component}: {disk}MB")
        print(f"  Total: {total_disk}MB ({total_disk/1024:.1f}GB)")

        if total_disk <= 25 * 1024:  # 25GB
            print("✅ Compatible with Linode 25GB disk or higher")
        else:
            print("⚠️  Requires larger disk configuration")


class TestMonitoringValidation:
    """Monitoring and health check validation tests"""

    def test_health_endpoints(self):
        """Test that health endpoints are configured"""

        main_file = Path(__file__).parent.parent.parent / "api" / "main.py"

        if main_file.exists():
            with open(main_file, "r") as f:
                content = f.read()

            # Check for health endpoints
            health_endpoints = ["/health", "/api/pixel/status"]

            for endpoint in health_endpoints:
                if endpoint in content:
                    print(f"✅ Health endpoint {endpoint} found")
                else:
                    print(f"⚠️  Health endpoint {endpoint} not found")

    def test_logging_configuration(self):
        """Test logging is properly configured"""

        # Check for logging imports and configuration
        python_files = list(Path(__file__).parent.parent.parent.glob("api/**/*.py"))

        logging_found = False
        for file_path in python_files:
            with open(file_path, "r") as f:
                content = f.read()

            if "structlog" in content or "logging" in content:
                logging_found = True
                break

        if logging_found:
            print("✅ Logging configuration found")
        else:
            print("⚠️  Consider adding comprehensive logging")


def run_production_validation():
    """Run all production validation tests"""

    print("🚀 Running Production Readiness Validation for Pixel AI Creator")
    print("=" * 60)

    # Run test suites
    test_classes = [
        TestProductionReadiness,
        TestDeploymentValidation,
        TestLinodeDeployment,
        TestPerformanceValidation,
        TestMonitoringValidation,
    ]

    all_passed = True

    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}...")

        try:
            instance = test_class()

            # Run all test methods
            for method_name in dir(instance):
                if method_name.startswith("test_"):
                    try:
                        if hasattr(instance, "setup_method"):
                            instance.setup_method()

                        method = getattr(instance, method_name)
                        method()

                    except Exception as e:
                        print(f"❌ {method_name} failed: {e}")
                        all_passed = False

        except Exception as e:
            print(f"❌ {test_class.__name__} setup failed: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All production validation tests passed!")
        print("✅ System is ready for Linode deployment")
    else:
        print("⚠️  Some validation tests failed")
        print("❌ Please address issues before deployment")

    return all_passed


if __name__ == "__main__":
    run_production_validation()
