"""
User authentication models for API requests and responses.

This module provides:
- User registration models
- Login request/response models
- User profile models
- Token models
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for role-based access control."""

    ADMIN = "admin"
    CLIENT = "client"
    USER = "user"


class UserRegistrationRequest(BaseModel):
    """Request model for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, description="Password (minimum 8 characters)"
    )
    first_name: str = Field(..., min_length=1, description="First name")
    last_name: str = Field(..., min_length=1, description="Last name")
    company_name: Optional[str] = Field(None, description="Company name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: UserRole = Field(UserRole.USER, description="User role")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123",
                "first_name": "John",
                "last_name": "Doe",
                "company_name": "Acme Corp",
                "phone": "+1234567890",
                "role": "user",
            }
        }


class UserLoginRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        schema_extra = {
            "example": {"email": "user@example.com", "password": "SecurePassword123"}
        }


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_id: int = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role")

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_id": 123,
                "role": "user",
            }
        }


class UserProfile(BaseModel):
    """User profile information."""

    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    company_name: Optional[str] = Field(None, description="Company name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="User active status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 123,
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "company_name": "Acme Corp",
                "phone": "+1234567890",
                "role": "user",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "last_login": "2023-01-15T10:30:00",
            }
        }


class UserRegistrationResponse(BaseModel):
    """Response model for successful user registration."""

    message: str = Field(..., description="Success message")
    user_id: int = Field(..., description="Created user ID")
    email: EmailStr = Field(..., description="User email")
    role: UserRole = Field(..., description="User role")

    class Config:
        schema_extra = {
            "example": {
                "message": "User registered successfully",
                "user_id": 123,
                "email": "user@example.com",
                "role": "user",
            }
        }


class PasswordChangeRequest(BaseModel):
    """Request model for password change."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, description="New password (minimum 8 characters)"
    )

    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPassword123",
                "new_password": "NewSecurePassword456",
            }
        }


class UserUpdateRequest(BaseModel):
    """Request model for updating user profile."""

    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    company_name: Optional[str] = Field(None, description="Company name")
    phone: Optional[str] = Field(None, description="Phone number")

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Smith",
                "company_name": "New Corp",
                "phone": "+0987654321",
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")

    class Config:
        schema_extra = {
            "example": {"detail": "Invalid credentials", "error_code": "AUTH_001"}
        }


class SuccessResponse(BaseModel):
    """Standard success response model."""

    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")

    class Config:
        schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "data": {"result": "success"},
            }
        }
