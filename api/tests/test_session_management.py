"""
Session Management Test Suite

Test the session management functionality including:
- Session creation and management
- Device tracking
- Security monitoring
- Session timeout and cleanup
"""

import pytest
import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.core.database import Base, get_db
from api.models.user import User
from api.models.session import UserSession, SessionActivity, SecurityAlert
from api.services.session_service import SessionManager
from api.auth.session_models import SessionCreateRequest

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_sessions.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


class TestSessionManagement:
    """Test session management functionality."""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Setup test database."""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)

    @pytest.fixture
    def test_user(self):
        """Create a test user."""
        db = TestingSessionLocal()
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            role="user",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        yield user
        db.close()

    @pytest.fixture
    def session_manager(self):
        """Create session manager instance."""
        db = TestingSessionLocal()
        manager = SessionManager(db)
        yield manager
        db.close()

    def test_create_session(self, test_user, session_manager):
        """Test session creation."""
        request_data = SessionCreateRequest(
            device_type="desktop",
            device_id="test-device-123",
            user_agent="Mozilla/5.0 Test Browser",
            ip_address="192.168.1.100",
            location="Test City, TC",
        )

        refresh_token = str(uuid.uuid4())

        session = session_manager.create_session(
            user_id=test_user.id,
            refresh_token=refresh_token,
            request_data=request_data,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 Test Browser",
        )

        assert session is not None
        assert session.user_id == test_user.id
        assert session.device_type == "desktop"
        assert session.device_id == "test-device-123"
        assert session.ip_address == "192.168.1.100"
        assert session.is_active()

    def test_session_refresh(self, test_user, session_manager):
        """Test session refresh functionality."""
        request_data = SessionCreateRequest(
            device_type="mobile", ip_address="192.168.1.101"
        )

        refresh_token = str(uuid.uuid4())

        # Create session
        session = session_manager.create_session(
            user_id=test_user.id, refresh_token=refresh_token, request_data=request_data
        )

        original_expires_at = session.expires_at

        # Refresh session
        refreshed_session = session_manager.refresh_session(session.id)

        assert refreshed_session is not None
        assert refreshed_session.expires_at > original_expires_at
        assert refreshed_session.is_active()

    def test_session_termination(self, test_user, session_manager):
        """Test session termination."""
        request_data = SessionCreateRequest(
            device_type="tablet", ip_address="192.168.1.102"
        )

        refresh_token = str(uuid.uuid4())

        # Create session
        session = session_manager.create_session(
            user_id=test_user.id, refresh_token=refresh_token, request_data=request_data
        )

        # Terminate session
        success = session_manager.terminate_session(session.id, "test_logout")

        assert success is True

        # Verify session is terminated
        terminated_session = session_manager.get_session(session.id)
        assert terminated_session.status == "terminated"
        assert not terminated_session.is_active()

    def test_concurrent_session_limit(self, test_user, session_manager):
        """Test concurrent session limits."""
        # Create multiple sessions
        sessions = []
        for i in range(3):
            request_data = SessionCreateRequest(
                device_type="desktop",
                device_id=f"device-{i}",
                ip_address=f"192.168.1.{100 + i}",
            )

            refresh_token = str(uuid.uuid4())

            session = session_manager.create_session(
                user_id=test_user.id,
                refresh_token=refresh_token,
                request_data=request_data,
            )
            sessions.append(session)

        # All sessions should be created successfully
        assert len(sessions) == 3

        # Check that all sessions are active
        active_sessions = session_manager.get_user_sessions(
            user_id=test_user.id, active_only=True
        )
        assert len(active_sessions) >= 3

    def test_session_statistics(self, test_user, session_manager):
        """Test session statistics."""
        # Create some test sessions
        for i in range(2):
            request_data = SessionCreateRequest(
                device_type="desktop",
                device_id=f"stats-device-{i}",
                ip_address=f"192.168.1.{110 + i}",
            )

            refresh_token = str(uuid.uuid4())

            session_manager.create_session(
                user_id=test_user.id,
                refresh_token=refresh_token,
                request_data=request_data,
            )

        # Get statistics
        stats = session_manager.get_session_statistics(user_id=test_user.id)

        assert stats["total_sessions"] >= 2
        assert stats["active_sessions"] >= 2
        assert stats["unique_devices"] >= 2

    def test_expired_session_cleanup(self, test_user, session_manager):
        """Test cleanup of expired sessions."""
        request_data = SessionCreateRequest(
            device_type="desktop", ip_address="192.168.1.120"
        )

        refresh_token = str(uuid.uuid4())

        # Create session
        session = session_manager.create_session(
            user_id=test_user.id, refresh_token=refresh_token, request_data=request_data
        )

        # Manually expire the session
        session.expires_at = datetime.utcnow() - timedelta(hours=1)
        session_manager.db.commit()

        # Run cleanup
        cleaned_count = session_manager.cleanup_expired_sessions()

        assert cleaned_count >= 1

        # Verify session is marked as expired
        expired_session = session_manager.get_session(session.id)
        assert expired_session.status == "expired"

    def test_suspicious_activity_detection(self, test_user, session_manager):
        """Test suspicious activity detection."""
        # Create a normal session first
        normal_request = SessionCreateRequest(
            device_type="desktop",
            ip_address="192.168.1.100",
            location="Normal City, NC",
        )

        refresh_token1 = str(uuid.uuid4())

        session_manager.create_session(
            user_id=test_user.id,
            refresh_token=refresh_token1,
            request_data=normal_request,
        )

        # Create a suspicious session (different location and IP)
        suspicious_request = SessionCreateRequest(
            device_type="mobile",
            ip_address="203.0.113.1",  # Different IP range
            location="Suspicious City, SC",
        )

        refresh_token2 = str(uuid.uuid4())

        suspicious_session = session_manager.create_session(
            user_id=test_user.id,
            refresh_token=refresh_token2,
            request_data=suspicious_request,
            ip_address="203.0.113.1",
        )

        # The session should be marked as suspicious
        assert suspicious_session.is_suspicious is True

    def test_session_activity_logging(self, test_user, session_manager):
        """Test session activity logging."""
        request_data = SessionCreateRequest(
            device_type="desktop", ip_address="192.168.1.130"
        )

        refresh_token = str(uuid.uuid4())

        # Create session
        session = session_manager.create_session(
            user_id=test_user.id, refresh_token=refresh_token, request_data=request_data
        )

        # Log additional activity
        from api.auth.session_models import ActivityType

        session_manager._log_activity(
            session_id=session.id,
            user_id=test_user.id,
            activity_type=ActivityType.API_CALL,
            endpoint="/api/test",
            method="GET",
            metadata={"test": True},
        )

        # Check activity was logged
        activities = (
            session_manager.db.query(SessionActivity)
            .filter(SessionActivity.session_id == session.id)
            .all()
        )

        # Should have login activity + our test activity
        assert len(activities) >= 2

        # Find our test activity
        test_activity = next(
            (a for a in activities if a.activity_type == "api_call"), None
        )
        assert test_activity is not None
        assert test_activity.endpoint == "/api/test"
        assert test_activity.method == "GET"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
