"""
Password Strength Validation Service

This module provides comprehensive password strength validation including:
- zxcvbn-based password strength scoring
- Custom password policy enforcement
- Password history tracking
- Breach detection (optional)
- Password generation utilities
"""

import re
import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from zxcvbn import zxcvbn
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from fastapi import HTTPException, status

from auth.advanced_database_models import PasswordHistory
from auth.jwt import hash_password
from models.database_schema import User

logger = logging.getLogger(__name__)


class PasswordPolicy:
    """Password policy configuration"""

    def __init__(self):
        # Minimum requirements
        self.min_length = 8
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_numbers = True
        self.require_symbols = True

        # Advanced requirements
        self.min_score = 2  # zxcvbn score 0-4
        self.prevent_reuse_count = 5  # Prevent reusing last N passwords
        self.max_age_days = 90  # Force password change after N days
        self.prevent_common = True  # Prevent common passwords

        # Symbol characters
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"


class PasswordStrengthService:
    """Password strength validation and policy enforcement service"""

    def __init__(self, policy: Optional[PasswordPolicy] = None):
        self.policy = policy or PasswordPolicy()

        # Common weak passwords (subset)
        self.common_passwords = {
            "password",
            "123456",
            "password123",
            "admin",
            "qwerty",
            "letmein",
            "welcome",
            "monkey",
            "dragon",
            "master",
            "1234567890",
            "password1",
            "123123",
            "abc123",
        }

    def analyze_password_strength(
        self, password: str, user_inputs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze password strength using multiple criteria

        Args:
            password: Password to analyze
            user_inputs: List of user-specific inputs (name, email, etc.)

        Returns:
            Dictionary with strength analysis
        """
        if user_inputs is None:
            user_inputs = []

        # Basic validation
        basic_checks = self._check_basic_requirements(password)

        # zxcvbn analysis
        zxcvbn_result = zxcvbn(password, user_inputs=user_inputs)

        # Custom analysis
        custom_checks = self._custom_analysis(password)

        # Combine results
        overall_score = min(basic_checks["score"], zxcvbn_result["score"])

        # Generate feedback
        feedback = self._generate_feedback(
            password, basic_checks, zxcvbn_result, custom_checks
        )

        # Determine if password meets policy
        meets_policy = (
            basic_checks["valid"]
            and overall_score >= self.policy.min_score
            and not custom_checks["is_common"]
        )

        return {
            "score": overall_score,
            "is_valid": meets_policy,
            "feedback": {
                "basic_checks": basic_checks,
                "zxcvbn": {
                    "score": zxcvbn_result["score"],
                    "guesses": zxcvbn_result["guesses"],
                    "crack_times": zxcvbn_result["crack_times_display"],
                    "feedback": zxcvbn_result["feedback"],
                },
                "custom_checks": custom_checks,
            },
            "suggestions": feedback["suggestions"],
            "warnings": feedback["warnings"],
            "estimated_crack_time": zxcvbn_result["crack_times_display"][
                "offline_slow_hashing_1e4_per_second"
            ],
        }

    def _check_basic_requirements(self, password: str) -> Dict[str, Any]:
        """Check basic password requirements"""
        checks = {
            "length": len(password) >= self.policy.min_length
            and len(password) <= self.policy.max_length,
            "uppercase": not self.policy.require_uppercase
            or bool(re.search(r"[A-Z]", password)),
            "lowercase": not self.policy.require_lowercase
            or bool(re.search(r"[a-z]", password)),
            "numbers": not self.policy.require_numbers
            or bool(re.search(r"\d", password)),
            "symbols": not self.policy.require_symbols
            or bool(re.search(f"[{re.escape(self.policy.symbols)}]", password)),
        }

        # Calculate basic score (0-4 based on requirements met)
        score = sum(
            [
                checks["length"],
                checks["uppercase"],
                checks["lowercase"],
                checks["numbers"],
                checks["symbols"],
            ]
        )

        # Normalize to 0-4 scale
        score = min(4, max(0, score - 1))  # Subtract 1 because length is mandatory

        checks.update({"score": score, "valid": all(checks.values())})

        return checks

    def _custom_analysis(self, password: str) -> Dict[str, Any]:
        """Custom password analysis"""
        analysis = {
            "is_common": password.lower() in self.common_passwords,
            "has_repeating": self._has_excessive_repeating(password),
            "has_sequences": self._has_sequences(password),
            "entropy": self._calculate_entropy(password),
            "patterns": self._detect_patterns(password),
        }

        return analysis

    def _has_excessive_repeating(self, password: str, max_repeat: int = 3) -> bool:
        """Check for excessive character repetition"""
        for i in range(len(password) - max_repeat + 1):
            if len(set(password[i : i + max_repeat])) == 1:
                return True
        return False

    def _has_sequences(self, password: str, min_length: int = 3) -> bool:
        """Check for sequential characters"""
        sequences = [
            "abcdefghijklmnopqrstuvwxyz",
            "0123456789",
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm",
        ]

        password_lower = password.lower()

        for sequence in sequences:
            for i in range(len(sequence) - min_length + 1):
                subseq = sequence[i : i + min_length]
                if subseq in password_lower or subseq[::-1] in password_lower:
                    return True

        return False

    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy"""
        charset_size = 0

        if re.search(r"[a-z]", password):
            charset_size += 26
        if re.search(r"[A-Z]", password):
            charset_size += 26
        if re.search(r"\d", password):
            charset_size += 10
        if re.search(f"[{re.escape(self.policy.symbols)}]", password):
            charset_size += len(self.policy.symbols)

        if charset_size == 0:
            return 0.0

        import math

        return len(password) * math.log2(charset_size)

    def _detect_patterns(self, password: str) -> List[str]:
        """Detect common password patterns"""
        patterns = []

        # Date patterns
        if re.search(r"\d{4}", password):  # Year
            patterns.append("contains_year")
        if re.search(r"\d{1,2}/\d{1,2}", password):  # Date
            patterns.append("contains_date")

        # Keyboard patterns
        keyboard_patterns = ["qwer", "asdf", "zxcv", "1234"]
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                patterns.append("keyboard_pattern")
                break

        # Word + number pattern
        if re.search(r"^[a-zA-Z]+\d+$", password) or re.search(
            r"^\d+[a-zA-Z]+$", password
        ):
            patterns.append("word_number_pattern")

        return patterns

    def _generate_feedback(
        self,
        password: str,
        basic_checks: Dict[str, Any],
        zxcvbn_result: Dict[str, Any],
        custom_checks: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate user-friendly feedback"""
        suggestions = []
        warnings = []

        # Basic requirement suggestions
        if not basic_checks["length"]:
            suggestions.append(f"Use at least {self.policy.min_length} characters")
        if not basic_checks["uppercase"]:
            suggestions.append("Add uppercase letters")
        if not basic_checks["lowercase"]:
            suggestions.append("Add lowercase letters")
        if not basic_checks["numbers"]:
            suggestions.append("Add numbers")
        if not basic_checks["symbols"]:
            suggestions.append("Add symbols")

        # zxcvbn feedback
        if zxcvbn_result["feedback"]["suggestions"]:
            suggestions.extend(zxcvbn_result["feedback"]["suggestions"])
        if zxcvbn_result["feedback"]["warning"]:
            warnings.append(zxcvbn_result["feedback"]["warning"])

        # Custom feedback
        if custom_checks["is_common"]:
            warnings.append("This is a commonly used password")
        if custom_checks["has_repeating"]:
            warnings.append("Avoid repeating characters")
        if custom_checks["has_sequences"]:
            warnings.append("Avoid sequences of characters")

        return {"suggestions": suggestions, "warnings": warnings}

    async def validate_password_history(
        self, user_id: int, new_password: str, db: AsyncSession
    ) -> bool:
        """Check if password was recently used"""
        try:
            # Get recent password history
            result = await db.execute(
                select(PasswordHistory)
                .where(PasswordHistory.user_id == user_id)
                .order_by(desc(PasswordHistory.created_at))
                .limit(self.policy.prevent_reuse_count)
            )

            recent_passwords = result.scalars().all()

            # Hash the new password for comparison
            new_password_hash = hash_password(new_password)

            # Check against recent passwords
            for password_record in recent_passwords:
                # For security, we compare hashes
                if password_record.password_hash == new_password_hash:
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating password history for user {user_id}: {e}")
            # On error, allow the password change but log it
            return True

    async def add_to_password_history(
        self,
        user_id: int,
        password_hash: str,
        db: AsyncSession,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        changed_by_user: bool = True,
    ) -> None:
        """Add password to history"""
        try:
            password_history = PasswordHistory(
                user_id=user_id,
                password_hash=password_hash,
                changed_by_user=changed_by_user,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            db.add(password_history)
            await db.commit()

            # Clean up old history (keep only the required count)
            cleanup_result = await db.execute(
                select(PasswordHistory)
                .where(PasswordHistory.user_id == user_id)
                .order_by(desc(PasswordHistory.created_at))
                .offset(self.policy.prevent_reuse_count)
            )

            old_records = cleanup_result.scalars().all()
            for record in old_records:
                await db.delete(record)

            await db.commit()

        except Exception as e:
            logger.error(f"Error adding password to history for user {user_id}: {e}")
            await db.rollback()

    def generate_strong_password(self, length: int = 16) -> str:
        """Generate a cryptographically strong password"""
        import secrets
        import string

        # Ensure we meet all requirements
        password = []

        # Add required character types
        if self.policy.require_uppercase:
            password.append(secrets.choice(string.ascii_uppercase))
        if self.policy.require_lowercase:
            password.append(secrets.choice(string.ascii_lowercase))
        if self.policy.require_numbers:
            password.append(secrets.choice(string.digits))
        if self.policy.require_symbols:
            password.append(secrets.choice(self.policy.symbols))

        # Fill remaining length
        all_chars = ""
        if self.policy.require_uppercase:
            all_chars += string.ascii_uppercase
        if self.policy.require_lowercase:
            all_chars += string.ascii_lowercase
        if self.policy.require_numbers:
            all_chars += string.digits
        if self.policy.require_symbols:
            all_chars += self.policy.symbols

        remaining_length = length - len(password)
        for _ in range(remaining_length):
            password.append(secrets.choice(all_chars))

        # Shuffle the password
        secrets.SystemRandom().shuffle(password)

        return "".join(password)


# Global password strength service
password_strength_service = PasswordStrengthService()
