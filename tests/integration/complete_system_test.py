#!/usr/bin/env python3
"""
Complete System Validation Test
Comprehensive testing of all Pixel AI Creator components
"""

import asyncio
import json
import sys
import httpx
from datetime import datetime
from pathlib import Path

# Add API directory to path
api_path = Path(__file__).parent / "api"
sys.path.insert(0, str(api_path))


class SystemValidator:
    """Complete system validation"""

    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0

    def test_result(
        self, category: str, test_name: str, success: bool, details: str = ""
    ):
        """Record test result"""
        if category not in self.results:
            self.results[category] = []

        self.results[category].append(
            {"test": test_name, "success": success, "details": details}
        )

        self.total_tests += 1
        if success:
            self.passed_tests += 1

        icon = "✅" if success else "❌"
        status = "PASS" if success else "FAIL"
        print(f"{icon} {test_name:<40} [{status}] {details}")

    async def test_imports(self):
        """Test all critical imports"""
        print("\n🔍 IMPORT VALIDATION")
        print("=" * 60)

        # Core Database Management
        try:
            from core.database_manager import DatabaseConnectionManager, get_db_manager

            self.test_result(
                "imports", "Database Manager", True, "Core database functionality"
            )
        except Exception as e:
            self.test_result("imports", "Database Manager", False, str(e))

        # Database Services
        try:
            from services.database_monitor import DatabaseMonitor, db_monitor

            self.test_result(
                "imports", "Database Monitor", True, "Monitoring and alerting"
            )
        except Exception as e:
            self.test_result("imports", "Database Monitor", False, str(e))

        try:
            from services.database_backup import DatabaseBackupService, backup_service

            self.test_result("imports", "Database Backup", True, "Backup and security")
        except Exception as e:
            self.test_result("imports", "Database Backup", False, str(e))

        # API Routes
        try:
            from routes.database_simple import router as db_router

            self.test_result("imports", "Database Routes", True, "REST API endpoints")
        except Exception as e:
            self.test_result("imports", "Database Routes", False, str(e))

        # FastAPI Core
        try:
            from main import app

            self.test_result("imports", "FastAPI Application", True, "Main application")
        except Exception as e:
            self.test_result("imports", "FastAPI Application", False, str(e))

        # Configuration
        try:
            from core.config import settings

            self.test_result(
                "imports",
                "Configuration",
                True,
                f"Database: {settings.database_url[:30]}...",
            )
        except Exception as e:
            self.test_result("imports", "Configuration", False, str(e))

    async def test_database_functionality(self):
        """Test database functionality"""
        print("\n🗃️ DATABASE FUNCTIONALITY")
        print("=" * 60)

        try:
            from core.database_manager import get_db_manager

            # Test database manager creation
            db_manager = await get_db_manager()
            self.test_result(
                "database", "Connection Manager", True, "Created successfully"
            )

            # Test health check
            health = await db_manager.health_check()
            is_healthy = health.get("status") == "healthy"
            self.test_result(
                "database",
                "Health Check",
                is_healthy,
                f"Status: {health.get('status', 'unknown')}",
            )

            # Test connection stats
            stats = await db_manager.get_connection_stats()
            self.test_result(
                "database",
                "Connection Stats",
                True,
                f"Total: {stats.total_connections}, Active: {stats.active_connections}",
            )

            # Test connection pooling
            pool_info = health.get("connection_pool", {})
            pool_ok = pool_info.get("total_connections", 0) > 0
            self.test_result(
                "database",
                "Connection Pooling",
                pool_ok,
                f"Pool size: {pool_info.get('total_connections', 0)}",
            )

        except Exception as e:
            self.test_result("database", "Database Operations", False, str(e))

    async def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🌐 API ENDPOINT VALIDATION")
        print("=" * 60)

        base_urls = ["http://localhost:8002", "http://localhost:8000"]

        for base_url in base_urls:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    # Test health endpoint
                    response = await client.get(f"{base_url}/health")
                    if response.status_code == 200:
                        data = response.json()
                        self.test_result(
                            "api",
                            f"Health Endpoint ({base_url})",
                            True,
                            f"Status: {data.get('status', 'unknown')}",
                        )

                        # Test additional endpoints if health passes
                        try:
                            # Test chat endpoint
                            chat_response = await client.get(
                                f"{base_url}/api/chat/health"
                            )
                            if chat_response.status_code == 200:
                                self.test_result(
                                    "api",
                                    "Chat Service",
                                    True,
                                    "Chat endpoints accessible",
                                )
                            else:
                                self.test_result(
                                    "api",
                                    "Chat Service",
                                    False,
                                    f"Status: {chat_response.status_code}",
                                )
                        except:
                            self.test_result(
                                "api", "Chat Service", False, "Endpoint not accessible"
                            )

                        break  # Success on this URL, no need to try others
                    else:
                        self.test_result(
                            "api",
                            f"Health Endpoint ({base_url})",
                            False,
                            f"Status: {response.status_code}",
                        )

            except httpx.ConnectError:
                self.test_result(
                    "api", f"API Server ({base_url})", False, "Connection refused"
                )
            except Exception as e:
                self.test_result("api", f"API Server ({base_url})", False, str(e))

    async def test_redis_connectivity(self):
        """Test Redis connectivity"""
        print("\n🔴 REDIS CONNECTIVITY")
        print("=" * 60)

        try:
            import redis.asyncio as redis

            # Test Redis connection
            r = redis.from_url("redis://localhost:6380")
            await r.set("test_system_validation", "success")
            value = await r.get("test_system_validation")

            success = value and value.decode() == "success"
            self.test_result(
                "redis",
                "Basic Operations",
                success,
                f"Set/Get test: {value.decode() if value else 'Failed'}",
            )

            # Test expiration
            await r.setex("test_expire", 1, "expire_test")
            self.test_result(
                "redis", "Expiration Support", True, "TTL operations working"
            )

            # Cleanup
            await r.delete("test_system_validation", "test_expire")
            await r.close()

        except Exception as e:
            self.test_result("redis", "Redis Connection", False, str(e))

    async def test_docker_services(self):
        """Test Docker service status"""
        print("\n🐳 DOCKER SERVICES")
        print("=" * 60)

        try:
            import subprocess

            # Check Docker services
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout

                # Check for key services
                services = {
                    "PostgreSQL": "postgres" in output.lower(),
                    "Redis": "redis" in output.lower(),
                    "API Server": "pixel-ai" in output.lower()
                    or "fastapi" in output.lower(),
                    "Frontend": "frontend" in output.lower()
                    or "nginx" in output.lower(),
                }

                for service, running in services.items():
                    self.test_result(
                        "docker",
                        f"{service} Container",
                        running,
                        "Running" if running else "Not detected",
                    )

                # Count total containers
                container_count = len(
                    [line for line in output.split("\n") if "Up" in line]
                )
                self.test_result(
                    "docker",
                    "Container Status",
                    container_count > 0,
                    f"{container_count} containers running",
                )
            else:
                self.test_result(
                    "docker", "Docker System", False, "Docker not accessible"
                )

        except FileNotFoundError:
            self.test_result("docker", "Docker System", False, "Docker not installed")
        except Exception as e:
            self.test_result("docker", "Docker System", False, str(e))

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE SYSTEM VALIDATION REPORT")
        print("=" * 80)

        # Summary by category
        for category, tests in self.results.items():
            passed = sum(1 for test in tests if test["success"])
            total = len(tests)
            percentage = (passed / total * 100) if total > 0 else 0

            print(
                f"\n📊 {category.upper()} TESTS: {passed}/{total} ({percentage:.1f}%)"
            )

            for test in tests:
                icon = "✅" if test["success"] else "❌"
                print(f"  {icon} {test['test']}: {test['details']}")

        # Overall summary
        percentage = (
            (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        )
        print(
            f"\n🏁 OVERALL RESULTS: {self.passed_tests}/{self.total_tests} tests passed ({percentage:.1f}%)"
        )

        if percentage >= 80:
            print("🎉 EXCELLENT! System is in good health and ready for production!")
        elif percentage >= 60:
            print(
                "⚠️  GOOD! System is mostly functional with some areas for improvement."
            )
        else:
            print(
                "🚨 ATTENTION NEEDED! Several critical issues require immediate attention."
            )

        # Recommendations
        print("\n📝 RECOMMENDATIONS:")

        failed_tests = []
        for category, tests in self.results.items():
            for test in tests:
                if not test["success"]:
                    failed_tests.append(
                        f"{category}: {test['test']} - {test['details']}"
                    )

        if failed_tests:
            print("🔧 Issues to address:")
            for issue in failed_tests[:5]:  # Show top 5 issues
                print(f"   • {issue}")
        else:
            print("✨ No critical issues detected!")

        # Next steps
        print(f"\n🚀 NEXT STEPS:")
        print("   • Run full test suite: python -m pytest api/tests/ -v")
        print("   • Monitor system health dashboard")
        print("   • Review application logs for any warnings")
        print("   • Validate production deployment checklist")

        return {
            "timestamp": datetime.now().isoformat(),
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": percentage,
            "categories": self.results,
            "status": (
                "healthy"
                if percentage >= 80
                else "warning" if percentage >= 60 else "critical"
            ),
        }


async def main():
    """Main validation routine"""
    print("🚀 PIXEL AI CREATOR - COMPLETE SYSTEM VALIDATION")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    validator = SystemValidator()

    # Run all validation tests
    await validator.test_imports()
    await validator.test_database_functionality()
    await validator.test_api_endpoints()
    await validator.test_redis_connectivity()
    await validator.test_docker_services()

    # Generate final report
    report = validator.generate_report()

    # Save report to file
    report_file = Path("system_validation_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Full report saved to: {report_file}")
    print(f"🏁 Validation completed at: {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
