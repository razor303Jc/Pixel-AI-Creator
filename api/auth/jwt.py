"""
JWT Authentication utilities for Pixel AI Creator.

This module provides:
- JWT token generation and validation
- Password hashing and verification
- User authentication helpers
- Token refresh functionality
"""

from jose import jwt, JWTError, ExpiredSignatureError
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import HTTPException, status
from api.core.config import Settings

settings = Settings()


class JWTHandler:
    """JWT token handler for authentication."""

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.access_token_expire_minutes

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a new access token.

        Args:
            data: Data to encode in the token (user_id, email, etc.)

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a new refresh token.

        Args:
            data: Data to encode in the token

        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)  # 7 days for refresh
        to_encode.update({"exp": expire, "type": "refresh"})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_user_from_token(self, token: str) -> Dict[str, Any]:
        """Extract user information from token.

        Args:
            token: JWT token

        Returns:
            User information from token payload
        """
        payload = self.verify_token(token)

        # Extract user info
        user_info = {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "client_id": payload.get("client_id"),
        }

        if not user_info["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        return user_info


class PasswordHandler:
    """Password hashing and verification utilities."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        # Generate salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            password: Plain text password to verify
            hashed_password: Stored hashed password

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


# Global instances
jwt_handler = JWTHandler()
password_handler = PasswordHandler()


def create_user_tokens(user_data: Dict[str, Any]) -> Dict[str, str]:
    """Create access and refresh tokens for a user.

    Args:
        user_data: User information to encode in tokens

    Returns:
        Dictionary with access_token and refresh_token
    """
    access_token = jwt_handler.create_access_token(user_data)
    refresh_token = jwt_handler.create_refresh_token(user_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def create_user_token(user_data: Dict[str, Any]) -> tuple[str, int]:
    """Create access token for a user.

    Args:
        user_data: User information to encode in token

    Returns:
        Tuple of (access_token, expires_in_seconds)
    """
    access_token = jwt_handler.create_access_token(user_data)
    expires_in = settings.access_token_expire_minutes * 60
    return access_token, expires_in


def verify_user_token(token: str) -> Dict[str, Any]:
    """Verify a user token and return user info.

    Args:
        token: JWT token to verify

    Returns:
        User information from token
    """
    return jwt_handler.get_user_from_token(token)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return password_handler.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        password: Plain text password
        hashed_password: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    return password_handler.verify_password(password, hashed_password)
