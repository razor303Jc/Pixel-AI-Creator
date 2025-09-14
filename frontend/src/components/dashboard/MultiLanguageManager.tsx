import React, { useState, useEffect, createContext, useContext } from 'react';
import { Card, Button, Form, Row, Col, Badge, Alert, Spinner } from 'react-bootstrap';
import { Globe, Languages, MessageCircle, Settings, BarChart3 } from 'lucide-react';
import apiService from '../../services/api';

// Language Context
const LanguageContext = createContext(null);

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Language Provider Component
export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const [autoDetect, setAutoDetect] = useState(true);
  const [translationEnabled, setTranslationEnabled] = useState(true);

  const value = {
    currentLanguage,
    setCurrentLanguage,
    supportedLanguages,
    setSupportedLanguages,
    autoDetect,
    setAutoDetect,
    translationEnabled,
    setTranslationEnabled
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

// Language Settings Component
const LanguageSettings = ({ chatbotId }) => {
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState({
    default_language: 'en',
    supported_languages: ['en', 'es', 'fr'],
    auto_detect: true,
    fallback_language: 'en',
    translation_service: 'google'
  });
  const [availableLanguages, setAvailableLanguages] = useState({});
  const [saveStatus, setSaveStatus] = useState(null);

  const loadSupportedLanguages = async () => {
    try {
      const response = await apiService.get('/api/language/supported');
      setAvailableLanguages(response.data.supported_languages);
    } catch (error) {
      console.error('Failed to load supported languages:', error);
    }
  };

  const loadChatbotConfig = async () => {
    try {
      setLoading(true);
      const response = await apiService.get(`/api/language/chatbot/${chatbotId}/languages`);
      setConfig(response.data.language_config);
    } catch (error) {
      console.error('Failed to load chatbot language config:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const initialize = async () => {
      await loadSupportedLanguages();
      if (chatbotId) {
        await loadChatbotConfig();
      }
    };
    initialize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatbotId]);

  const saveConfig = async () => {
    try {
      setLoading(true);
      await apiService.put(`/api/language/chatbot/${chatbotId}/languages`, config);
      setSaveStatus({ type: 'success', message: 'Language configuration saved successfully!' });
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (error) {
      setSaveStatus({ type: 'error', message: 'Failed to save configuration.' });
      setTimeout(() => setSaveStatus(null), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageToggle = (langCode) => {
    const updatedLanguages = config.supported_languages.includes(langCode)
      ? config.supported_languages.filter(lang => lang !== langCode)
      : [...config.supported_languages, langCode];
    
    setConfig(prev => ({
      ...prev,
      supported_languages: updatedLanguages
    }));
  };

  return (
    <Card className="h-100">
      <Card.Header className="d-flex align-items-center">
        <Settings className="me-2" size={20} />
        <h5 className="mb-0">Language Configuration</h5>
      </Card.Header>
      <Card.Body>
        {saveStatus && (
          <Alert variant={saveStatus.type === 'success' ? 'success' : 'danger'}>
            {saveStatus.message}
          </Alert>
        )}

        <Form>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label htmlFor="defaultLanguage">Default Language</Form.Label>
                <Form.Select
                  id="defaultLanguage"
                  name="defaultLanguage"
                  value={config.default_language}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    default_language: e.target.value
                  }))}
                  autoComplete="language"
                >
                  {Object.entries(availableLanguages).map(([code, name]) => (
                    <option key={code} value={code}>{String(name)}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label htmlFor="fallbackLanguage">Fallback Language</Form.Label>
                <Form.Select
                  id="fallbackLanguage"
                  name="fallbackLanguage"
                  value={config.fallback_language}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    fallback_language: e.target.value
                  }))}
                  autoComplete="language"
                >
                  {Object.entries(availableLanguages).map(([code, name]) => (
                    <option key={code} value={code}>{String(name)}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Check
              id="autoDetect"
              name="autoDetect"
              type="checkbox"
              label="Enable automatic language detection"
              checked={config.auto_detect}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                auto_detect: e.target.checked
              }))}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Supported Languages</Form.Label>
            <div className="d-flex flex-wrap gap-2 mt-2">
              {Object.entries(availableLanguages).slice(0, 20).map(([code, name]) => (
                <Badge
                  key={code}
                  bg={config.supported_languages.includes(code) ? 'primary' : 'secondary'}
                  style={{ cursor: 'pointer' }}
                  onClick={() => handleLanguageToggle(code)}
                >
                  {String(name)} ({code})
                </Badge>
              ))}
            </div>
            <Form.Text className="text-muted">
              Click languages to toggle support. Selected: {config.supported_languages.length}
            </Form.Text>
          </Form.Group>

          <Button
            variant="primary"
            onClick={saveConfig}
            disabled={loading}
            className="w-100"
          >
            {loading ? (
              <>
                <Spinner size="sm" className="me-2" />
                Saving...
              </>
            ) : (
              'Save Configuration'
            )}
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

// Language Detection Component
const LanguageDetection = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const detectLanguage = async () => {
    if (!text.trim()) return;

    try {
      setLoading(true);
      const response = await apiService.post('/api/language/detect', { text });
      setResult(response.data);
    } catch (error) {
      console.error('Language detection failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="h-100">
      <Card.Header className="d-flex align-items-center">
        <Globe className="me-2" size={20} />
        <h5 className="mb-0">Language Detection</h5>
      </Card.Header>
      <Card.Body>
        <Form.Group className="mb-3">
          <Form.Label>Enter text to detect language</Form.Label>
          <Form.Control
            as="textarea"
            rows={4}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type or paste text here..."
          />
        </Form.Group>

        <Button
          variant="primary"
          onClick={detectLanguage}
          disabled={loading || !text.trim()}
          className="w-100 mb-3"
        >
          {loading ? (
            <>
              <Spinner size="sm" className="me-2" />
              Detecting...
            </>
          ) : (
            'Detect Language'
          )}
        </Button>

        {result && (
          <Alert variant="info">
            <strong>Detected Language:</strong> {result.language_name} ({result.language_code})<br />
            <strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%<br />
            <strong>Method:</strong> {result.detection_method}<br />
            <strong>Supported:</strong> {result.is_supported ? 'Yes' : 'No'}
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

// Translation Component
const TranslationTool = () => {
  const [text, setText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('es');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [languages, setLanguages] = useState({});

  useEffect(() => {
    loadLanguages();
  }, []);

  const loadLanguages = async () => {
    try {
      const response = await apiService.get('/api/language/supported');
      setLanguages(response.data.supported_languages);
    } catch (error) {
      console.error('Failed to load languages:', error);
    }
  };

  const translateText = async () => {
    if (!text.trim()) return;

    try {
      setLoading(true);
      const response = await apiService.post('/api/language/translate', {
        text,
        target_language: targetLanguage
      });
      setResult(response.data);
    } catch (error) {
      console.error('Translation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="h-100">
      <Card.Header className="d-flex align-items-center">
        <Languages className="me-2" size={20} />
        <h5 className="mb-0">Translation Tool</h5>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={8}>
            <Form.Group className="mb-3">
              <Form.Label>Text to translate</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter text to translate..."
              />
            </Form.Group>
          </Col>
          <Col md={4}>
            <Form.Group className="mb-3">
              <Form.Label>Target Language</Form.Label>
              <Form.Select
                value={targetLanguage}
                onChange={(e) => setTargetLanguage(e.target.value)}
              >
                {Object.entries(languages).map(([code, name]) => (
                  <option key={code} value={code}>{String(name)}</option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
        </Row>

        <Button
          variant="primary"
          onClick={translateText}
          disabled={loading || !text.trim()}
          className="w-100 mb-3"
        >
          {loading ? (
            <>
              <Spinner size="sm" className="me-2" />
              Translating...
            </>
          ) : (
            'Translate'
          )}
        </Button>

        {result && (
          <div>
            <Alert variant="success">
              <strong>Translation:</strong>
              <div className="mt-2 p-2 bg-light rounded">
                {result.translated_text}
              </div>
            </Alert>
            <small className="text-muted">
              From: {result.source_language} → To: {result.target_language} | 
              Service: {result.translation_service} | 
              Confidence: {(result.confidence * 100).toFixed(1)}%
            </small>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

// Language Analytics Component
const LanguageAnalytics = ({ chatbotId }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await apiService.get(`/api/language/chatbot/${chatbotId}/languages`);
      setStats(response.data.usage_stats);
    } catch (error) {
      console.error('Failed to load language stats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (chatbotId) {
      loadStats();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatbotId]);

  if (loading) {
    return (
      <Card className="h-100">
        <Card.Body className="d-flex justify-content-center align-items-center">
          <Spinner />
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="h-100">
      <Card.Header className="d-flex align-items-center">
        <BarChart3 className="me-2" size={20} />
        <h5 className="mb-0">Language Usage Analytics</h5>
      </Card.Header>
      <Card.Body>
        {stats ? (
          <div>
            <Row className="mb-3">
              <Col>
                <div className="text-center">
                  <h4 className="text-primary">{stats.total_conversations}</h4>
                  <small className="text-muted">Total Conversations</small>
                </div>
              </Col>
              <Col>
                <div className="text-center">
                  <h4 className="text-success">{stats.multilingual_conversations}</h4>
                  <small className="text-muted">Multilingual</small>
                </div>
              </Col>
              <Col>
                <div className="text-center">
                  <h4 className="text-info">{stats.translation_requests}</h4>
                  <small className="text-muted">Translations</small>
                </div>
              </Col>
            </Row>

            <div className="mb-3">
              <strong>Most Common Languages:</strong>
              <div className="d-flex flex-wrap gap-1 mt-2">
                {stats.most_common_languages.map((lang, index) => (
                  <Badge key={lang} bg="primary">
                    #{index + 1} {lang.toUpperCase()}
                  </Badge>
                ))}
              </div>
            </div>

            <Alert variant="info">
              <MessageCircle className="me-2" size={16} />
              <strong>Multilingual Usage:</strong> {' '}
              {((stats.multilingual_conversations / stats.total_conversations) * 100).toFixed(1)}% 
              of conversations use multiple languages
            </Alert>
          </div>
        ) : (
          <Alert variant="warning">
            No language statistics available yet.
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

// Main Multi-Language Manager Component
const MultiLanguageManager = ({ chatbotId }) => {
  return (
    <LanguageProvider>
      <div className="multi-language-manager">
        <h3 className="mb-4">
          <Globe className="me-2" />
          Multi-Language Support
        </h3>

        <Row className="g-4">
          <Col lg={6}>
            <LanguageSettings chatbotId={chatbotId} />
          </Col>
          <Col lg={6}>
            <LanguageAnalytics chatbotId={chatbotId} />
          </Col>
        </Row>

        <Row className="g-4 mt-2">
          <Col lg={6}>
            <LanguageDetection />
          </Col>
          <Col lg={6}>
            <TranslationTool />
          </Col>
        </Row>
      </div>
    </LanguageProvider>
  );
};

export default MultiLanguageManager;
