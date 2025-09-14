/**
 * Enhanced Client Dashboard Component with Editable Cards
 * Displays client-specific metrics with full card editing and layout customization
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  Container,
  Row,
  Col,
  Button,
  Tabs,
  Tab,
  Alert,
  Spinner
} from 'react-bootstrap';
import { motion } from 'framer-motion';
import {
  User,
  Bot,
  MessageCircle,
  DollarSign,
  TrendingUp,
  Clock,
  Star,
  Download,
  CreditCard,
  Activity,
  BarChart3
} from 'lucide-react';
import CardLayoutManager, { DashboardCard, LayoutConfig } from './CardLayoutManager';
import { apiService } from '../../services/api';

interface ClientMetrics {
  totalConversations: number;
  totalMessages: number;
  averageRating: number;
  responseTime: number;
  monthlySpend: number;
  activeChats: number;
  satisfaction: number;
  uptime: number;
}

interface EnhancedClientDashboardProps {
  clientId?: number;
}

const EnhancedClientDashboard: React.FC<EnhancedClientDashboardProps> = ({ clientId }) => {
  const [metrics, setMetrics] = useState<ClientMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardCards, setDashboardCards] = useState<DashboardCard[]>([]);
  const [savedLayouts, setSavedLayouts] = useState<LayoutConfig[]>([]);

  const generateMockMetrics = useCallback((): ClientMetrics => ({
    totalConversations: 1247,
    totalMessages: 8934,
    averageRating: 4.6,
    responseTime: 1.8,
    monthlySpend: 147.30,
    activeChats: 23,
    satisfaction: 92.5,
    uptime: 99.2
  }), []);

  const loadClientMetrics = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      if (clientId) {
        const response = await apiService.get(`/api/clients/${clientId}/metrics`);
        setMetrics(response.data);
      } else {
        // Generate mock data for demonstration
        setMetrics(generateMockMetrics());
      }
    } catch (err: any) {
      setError('Failed to load client metrics');
      // Use mock data as fallback
      setMetrics(generateMockMetrics());
    } finally {
      setLoading(false);
    }
  }, [clientId, generateMockMetrics]);

  const loadSavedLayouts = useCallback(async () => {
    try {
      const response = await apiService.get('/api/dashboard/layouts');
      setSavedLayouts(response.data || []);
    } catch (err) {
      // Use mock layouts if API fails
      setSavedLayouts([]);
    }
  }, []);

  const initializeDashboardCards = useCallback(() => {
    if (!metrics) return;

    const cards: DashboardCard[] = [
      {
        id: '1',
        title: 'Total Conversations',
        value: metrics.totalConversations,
        subtitle: 'All time',
        icon: <MessageCircle size={24} />,
        color: 'primary',
        position: { row: 0, col: 0 },
        size: { width: 3 },
        editable: true,
        deletable: false,
        copyable: true,
        refreshable: true,
        formatValue: (value) => value.toLocaleString(),
        validateValue: (value) => !isNaN(Number(value)) && Number(value) >= 0,
        inputType: 'number'
      },
      {
        id: '2',
        title: 'Average Rating',
        value: metrics.averageRating,
        subtitle: 'Out of 5.0',
        icon: <Star size={24} />,
        color: 'success',
        position: { row: 0, col: 3 },
        size: { width: 3 },
        editable: true,
        deletable: false,
        copyable: true,
        refreshable: true,
        formatValue: (value) => `${Number(value).toFixed(1)}/5`,
        validateValue: (value) => !isNaN(Number(value)) && Number(value) >= 0 && Number(value) <= 5,
        inputType: 'number'
      },
      {
        id: '3',
        title: 'Response Time',
        value: metrics.responseTime,
        subtitle: 'Average seconds',
        icon: <Clock size={24} />,
        color: 'info',
        position: { row: 0, col: 6 },
        size: { width: 3 },
        editable: true,
        deletable: false,
        copyable: true,
        refreshable: true,
        formatValue: (value) => `${Number(value).toFixed(1)}s`,
        validateValue: (value) => !isNaN(Number(value)) && Number(value) >= 0,
        inputType: 'number'
      },
      {
        id: '4',
        title: 'Monthly Spend',
        value: metrics.monthlySpend,
        subtitle: 'Current month',
        icon: <DollarSign size={24} />,
        color: 'warning',
        position: { row: 0, col: 9 },
        size: { width: 3 },
        editable: true,
        deletable: false,
        copyable: true,
        refreshable: true,
        formatValue: (value) => `$${Number(value).toFixed(2)}`,
        validateValue: (value) => !isNaN(Number(value)) && Number(value) >= 0,
        inputType: 'number'
      },
      {
        id: '5',
        title: 'Active Chats',
        value: metrics.activeChats,
        subtitle: 'Currently online',
        icon: <Activity size={24} />,
        color: 'success',
        position: { row: 1, col: 0 },
        size: { width: 4 },
        editable: true,
        deletable: true,
        copyable: true,
        refreshable: true,
        formatValue: (value) => value.toLocaleString(),
        validateValue: (value) => !isNaN(Number(value)) && Number(value) >= 0,
        inputType: 'number'
      },
      {
        id: '6',
        title: 'Customer Satisfaction',
        value: metrics.satisfaction,
        subtitle: 'Percentage',
        icon: <TrendingUp size={24} />,
        color: 'success',
        position: { row: 1, col: 4 },
        size: { width: 4 },
        editable: true,
        deletable: true,
        copyable: true,
        refreshable: true,
        formatValue: (value) => `${Number(value).toFixed(1)}%`,
        validateValue: (value) => !isNaN(Number(value)) && Number(value) >= 0 && Number(value) <= 100,
        inputType: 'number'
      },
      {
        id: '7',
        title: 'System Uptime',
        value: metrics.uptime,
        subtitle: 'Reliability',
        icon: <BarChart3 size={24} />,
        color: 'info',
        position: { row: 1, col: 8 },
        size: { width: 4 },
        editable: true,
        deletable: true,
        copyable: true,
        refreshable: true,
        formatValue: (value) => `${Number(value).toFixed(1)}%`,
        validateValue: (value) => !isNaN(Number(value)) && Number(value) >= 0 && Number(value) <= 100,
        inputType: 'number'
      }
    ];

    setDashboardCards(cards);
  }, [metrics]);

  // Effects
  useEffect(() => {
    loadClientMetrics();
    loadSavedLayouts();
  }, [loadClientMetrics, loadSavedLayouts]);

  useEffect(() => {
    if (metrics) {
      initializeDashboardCards();
    }
  }, [metrics, initializeDashboardCards]);

  const handleCardsChange = (newCards: DashboardCard[]) => {
    setDashboardCards(newCards);
    
    // Update metrics state based on card changes
    const updatedMetrics = { ...metrics } as ClientMetrics;
    newCards.forEach(card => {
      switch (card.id) {
        case '1':
          updatedMetrics.totalConversations = Number(card.value);
          break;
        case '2':
          updatedMetrics.averageRating = Number(card.value);
          break;
        case '3':
          updatedMetrics.responseTime = Number(card.value);
          break;
        case '4':
          updatedMetrics.monthlySpend = Number(card.value);
          break;
        case '5':
          updatedMetrics.activeChats = Number(card.value);
          break;
        case '6':
          updatedMetrics.satisfaction = Number(card.value);
          break;
        case '7':
          updatedMetrics.uptime = Number(card.value);
          break;
      }
    });
    
    setMetrics(updatedMetrics);
  };

  const handleSaveLayout = async (layout: LayoutConfig) => {
    try {
      await apiService.post('/api/dashboard/layouts', layout);
      setSavedLayouts([...savedLayouts, layout]);
    } catch (err) {
      console.error('Failed to save layout:', err);
    }
  };

  const handleLoadLayout = async (layoutId: string) => {
    try {
      const response = await apiService.get(`/api/dashboard/layouts/${layoutId}`);
      const layout = response.data;
      setDashboardCards(layout.cards);
    } catch (err) {
      console.error('Failed to load layout:', err);
    }
  };

  const exportReport = () => {
    const reportData = {
      metrics,
      cards: dashboardCards,
      exportedAt: new Date().toISOString(),
      clientId
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `client-dashboard-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
        <Spinner animation="border" variant="primary" />
      </Container>
    );
  }

  if (error && !metrics) {
    return (
      <Container>
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container fluid className="py-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <Row className="mb-4">
          <Col>
            <div className="d-flex justify-content-between align-items-center">
              <h2 className="fw-bold text-dark">
                <User className="me-2" />
                Enhanced Client Dashboard
              </h2>
              <div className="d-flex gap-2">
                <Button variant="outline-primary" size="sm">
                  <CreditCard className="me-1" size={16} />
                  Billing
                </Button>
                <Button variant="success" size="sm" onClick={exportReport}>
                  <Download className="me-1" size={16} />
                  Export Report
                </Button>
              </div>
            </div>
          </Col>
        </Row>

        {/* Error Alert */}
        {error && (
          <Row className="mb-3">
            <Col>
              <Alert variant="warning" dismissible onClose={() => setError('')}>
                {error}
              </Alert>
            </Col>
          </Row>
        )}

        {/* Main Content Tabs */}
        <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k || 'overview')} className="mb-4">
          <Tab eventKey="overview" title="Dashboard Overview">
            <CardLayoutManager
              cards={dashboardCards}
              onCardsChange={handleCardsChange}
              onSaveLayout={handleSaveLayout}
              onLoadLayout={handleLoadLayout}
              savedLayouts={savedLayouts}
              allowCustomCards={true}
              maxColumns={12}
            />
          </Tab>
          
          <Tab eventKey="analytics" title="Analytics">
            <Row>
              <Col>
                <div className="text-center py-5">
                  <Bot size={48} className="text-muted mb-3" />
                  <h4 className="text-muted">Advanced Analytics</h4>
                  <p className="text-muted">
                    Detailed analytics and reporting features will be available here.
                  </p>
                </div>
              </Col>
            </Row>
          </Tab>
          
          <Tab eventKey="settings" title="Settings">
            <Row>
              <Col>
                <div className="text-center py-5">
                  <Bot size={48} className="text-muted mb-3" />
                  <h4 className="text-muted">Dashboard Settings</h4>
                  <p className="text-muted">
                    Configure dashboard preferences and customization options.
                  </p>
                </div>
              </Col>
            </Row>
          </Tab>
        </Tabs>
      </motion.div>
    </Container>
  );
};

export default EnhancedClientDashboard;