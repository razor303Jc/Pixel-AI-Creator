import React, { useState, useEffect } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Alert,
  Button,
  Badge,
  ProgressBar,
  Spinner,
  Table,
  Modal,
  Form,
  Tabs,
  Tab
} from 'react-bootstrap';
import {
  FaCogs,
  FaChartLine,
  FaMemory,
  FaMicrochip,
  FaRedoAlt,
  FaTrash,
  FaClock,
  FaPlay,
  FaStop,
  FaEye
} from 'react-icons/fa';

interface CacheStats {
  hit_rate: number;
  total_keys: number;
  memory_usage: string;
  operations_per_second: number;
}

interface SystemHealth {
  system: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
  };
  services: {
    redis_healthy: boolean;
    database_healthy: boolean;
  };
}

interface TaskInfo {
  task_id: string;
  name: string;
  status: string;
  worker: string;
  args: any[];
  kwargs: any;
}

interface PerformanceSummary {
  cache_performance: CacheStats;
  system_health: SystemHealth;
  active_tasks_count: number;
  performance_score: number;
}

const PerformanceMonitor: React.FC = () => {
  const [performanceSummary, setPerformanceSummary] = useState<PerformanceSummary | null>(null);
  const [activeTasks, setActiveTasks] = useState<TaskInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showClearCacheModal, setShowClearCacheModal] = useState(false);
  const [cachePattern, setCachePattern] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch performance data
  const fetchPerformanceData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const [summaryResponse, tasksResponse] = await Promise.all([
        fetch('/api/performance/performance/summary', { headers }),
        fetch('/api/performance/tasks/active', { headers })
      ]);

      if (!summaryResponse.ok || !tasksResponse.ok) {
        throw new Error('Failed to fetch performance data');
      }

      const summaryData = await summaryResponse.json();
      const tasksData = await tasksResponse.json();

      setPerformanceSummary(summaryData.performance_summary);
      setActiveTasks(tasksData.active_tasks);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Clear cache
  const clearCache = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/performance/cache/clear', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          pattern: cachePattern || undefined
        })
      });

      if (!response.ok) {
        throw new Error('Failed to clear cache');
      }

      setShowClearCacheModal(false);
      setCachePattern('');
      fetchPerformanceData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear cache');
    }
  };

  // Cancel task
  const cancelTask = async (taskId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/performance/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to cancel task');
      }

      fetchPerformanceData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel task');
    }
  };

  // Trigger maintenance cleanup
  const triggerCleanup = async (cleanupType: string = 'all') => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/performance/maintenance/cleanup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          cleanup_type: cleanupType
        })
      });

      if (!response.ok) {
        throw new Error('Failed to trigger cleanup');
      }

      fetchPerformanceData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger cleanup');
    }
  };

  // Auto-refresh effect
  useEffect(() => {
    fetchPerformanceData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchPerformanceData, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // Get performance score color
  const getPerformanceScoreColor = (score: number): string => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    return 'danger';
  };

  // Get system status badge
  const getSystemStatusBadge = (healthy: boolean) => (
    <Badge bg={healthy ? 'success' : 'danger'}>
      {healthy ? 'Healthy' : 'Unhealthy'}
    </Badge>
  );

  if (loading) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }

  return (
    <Container fluid className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2><FaCogs className="me-2" />Performance Monitor</h2>
        <div>
          <Button
            variant="outline-primary"
            size="sm"
            className="me-2"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? <FaStop /> : <FaPlay />} Auto Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={fetchPerformanceData}
          >
            <FaRedoAlt /> Refresh
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k || 'overview')}
        className="mb-4"
      >
        <Tab eventKey="overview" title="Overview">
          {performanceSummary && (
            <Row>
              {/* Performance Score Card */}
              <Col md={6} lg={3} className="mb-4">
                <Card className="h-100">
                  <Card.Body className="text-center">
                    <h5><FaChartLine className="me-2" />Performance Score</h5>
                    <h2 className={`text-${getPerformanceScoreColor(performanceSummary.performance_score)}`}>
                      {performanceSummary.performance_score.toFixed(1)}%
                    </h2>
                    <ProgressBar
                      variant={getPerformanceScoreColor(performanceSummary.performance_score)}
                      now={performanceSummary.performance_score}
                      className="mt-2"
                    />
                  </Card.Body>
                </Card>
              </Col>

              {/* System Health Card */}
              <Col md={6} lg={3} className="mb-4">
                <Card className="h-100">
                  <Card.Body>
                    <h5><FaMicrochip className="me-2" />System Health</h5>
                    <div className="mb-2">
                      <small>CPU Usage:</small>
                      <ProgressBar
                        variant={performanceSummary.system_health.system.cpu_percent > 80 ? 'danger' : 'info'}
                        now={performanceSummary.system_health.system.cpu_percent}
                        label={`${performanceSummary.system_health.system.cpu_percent}%`}
                        className="mb-1"
                      />
                    </div>
                    <div className="mb-2">
                      <small>Memory Usage:</small>
                      <ProgressBar
                        variant={performanceSummary.system_health.system.memory_percent > 85 ? 'danger' : 'info'}
                        now={performanceSummary.system_health.system.memory_percent}
                        label={`${performanceSummary.system_health.system.memory_percent}%`}
                      />
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              {/* Cache Performance Card */}
              <Col md={6} lg={3} className="mb-4">
                <Card className="h-100">
                  <Card.Body>
                    <h5><FaMemory className="me-2" />Cache Performance</h5>
                    <div className="mb-2">
                      <small>Hit Rate:</small>
                      <ProgressBar
                        variant={performanceSummary.cache_performance.hit_rate > 80 ? 'success' : 'warning'}
                        now={performanceSummary.cache_performance.hit_rate}
                        label={`${performanceSummary.cache_performance.hit_rate}%`}
                        className="mb-1"
                      />
                    </div>
                    <div className="d-flex justify-content-between">
                      <small>Keys: {performanceSummary.cache_performance.total_keys}</small>
                      <small>Memory: {performanceSummary.cache_performance.memory_usage}</small>
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              {/* Active Tasks Card */}
              <Col md={6} lg={3} className="mb-4">
                <Card className="h-100">
                  <Card.Body className="text-center">
                    <h5><FaClock className="me-2" />Active Tasks</h5>
                    <h2 className="text-info">{performanceSummary.active_tasks_count}</h2>
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={() => setActiveTab('tasks')}
                    >
                      <FaEye /> View Tasks
                    </Button>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}

          {/* Services Status */}
          {performanceSummary && (
            <Row>
              <Col md={12}>
                <Card className="mb-4">
                  <Card.Header>
                    <h5 className="mb-0">Service Status</h5>
                  </Card.Header>
                  <Card.Body>
                    <Row>
                      <Col md={6}>
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span>Redis Cache:</span>
                          {getSystemStatusBadge(performanceSummary.system_health.services.redis_healthy)}
                        </div>
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span>Database:</span>
                          {getSystemStatusBadge(performanceSummary.system_health.services.database_healthy)}
                        </div>
                      </Col>
                      <Col md={6}>
                        <Button
                          variant="warning"
                          size="sm"
                          className="me-2 mb-2"
                          onClick={() => setShowClearCacheModal(true)}
                        >
                          <FaTrash /> Clear Cache
                        </Button>
                        <Button
                          variant="info"
                          size="sm"
                          className="mb-2"
                          onClick={() => triggerCleanup()}
                        >
                          <FaCogs /> Run Cleanup
                        </Button>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}
        </Tab>

        <Tab eventKey="tasks" title="Background Tasks">
          <Card>
            <Card.Header>
              <h5 className="mb-0">Active Background Tasks</h5>
            </Card.Header>
            <Card.Body>
              {activeTasks.length === 0 ? (
                <Alert variant="info">No active tasks running</Alert>
              ) : (
                <Table responsive striped>
                  <thead>
                    <tr>
                      <th>Task ID</th>
                      <th>Name</th>
                      <th>Worker</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeTasks.map((task) => (
                      <tr key={task.task_id}>
                        <td>
                          <code>{task.task_id.slice(0, 8)}...</code>
                        </td>
                        <td>{task.name}</td>
                        <td>{task.worker}</td>
                        <td>
                          <Badge bg="primary">{task.status}</Badge>
                        </td>
                        <td>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => cancelTask(task.task_id)}
                          >
                            Cancel
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="analytics" title="Analytics">
          <Card>
            <Card.Header>
              <h5 className="mb-0">Performance Analytics</h5>
            </Card.Header>
            <Card.Body>
              <Alert variant="info">
                Performance analytics and historical data will be displayed here.
                This section can include charts showing system performance over time,
                cache hit rates, task processing times, and other metrics.
              </Alert>
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>

      {/* Clear Cache Modal */}
      <Modal show={showClearCacheModal} onHide={() => setShowClearCacheModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Clear Cache</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Cache Pattern (optional)</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g., conversation:*, analytics:*"
                value={cachePattern}
                onChange={(e) => setCachePattern(e.target.value)}
              />
              <Form.Text className="text-muted">
                Leave empty to clear all cache entries. Use patterns like "conversation:*" to clear specific keys.
              </Form.Text>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowClearCacheModal(false)}>
            Cancel
          </Button>
          <Button variant="warning" onClick={clearCache}>
            Clear Cache
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default PerformanceMonitor;
