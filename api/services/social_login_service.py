"""
Social Login Integration Service

This module provides OAuth2 integration for multiple social providers:
- Google OAuth2
- GitHub OAuth2
- LinkedIn OAuth2
- Microsoft OAuth2 (extensible)

Features:
- OAuth2 flow management
- User profile data fetching
- Account linking/unlinking
- Social provider management
"""

import logging
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs
import httpx
from authlib.integrations.starlette_client import OAuth
from authlib.oauth2.rfc6749 import OAuth2Error
from fastapi import HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from auth.advanced_models import SocialLogin, SocialProvider, User
from core.config import settings

logger = logging.getLogger(__name__)


class SocialAuthConfig:
    """Social authentication provider configurations"""

    def __init__(self):
        self.providers = {
            SocialProvider.GOOGLE: {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scopes": ["openid", "email", "profile"],
                "name": "google",
            },
            SocialProvider.GITHUB: {
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "scopes": ["user:email"],
                "name": "github",
            },
            SocialProvider.LINKEDIN: {
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET,
                "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "userinfo_url": "https://api.linkedin.com/v2/me",
                "scopes": ["r_liteprofile", "r_emailaddress"],
                "name": "linkedin",
            },
        }


class SocialLoginService:
    """Social login integration service"""

    def __init__(self):
        self.config = SocialAuthConfig()
        self.oauth = OAuth()
        self._setup_oauth_clients()

        # State storage for OAuth flows (in production, use Redis)
        self._state_storage = {}

    def _setup_oauth_clients(self):
        """Setup OAuth clients for each provider"""
        for provider, config in self.config.providers.items():
            if config["client_id"] and config["client_secret"]:
                self.oauth.register(
                    name=config["name"],
                    client_id=config["client_id"],
                    client_secret=config["client_secret"],
                    authorize_url=config["auth_url"],
                    access_token_url=config["token_url"],
                    client_kwargs={"scope": " ".join(config["scopes"])},
                )

    def get_authorization_url(
        self, provider: SocialProvider, redirect_uri: str, state: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate OAuth2 authorization URL for social login

        Args:
            provider: Social provider enum
            redirect_uri: Callback URL after authorization
            state: Optional state parameter for CSRF protection

        Returns:
            Dictionary with authorization URL and state
        """
        if provider not in self.config.providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider {provider.value} not supported",
            )

        config = self.config.providers[provider]

        # Generate state for CSRF protection
        if not state:
            state = secrets.token_urlsafe(32)

        # Store state with expiration (5 minutes)
        self._state_storage[state] = {
            "provider": provider,
            "redirect_uri": redirect_uri,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
        }

        # Build authorization URL
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": " ".join(config["scopes"]),
            "response_type": "code",
            "state": state,
        }

        # Provider-specific parameters
        if provider == SocialProvider.GOOGLE:
            params["access_type"] = "offline"
            params["prompt"] = "consent"
        elif provider == SocialProvider.LINKEDIN:
            params["response_type"] = "code"

        auth_url = f"{config['auth_url']}?{urlencode(params)}"

        return {
            "authorization_url": auth_url,
            "state": state,
            "provider": provider.value,
        }

    async def handle_oauth_callback(
        self, provider: SocialProvider, code: str, state: str, db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Handle OAuth2 callback and retrieve user information

        Args:
            provider: Social provider enum
            code: Authorization code from callback
            state: State parameter for CSRF validation
            db: Database session

        Returns:
            Dictionary with user info and social login data
        """
        # Validate state
        if state not in self._state_storage:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state parameter",
            )

        state_data = self._state_storage[state]

        # Check expiration
        if datetime.utcnow() > state_data["expires_at"]:
            del self._state_storage[state]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State parameter expired",
            )

        # Validate provider matches
        if state_data["provider"] != provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Provider mismatch"
            )

        try:
            # Exchange code for token
            token_data = await self._exchange_code_for_token(
                provider, code, state_data["redirect_uri"]
            )

            # Get user info from provider
            user_info = await self._get_user_info(provider, token_data["access_token"])

            # Find or create social login record
            social_login = await self._find_or_create_social_login(
                provider, user_info, token_data, db
            )

            # Clean up state
            del self._state_storage[state]

            return {
                "social_login": social_login,
                "user_info": user_info,
                "provider": provider.value,
                "is_new_user": social_login.user_id is None,
            }

        except OAuth2Error as e:
            logger.error(f"OAuth2 error for {provider.value}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth2 authentication failed: {e.description}",
            )
        except Exception as e:
            logger.error(f"Social login error for {provider.value}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Social authentication failed",
            )

    async def _exchange_code_for_token(
        self, provider: SocialProvider, code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        config = self.config.providers[provider]

        token_data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data=token_data,
                headers={"Accept": "application/json"},
            )

            if response.status_code != 200:
                raise OAuth2Error(
                    f"Token exchange failed: {response.status_code} {response.text}"
                )

            return response.json()

    async def _get_user_info(
        self, provider: SocialProvider, access_token: str
    ) -> Dict[str, Any]:
        """Get user information from social provider"""
        config = self.config.providers[provider]

        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            if provider == SocialProvider.GITHUB:
                # GitHub requires user agent
                headers["User-Agent"] = "RazorFlow-AI"

                # Get user info
                user_response = await client.get(
                    config["userinfo_url"], headers=headers
                )
                if user_response.status_code != 200:
                    raise Exception(f"Failed to get user info: {user_response.text}")

                user_data = user_response.json()

                # Get primary email (GitHub specific)
                email_response = await client.get(
                    "https://api.github.com/user/emails", headers=headers
                )
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next(
                        (e["email"] for e in emails if e["primary"]),
                        user_data.get("email"),
                    )
                    user_data["email"] = primary_email

                return self._normalize_github_user_info(user_data)

            elif provider == SocialProvider.LINKEDIN:
                # LinkedIn requires multiple API calls

                # Get basic profile
                profile_response = await client.get(
                    config["userinfo_url"], headers=headers
                )
                if profile_response.status_code != 200:
                    raise Exception(f"Failed to get profile: {profile_response.text}")

                profile_data = profile_response.json()

                # Get email
                email_response = await client.get(
                    "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
                    headers=headers,
                )
                if email_response.status_code == 200:
                    email_data = email_response.json()
                    if email_data.get("elements"):
                        profile_data["email"] = email_data["elements"][0]["handle~"][
                            "emailAddress"
                        ]

                return self._normalize_linkedin_user_info(profile_data)

            else:  # Google
                response = await client.get(config["userinfo_url"], headers=headers)
                if response.status_code != 200:
                    raise Exception(f"Failed to get user info: {response.text}")

                return self._normalize_google_user_info(response.json())

    def _normalize_google_user_info(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Google user info to standard format"""
        return {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "first_name": user_data.get("given_name"),
            "last_name": user_data.get("family_name"),
            "avatar_url": user_data.get("picture"),
            "verified_email": user_data.get("verified_email", False),
            "locale": user_data.get("locale"),
            "provider": SocialProvider.GOOGLE.value,
        }

    def _normalize_github_user_info(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize GitHub user info to standard format"""
        full_name = user_data.get("name", "").strip()
        name_parts = full_name.split(" ", 1) if full_name else ["", ""]

        return {
            "id": str(user_data.get("id")),
            "email": user_data.get("email"),
            "name": full_name or user_data.get("login"),
            "first_name": name_parts[0] if len(name_parts) > 0 else "",
            "last_name": name_parts[1] if len(name_parts) > 1 else "",
            "avatar_url": user_data.get("avatar_url"),
            "verified_email": True,  # GitHub emails are verified
            "username": user_data.get("login"),
            "provider": SocialProvider.GITHUB.value,
        }

    def _normalize_linkedin_user_info(
        self, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize LinkedIn user info to standard format"""
        # LinkedIn v2 API response structure
        first_name = ""
        last_name = ""

        if "firstName" in user_data and "localized" in user_data["firstName"]:
            first_name = list(user_data["firstName"]["localized"].values())[0]

        if "lastName" in user_data and "localized" in user_data["lastName"]:
            last_name = list(user_data["lastName"]["localized"].values())[0]

        full_name = f"{first_name} {last_name}".strip()

        # Profile picture
        avatar_url = None
        if (
            "profilePicture" in user_data
            and "displayImage~" in user_data["profilePicture"]
        ):
            elements = user_data["profilePicture"]["displayImage~"].get("elements", [])
            if elements:
                avatar_url = elements[-1].get("identifiers", [{}])[0].get("identifier")

        return {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "avatar_url": avatar_url,
            "verified_email": True,  # LinkedIn emails are verified
            "provider": SocialProvider.LINKEDIN.value,
        }

    async def _find_or_create_social_login(
        self,
        provider: SocialProvider,
        user_info: Dict[str, Any],
        token_data: Dict[str, Any],
        db: AsyncSession,
    ) -> SocialLogin:
        """Find existing social login or create new one"""

        # Look for existing social login
        result = await db.execute(
            select(SocialLogin)
            .options(selectinload(SocialLogin.user))
            .where(
                SocialLogin.provider == provider,
                SocialLogin.provider_user_id == user_info["id"],
            )
        )

        social_login = result.scalar_one_or_none()

        if social_login:
            # Update existing record with fresh token data
            social_login.access_token = token_data.get("access_token")
            social_login.refresh_token = token_data.get("refresh_token")
            social_login.token_expires_at = self._calculate_token_expiry(token_data)
            social_login.last_login_at = datetime.utcnow()
            social_login.user_info = user_info

        else:
            # Create new social login record
            social_login = SocialLogin(
                provider=provider,
                provider_user_id=user_info["id"],
                email=user_info.get("email"),
                display_name=user_info.get("name"),
                avatar_url=user_info.get("avatar_url"),
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                token_expires_at=self._calculate_token_expiry(token_data),
                user_info=user_info,
                last_login_at=datetime.utcnow(),
            )

            db.add(social_login)

        await db.commit()
        await db.refresh(social_login)

        return social_login

    def _calculate_token_expiry(self, token_data: Dict[str, Any]) -> Optional[datetime]:
        """Calculate token expiry time"""
        expires_in = token_data.get("expires_in")
        if expires_in:
            return datetime.utcnow() + timedelta(seconds=int(expires_in))
        return None

    async def link_social_account(
        self, user_id: int, social_login_id: int, db: AsyncSession
    ) -> SocialLogin:
        """Link social account to existing user"""

        # Get social login record
        result = await db.execute(
            select(SocialLogin).where(SocialLogin.id == social_login_id)
        )

        social_login = result.scalar_one_or_none()
        if not social_login:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Social login not found"
            )

        if social_login.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Social account already linked",
            )

        # Check if email is already associated with another user
        if social_login.email:
            existing_user = await db.execute(
                select(User).where(User.email == social_login.email)
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already associated with another account",
                )

        # Link the account
        social_login.user_id = user_id
        social_login.linked_at = datetime.utcnow()

        await db.commit()
        await db.refresh(social_login)

        return social_login

    async def unlink_social_account(
        self, user_id: int, provider: SocialProvider, db: AsyncSession
    ) -> bool:
        """Unlink social account from user"""

        result = await db.execute(
            select(SocialLogin).where(
                SocialLogin.user_id == user_id, SocialLogin.provider == provider
            )
        )

        social_login = result.scalar_one_or_none()
        if not social_login:
            return False

        # Ensure user has other authentication methods
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if not user or not user.password_hash:
            # Check if user has other social logins
            other_socials = await db.execute(
                select(SocialLogin).where(
                    SocialLogin.user_id == user_id, SocialLogin.provider != provider
                )
            )

            if not other_socials.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot unlink the only authentication method",
                )

        # Unlink the account
        social_login.user_id = None
        social_login.linked_at = None

        await db.commit()

        return True

    async def get_user_social_accounts(
        self, user_id: int, db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get all social accounts linked to user"""

        result = await db.execute(
            select(SocialLogin).where(SocialLogin.user_id == user_id)
        )

        social_logins = result.scalars().all()

        return [
            {
                "id": login.id,
                "provider": login.provider.value,
                "email": login.email,
                "display_name": login.display_name,
                "avatar_url": login.avatar_url,
                "linked_at": login.linked_at,
                "last_login_at": login.last_login_at,
            }
            for login in social_logins
        ]


# Global social login service
social_login_service = SocialLoginService()
