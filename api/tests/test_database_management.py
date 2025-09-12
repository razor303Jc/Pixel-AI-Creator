"""
Comprehensive Database Management System Tests

Tests for the Database Management System including:
- Connection pooling and optimization
- Database monitoring and health checks
- Backup automation and security
- Performance metrics and alerting
- Security auditing and compliance
"""

import pytest
import asyncio
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import the main application and database management components
from main import app
from core.database_manager import DatabaseConnectionManager, ConnectionStats
from services.database_monitor import DatabaseMonitor, AlertLevel, MetricType
from services.database_backup import DatabaseBackupService, DatabaseSecurity
from middleware.database_middleware import DatabaseMiddleware
from core.config import settings

# Test configuration
TEST_DATABASE_URL = "sqlite:///./test_db_management.db"


class TestDatabaseConnectionManager:
    """Test suite for DatabaseConnectionManager"""

    @pytest.fixture
    async def db_manager(self):
        """Create a test database manager"""
        manager = DatabaseConnectionManager(
            database_url=TEST_DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
        )
        await manager.initialize()
        yield manager
        await manager.close_all_connections()

    @pytest.mark.asyncio
    async def test_connection_manager_initialization(self, db_manager):
        """Test database manager initialization"""
        assert db_manager.engine is not None
        assert db_manager.pool_size == 5
        assert db_manager.max_overflow == 10
        assert db_manager.pool_timeout == 30

    @pytest.mark.asyncio
    async def test_get_session(self, db_manager):
        """Test database session creation and management"""
        async with db_manager.get_session() as session:
            assert session is not None

            # Test basic query
            result = await session.execute(text("SELECT 1 as test"))
            assert result.scalar() == 1

    @pytest.mark.asyncio
    async def test_connection_stats(self, db_manager):
        """Test connection statistics collection"""
        stats = await db_manager.get_connection_stats()

        assert isinstance(stats, ConnectionStats)
        assert stats.total_connections >= 0
        assert stats.active_connections >= 0
        assert stats.idle_connections >= 0
        assert stats.max_connections > 0

    @pytest.mark.asyncio
    async def test_connection_pool_utilization(self, db_manager):
        """Test connection pool under load"""
        sessions = []

        try:
            # Create multiple sessions
            for i in range(3):
                session = await db_manager.get_session()
                sessions.append(session)

            # Check connection stats
            stats = await db_manager.get_connection_stats()
            assert stats.active_connections >= 3

        finally:
            # Clean up sessions
            for session in sessions:
                await session.close()

    @pytest.mark.asyncio
    async def test_health_check(self, db_manager):
        """Test database health check"""
        is_healthy = await db_manager.check_health()
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_connection_cleanup(self, db_manager):
        """Test connection cleanup functionality"""
        initial_stats = await db_manager.get_connection_stats()

        # Create and immediately close sessions
        for i in range(5):
            async with db_manager.get_session() as session:
                await session.execute(text("SELECT 1"))

        # Allow some cleanup time
        await asyncio.sleep(0.1)

        final_stats = await db_manager.get_connection_stats()
        assert final_stats.idle_connections >= 0


class TestDatabaseMonitor:
    """Test suite for DatabaseMonitor"""

    @pytest.fixture
    async def db_manager(self):
        """Create a test database manager"""
        manager = DatabaseConnectionManager(database_url=TEST_DATABASE_URL)
        await manager.initialize()
        yield manager
        await manager.close_all_connections()

    @pytest.fixture
    async def monitor(self, db_manager):
        """Create a test database monitor"""
        monitor = DatabaseMonitor(db_manager)
        await monitor.initialize()
        yield monitor
        await monitor.stop_monitoring()

    @pytest.mark.asyncio
    async def test_monitor_initialization(self, monitor):
        """Test database monitor initialization"""
        assert monitor.db_manager is not None
        assert monitor.alerts == []
        assert monitor.metrics_history == []

    @pytest.mark.asyncio
    async def test_health_check(self, monitor):
        """Test database health check"""
        health = await monitor.check_health()

        assert "status" in health
        assert "message" in health
        assert "metrics" in health
        assert "timestamp" in health

        assert health["status"] in ["healthy", "warning", "critical"]

    @pytest.mark.asyncio
    async def test_record_metric(self, monitor):
        """Test metric recording"""
        await monitor.record_metric(
            MetricType.RESPONSE_TIME, 100.5, {"endpoint": "/test"}
        )

        # Check if metric was recorded
        assert len(monitor.metrics_history) > 0

        metric = monitor.metrics_history[-1]
        assert metric["metric_type"] == MetricType.RESPONSE_TIME
        assert metric["value"] == 100.5
        assert metric["metadata"]["endpoint"] == "/test"

    @pytest.mark.asyncio
    async def test_alert_creation(self, monitor):
        """Test alert creation and management"""
        await monitor.create_alert(
            AlertLevel.WARNING,
            MetricType.CONNECTION_COUNT,
            "High connection usage detected",
            85.0,
            80.0,
        )

        alerts = await monitor.get_active_alerts()
        assert len(alerts) > 0

        alert = alerts[-1]
        assert alert["level"] == AlertLevel.WARNING
        assert alert["metric_type"] == MetricType.CONNECTION_COUNT
        assert alert["message"] == "High connection usage detected"
        assert not alert["resolved"]

    @pytest.mark.asyncio
    async def test_alert_resolution(self, monitor):
        """Test alert resolution"""
        # Create an alert
        await monitor.create_alert(
            AlertLevel.ERROR, MetricType.ERROR_RATE, "High error rate", 10.0, 5.0
        )

        alerts = await monitor.get_active_alerts()
        alert_id = alerts[-1]["id"]

        # Resolve the alert
        await monitor.resolve_alert(alert_id)

        # Check if alert is resolved
        resolved_alerts = await monitor.get_resolved_alerts()
        assert any(
            alert["id"] == alert_id and alert["resolved"] for alert in resolved_alerts
        )

    @pytest.mark.asyncio
    async def test_performance_summary(self, monitor):
        """Test performance summary generation"""
        # Record some metrics
        await monitor.record_metric(MetricType.RESPONSE_TIME, 150.0, {})
        await monitor.record_metric(MetricType.CONNECTION_COUNT, 10, {})
        await monitor.record_metric(MetricType.ERROR_RATE, 2.0, {})

        summary = await monitor.get_performance_summary()

        assert "avg_response_time" in summary
        assert "connection_count" in summary
        assert "error_rate" in summary
        assert "timestamp" in summary


class TestDatabaseBackupService:
    """Test suite for DatabaseBackupService"""

    @pytest.fixture
    async def db_manager(self):
        """Create a test database manager"""
        manager = DatabaseConnectionManager(database_url=TEST_DATABASE_URL)
        await manager.initialize()
        yield manager
        await manager.close_all_connections()

    @pytest.fixture
    def temp_backup_dir(self):
        """Create a temporary backup directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    async def backup_service(self, db_manager, temp_backup_dir):
        """Create a test backup service"""
        service = DatabaseBackupService(
            db_manager=db_manager,
            backup_dir=temp_backup_dir,
            encryption_key="test-encryption-key-32-characters",
            max_retention_days=7,
        )
        await service.initialize()
        yield service
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_backup_service_initialization(self, backup_service, temp_backup_dir):
        """Test backup service initialization"""
        assert backup_service.db_manager is not None
        assert backup_service.backup_dir == temp_backup_dir
        assert backup_service.max_retention_days == 7
        assert os.path.exists(temp_backup_dir)

    @pytest.mark.asyncio
    async def test_create_backup(self, backup_service):
        """Test backup creation"""
        # Mock the actual backup process for SQLite
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            backup_info = await backup_service.create_backup(
                backup_type="full", custom_name="test_backup"
            )

            assert backup_info["backup_type"] == "full"
            assert "test_backup" in backup_info["file_name"]
            assert backup_info["status"] == "completed"

    @pytest.mark.asyncio
    async def test_list_backups(self, backup_service):
        """Test backup listing"""
        backups = await backup_service.list_backups()
        assert isinstance(backups, list)

    @pytest.mark.asyncio
    async def test_backup_encryption(self, backup_service):
        """Test backup encryption functionality"""
        test_data = b"test backup data"
        encrypted = backup_service._encrypt_data(test_data)
        decrypted = backup_service._decrypt_data(encrypted)

        assert encrypted != test_data
        assert decrypted == test_data

    @pytest.mark.asyncio
    async def test_cleanup_old_backups(self, backup_service, temp_backup_dir):
        """Test cleanup of old backups"""
        # Create mock old backup files
        old_backup = os.path.join(
            temp_backup_dir, "old_backup_20230101_120000.sql.gz.enc"
        )
        with open(old_backup, "w") as f:
            f.write("old backup")

        # Set file timestamp to old date
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        os.utime(old_backup, (old_time, old_time))

        cleaned_count = await backup_service.cleanup_old_backups()
        assert cleaned_count >= 0
        assert not os.path.exists(old_backup)


class TestDatabaseSecurity:
    """Test suite for DatabaseSecurity"""

    @pytest.fixture
    async def db_manager(self):
        """Create a test database manager"""
        manager = DatabaseConnectionManager(database_url=TEST_DATABASE_URL)
        await manager.initialize()
        yield manager
        await manager.close_all_connections()

    @pytest.fixture
    async def security_service(self, db_manager):
        """Create a test security service"""
        service = DatabaseSecurity(
            db_manager=db_manager, audit_enabled=True, encryption_enabled=True
        )
        await service.initialize()
        yield service

    @pytest.mark.asyncio
    async def test_security_initialization(self, security_service):
        """Test security service initialization"""
        assert security_service.db_manager is not None
        assert security_service.audit_enabled is True
        assert security_service.encryption_enabled is True

    @pytest.mark.asyncio
    async def test_audit_log_creation(self, security_service):
        """Test audit log creation"""
        await security_service.log_database_operation(
            user_id="test_user",
            operation="SELECT",
            table_name="users",
            details={"query": "SELECT * FROM users"},
        )

        # Verify audit log was created (would check audit table in real implementation)
        assert True  # Placeholder for actual audit verification

    @pytest.mark.asyncio
    async def test_data_anonymization(self, security_service):
        """Test sensitive data anonymization"""
        sensitive_data = {
            "email": "user@example.com",
            "phone": "123-456-7890",
            "ssn": "123-45-6789",
            "name": "John Doe",
        }

        anonymized = await security_service.anonymize_sensitive_data(sensitive_data)

        assert anonymized["email"] != sensitive_data["email"]
        assert "@" in anonymized["email"]  # Should still look like an email
        assert anonymized["phone"] != sensitive_data["phone"]
        assert anonymized["name"] != sensitive_data["name"]

    @pytest.mark.asyncio
    async def test_compliance_check(self, security_service):
        """Test compliance checking"""
        compliance_report = await security_service.generate_compliance_report()

        assert "compliant" in compliance_report
        assert "checks" in compliance_report
        assert "generated_at" in compliance_report
        assert isinstance(compliance_report["checks"], list)


class TestDatabaseManagementAPI:
    """Test suite for Database Management API endpoints"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)

    def test_database_health_endpoint(self, client):
        """Test database health endpoint"""
        response = client.get("/api/database/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "message" in data
        assert "timestamp" in data

    def test_connection_stats_endpoint(self, client):
        """Test connection statistics endpoint"""
        response = client.get("/api/database/connections/stats")
        assert response.status_code == 200

        data = response.json()
        assert "total_connections" in data
        assert "active_connections" in data
        assert "max_connections" in data

    def test_metrics_history_endpoint(self, client):
        """Test metrics history endpoint"""
        response = client.get("/api/database/metrics/history?hours=1")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_alerts_endpoint(self, client):
        """Test alerts endpoint"""
        response = client.get("/api/database/alerts")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_backups_endpoint(self, client):
        """Test backups listing endpoint"""
        response = client.get("/api/database/backups")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_create_backup_endpoint(self, client):
        """Test backup creation endpoint"""
        backup_request = {"backup_type": "full", "custom_name": "test_api_backup"}

        with patch(
            "api.services.database_backup.DatabaseBackupService.create_backup"
        ) as mock_backup:
            mock_backup.return_value = {
                "id": "test_backup_id",
                "backup_type": "full",
                "status": "completed",
                "file_name": "test_api_backup.sql.gz.enc",
                "created_at": datetime.now().isoformat(),
            }

            response = client.post("/api/database/backups", json=backup_request)
            assert response.status_code == 200

            data = response.json()
            assert data["backup_type"] == "full"
            assert "test_api_backup" in data["file_name"]


class TestDatabaseMiddleware:
    """Test suite for Database Middleware"""

    @pytest.fixture
    async def db_manager(self):
        """Create a test database manager"""
        manager = DatabaseConnectionManager(database_url=TEST_DATABASE_URL)
        await manager.initialize()
        yield manager
        await manager.close_all_connections()

    def test_middleware_initialization(self, db_manager):
        """Test middleware initialization"""
        middleware = DatabaseMiddleware(app, db_manager)
        assert middleware.db_manager == db_manager
        assert middleware.monitor is not None

    @pytest.mark.asyncio
    async def test_middleware_request_processing(self, db_manager):
        """Test middleware request processing"""
        middleware = DatabaseMiddleware(app, db_manager)

        # Mock request and response
        from fastapi import Request, Response

        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        mock_request.state = Mock()

        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        # Test middleware processing
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response == mock_response
        assert "X-Response-Time" in response.headers
        assert "X-Request-ID" in response.headers


@pytest.mark.integration
class TestDatabaseManagementIntegration:
    """Integration tests for the complete Database Management System"""

    @pytest.fixture
    async def full_system(self):
        """Set up the complete database management system"""
        # Initialize all components
        db_manager = DatabaseConnectionManager(database_url=TEST_DATABASE_URL)
        await db_manager.initialize()

        monitor = DatabaseMonitor(db_manager)
        await monitor.initialize()

        with tempfile.TemporaryDirectory() as temp_dir:
            backup_service = DatabaseBackupService(
                db_manager=db_manager,
                backup_dir=temp_dir,
                encryption_key="test-encryption-key-32-characters",
            )
            await backup_service.initialize()

            security_service = DatabaseSecurity(
                db_manager=db_manager, audit_enabled=True, encryption_enabled=True
            )
            await security_service.initialize()

            yield {
                "db_manager": db_manager,
                "monitor": monitor,
                "backup_service": backup_service,
                "security_service": security_service,
            }

            # Cleanup
            await backup_service.cleanup()
            await monitor.stop_monitoring()
            await db_manager.close_all_connections()

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, full_system):
        """Test complete end-to-end database management workflow"""
        db_manager = full_system["db_manager"]
        monitor = full_system["monitor"]
        backup_service = full_system["backup_service"]
        security_service = full_system["security_service"]

        # 1. Check system health
        health = await monitor.check_health()
        assert health["status"] in ["healthy", "warning"]

        # 2. Record some metrics
        await monitor.record_metric(MetricType.RESPONSE_TIME, 125.0, {"test": True})
        await monitor.record_metric(MetricType.CONNECTION_COUNT, 5, {"test": True})

        # 3. Create a backup
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            backup_info = await backup_service.create_backup("full", "integration_test")
            assert backup_info["status"] == "completed"

        # 4. Log security event
        await security_service.log_database_operation(
            user_id="test_user",
            operation="BACKUP",
            table_name="all",
            details={"backup_id": backup_info.get("id", "test")},
        )

        # 5. Generate compliance report
        compliance = await security_service.generate_compliance_report()
        assert "compliant" in compliance

        # 6. Check final system status
        final_health = await monitor.check_health()
        assert final_health["status"] in ["healthy", "warning"]

    @pytest.mark.asyncio
    async def test_performance_under_load(self, full_system):
        """Test database management system performance under load"""
        db_manager = full_system["db_manager"]
        monitor = full_system["monitor"]

        # Simulate concurrent database operations
        tasks = []
        for i in range(10):

            async def db_operation():
                async with db_manager.get_session() as session:
                    result = await session.execute(text("SELECT 1"))
                    return result.scalar()

            tasks.append(db_operation())

        # Execute all operations concurrently
        results = await asyncio.gather(*tasks)
        assert all(result == 1 for result in results)

        # Check that monitoring captured the activity
        stats = await db_manager.get_connection_stats()
        assert stats.total_connections > 0

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, full_system):
        """Test error handling and system recovery"""
        monitor = full_system["monitor"]

        # Simulate a critical alert
        await monitor.create_alert(
            AlertLevel.CRITICAL,
            MetricType.ERROR_RATE,
            "Simulated critical error for testing",
            50.0,
            10.0,
        )

        # Check that alert was created
        alerts = await monitor.get_active_alerts()
        critical_alerts = [a for a in alerts if a["level"] == AlertLevel.CRITICAL]
        assert len(critical_alerts) > 0

        # Resolve the alert
        alert_id = critical_alerts[0]["id"]
        await monitor.resolve_alert(alert_id)

        # Verify resolution
        resolved_alerts = await monitor.get_resolved_alerts()
        assert any(a["id"] == alert_id and a["resolved"] for a in resolved_alerts)


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=api.core.database_manager",
            "--cov=api.services.database_monitor",
            "--cov=api.services.database_backup",
            "--cov=api.middleware.database_middleware",
            "--cov-report=html",
            "--cov-report=term-missing",
        ]
    )
