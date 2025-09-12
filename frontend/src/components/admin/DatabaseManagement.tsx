import React, { useState, useEffect } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Table,
  Button,
  Badge,
  Alert,
  Modal,
  Form,
  Spinner,
  ProgressBar,
  Dropdown
} from 'react-bootstrap';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { 
  Database, 
  Activity, 
  AlertTriangle, 
  Shield, 
  Download,
  Upload,
  Trash2,
  Settings,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';

interface DatabaseStats {
  total_connections: number;
  active_connections: number;
  idle_connections: number;
  max_connections: number;
  avg_response_time: number;
  status: string;
}

interface DatabaseHealth {
  status: string;
  message: string;
  metrics: {
    connections: number;
    avg_response_time_ms: number;
    error_rate_percent: number;
    total_queries: number;
  };
  alerts: {
    critical: number;
    error: number;
    warning: number;
    total: number;
  };
  timestamp: string;
}

interface DatabaseMetrics {
  timestamp: string;
  connection_count: number;
  avg_response_time: number;
  error_rate: number;
  total_queries: number;
}

interface DatabaseAlert {
  id: string;
  level: string;
  metric_type: string;
  message: string;
  value: number;
  threshold: number;
  timestamp: string;
  resolved: boolean;
}

interface DatabaseBackup {
  id: string;
  backup_type: string;
  file_size: number;
  status: string;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  encrypted: boolean;
}

const DatabaseManagement: React.FC = () => {
  // State management
  const [healthData, setHealthData] = useState<DatabaseHealth | null>(null);
  const [connectionStats, setConnectionStats] = useState<DatabaseStats | null>(null);
  const [metricsHistory, setMetricsHistory] = useState<DatabaseMetrics[]>([]);
  const [activeAlerts, setActiveAlerts] = useState<DatabaseAlert[]>([]);
  const [backups, setBackups] = useState<DatabaseBackup[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modal states
  const [showBackupModal, setShowBackupModal] = useState(false);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState<DatabaseBackup | null>(null);
  
  // Form states
  const [backupType, setBackupType] = useState('full');
  const [customName, setCustomName] = useState('');
  const [isCreatingBackup, setIsCreatingBackup] = useState(false);

  // API calls
  const fetchDatabaseHealth = async () => {
    try {
      const response = await fetch('/api/database/health');
      if (!response.ok) throw new Error('Failed to fetch health data');
      const data = await response.json();
      setHealthData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const fetchConnectionStats = async () => {
    try {
      const response = await fetch('/api/database/connections/stats');
      if (!response.ok) throw new Error('Failed to fetch connection stats');
      const data = await response.json();
      setConnectionStats(data);
    } catch (err) {
      console.error('Connection stats error:', err);
    }
  };

  const fetchMetricsHistory = async () => {
    try {
      const response = await fetch('/api/database/metrics/history?hours=24');
      if (!response.ok) throw new Error('Failed to fetch metrics history');
      const data = await response.json();
      setMetricsHistory(data);
    } catch (err) {
      console.error('Metrics history error:', err);
    }
  };

  const fetchActiveAlerts = async () => {
    try {
      const response = await fetch('/api/database/alerts');
      if (!response.ok) throw new Error('Failed to fetch alerts');
      const data = await response.json();
      setActiveAlerts(data);
    } catch (err) {
      console.error('Alerts error:', err);
    }
  };

  const fetchBackups = async () => {
    try {
      const response = await fetch('/api/database/backups');
      if (!response.ok) throw new Error('Failed to fetch backups');
      const data = await response.json();
      setBackups(data);
    } catch (err) {
      console.error('Backups error:', err);
    }
  };

  const createBackup = async () => {
    setIsCreatingBackup(true);
    try {
      const response = await fetch('/api/database/backups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          backup_type: backupType,
          custom_name: customName || undefined
        })
      });
      
      if (!response.ok) throw new Error('Failed to create backup');
      
      await fetchBackups();
      setShowBackupModal(false);
      setCustomName('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Backup creation failed');
    } finally {
      setIsCreatingBackup(false);
    }
  };

  const resolveAlert = async (alertId: string) => {
    try {
      const response = await fetch(`/api/database/alerts/${alertId}/resolve`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to resolve alert');
      
      await fetchActiveAlerts();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve alert');
    }
  };

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchDatabaseHealth(),
        fetchConnectionStats(),
        fetchMetricsHistory(),
        fetchActiveAlerts(),
        fetchBackups()
      ]);
      setLoading(false);
    };

    loadData();

    // Set up auto-refresh
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Helper functions
  const getStatusBadge = (status: string) => {
    const variant = {
      healthy: 'success',
      warning: 'warning',
      critical: 'danger',
      error: 'danger'
    }[status] || 'secondary';

    return <Badge bg={variant}>{status.toUpperCase()}</Badge>;
  };

  const getAlertBadge = (level: string) => {
    const variant = {
      critical: 'danger',
      error: 'danger',
      warning: 'warning',
      info: 'info'
    }[level] || 'secondary';

    return <Badge bg={variant}>{level.toUpperCase()}</Badge>;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <Container className="py-4 text-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-2">Loading database management dashboard...</p>
      </Container>
    );
  }

  return (
    <Container fluid className="py-4">
      <Row className="mb-4">
        <Col>
          <h1 className="d-flex align-items-center">
            <Database className="me-2" />
            Database Management
          </h1>
          <p className="text-muted">
            Monitor database health, manage backups, and track performance metrics
          </p>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Health Status Overview */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="h-100">
            <Card.Body>
              <div className="d-flex align-items-center">
                <Activity className="me-2 text-primary" size={24} />
                <div>
                  <h6 className="mb-1">Database Health</h6>
                  {healthData && getStatusBadge(healthData.status)}
                </div>
              </div>
              {healthData && (
                <small className="text-muted d-block mt-2">
                  {healthData.message}
                </small>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="h-100">
            <Card.Body>
              <div className="d-flex align-items-center">
                <Settings className="me-2 text-info" size={24} />
                <div>
                  <h6 className="mb-1">Connections</h6>
                  <h4 className="mb-0">
                    {connectionStats?.active_connections || 0} / {connectionStats?.max_connections || 0}
                  </h4>
                </div>
              </div>
              {connectionStats && (
                <ProgressBar 
                  now={(connectionStats.active_connections / connectionStats.max_connections) * 100}
                  className="mt-2 progress-sm"
                  style={{ height: '8px' }}
                />
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="h-100">
            <Card.Body>
              <div className="d-flex align-items-center">
                <AlertTriangle className="me-2 text-warning" size={24} />
                <div>
                  <h6 className="mb-1">Active Alerts</h6>
                  <h4 className="mb-0">{activeAlerts.length}</h4>
                </div>
              </div>
              {healthData && (
                <small className="text-muted">
                  {healthData.alerts.critical} critical, {healthData.alerts.warning} warning
                </small>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="h-100">
            <Card.Body>
              <div className="d-flex align-items-center">
                <Shield className="me-2 text-success" size={24} />
                <div>
                  <h6 className="mb-1">Recent Backups</h6>
                  <h4 className="mb-0">{backups.length}</h4>
                </div>
              </div>
              {backups.length > 0 && (
                <small className="text-muted">
                  Last: {formatTimestamp(backups[0]?.created_at)}
                </small>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Performance Metrics Chart */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header>
              <h5>Performance Metrics (24 Hours)</h5>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={metricsHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                  />
                  <Legend />
                  <Line 
                    yAxisId="left"
                    type="monotone" 
                    dataKey="connection_count" 
                    stroke="#8884d8" 
                    name="Connections"
                  />
                  <Line 
                    yAxisId="right"
                    type="monotone" 
                    dataKey="avg_response_time" 
                    stroke="#82ca9d" 
                    name="Response Time (ms)"
                  />
                  <Line 
                    yAxisId="right"
                    type="monotone" 
                    dataKey="error_rate" 
                    stroke="#ff7300" 
                    name="Error Rate (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        {/* Active Alerts */}
        <Col md={6} className="mb-4">
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5>Active Alerts</h5>
              <Button variant="outline-primary" size="sm" onClick={fetchActiveAlerts}>
                Refresh
              </Button>
            </Card.Header>
            <Card.Body>
              {activeAlerts.length === 0 ? (
                <p className="text-muted text-center py-3">No active alerts</p>
              ) : (
                <Table responsive size="sm">
                  <thead>
                    <tr>
                      <th>Level</th>
                      <th>Message</th>
                      <th>Time</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeAlerts.slice(0, 5).map((alert) => (
                      <tr key={alert.id}>
                        <td>{getAlertBadge(alert.level)}</td>
                        <td>{alert.message}</td>
                        <td>
                          <small>{formatTimestamp(alert.timestamp)}</small>
                        </td>
                        <td>
                          <Button
                            variant="outline-success"
                            size="sm"
                            onClick={() => resolveAlert(alert.id)}
                          >
                            Resolve
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Recent Backups */}
        <Col md={6} className="mb-4">
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5>Database Backups</h5>
              <Button 
                variant="primary" 
                size="sm" 
                onClick={() => setShowBackupModal(true)}
              >
                <Download className="me-1" size={16} />
                Create Backup
              </Button>
            </Card.Header>
            <Card.Body>
              {backups.length === 0 ? (
                <p className="text-muted text-center py-3">No backups available</p>
              ) : (
                <Table responsive size="sm">
                  <thead>
                    <tr>
                      <th>Type</th>
                      <th>Size</th>
                      <th>Status</th>
                      <th>Created</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {backups.slice(0, 5).map((backup) => (
                      <tr key={backup.id}>
                        <td>
                          <Badge bg="info">{backup.backup_type}</Badge>
                          {backup.encrypted && (
                            <span title="Encrypted">
                              <Shield className="ms-1" size={14} />
                            </span>
                          )}
                        </td>
                        <td>{formatFileSize(backup.file_size)}</td>
                        <td>{getStatusBadge(backup.status)}</td>
                        <td>
                          <small>{formatTimestamp(backup.created_at)}</small>
                        </td>
                        <td>
                          <Dropdown>
                            <Dropdown.Toggle variant="outline-secondary" size="sm">
                              Actions
                            </Dropdown.Toggle>
                            <Dropdown.Menu>
                              <Dropdown.Item
                                onClick={() => {
                                  setSelectedBackup(backup);
                                  setShowRestoreModal(true);
                                }}
                              >
                                <Upload className="me-1" size={14} />
                                Restore
                              </Dropdown.Item>
                              <Dropdown.Divider />
                              <Dropdown.Item className="text-danger">
                                <Trash2 className="me-1" size={14} />
                                Delete
                              </Dropdown.Item>
                            </Dropdown.Menu>
                          </Dropdown>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Create Backup Modal */}
      <Modal show={showBackupModal} onHide={() => setShowBackupModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Create Database Backup</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Backup Type</Form.Label>
              <Form.Select 
                value={backupType} 
                onChange={(e) => setBackupType(e.target.value)}
              >
                <option value="full">Full Backup</option>
                <option value="schema_only">Schema Only</option>
                <option value="data_only">Data Only</option>
              </Form.Select>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Custom Name (Optional)</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g., pre-deployment-backup"
                value={customName}
                onChange={(e) => setCustomName(e.target.value)}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowBackupModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={createBackup}
            disabled={isCreatingBackup}
          >
            {isCreatingBackup ? (
              <>
                <Spinner size="sm" className="me-1" />
                Creating...
              </>
            ) : (
              'Create Backup'
            )}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Restore Backup Modal */}
      <Modal show={showRestoreModal} onHide={() => setShowRestoreModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Restore Database</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="warning">
            <AlertTriangle className="me-2" />
            <strong>Warning:</strong> This will replace all current data with the backup data. 
            This action cannot be undone.
          </Alert>
          
          {selectedBackup && (
            <div>
              <p><strong>Backup ID:</strong> {selectedBackup.id}</p>
              <p><strong>Type:</strong> {selectedBackup.backup_type}</p>
              <p><strong>Size:</strong> {formatFileSize(selectedBackup.file_size)}</p>
              <p><strong>Created:</strong> {formatTimestamp(selectedBackup.created_at)}</p>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowRestoreModal(false)}>
            Cancel
          </Button>
          <Button variant="danger">
            Confirm Restore
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default DatabaseManagement;
