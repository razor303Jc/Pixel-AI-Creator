"""
Multi-language API routes for Pixel AI Creator.

Provides endpoints for language detection, translation services,
and localization management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from auth.middleware import get_current_user
from models.database_schema import User
from services.language_service import LanguageService, LocalizationConfig

router = APIRouter(prefix="/api/language", tags=["language"])


# Request/Response Models
class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = None


class LanguageDetectionRequest(BaseModel):
    text: str


class LocalizationConfigRequest(BaseModel):
    default_language: str = "en"
    supported_languages: List[str] = ["en", "es", "fr", "de", "it"]
    auto_detect: bool = True
    fallback_language: str = "en"
    translation_service: str = "google"


class ConversationTranslationRequest(BaseModel):
    message: str
    target_language: str
    context: Optional[Dict[str, Any]] = None


@router.get("/supported")
async def get_supported_languages() -> Dict[str, Any]:
    """Get list of all supported languages."""
    language_service = LanguageService()
    return {
        "supported_languages": language_service.get_supported_languages(),
        "total_count": len(language_service.get_supported_languages()),
        "service_status": {
            "google_translate": language_service.translator is not None,
            "language_detection": True,
        },
    }


@router.post("/detect")
async def detect_language(
    request: LanguageDetectionRequest, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Detect the language of given text."""
    if not request.text.strip():
        raise HTTPException(
            status_code=400, detail="Text is required for language detection"
        )

    try:
        language_service = LanguageService()
        result = language_service.detect_language(request.text)

        return {
            "language_code": result.language_code,
            "language_name": result.language_name,
            "confidence": result.confidence,
            "detection_method": result.method,
            "text_length": len(request.text),
            "is_supported": language_service.is_language_supported(
                result.language_code
            ),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Language detection failed: {str(e)}"
        )


@router.post("/translate")
async def translate_text(
    request: TranslationRequest, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Translate text to target language."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required for translation")

    try:
        language_service = LanguageService()

        # Validate target language
        if not language_service.is_language_supported(request.target_language):
            raise HTTPException(
                status_code=400,
                detail=f"Target language '{request.target_language}' not supported",
            )

        result = language_service.translate_text(
            request.text, request.target_language, request.source_language
        )

        return {
            "original_text": result.original_text,
            "translated_text": result.translated_text,
            "source_language": result.source_language,
            "target_language": result.target_language,
            "confidence": result.confidence,
            "translation_service": result.service,
            "character_count": len(request.text),
            "translation_needed": result.source_language != result.target_language,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/conversation/translate")
async def translate_conversation_message(
    request: ConversationTranslationRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Translate a conversation message with context."""
    if not request.message.strip():
        raise HTTPException(
            status_code=400, detail="Message is required for translation"
        )

    try:
        language_service = LanguageService()

        # Validate target language
        if not language_service.is_language_supported(request.target_language):
            raise HTTPException(
                status_code=400,
                detail=f"Target language '{request.target_language}' not supported",
            )

        result = language_service.translate_conversation_message(
            request.message, request.target_language, request.context
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Conversation translation failed: {str(e)}"
        )


@router.post("/localization/config")
async def create_localization_config(
    request: LocalizationConfigRequest, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create localization configuration for a chatbot."""
    try:
        language_service = LanguageService()

        config = language_service.create_localization_config(
            default_language=request.default_language,
            supported_languages=request.supported_languages,
            auto_detect=request.auto_detect,
            fallback_language=request.fallback_language,
            translation_service=request.translation_service,
        )

        return {
            "default_language": config.default_language,
            "supported_languages": config.supported_languages,
            "auto_detect": config.auto_detect,
            "fallback_language": config.fallback_language,
            "translation_service": config.translation_service,
            "config_valid": True,
            "supported_count": len(config.supported_languages),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Configuration creation failed: {str(e)}"
        )


@router.post("/analyze/messages")
async def analyze_language_usage(
    messages: List[str], current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Analyze language usage in a set of messages."""
    if not messages:
        raise HTTPException(
            status_code=400, detail="At least one message is required for analysis"
        )

    try:
        language_service = LanguageService()
        stats = language_service.get_language_statistics(messages)

        return {
            "analysis_results": stats,
            "recommendations": {
                "enable_translation": stats["multilingual"],
                "suggested_languages": list(stats["languages_detected"].keys())[:5],
                "primary_language_confidence": stats.get("avg_detection_confidence", 0),
            },
            "analysis_meta": {
                "total_messages_analyzed": len(messages),
                "valid_messages": stats["total_messages"],
                "analysis_timestamp": "2025-09-11T18:30:00Z",
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Language analysis failed: {str(e)}"
        )


@router.get("/chatbot/{chatbot_id}/languages")
async def get_chatbot_language_config(
    chatbot_id: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get language configuration for a specific chatbot."""
    # This would typically fetch from database
    # For now, return a mock configuration
    return {
        "chatbot_id": chatbot_id,
        "language_config": {
            "default_language": "en",
            "supported_languages": ["en", "es", "fr"],
            "auto_detect": True,
            "fallback_language": "en",
            "translation_enabled": True,
        },
        "usage_stats": {
            "total_conversations": 150,
            "multilingual_conversations": 45,
            "most_common_languages": ["en", "es", "fr"],
            "translation_requests": 230,
        },
    }


@router.put("/chatbot/{chatbot_id}/languages")
async def update_chatbot_language_config(
    chatbot_id: str,
    request: LocalizationConfigRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update language configuration for a specific chatbot."""
    try:
        language_service = LanguageService()

        config = language_service.create_localization_config(
            default_language=request.default_language,
            supported_languages=request.supported_languages,
            auto_detect=request.auto_detect,
            fallback_language=request.fallback_language,
            translation_service=request.translation_service,
        )

        # In a real implementation, save to database here

        return {
            "chatbot_id": chatbot_id,
            "updated_config": {
                "default_language": config.default_language,
                "supported_languages": config.supported_languages,
                "auto_detect": config.auto_detect,
                "fallback_language": config.fallback_language,
                "translation_service": config.translation_service,
            },
            "update_timestamp": "2025-09-11T18:30:00Z",
            "success": True,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Configuration update failed: {str(e)}"
        )


@router.get("/health")
async def language_service_health() -> Dict[str, Any]:
    """Health check for language service."""
    language_service = LanguageService()

    return {
        "status": "healthy",
        "service": "language",
        "capabilities": {
            "language_detection": True,
            "google_translate": language_service.translator is not None,
            "supported_languages_count": len(
                language_service.get_supported_languages()
            ),
            "pattern_based_detection": True,
        },
        "version": "1.0.0",
    }
