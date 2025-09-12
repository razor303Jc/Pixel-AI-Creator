"""
Password Strength and Policy Service
Provides comprehensive password validation, strength analysis, and policy enforcement.
"""

import re
import math
import string
from typing import List, Dict, Any, Set
from .advanced_models import PasswordPolicy, PasswordStrengthResponse
import logging

logger = logging.getLogger(__name__)


class PasswordPolicyService:
    """Password policy and strength validation service"""

    def __init__(self):
        # Common weak passwords (subset - in production, use a comprehensive list)
        self.common_passwords = {
            "password",
            "123456",
            "123456789",
            "qwerty",
            "abc123",
            "password123",
            "admin",
            "letmein",
            "welcome",
            "monkey",
            "1234567890",
            "password1",
            "123123",
            "qwertyuiop",
            "iloveyou",
            "adobe123",
            "123qwe",
            "admin123",
        }

        # Character sets for entropy calculation
        self.char_sets = {
            "lowercase": set(string.ascii_lowercase),
            "uppercase": set(string.ascii_uppercase),
            "digits": set(string.digits),
            "special": set("!@#$%^&*(),.?\":{}|<>[]\\;'`~_+-="),
        }

    def get_default_policy(self) -> PasswordPolicy:
        """Get default password policy

        Returns:
            Default password policy configuration
        """
        return PasswordPolicy()

    def calculate_entropy(self, password: str) -> float:
        """Calculate password entropy

        Args:
            password: Password to analyze

        Returns:
            Entropy value in bits
        """
        if not password:
            return 0.0

        # Determine character set size
        charset_size = 0
        used_chars = set(password)

        for char_set in self.char_sets.values():
            if used_chars & char_set:
                charset_size += len(char_set)

        if charset_size == 0:
            charset_size = 1

        # Calculate entropy: log2(charset_size^length)
        entropy = len(password) * math.log2(charset_size)
        return entropy

    def estimate_crack_time(self, entropy: float) -> str:
        """Estimate time to crack password based on entropy

        Args:
            entropy: Password entropy in bits

        Returns:
            Human-readable crack time estimate
        """
        # Assume 1 billion guesses per second (conservative for modern hardware)
        guesses_per_second = 1_000_000_000

        # Average time is half the keyspace
        total_combinations = 2**entropy
        average_time_seconds = (total_combinations / 2) / guesses_per_second

        if average_time_seconds < 1:
            return "Instantly"
        elif average_time_seconds < 60:
            return f"{int(average_time_seconds)} seconds"
        elif average_time_seconds < 3600:
            return f"{int(average_time_seconds / 60)} minutes"
        elif average_time_seconds < 86400:
            return f"{int(average_time_seconds / 3600)} hours"
        elif average_time_seconds < 31536000:
            return f"{int(average_time_seconds / 86400)} days"
        elif average_time_seconds < 31536000000:
            return f"{int(average_time_seconds / 31536000)} years"
        else:
            return "Centuries"

    def check_common_patterns(self, password: str) -> List[str]:
        """Check for common weak patterns

        Args:
            password: Password to check

        Returns:
            List of detected weak patterns
        """
        patterns = []

        # Check for common passwords
        if password.lower() in self.common_passwords:
            patterns.append("This is a commonly used password")

        # Check for keyboard patterns
        keyboard_patterns = ["qwerty", "asdf", "zxcv", "1234", "abcd"]
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                patterns.append(f"Contains keyboard pattern: {pattern}")

        # Check for repeated characters
        if re.search(r"(.)\1{2,}", password):
            patterns.append("Contains repeated characters")

        # Check for simple sequences
        if re.search(r"(012|123|234|345|456|567|678|789|890)", password):
            patterns.append("Contains number sequence")

        if re.search(
            r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",
            password.lower(),
        ):
            patterns.append("Contains alphabetical sequence")

        # Check for years
        current_year = 2025
        for year in range(1950, current_year + 10):
            if str(year) in password:
                patterns.append(f"Contains year: {year}")
                break

        return patterns

    def check_personal_info(
        self, password: str, user_info: Dict[str, str]
    ) -> List[str]:
        """Check if password contains personal information

        Args:
            password: Password to check
            user_info: Dictionary containing user's personal info

        Returns:
            List of personal info found in password
        """
        issues = []
        password_lower = password.lower()

        # Check common personal info fields
        personal_fields = ["first_name", "last_name", "email", "company_name", "phone"]

        for field in personal_fields:
            if field in user_info and user_info[field]:
                value = str(user_info[field]).lower()

                # Remove common separators and check
                clean_value = re.sub(r"[.@_-]", "", value)
                if len(clean_value) > 2 and clean_value in password_lower:
                    issues.append(f"Contains {field.replace('_', ' ')}")

                # Check email username
                if field == "email" and "@" in value:
                    username = value.split("@")[0]
                    if len(username) > 2 and username in password_lower:
                        issues.append("Contains email username")

        return issues

    def validate_policy_compliance(
        self, password: str, policy: PasswordPolicy
    ) -> List[str]:
        """Check password against policy requirements

        Args:
            password: Password to validate
            policy: Password policy to check against

        Returns:
            List of policy violations
        """
        violations = []

        # Check length
        if len(password) < policy.min_length:
            violations.append(f"Must be at least {policy.min_length} characters long")

        if len(password) > policy.max_length:
            violations.append(
                f"Must be no more than {policy.max_length} characters long"
            )

        # Check character requirements
        if policy.require_uppercase and not re.search(r"[A-Z]", password):
            violations.append("Must contain at least one uppercase letter")

        if policy.require_lowercase and not re.search(r"[a-z]", password):
            violations.append("Must contain at least one lowercase letter")

        if policy.require_numbers and not re.search(r"\d", password):
            violations.append("Must contain at least one number")

        if policy.require_special_chars:
            special_count = len(
                re.findall(r"[!@#$%^&*(),.?\":{}|<>[\]\\;\'`~_+\-=]", password)
            )
            if special_count == 0:
                violations.append("Must contain at least one special character")
            elif special_count < policy.min_special_chars:
                violations.append(
                    f"Must contain at least {policy.min_special_chars} special characters"
                )

        return violations

    def calculate_password_score(self, password: str, policy: PasswordPolicy) -> int:
        """Calculate password strength score (0-100)

        Args:
            password: Password to score
            policy: Password policy for scoring criteria

        Returns:
            Password strength score (0-100)
        """
        if not password:
            return 0

        score = 0

        # Length score (30 points max)
        length_score = min(30, (len(password) / policy.max_length) * 30)
        score += length_score

        # Character diversity score (40 points max)
        char_types = 0
        if re.search(r"[a-z]", password):
            char_types += 1
        if re.search(r"[A-Z]", password):
            char_types += 1
        if re.search(r"\d", password):
            char_types += 1
        if re.search(r"[!@#$%^&*(),.?\":{}|<>[\]\\;\'`~_+\-=]", password):
            char_types += 1

        diversity_score = (char_types / 4) * 40
        score += diversity_score

        # Entropy score (20 points max)
        entropy = self.calculate_entropy(password)
        entropy_score = min(20, (entropy / 80) * 20)  # 80 bits is considered strong
        score += entropy_score

        # Pattern penalty (deduct points for weak patterns)
        patterns = self.check_common_patterns(password)
        pattern_penalty = min(30, len(patterns) * 10)
        score -= pattern_penalty

        # Ensure score is between 0 and 100
        return max(0, min(100, int(score)))

    def get_strength_level(self, score: int) -> str:
        """Get password strength level based on score

        Args:
            score: Password strength score (0-100)

        Returns:
            Strength level description
        """
        if score < 25:
            return "Very Weak"
        elif score < 50:
            return "Weak"
        elif score < 70:
            return "Fair"
        elif score < 85:
            return "Good"
        else:
            return "Strong"

    def analyze_password_strength(
        self,
        password: str,
        policy: PasswordPolicy = None,
        user_info: Dict[str, str] = None,
    ) -> PasswordStrengthResponse:
        """Comprehensive password strength analysis

        Args:
            password: Password to analyze
            policy: Password policy to check against (optional)
            user_info: User's personal information (optional)

        Returns:
            Comprehensive password strength analysis
        """
        if policy is None:
            policy = self.get_default_policy()

        if user_info is None:
            user_info = {}

        # Calculate score and strength
        score = self.calculate_password_score(password, policy)
        strength = self.get_strength_level(score)

        # Check policy compliance
        policy_violations = self.validate_policy_compliance(password, policy)
        meets_policy = len(policy_violations) == 0

        # Generate feedback
        feedback = []

        # Add policy violations to feedback
        feedback.extend(policy_violations)

        # Add pattern warnings
        patterns = self.check_common_patterns(password)
        feedback.extend(patterns)

        # Add personal info warnings
        if policy.prevent_personal_info:
            personal_issues = self.check_personal_info(password, user_info)
            feedback.extend(personal_issues)

        # Add positive feedback for strong passwords
        if score >= 85:
            feedback.append("Excellent password strength!")
        elif score >= 70:
            feedback.append("Good password strength")

        # Calculate crack time estimate
        entropy = self.calculate_entropy(password)
        crack_time = self.estimate_crack_time(entropy)

        return PasswordStrengthResponse(
            score=score,
            strength=strength,
            feedback=feedback,
            meets_policy=meets_policy,
            estimated_crack_time=crack_time,
        )

    def validate_password(
        self,
        password: str,
        policy: PasswordPolicy = None,
        user_info: Dict[str, str] = None,
    ) -> bool:
        """Simple password validation

        Args:
            password: Password to validate
            policy: Password policy to check against (optional)
            user_info: User's personal information (optional)

        Returns:
            True if password meets policy requirements, False otherwise
        """
        analysis = self.analyze_password_strength(password, policy, user_info)
        return analysis.meets_policy


# Global password policy service instance
password_policy_service = PasswordPolicyService()
