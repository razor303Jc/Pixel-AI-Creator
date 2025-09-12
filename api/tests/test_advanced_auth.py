"""
Comprehensive tests for advanced authentication features
Tests MFA, social login, password policies, and security features
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

from main import app
from auth.mfa_service import mfa_service
from auth.password_service import password_policy_service
from auth.social_service import social_login_service
from auth.advanced_models import (
    MFAMethod,
    SocialProvider,
    MFASetupRequest,
    MFAVerificationRequest,
    SocialLoginRequest,
)

client = TestClient(app)


@pytest.fixture
def auth_headers():
    """Get authentication headers for testing"""
    # Register a test user
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    # Login to get token
    login_response = client.post(
        "/auth/login", json={"email": "test@example.com", "password": "SecurePass123!"}
    )

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestMFAEndpoints:
    """Test Multi-Factor Authentication endpoints"""

    def test_mfa_setup_totp(self, auth_headers):
        """Test TOTP MFA setup"""
        response = client.post(
            "/auth/advanced/mfa/setup", json={"method": "totp"}, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "totp"
        assert "secret" in data
        assert "qr_code" in data
        assert "backup_codes" in data

    def test_mfa_setup_sms(self, auth_headers):
        """Test SMS MFA setup"""
        with patch.object(mfa_service, "send_sms_code", return_value=True):
            response = client.post(
                "/auth/advanced/mfa/setup",
                json={"method": "sms", "phone_number": "+1234567890"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["method"] == "sms"
            assert "***-***-7890" in data["phone_number"]

    def test_mfa_setup_missing_phone(self, auth_headers):
        """Test SMS MFA setup without phone number"""
        response = client.post(
            "/auth/advanced/mfa/setup", json={"method": "sms"}, headers=auth_headers
        )

        assert response.status_code == 400
        assert "Phone number is required" in response.json()["detail"]

    def test_mfa_verification_success(self, auth_headers):
        """Test successful MFA verification"""
        with patch.object(mfa_service, "verify_mfa_code", return_value=True):
            response = client.post(
                "/auth/advanced/mfa/verify",
                json={"method": "totp", "code": "123456"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            assert "MFA code verified successfully" in response.json()["message"]

    def test_mfa_verification_failure(self, auth_headers):
        """Test failed MFA verification"""
        with patch.object(mfa_service, "verify_mfa_code", return_value=False):
            response = client.post(
                "/auth/advanced/mfa/verify",
                json={"method": "totp", "code": "invalid"},
                headers=auth_headers,
            )

            assert response.status_code == 400
            assert "Invalid MFA code" in response.json()["detail"]

    def test_mfa_status(self, auth_headers):
        """Test MFA status endpoint"""
        mock_status = MagicMock()
        mock_status.enabled = True
        mock_status.methods = ["totp"]
        mock_status.backup_codes_remaining = 5

        with patch.object(mfa_service, "get_mfa_status", return_value=mock_status):
            response = client.get("/auth/advanced/mfa/status", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["enabled"] is True
            assert "totp" in data["methods"]


class TestPasswordEndpoints:
    """Test password strength and policy endpoints"""

    def test_password_strength_check(self, auth_headers):
        """Test password strength analysis"""
        response = client.post(
            "/auth/advanced/password/check-strength",
            json={"password": "MySecurePassword123!"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "feedback" in data
        assert "is_valid" in data
        assert "entropy" in data

    def test_password_strength_weak(self, auth_headers):
        """Test weak password analysis"""
        response = client.post(
            "/auth/advanced/password/check-strength",
            json={"password": "123"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] < 50
        assert data["is_valid"] is False
        assert len(data["feedback"]) > 0

    def test_password_missing(self, auth_headers):
        """Test password strength check without password"""
        response = client.post(
            "/auth/advanced/password/check-strength", json={}, headers=auth_headers
        )

        assert response.status_code == 400
        assert "Password is required" in response.json()["detail"]

    def test_advanced_password_change_success(self, auth_headers):
        """Test successful advanced password change"""
        with patch.object(
            password_policy_service, "validate_password", return_value=True
        ):
            response = client.post(
                "/auth/advanced/password/change-advanced",
                json={
                    "current_password": "SecurePass123!",
                    "new_password": "NewSecurePass123!",
                    "confirm_password": "NewSecurePass123!",
                },
                headers=auth_headers,
            )

            assert response.status_code == 200
            assert "Password changed successfully" in response.json()["message"]

    def test_advanced_password_change_with_mfa(self, auth_headers):
        """Test password change with MFA verification"""
        mock_status = MagicMock()
        mock_status.enabled = True

        with patch.object(
            mfa_service, "get_mfa_status", return_value=mock_status
        ), patch.object(
            mfa_service, "verify_mfa_code", return_value=True
        ), patch.object(
            password_policy_service, "validate_password", return_value=True
        ):

            response = client.post(
                "/auth/advanced/password/change-advanced",
                json={
                    "current_password": "SecurePass123!",
                    "new_password": "NewSecurePass123!",
                    "confirm_password": "NewSecurePass123!",
                    "mfa_code": "123456",
                },
                headers=auth_headers,
            )

            assert response.status_code == 200


class TestSocialLoginEndpoints:
    """Test social login endpoints"""

    def test_get_social_providers(self):
        """Test getting available social providers"""
        response = client.get("/auth/advanced/social/providers")

        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "enabled" in data
        assert "google" in data["providers"]
        assert "github" in data["providers"]

    def test_get_social_auth_url(self):
        """Test getting social authorization URL"""
        response = client.get(
            "/auth/advanced/social/google/authorize",
            params={
                "redirect_uri": "http://localhost:3000/callback",
                "state": "test_state",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert data["provider"] == "google"
        assert data["state"] == "test_state"

    def test_social_login_new_user(self):
        """Test social login for new user"""
        mock_user_data = {
            "email": "social@example.com",
            "first_name": "Social",
            "last_name": "User",
            "avatar_url": "https://example.com/avatar.jpg",
        }

        with patch.object(
            social_login_service,
            "get_user_info_from_token",
            return_value=mock_user_data,
        ):
            response = client.post(
                "/auth/advanced/social/login",
                json={
                    "provider": "google",
                    "access_token": "mock_token",
                    "redirect_uri": "http://localhost:3000/callback",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "social@example.com"
            assert data["is_new_user"] is True
            assert "access_token" in data

    def test_social_login_existing_user(self):
        """Test social login for existing user"""
        # First create a user
        client.post(
            "/auth/register",
            json={
                "email": "existing@example.com",
                "password": "SecurePass123!",
                "first_name": "Existing",
                "last_name": "User",
            },
        )

        mock_user_data = {
            "email": "existing@example.com",
            "first_name": "Existing",
            "last_name": "User",
        }

        with patch.object(
            social_login_service,
            "get_user_info_from_token",
            return_value=mock_user_data,
        ):
            response = client.post(
                "/auth/advanced/social/login",
                json={
                    "provider": "google",
                    "access_token": "mock_token",
                    "redirect_uri": "http://localhost:3000/callback",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "existing@example.com"
            assert data["is_new_user"] is False

    def test_social_login_no_email(self):
        """Test social login without email"""
        mock_user_data = {"first_name": "No", "last_name": "Email"}

        with patch.object(
            social_login_service,
            "get_user_info_from_token",
            return_value=mock_user_data,
        ):
            response = client.post(
                "/auth/advanced/social/login",
                json={
                    "provider": "google",
                    "access_token": "mock_token",
                    "redirect_uri": "http://localhost:3000/callback",
                },
            )

            assert response.status_code == 400
            assert "Email not provided" in response.json()["detail"]


class TestEnhancedLogin:
    """Test enhanced login with security features"""

    def test_enhanced_login_success(self):
        """Test successful enhanced login"""
        # First register a user
        client.post(
            "/auth/register",
            json={
                "email": "enhanced@example.com",
                "password": "SecurePass123!",
                "first_name": "Enhanced",
                "last_name": "User",
            },
        )

        response = client.post(
            "/auth/advanced/login-enhanced",
            json={"email": "enhanced@example.com", "password": "SecurePass123!"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "enhanced@example.com"
        assert "security_score" in data
        assert "device_fingerprint" in data
        assert "session_id" in data
        assert data["mfa_enabled"] is False

    def test_enhanced_login_invalid_credentials(self):
        """Test enhanced login with invalid credentials"""
        response = client.post(
            "/auth/advanced/login-enhanced",
            json={"email": "nonexistent@example.com", "password": "WrongPassword"},
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]


class TestSecurityDashboard:
    """Test security dashboard endpoint"""

    def test_security_dashboard(self, auth_headers):
        """Test security dashboard data"""
        mock_status = MagicMock()
        mock_status.enabled = False
        mock_status.methods = []
        mock_status.backup_codes_remaining = 0

        with patch.object(mfa_service, "get_mfa_status", return_value=mock_status):
            response = client.get(
                "/auth/advanced/security/dashboard", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert "mfa_status" in data
            assert "recent_logins" in data
            assert "active_sessions" in data
            assert "security_events" in data
            assert "account_security_score" in data


class TestPasswordPolicyService:
    """Test password policy service directly"""

    def test_password_entropy_calculation(self):
        """Test password entropy calculation"""
        entropy = password_policy_service.calculate_entropy("Password123!")
        assert entropy > 0

        # Longer, more complex password should have higher entropy
        complex_entropy = password_policy_service.calculate_entropy(
            "VeryComplex!Password123@#"
        )
        assert complex_entropy > entropy

    def test_password_strength_analysis(self):
        """Test password strength analysis"""
        weak_analysis = password_policy_service.analyze_password_strength("123")
        assert weak_analysis.score < 30
        assert not weak_analysis.is_valid
        assert len(weak_analysis.feedback) > 0

        strong_analysis = password_policy_service.analyze_password_strength(
            "MyVeryStrongPassword123!"
        )
        assert strong_analysis.score > 70
        assert strong_analysis.is_valid

    def test_password_validation(self):
        """Test password validation against policy"""
        # Weak password
        assert not password_policy_service.validate_password("123")

        # Strong password
        assert password_policy_service.validate_password("MyStrongPassword123!")

        # Password with personal info
        user_info = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
        }
        assert not password_policy_service.validate_password(
            "JohnDoe123", user_info=user_info
        )


class TestMFAService:
    """Test MFA service directly"""

    @pytest.mark.asyncio
    async def test_totp_generation(self):
        """Test TOTP secret generation"""
        secret = mfa_service.generate_totp_secret()
        assert len(secret) == 32  # Base32 encoded secret
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567" for c in secret)

    def test_qr_code_generation(self):
        """Test QR code generation"""
        secret = "JBSWY3DPEHPK3PXP"
        email = "test@example.com"
        qr_code = mfa_service.generate_qr_code(secret, email)

        assert qr_code.startswith("data:image/png;base64,")
        assert len(qr_code) > 100  # Should be a valid base64 image

    def test_totp_verification(self):
        """Test TOTP code verification"""
        secret = "JBSWY3DPEHPK3PXP"

        # Generate a valid code
        import pyotp

        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        # Verify the code
        is_valid = mfa_service.verify_totp_code(secret, valid_code)
        assert is_valid

        # Verify invalid code
        is_invalid = mfa_service.verify_totp_code(secret, "000000")
        assert not is_invalid

    def test_backup_codes_generation(self):
        """Test backup codes generation"""
        codes = mfa_service.generate_backup_codes()
        assert len(codes) == 10

        for code in codes:
            assert len(code) == 8
            assert code.isalnum()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
