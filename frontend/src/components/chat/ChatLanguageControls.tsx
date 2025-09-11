import React, { useState, useEffect } from 'react';
import { Button, Dropdown, Badge, Alert, Spinner } from 'react-bootstrap';
import { Globe, Languages, MessageCircle, Volume2, VolumeX } from 'lucide-react';
import apiService from '../../services/api';

interface ChatLanguageControlsProps {
  chatbotId: string;
  currentLanguage: string;
  onLanguageChange: (language: string) => void;
  autoTranslate?: boolean;
  onAutoTranslateToggle?: (enabled: boolean) => void;
  messagesCount?: number;
}

interface TranslationResult {
  translated_text: string;
  source_language: string;
  target_language: string;
  confidence: number;
}

const ChatLanguageControls: React.FC<ChatLanguageControlsProps> = ({
  chatbotId,
  currentLanguage,
  onLanguageChange,
  autoTranslate = false,
  onAutoTranslateToggle,
  messagesCount = 0
}) => {
  const [supportedLanguages, setSupportedLanguages] = useState<Record<string, string>>({});
  const [detectedLanguage, setDetectedLanguage] = useState<string | null>(null);
  const [translating] = useState(false);
  const [languageStats, setLanguageStats] = useState<{
    total_languages: number;
    primary_language: string;
    multilingual_percentage: number;
  } | null>(null);

  const loadSupportedLanguages = async () => {
    try {
      const response = await apiService.get('/api/language/supported');
      setSupportedLanguages(response.data.supported_languages);
    } catch (error) {
      console.error('Failed to load supported languages:', error);
    }
  };

  const loadLanguageStats = async () => {
    try {
      const response = await apiService.get(`/api/language/chatbot/${chatbotId}/languages`);
      setLanguageStats(response.data.usage_stats);
    } catch (error) {
      console.error('Failed to load language stats:', error);
    }
  };

  useEffect(() => {
    const initialize = async () => {
      await loadSupportedLanguages();
      if (chatbotId) {
        await loadLanguageStats();
      }
    };
    initialize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatbotId]);

  const handleLanguageSelect = (langCode: string) => {
    onLanguageChange(langCode);
    setDetectedLanguage(null);
  };

  const getCurrentLanguageName = () => {
    return supportedLanguages[currentLanguage] || currentLanguage.toUpperCase();
  };

  return (
    <div className="chat-language-controls d-flex align-items-center gap-2 mb-3">
      {/* Language Selector */}
      <Dropdown>
        <Dropdown.Toggle variant="outline-primary" size="sm" className="d-flex align-items-center">
          <Globe className="me-1" size={16} />
          {getCurrentLanguageName()}
        </Dropdown.Toggle>
        <Dropdown.Menu style={{ maxHeight: '300px', overflowY: 'auto' }}>
          <Dropdown.Header>Select Language</Dropdown.Header>
          {Object.entries(supportedLanguages).map(([code, name]) => (
            <Dropdown.Item
              key={code}
              active={code === currentLanguage}
              onClick={() => handleLanguageSelect(code)}
            >
              {name} ({code.toUpperCase()})
            </Dropdown.Item>
          ))}
        </Dropdown.Menu>
      </Dropdown>

      {/* Auto-translate Toggle */}
      {onAutoTranslateToggle && (
        <Button
          variant={autoTranslate ? "success" : "outline-secondary"}
          size="sm"
          onClick={() => onAutoTranslateToggle(!autoTranslate)}
          className="d-flex align-items-center"
        >
          {autoTranslate ? <Volume2 size={16} /> : <VolumeX size={16} />}
          <span className="ms-1 d-none d-md-inline">
            {autoTranslate ? 'Auto-translate ON' : 'Auto-translate OFF'}
          </span>
        </Button>
      )}

      {/* Translation Status */}
      {translating && (
        <div className="d-flex align-items-center text-muted">
          <Spinner size="sm" className="me-1" />
          <small>Translating...</small>
        </div>
      )}

      {/* Detected Language Badge */}
      {detectedLanguage && detectedLanguage !== currentLanguage && (
        <Badge bg="info" className="d-flex align-items-center">
          <MessageCircle size={12} className="me-1" />
          Detected: {supportedLanguages[detectedLanguage] || detectedLanguage.toUpperCase()}
        </Badge>
      )}

      {/* Language Stats */}
      {languageStats && messagesCount > 0 && (
        <small className="text-muted d-none d-lg-inline">
          {languageStats.multilingual_percentage > 0 && (
            <span className="me-2">
              <Languages size={12} className="me-1" />
              {languageStats.multilingual_percentage.toFixed(1)}% multilingual
            </span>
          )}
          Primary: {supportedLanguages[languageStats.primary_language] || languageStats.primary_language.toUpperCase()}
        </small>
      )}
    </div>
  );
};

// Message Translation Component
interface MessageTranslationProps {
  messageText: string;
  originalLanguage?: string;
  targetLanguage: string;
  onTranslationComplete?: (translation: TranslationResult) => void;
}

export const MessageTranslation: React.FC<MessageTranslationProps> = ({
  messageText,
  originalLanguage,
  targetLanguage,
  onTranslationComplete
}) => {
  const [translation, setTranslation] = useState<TranslationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [showOriginal, setShowOriginal] = useState(false);

  const translateMessage = async () => {
    try {
      setLoading(true);
      const response = await apiService.post('/api/language/translate', {
        text: messageText,
        target_language: targetLanguage,
        source_language: originalLanguage
      });
      
      const result = response.data;
      setTranslation(result);
      
      if (onTranslationComplete) {
        onTranslationComplete(result);
      }
    } catch (error) {
      console.error('Translation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="message-translation text-muted">
        <Spinner size="sm" className="me-1" />
        <small>Translating...</small>
      </div>
    );
  }

  if (!translation) {
    return (
      <Button
        variant="link"
        size="sm"
        onClick={translateMessage}
        className="message-translation-trigger p-0 text-decoration-none"
      >
        <Languages size={14} className="me-1" />
        Translate to {targetLanguage.toUpperCase()}
      </Button>
    );
  }

  return (
    <div className="message-translation mt-2">
      <div className="translation-content p-2 bg-light rounded">
        <div className="translated-text">
          {showOriginal ? messageText : translation.translated_text}
        </div>
        <div className="d-flex justify-content-between align-items-center mt-1">
          <small className="text-muted">
            {showOriginal ? (
              <>Original ({translation.source_language.toUpperCase()})</>
            ) : (
              <>
                Translated to {translation.target_language.toUpperCase()} 
                {translation.confidence && ` • ${(translation.confidence * 100).toFixed(0)}% confidence`}
              </>
            )}
          </small>
          <Button
            variant="link"
            size="sm"
            onClick={() => setShowOriginal(!showOriginal)}
            className="p-0 text-decoration-none"
          >
            {showOriginal ? 'Show Translation' : 'Show Original'}
          </Button>
        </div>
      </div>
    </div>
  );
};

// Language-aware Conversation History
interface ConversationLanguageHistoryProps {
  chatbotId: string;
  conversationId: string;
}

export const ConversationLanguageHistory: React.FC<ConversationLanguageHistoryProps> = ({
  chatbotId,
  conversationId
}) => {
  const [languageBreakdown, setLanguageBreakdown] = useState<{
    languages_used: string[];
    message_counts: Record<string, number>;
    translation_count: number;
    multilingual: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(false);

  const loadConversationLanguageData = async () => {
    try {
      setLoading(true);
      const response = await apiService.post('/api/language/conversation/translate', {
        conversation_id: conversationId,
        target_language: 'en' // Just to get the analysis
      });
      setLanguageBreakdown(response.data.language_breakdown);
    } catch (error) {
      console.error('Failed to load conversation language data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (conversationId) {
      loadConversationLanguageData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversationId]);

  if (loading) {
    return (
      <div className="text-center py-2">
        <Spinner size="sm" />
      </div>
    );
  }

  if (!languageBreakdown) {
    return null;
  }

  return (
    <Alert variant="info" className="conversation-language-summary">
      <div className="d-flex align-items-center mb-2">
        <Languages className="me-2" size={16} />
        <strong>Conversation Languages</strong>
      </div>
      
      <div className="language-breakdown">
        {languageBreakdown.multilingual && (
          <Badge bg="success" className="me-2">Multilingual</Badge>
        )}
        
        {languageBreakdown.languages_used.map(lang => (
          <Badge key={lang} bg="primary" className="me-1">
            {lang.toUpperCase()}: {languageBreakdown.message_counts[lang]} messages
          </Badge>
        ))}
        
        {languageBreakdown.translation_count > 0 && (
          <Badge bg="info" className="ms-2">
            {languageBreakdown.translation_count} translations
          </Badge>
        )}
      </div>
    </Alert>
  );
};

export default ChatLanguageControls;
