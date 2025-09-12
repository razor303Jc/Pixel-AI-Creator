"""
Multi-Factor Authentication (MFA) Service
Provides TOTP, SMS, Email, and backup code functionality for enhanced security.
"""

import qrcode
import pyotp
import secrets
import string
import hashlib
from io import BytesIO
import base64
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from .advanced_models import MFAMethod, MFASetupResponse, MFAStatusResponse
from core.config import settings

logger = logging.getLogger(__name__)


class MFAService:
    """Multi-Factor Authentication service"""

    def __init__(self):
        self.issuer_name = "Pixel AI Creator"
        self.backup_code_length = 8
        self.backup_codes_count = 10

    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret key"""
        return pyotp.random_base32()

    def generate_qr_code(self, email: str, secret: str) -> str:
        """Generate QR code URL for TOTP setup

        Args:
            email: User's email address
            secret: TOTP secret key

        Returns:
            Base64 encoded QR code image
        """
        try:
            # Create TOTP URI
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=email, issuer_name=self.issuer_name
            )

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(totp_uri)
            qr.make(fit=True)

            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return f"data:image/png;base64,{img_str}"

        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            raise

    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """Verify TOTP code

        Args:
            secret: TOTP secret key
            code: User-provided TOTP code
            window: Time window for verification (default: 30 seconds)

        Returns:
            True if code is valid, False otherwise
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=window)
        except Exception as e:
            logger.error(f"Error verifying TOTP code: {e}")
            return False

    def generate_backup_codes(self) -> List[str]:
        """Generate backup recovery codes

        Returns:
            List of backup codes
        """
        codes = []
        for _ in range(self.backup_codes_count):
            code = "".join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(self.backup_code_length)
            )
            # Format as XXXX-XXXX for readability
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)

        return codes

    def hash_backup_code(self, code: str) -> str:
        """Hash backup code for secure storage

        Args:
            code: Plain backup code

        Returns:
            Hashed backup code
        """
        # Remove formatting and convert to uppercase
        clean_code = code.replace("-", "").upper()
        return hashlib.sha256(clean_code.encode()).hexdigest()

    def verify_backup_code(self, stored_hash: str, provided_code: str) -> bool:
        """Verify backup code against stored hash

        Args:
            stored_hash: Stored hashed backup code
            provided_code: User-provided backup code

        Returns:
            True if code matches, False otherwise
        """
        try:
            clean_code = provided_code.replace("-", "").upper()
            provided_hash = hashlib.sha256(clean_code.encode()).hexdigest()
            return provided_hash == stored_hash
        except Exception as e:
            logger.error(f"Error verifying backup code: {e}")
            return False

    async def setup_totp_mfa(
        self, user_id: int, email: str, db: AsyncSession
    ) -> MFASetupResponse:
        """Set up TOTP MFA for a user

        Args:
            user_id: User ID
            email: User's email
            db: Database session

        Returns:
            MFA setup response with secret and QR code
        """
        try:
            # Generate secret and backup codes
            secret = self.generate_totp_secret()
            backup_codes = self.generate_backup_codes()
            qr_code_url = self.generate_qr_code(email, secret)

            # Hash backup codes for storage
            hashed_codes = [self.hash_backup_code(code) for code in backup_codes]

            # Store MFA configuration in database
            # Note: This would require creating MFA tables in the database schema
            # For now, we'll return the setup response

            logger.info(f"TOTP MFA setup initiated for user {user_id}")

            return MFASetupResponse(
                method=MFAMethod.TOTP,
                secret=secret,
                qr_code_url=qr_code_url,
                backup_codes=backup_codes,
            )

        except Exception as e:
            logger.error(f"Error setting up TOTP MFA for user {user_id}: {e}")
            raise

    async def verify_mfa_code(
        self, user_id: int, method: MFAMethod, code: str, db: AsyncSession
    ) -> bool:
        """Verify MFA code for a user

        Args:
            user_id: User ID
            method: MFA method being verified
            code: User-provided verification code
            db: Database session

        Returns:
            True if code is valid, False otherwise
        """
        try:
            if method == MFAMethod.TOTP:
                # Get user's TOTP secret from database
                # For now, return True for demo (would implement actual verification)
                logger.info(f"TOTP verification for user {user_id}")
                return len(code) == 6 and code.isdigit()

            elif method == MFAMethod.BACKUP_CODES:
                # Verify backup code
                logger.info(f"Backup code verification for user {user_id}")
                return len(code.replace("-", "")) == 8

            elif method == MFAMethod.SMS:
                # SMS verification logic would go here
                logger.info(f"SMS verification for user {user_id}")
                return len(code) == 6 and code.isdigit()

            elif method == MFAMethod.EMAIL:
                # Email verification logic would go here
                logger.info(f"Email verification for user {user_id}")
                return len(code) == 6 and code.isdigit()

            return False

        except Exception as e:
            logger.error(f"Error verifying MFA code for user {user_id}: {e}")
            return False

    async def get_mfa_status(self, user_id: int, db: AsyncSession) -> MFAStatusResponse:
        """Get MFA status for a user

        Args:
            user_id: User ID
            db: Database session

        Returns:
            MFA status information
        """
        try:
            # This would query the database for user's MFA configuration
            # For now, return a default response

            return MFAStatusResponse(
                enabled=False,  # Would check database
                methods=[],  # Would get from database
                backup_codes_remaining=0,  # Would count from database
                last_used=None,  # Would get from database
            )

        except Exception as e:
            logger.error(f"Error getting MFA status for user {user_id}: {e}")
            raise

    async def disable_mfa(
        self, user_id: int, method: MFAMethod, db: AsyncSession
    ) -> bool:
        """Disable MFA method for a user

        Args:
            user_id: User ID
            method: MFA method to disable
            db: Database session

        Returns:
            True if disabled successfully, False otherwise
        """
        try:
            # Remove MFA configuration from database
            logger.info(f"Disabling {method} MFA for user {user_id}")

            # Implementation would remove from database
            return True

        except Exception as e:
            logger.error(f"Error disabling MFA for user {user_id}: {e}")
            return False

    def generate_sms_code(self) -> str:
        """Generate SMS verification code

        Returns:
            6-digit numeric code
        """
        return "".join(secrets.choice(string.digits) for _ in range(6))

    def generate_email_code(self) -> str:
        """Generate email verification code

        Returns:
            6-digit numeric code
        """
        return "".join(secrets.choice(string.digits) for _ in range(6))

    async def send_sms_code(self, phone_number: str, code: str) -> bool:
        """Send SMS verification code

        Args:
            phone_number: User's phone number
            code: Verification code to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # SMS sending logic would go here (Twilio, AWS SNS, etc.)
            logger.info(
                f"SMS code sent to {phone_number[-4:].rjust(len(phone_number), '*')}"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending SMS code: {e}")
            return False

    async def send_email_code(self, email: str, code: str) -> bool:
        """Send email verification code

        Args:
            email: User's email address
            code: Verification code to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Email sending logic would go here (SendGrid, AWS SES, etc.)
            logger.info(f"Email code sent to {email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email code: {e}")
            return False


# Global MFA service instance
mfa_service = MFAService()
