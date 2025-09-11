"""
Multi-language and Internationalization Service for Pixel AI Creator.

Provides language detection, translation services, and localization support
for chatbot conversations and UI components.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
import re

try:
    from deep_translator import GoogleTranslator

    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False

try:
    from langdetect import detect, detect_langs

    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

logger = logging.getLogger(__name__)


class SupportedLanguage(Enum):
    """Supported languages with ISO codes."""

    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE_SIMPLIFIED = "zh-cn"
    CHINESE_TRADITIONAL = "zh-tw"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    DUTCH = "nl"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    DANISH = "da"
    FINNISH = "fi"
    POLISH = "pl"
    CZECH = "cs"
    HUNGARIAN = "hu"
    ROMANIAN = "ro"
    BULGARIAN = "bg"
    CROATIAN = "hr"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    ESTONIAN = "et"
    LATVIAN = "lv"
    LITHUANIAN = "lt"
    TURKISH = "tr"
    GREEK = "el"
    HEBREW = "he"
    THAI = "th"
    VIETNAMESE = "vi"
    INDONESIAN = "id"
    MALAY = "ms"
    FILIPINO = "tl"


@dataclass
class LanguageDetectionResult:
    """Result of language detection."""

    language_code: str
    language_name: str
    confidence: float
    method: str


@dataclass
class TranslationResult:
    """Result of text translation."""

    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    service: str


@dataclass
class LocalizationConfig:
    """Configuration for chatbot localization."""

    default_language: str
    supported_languages: List[str]
    auto_detect: bool
    fallback_language: str
    translation_service: str


class LanguageService:
    """Comprehensive language and internationalization service."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.translator = None
        self.supported_languages = {
            lang.value: lang.name.replace("_", " ").title()
            for lang in SupportedLanguage
        }

        # Initialize language detection
        self.logger.info("Language service initialized")

        # Language patterns for detection fallback
        self.language_patterns = {
            "en": [r"\b(the|and|is|are|was|were|have|has|will|would)\b"],
            "es": [r"\b(el|la|los|las|es|son|fue|fueron|tiene|tendrá)\b"],
            "fr": [r"\b(le|la|les|est|sont|était|étaient|avoir|aura)\b"],
            "de": [r"\b(der|die|das|ist|sind|war|waren|haben|wird)\b"],
            "it": [r"\b(il|la|lo|è|sono|era|erano|avere|avrà)\b"],
            "pt": [r"\b(o|a|os|as|é|são|foi|foram|ter|terá)\b"],
            "ru": [r"[а-я]{3,}"],
            "zh-cn": [r"[\u4e00-\u9fff]"],
            "ja": [r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]"],
            "ko": [r"[\uac00-\ud7af]"],
            "ar": [r"[\u0600-\u06ff]"],
            "hi": [r"[\u0900-\u097f]"],
        }

    def detect_language(self, text: str) -> LanguageDetectionResult:
        """Detect the language of given text."""
        if not text or len(text.strip()) < 3:
            return LanguageDetectionResult(
                language_code="en",
                language_name="English",
                confidence=0.0,
                method="default",
            )

        # Try langdetect library first
        if LANGDETECT_AVAILABLE:
            try:
                detected_lang = detect(text)
                confidence = 0.8  # Default confidence for langdetect

                # Try to get more detailed confidence
                try:
                    lang_probs = detect_langs(text)
                    if lang_probs:
                        confidence = float(lang_probs[0].prob)
                        detected_lang = lang_probs[0].lang
                except:
                    pass

                # Normalize language code
                normalized_lang = self._normalize_language_code(detected_lang)
                language_name = self.supported_languages.get(
                    normalized_lang, detected_lang.title()
                )

                return LanguageDetectionResult(
                    language_code=normalized_lang,
                    language_name=language_name,
                    confidence=confidence,
                    method="langdetect",
                )
            except Exception as e:
                self.logger.warning(f"Language detection failed: {e}")

        # Fallback to pattern-based detection
        return self._pattern_based_detection(text)

    def _pattern_based_detection(self, text: str) -> LanguageDetectionResult:
        """Fallback pattern-based language detection."""
        text_lower = text.lower()
        scores = {}

        for lang_code, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)

            if score > 0:
                scores[lang_code] = score / len(text.split())

        if scores:
            best_lang = max(scores, key=scores.get)
            confidence = min(scores[best_lang] * 2, 1.0)  # Scale confidence

            return LanguageDetectionResult(
                language_code=best_lang,
                language_name=self.supported_languages.get(best_lang, best_lang),
                confidence=confidence,
                method="pattern",
            )

        # Default to English
        return LanguageDetectionResult(
            language_code="en",
            language_name="English",
            confidence=0.1,
            method="default",
        )

    def translate_text(
        self, text: str, target_language: str, source_language: Optional[str] = None
    ) -> TranslationResult:
        """Translate text to target language."""
        if not text:
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_language or "unknown",
                target_language=target_language,
                confidence=0.0,
                service="none",
            )

        # Detect source language if not provided
        if not source_language:
            detection = self.detect_language(text)
            source_language = detection.language_code

        # Normalize language codes
        source_lang = self._normalize_language_code(source_language)
        target_lang = self._normalize_language_code(target_language)

        # Skip translation if same language
        if source_lang == target_lang:
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                confidence=1.0,
                service="none",
            )

        # Try Google Translate
        if GOOGLE_TRANSLATE_AVAILABLE:
            try:
                translator = GoogleTranslator(source=source_lang, target=target_lang)
                translated_text = translator.translate(text)

                return TranslationResult(
                    original_text=text,
                    translated_text=translated_text,
                    source_language=source_lang,
                    target_language=target_lang,
                    confidence=0.8,  # Google Translate confidence estimate
                    service="google",
                )
            except Exception as e:
                self.logger.warning(f"Google Translate failed: {e}")

        # Fallback - return original text with warning
        self.logger.warning(
            f"No translation service available for {source_lang} -> {target_lang}"
        )
        return TranslationResult(
            original_text=text,
            translated_text=text,
            source_language=source_lang,
            target_language=target_lang,
            confidence=0.0,
            service="unavailable",
        )

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages."""
        return self.supported_languages.copy()

    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported."""
        normalized = self._normalize_language_code(language_code)
        return normalized in self.supported_languages

    def _normalize_language_code(self, lang_code: str) -> str:
        """Normalize language code to supported format."""
        if not lang_code:
            return "en"

        lang_code = lang_code.lower().strip()

        # Handle common variations
        normalizations = {
            "zh": "zh-cn",
            "zh-hans": "zh-cn",
            "zh-hant": "zh-tw",
            "nb": "no",  # Norwegian Bokmål -> Norwegian
            "nn": "no",  # Norwegian Nynorsk -> Norwegian
        }

        return normalizations.get(lang_code, lang_code)

    def create_localization_config(
        self,
        default_language: str = "en",
        supported_languages: Optional[List[str]] = None,
        auto_detect: bool = True,
        fallback_language: str = "en",
        translation_service: str = "google",
    ) -> LocalizationConfig:
        """Create localization configuration for a chatbot."""
        if supported_languages is None:
            supported_languages = ["en", "es", "fr", "de", "it"]

        # Validate languages
        valid_languages = [
            lang for lang in supported_languages if self.is_language_supported(lang)
        ]

        if not valid_languages:
            valid_languages = ["en"]

        return LocalizationConfig(
            default_language=self._normalize_language_code(default_language),
            supported_languages=valid_languages,
            auto_detect=auto_detect,
            fallback_language=self._normalize_language_code(fallback_language),
            translation_service=translation_service,
        )

    def translate_conversation_message(
        self,
        message: str,
        target_language: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Translate a conversation message with context."""
        # Detect language
        detection = self.detect_language(message)

        # Translate if needed
        translation = self.translate_text(
            message, target_language, detection.language_code
        )

        return {
            "original_message": message,
            "translated_message": translation.translated_text,
            "detected_language": {
                "code": detection.language_code,
                "name": detection.language_name,
                "confidence": detection.confidence,
            },
            "translation": {
                "target_language": target_language,
                "confidence": translation.confidence,
                "service": translation.service,
            },
            "context": context or {},
        }

    def get_language_statistics(self, messages: List[str]) -> Dict[str, Any]:
        """Analyze language usage in a set of messages."""
        if not messages:
            return {
                "total_messages": 0,
                "languages_detected": {},
                "primary_language": "en",
                "multilingual": False,
            }

        language_counts = {}
        total_confidence = 0

        for message in messages:
            if not message.strip():
                continue

            detection = self.detect_language(message)
            lang_code = detection.language_code

            if lang_code not in language_counts:
                language_counts[lang_code] = {
                    "count": 0,
                    "total_confidence": 0,
                    "name": detection.language_name,
                }

            language_counts[lang_code]["count"] += 1
            language_counts[lang_code]["total_confidence"] += detection.confidence
            total_confidence += detection.confidence

        # Calculate percentages and average confidence
        total_messages = len([m for m in messages if m.strip()])
        for lang_data in language_counts.values():
            lang_data["percentage"] = (lang_data["count"] / total_messages) * 100
            lang_data["avg_confidence"] = (
                lang_data["total_confidence"] / lang_data["count"]
            )

        # Find primary language
        primary_language = (
            max(language_counts.keys(), key=lambda x: language_counts[x]["count"])
            if language_counts
            else "en"
        )

        return {
            "total_messages": total_messages,
            "languages_detected": language_counts,
            "primary_language": primary_language,
            "multilingual": len(language_counts) > 1,
            "avg_detection_confidence": (
                total_confidence / total_messages if total_messages > 0 else 0
            ),
        }
