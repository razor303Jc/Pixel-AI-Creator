"""
Multi-Factor Authentication (MFA) Service

This module provides comprehensive MFA functionality including:
- TOTP (Time-based One-Time Password) generation and verification
- QR code generation for authenticator apps
- Backup codes generation and management
- MFA setup and verification workflows
- Recovery mechanisms
"""

import secrets
import base64
import qrcode
import pyotp
from io import BytesIO
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
import logging

from core.config import settings
from core.database import get_db
from auth.advanced_database_models import MFAConfiguration as UserMFA
from models.database_schema import User

logger = logging.getLogger(__name__)


class MFAService:
    """Multi-Factor Authentication service for TOTP and backup codes"""

    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.issuer_name = "Pixel AI Creator"

    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for MFA secrets"""
        # In production, this should be stored securely (e.g., environment variable, vault)
        key = getattr(settings, "MFA_ENCRYPTION_KEY", None)
        if not key or key == "pixel-mfa-encryption-key-2024-secure":
            # Generate a key (in production, store this securely)
            key = Fernet.generate_key()
            logger.warning(
                "Generated new MFA encryption key. In production, store this securely!"
            )
        elif isinstance(key, str):
            try:
                # Try to decode as base64 first
                import base64

                key = base64.urlsafe_b64decode(key.encode())
            except Exception:
                # If that fails, generate a new key
                key = Fernet.generate_key()
                logger.warning("Invalid MFA encryption key format. Generated new key.")
        return key

    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    def generate_secret_key(self) -> str:
        """Generate a new TOTP secret key"""
        return pyotp.random_base32()

    def generate_totp_uri(self, user_email: str, secret_key: str) -> str:
        """Generate TOTP URI for QR code"""
        return pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=user_email, issuer_name=self.issuer_name
        )

    def generate_qr_code(self, totp_uri: str) -> str:
        """Generate QR code image as base64 string"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup recovery codes"""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            code = "".join(
                secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(8)
            )
            # Format as XXXX-XXXX for readability
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes

    def verify_totp_code(self, secret_key: str, code: str, window: int = 1) -> bool:
        """Verify TOTP code"""
        try:
            totp = pyotp.TOTP(secret_key)
            return totp.verify(code, valid_window=window)
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False

    def verify_backup_code(
        self, backup_codes: List[str], code: str
    ) -> Tuple[bool, List[str]]:
        """Verify backup code and remove it from the list"""
        # Normalize the input code
        normalized_code = code.replace("-", "").replace(" ", "").upper()

        updated_codes = []
        code_found = False

        for backup_code in backup_codes:
            normalized_backup = backup_code.replace("-", "").replace(" ", "").upper()
            if normalized_backup == normalized_code and not code_found:
                code_found = True
                # Don't add this code to updated list (remove it)
                continue
            updated_codes.append(backup_code)

        return code_found, updated_codes

    async def setup_mfa_for_user(
        self,
        user_id: int,
        user_email: str,
        db: AsyncSession,
        phone_number: Optional[str] = None,
        recovery_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Set up MFA for a user"""
        try:
            # Generate secret key and backup codes
            secret_key = self.generate_secret_key()
            backup_codes = self.generate_backup_codes()

            # Generate QR code
            totp_uri = self.generate_totp_uri(user_email, secret_key)
            qr_code = self.generate_qr_code(totp_uri)

            # Encrypt sensitive data
            encrypted_secret = self._encrypt_data(secret_key)
            encrypted_backup_codes = [self._encrypt_data(code) for code in backup_codes]

            # Check if user already has MFA record
            result = await db.execute(select(UserMFA).where(UserMFA.user_id == user_id))
            user_mfa = result.scalar_one_or_none()

            if user_mfa:
                # Update existing record
                user_mfa.secret_key = encrypted_secret
                user_mfa.backup_codes = encrypted_backup_codes
                user_mfa.is_enabled = False  # Will be enabled after verification
                user_mfa.phone_number = phone_number
                user_mfa.recovery_email = recovery_email
                user_mfa.updated_at = datetime.utcnow()
            else:
                # Create new record
                user_mfa = UserMFA(
                    user_id=user_id,
                    secret_key=encrypted_secret,
                    backup_codes=encrypted_backup_codes,
                    phone_number=phone_number,
                    recovery_email=recovery_email,
                    is_enabled=False,
                )
                db.add(user_mfa)

            await db.commit()

            return {
                "secret_key": secret_key,
                "qr_code_url": qr_code,
                "backup_codes": backup_codes,
                "manual_entry_key": secret_key,
                "totp_uri": totp_uri,
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"MFA setup error for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set up MFA",
            )

    async def verify_mfa_setup(
        self, user_id: int, verification_code: str, db: AsyncSession
    ) -> bool:
        """Verify MFA setup with initial code"""
        try:
            # Get user's MFA record (not yet enabled)
            result = await db.execute(
                select(UserMFA).where(
                    UserMFA.user_id == user_id, UserMFA.is_enabled == False
                )
            )
            user_mfa = result.scalar_one_or_none()

            if not user_mfa or not user_mfa.secret_key:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No pending MFA setup found",
                )

            # Decrypt secret key
            secret_key = self._decrypt_data(user_mfa.secret_key)

            # Verify the code
            if self.verify_totp_code(secret_key, verification_code):
                # Enable MFA
                user_mfa.is_enabled = True
                user_mfa.last_used = datetime.utcnow()
                user_mfa.updated_at = datetime.utcnow()

                await db.commit()

                logger.info(f"MFA enabled for user {user_id}")
                return True
            else:
                logger.warning(f"Invalid MFA verification code for user {user_id}")
                return False

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"MFA verification error for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify MFA setup",
            )

    async def verify_mfa_login(
        self, user_id: int, code: str, db: AsyncSession, is_backup_code: bool = False
    ) -> bool:
        """Verify MFA code during login"""
        try:
            # Get user's MFA record
            result = await db.execute(
                select(UserMFA).where(
                    UserMFA.user_id == user_id,
                    UserMFA.is_enabled.is_(True),
                )
            )
            user_mfa = result.scalar_one_or_none()

            if not user_mfa:
                logger.warning(f"No enabled MFA found for user {user_id}")
                return False

            if is_backup_code:
                # Verify backup code
                if not user_mfa.backup_codes:
                    return False

                # Decrypt backup codes
                backup_codes = [
                    self._decrypt_data(code) for code in user_mfa.backup_codes
                ]

                # Verify and update backup codes
                is_valid, updated_codes = self.verify_backup_code(backup_codes, code)

                if is_valid:
                    # Encrypt and update remaining backup codes
                    user_mfa.backup_codes = [
                        self._encrypt_data(code) for code in updated_codes
                    ]
                    user_mfa.last_used = datetime.utcnow()
                    user_mfa.updated_at = datetime.utcnow()

                    await db.commit()
                    logger.info(f"Backup code used for user {user_id}")
                    return True
                else:
                    logger.warning(f"Invalid backup code for user {user_id}")
                    return False

            else:
                # Verify TOTP code
                if not user_mfa.secret_key:
                    return False

                secret_key = self._decrypt_data(user_mfa.secret_key)

                if self.verify_totp_code(secret_key, code):
                    user_mfa.last_verified = datetime.utcnow()
                    user_mfa.updated_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"TOTP code verified for user {user_id}")
                    return True
                else:
                    logger.warning(f"Invalid TOTP code for user {user_id}")
                    return False

        except Exception as e:
            await db.rollback()
            logger.error(f"MFA login verification error for user {user_id}: {e}")
            return False

    async def disable_mfa(self, user_id: int, db: AsyncSession) -> bool:
        """Disable MFA for a user"""
        try:
            result = await db.execute(select(UserMFA).where(UserMFA.user_id == user_id))
            user_mfa = result.scalar_one_or_none()

            if user_mfa:
                user_mfa.is_enabled = False
                user_mfa.secret_key = None
                user_mfa.backup_codes = None
                user_mfa.updated_at = datetime.utcnow()

                await db.commit()
                logger.info(f"MFA disabled for user {user_id}")
                return True

            return False

        except Exception as e:
            await db.rollback()
            logger.error(f"MFA disable error for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to disable MFA",
            )

    async def get_user_mfa_status(
        self, user_id: int, db: AsyncSession
    ) -> Dict[str, Any]:
        """Get user's MFA status and information"""
        try:
            result = await db.execute(select(UserMFA).where(UserMFA.user_id == user_id))
            user_mfa = result.scalar_one_or_none()

            if not user_mfa:
                return {
                    "is_enabled": False,
                    "backup_codes_remaining": 0,
                    "last_used": None,
                }

            backup_codes_remaining = (
                len(user_mfa.backup_codes) if user_mfa.backup_codes else 0
            )

            return {
                "is_enabled": user_mfa.is_enabled,
                "backup_codes_remaining": backup_codes_remaining,
                "last_used": user_mfa.last_used,
                "phone_number": user_mfa.phone_number,
                "recovery_email": user_mfa.recovery_email,
            }

        except Exception as e:
            logger.error(f"Error getting MFA status for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get MFA status",
            )

    async def regenerate_backup_codes(
        self, user_id: int, db: AsyncSession
    ) -> List[str]:
        """Regenerate backup codes for a user"""
        try:
            result = await db.execute(
                select(UserMFA).where(
                    UserMFA.user_id == user_id, UserMFA.is_enabled.is_(True)
                )
            )
            user_mfa = result.scalar_one_or_none()

            if not user_mfa:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="MFA not enabled for user",
                )

            # Generate new backup codes
            new_backup_codes = self.generate_backup_codes()
            encrypted_backup_codes = [
                self._encrypt_data(code) for code in new_backup_codes
            ]

            # Update the record
            user_mfa.backup_codes = encrypted_backup_codes
            user_mfa.updated_at = datetime.utcnow()

            await db.commit()

            logger.info(f"Backup codes regenerated for user {user_id}")
            return new_backup_codes

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error regenerating backup codes for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to regenerate backup codes",
            )


# Global MFA service instance
mfa_service = MFAService()
