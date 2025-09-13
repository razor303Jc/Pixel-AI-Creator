"""
Social Login Integration Service
Provides OAuth integration with Google, GitHub, LinkedIn, and Microsoft.
"""

import httpx
import jwt
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .advanced_models import (
    SocialProvider,
    SocialLoginRequest,
    SocialLoginResponse,
    SocialAccountLink,
)
from core.config import settings

logger = logging.getLogger(__name__)


class SocialLoginService:
    """Social login integration service"""

    def __init__(self):
        self.google_client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
        self.github_client_id = getattr(settings, "GITHUB_CLIENT_ID", "")
        self.linkedin_client_id = getattr(settings, "LINKEDIN_CLIENT_ID", "")
        self.microsoft_client_id = getattr(settings, "MICROSOFT_CLIENT_ID", "")

        # Provider configurations
        self.provider_configs = {
            SocialProvider.GOOGLE: {
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scope": "openid email profile",
                "client_id": self.google_client_id,
            },
            SocialProvider.GITHUB: {
                "token_url": "https://github.com/login/oauth/access_token",
                "user_info_url": "https://api.github.com/user",
                "scope": "user:email",
                "client_id": self.github_client_id,
            },
            SocialProvider.LINKEDIN: {
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "user_info_url": "https://api.linkedin.com/v2/people/~",
                "scope": "r_liteprofile r_emailaddress",
                "client_id": self.linkedin_client_id,
            },
            SocialProvider.MICROSOFT: {
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "user_info_url": "https://graph.microsoft.com/v1.0/me",
                "scope": "openid email profile",
                "client_id": self.microsoft_client_id,
            },
        }

    async def get_user_info_from_token(
        self, provider: SocialProvider, access_token: str
    ) -> Dict[str, Any]:
        """Get user information from social provider using access token

        Args:
            provider: Social provider
            access_token: OAuth access token

        Returns:
            User information from provider

        Raises:
            Exception: If unable to fetch user information
        """
        try:
            config = self.provider_configs.get(provider)
            if not config:
                raise ValueError(f"Unsupported provider: {provider}")

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    config["user_info_url"], headers=headers, timeout=10.0
                )

                if response.status_code != 200:
                    logger.error(
                        f"Failed to fetch user info from {provider}: {response.status_code}"
                    )
                    raise Exception(f"Failed to fetch user information from {provider}")

                user_data = response.json()

                # Normalize user data across providers
                return self._normalize_user_data(provider, user_data)

        except Exception as e:
            logger.error(f"Error fetching user info from {provider}: {e}")
            raise

    def _normalize_user_data(
        self, provider: SocialProvider, raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize user data from different providers to a common format

        Args:
            provider: Social provider
            raw_data: Raw user data from provider

        Returns:
            Normalized user data
        """
        if provider == SocialProvider.GOOGLE:
            return {
                "provider_id": raw_data.get("id"),
                "email": raw_data.get("email"),
                "first_name": raw_data.get("given_name", ""),
                "last_name": raw_data.get("family_name", ""),
                "full_name": raw_data.get("name", ""),
                "avatar_url": raw_data.get("picture"),
                "profile_url": None,
                "verified_email": raw_data.get("verified_email", False),
            }

        elif provider == SocialProvider.GITHUB:
            return {
                "provider_id": str(raw_data.get("id")),
                "email": raw_data.get("email"),
                "first_name": (
                    raw_data.get("name", "").split(" ")[0]
                    if raw_data.get("name")
                    else ""
                ),
                "last_name": (
                    " ".join(raw_data.get("name", "").split(" ")[1:])
                    if raw_data.get("name")
                    else ""
                ),
                "full_name": raw_data.get("name", ""),
                "avatar_url": raw_data.get("avatar_url"),
                "profile_url": raw_data.get("html_url"),
                "verified_email": True,  # GitHub provides verified emails
            }

        elif provider == SocialProvider.LINKEDIN:
            return {
                "provider_id": raw_data.get("id"),
                "email": raw_data.get("emailAddress"),  # From additional API call
                "first_name": raw_data.get("localizedFirstName", ""),
                "last_name": raw_data.get("localizedLastName", ""),
                "full_name": f"{raw_data.get('localizedFirstName', '')} {raw_data.get('localizedLastName', '')}".strip(),
                "avatar_url": None,  # Would need additional API call
                "profile_url": None,
                "verified_email": True,
            }

        elif provider == SocialProvider.MICROSOFT:
            return {
                "provider_id": raw_data.get("id"),
                "email": raw_data.get("mail") or raw_data.get("userPrincipalName"),
                "first_name": raw_data.get("givenName", ""),
                "last_name": raw_data.get("surname", ""),
                "full_name": raw_data.get("displayName", ""),
                "avatar_url": None,  # Would need Microsoft Graph photo endpoint
                "profile_url": None,
                "verified_email": True,
            }

        else:
            # Default format
            return {
                "provider_id": str(raw_data.get("id")),
                "email": raw_data.get("email"),
                "first_name": raw_data.get("first_name", ""),
                "last_name": raw_data.get("last_name", ""),
                "full_name": raw_data.get("name", ""),
                "avatar_url": raw_data.get("avatar_url"),
                "profile_url": raw_data.get("profile_url"),
                "verified_email": False,
            }

    async def verify_google_token(self, access_token: str) -> Dict[str, Any]:
        """Verify Google OAuth token and get user info

        Args:
            access_token: Google OAuth access token

        Returns:
            Verified user information
        """
        try:
            # Verify token with Google
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}",
                    timeout=10.0,
                )

                if response.status_code != 200:
                    raise Exception("Invalid Google token")

                token_info = response.json()

                # Check if token is for our app
                if token_info.get("audience") != self.google_client_id:
                    raise Exception("Token not for this application")

                # Get user info
                return await self.get_user_info_from_token(
                    SocialProvider.GOOGLE, access_token
                )

        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            raise

    async def verify_github_token(self, access_token: str) -> Dict[str, Any]:
        """Verify GitHub OAuth token and get user info

        Args:
            access_token: GitHub OAuth access token

        Returns:
            Verified user information
        """
        try:
            # GitHub doesn't have a token verification endpoint,
            # so we'll try to get user info directly
            return await self.get_user_info_from_token(
                SocialProvider.GITHUB, access_token
            )

        except Exception as e:
            logger.error(f"Error verifying GitHub token: {e}")
            raise

    def get_authorization_url(
        self, provider: SocialProvider, redirect_uri: str, state: str
    ) -> str:
        """Get OAuth authorization URL for a provider

        Args:
            provider: Social provider
            redirect_uri: Redirect URI after authorization
            state: State parameter for security

        Returns:
            Authorization URL
        """
        config = self.provider_configs.get(provider)
        if not config:
            raise ValueError(f"Unsupported provider: {provider}")

        if provider == SocialProvider.GOOGLE:
            return (
                f"https://accounts.google.com/o/oauth2/v2/auth?"
                f"client_id={config['client_id']}&"
                f"redirect_uri={redirect_uri}&"
                f"scope={config['scope']}&"
                f"response_type=code&"
                f"state={state}"
            )

        elif provider == SocialProvider.GITHUB:
            return (
                f"https://github.com/login/oauth/authorize?"
                f"client_id={config['client_id']}&"
                f"redirect_uri={redirect_uri}&"
                f"scope={config['scope']}&"
                f"state={state}"
            )

        elif provider == SocialProvider.LINKEDIN:
            return (
                f"https://www.linkedin.com/oauth/v2/authorization?"
                f"response_type=code&"
                f"client_id={config['client_id']}&"
                f"redirect_uri={redirect_uri}&"
                f"scope={config['scope']}&"
                f"state={state}"
            )

        elif provider == SocialProvider.MICROSOFT:
            return (
                f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
                f"client_id={config['client_id']}&"
                f"response_type=code&"
                f"redirect_uri={redirect_uri}&"
                f"scope={config['scope']}&"
                f"state={state}"
            )

        else:
            raise ValueError(f"Authorization URL not implemented for {provider}")

    async def exchange_code_for_token(
        self, provider: SocialProvider, code: str, redirect_uri: str
    ) -> str:
        """Exchange authorization code for access token

        Args:
            provider: Social provider
            code: Authorization code
            redirect_uri: Redirect URI used in authorization

        Returns:
            Access token
        """
        config = self.provider_configs.get(provider)
        if not config:
            raise ValueError(f"Unsupported provider: {provider}")

        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "client_id": config["client_id"],
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }

                # Add client secret (would be configured in settings)
                client_secret = getattr(
                    settings, f"{provider.upper()}_CLIENT_SECRET", ""
                )
                if client_secret:
                    data["client_secret"] = client_secret

                response = await client.post(
                    config["token_url"],
                    data=data,
                    headers={"Accept": "application/json"},
                    timeout=10.0,
                )

                if response.status_code != 200:
                    logger.error(
                        f"Token exchange failed for {provider}: {response.status_code}"
                    )
                    raise Exception(f"Failed to exchange code for token")

                token_data = response.json()
                return token_data.get("access_token")

        except Exception as e:
            logger.error(f"Error exchanging code for token ({provider}): {e}")
            raise

    def create_social_account_link(
        self, provider: SocialProvider, user_data: Dict[str, Any]
    ) -> SocialAccountLink:
        """Create social account link information

        Args:
            provider: Social provider
            user_data: Normalized user data

        Returns:
            Social account link information
        """
        return SocialAccountLink(
            provider=provider,
            provider_id=user_data["provider_id"],
            email=user_data["email"],
            profile_url=user_data.get("profile_url"),
            avatar_url=user_data.get("avatar_url"),
            linked_at=datetime.utcnow(),
        )


# Global social login service instance
social_login_service = SocialLoginService()
