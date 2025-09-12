import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Badge, Button, Alert, Modal, Spinner, ProgressBar } from 'react-bootstrap';
import { 
  Shield, 
  Smartphone, 
  Monitor, 
  Globe, 
  Clock, 
  MapPin, 
  Trash2, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Eye,
  RefreshCw,
  Download
} from 'lucide-react';
import { motion } from 'framer-motion';

interface LoginHistory {
  id: string;
  timestamp: string;
  ip_address: string;
  location: string;
  device_type: string;
  browser: string;
  os: string;
  success: boolean;
  risk_level: 'low' | 'medium' | 'high';
}

interface Device {
  id: string;
  name: string;
  device_type: string;
  browser: string;
  os: string;
  last_seen: string;
  ip_address: string;
  location: string;
  is_current: boolean;
  trusted: boolean;
}

interface SecurityStats {
  total_logins: number;
  failed_logins: number;
  successful_logins: number;
  unique_devices: number;
  security_score: number;
  last_password_change: string;
  mfa_enabled: boolean;
}

const SecurityDashboard: React.FC = () => {
  const [loginHistory, setLoginHistory] = useState<LoginHistory[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [securityStats, setSecurityStats] = useState<SecurityStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRemoveDeviceModal, setShowRemoveDeviceModal] = useState(false);
  const [deviceToRemove, setDeviceToRemove] = useState<Device | null>(null);
  const [isRemoving, setIsRemoving] = useState(false);

  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`
      };

      // Load all security data in parallel
      const [historyRes, devicesRes, statsRes] = await Promise.all([
        fetch('/api/v1/auth/security/login-history', { headers }),
        fetch('/api/v1/auth/security/devices', { headers }),
        fetch('/api/v1/auth/security/stats', { headers })
      ]);

      if (!historyRes.ok || !devicesRes.ok || !statsRes.ok) {
        throw new Error('Failed to load security data');
      }

      const [historyData, devicesData, statsData] = await Promise.all([
        historyRes.json(),
        devicesRes.json(),
        statsRes.json()
      ]);

      setLoginHistory(historyData);
      setDevices(devicesData);
      setSecurityStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load security data');
    } finally {
      setIsLoading(false);
    }
  };

  const removeDevice = async (device: Device) => {
    setIsRemoving(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/auth/security/devices/${device.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to remove device');
      }

      setDevices(devices.filter(d => d.id !== device.id));
      setShowRemoveDeviceModal(false);
      setDeviceToRemove(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove device');
    } finally {
      setIsRemoving(false);
    }
  };

  const toggleDeviceTrust = async (device: Device) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/auth/security/devices/${device.id}/trust`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ trusted: !device.trusted })
      });

      if (!response.ok) {
        throw new Error('Failed to update device trust');
      }

      setDevices(devices.map(d => 
        d.id === device.id ? { ...d, trusted: !d.trusted } : d
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update device trust');
    }
  };

  const exportSecurityReport = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/security/export', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to export security report');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `security-report-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export security report');
    }
  };

  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType.toLowerCase()) {
      case 'mobile':
        return <Smartphone size={16} />;
      case 'desktop':
        return <Monitor size={16} />;
      default:
        return <Globe size={16} />;
    }
  };

  const getRiskBadge = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return <Badge bg="success">Low Risk</Badge>;
      case 'medium':
        return <Badge bg="warning">Medium Risk</Badge>;
      case 'high':
        return <Badge bg="danger">High Risk</Badge>;
      default:
        return <Badge bg="secondary">Unknown</Badge>;
    }
  };

  const getSecurityScoreColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  if (isLoading) {
    return (
      <Card className="text-center p-4">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading security dashboard...</span>
        </Spinner>
        <p className="mt-3 mb-0">Loading security dashboard...</p>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="mb-0 d-flex align-items-center">
          <Shield className="me-2" size={24} />
          Security Dashboard
        </h4>
        <div className="d-flex gap-2">
          <Button
            variant="outline-primary"
            size="sm"
            onClick={loadSecurityData}
            className="d-flex align-items-center"
          >
            <RefreshCw size={14} className="me-2" />
            Refresh
          </Button>
          <Button
            variant="outline-secondary"
            size="sm"
            onClick={exportSecurityReport}
            className="d-flex align-items-center"
          >
            <Download size={14} className="me-2" />
            Export Report
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <AlertTriangle size={16} className="me-2" />
          {error}
        </Alert>
      )}

      {/* Security Overview */}
      {securityStats && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="h-100">
              <Card.Body className="text-center">
                <div className="d-flex justify-content-center mb-2">
                  {securityStats.security_score >= 80 ? (
                    <CheckCircle className="text-success" size={32} />
                  ) : securityStats.security_score >= 60 ? (
                    <AlertTriangle className="text-warning" size={32} />
                  ) : (
                    <XCircle className="text-danger" size={32} />
                  )}
                </div>
                <h3 className={`text-${getSecurityScoreColor(securityStats.security_score)}`}>
                  {securityStats.security_score}%
                </h3>
                <p className="mb-0 text-muted">Security Score</p>
                <ProgressBar
                  variant={getSecurityScoreColor(securityStats.security_score)}
                  now={securityStats.security_score}
                  className="mt-2"
                  style={{ height: '4px' }}
                />
              </Card.Body>
            </Card>
          </Col>

          <Col md={3}>
            <Card className="h-100">
              <Card.Body className="text-center">
                <div className="d-flex justify-content-center mb-2">
                  <Clock className="text-primary" size={32} />
                </div>
                <h3 className="text-primary">{securityStats.total_logins}</h3>
                <p className="mb-0 text-muted">Total Logins</p>
                <small className="text-success">
                  {Math.round((securityStats.successful_logins / securityStats.total_logins) * 100)}% success rate
                </small>
              </Card.Body>
            </Card>
          </Col>

          <Col md={3}>
            <Card className="h-100">
              <Card.Body className="text-center">
                <div className="d-flex justify-content-center mb-2">
                  <Monitor className="text-info" size={32} />
                </div>
                <h3 className="text-info">{securityStats.unique_devices}</h3>
                <p className="mb-0 text-muted">Active Devices</p>
                <small className="text-muted">
                  Trusted: {devices.filter(d => d.trusted).length}
                </small>
              </Card.Body>
            </Card>
          </Col>

          <Col md={3}>
            <Card className="h-100">
              <Card.Body className="text-center">
                <div className="d-flex justify-content-center mb-2">
                  <Shield className={`text-${securityStats.mfa_enabled ? 'success' : 'warning'}`} size={32} />
                </div>
                <h5 className={`text-${securityStats.mfa_enabled ? 'success' : 'warning'}`}>
                  {securityStats.mfa_enabled ? 'Enabled' : 'Disabled'}
                </h5>
                <p className="mb-0 text-muted">Two-Factor Auth</p>
                <small className="text-muted">
                  Last password change: {new Date(securityStats.last_password_change).toLocaleDateString()}
                </small>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      <Row>
        {/* Active Devices */}
        <Col lg={6} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="mb-0 d-flex align-items-center">
                <Monitor className="me-2" size={20} />
                Active Devices ({devices.length})
              </h5>
            </Card.Header>
            <Card.Body className="p-0">
              {devices.length === 0 ? (
                <div className="text-center p-4 text-muted">
                  <Monitor size={48} className="mb-3 opacity-50" />
                  <p>No devices found</p>
                </div>
              ) : (
                <Table responsive className="mb-0">
                  <thead>
                    <tr>
                      <th>Device</th>
                      <th>Location</th>
                      <th>Last Seen</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {devices.map((device) => (
                      <tr key={device.id}>
                        <td>
                          <div className="d-flex align-items-center">
                            {getDeviceIcon(device.device_type)}
                            <div className="ms-2">
                              <div className="fw-bold">
                                {device.name || `${device.os} - ${device.browser}`}
                                {device.is_current && (
                                  <Badge bg="primary" className="ms-2">Current</Badge>
                                )}
                              </div>
                              <small className="text-muted">
                                {device.os} • {device.browser}
                              </small>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div className="d-flex align-items-center">
                            <MapPin size={14} className="me-1 text-muted" />
                            <small>{device.location}</small>
                          </div>
                          <small className="text-muted d-block">{device.ip_address}</small>
                        </td>
                        <td>
                          <small>{new Date(device.last_seen).toLocaleString()}</small>
                        </td>
                        <td>
                          <div className="d-flex gap-1">
                            <Button
                              variant={device.trusted ? "success" : "outline-secondary"}
                              size="sm"
                              onClick={() => toggleDeviceTrust(device)}
                              disabled={device.is_current}
                            >
                              {device.trusted ? "Trusted" : "Trust"}
                            </Button>
                            {!device.is_current && (
                              <Button
                                variant="outline-danger"
                                size="sm"
                                onClick={() => {
                                  setDeviceToRemove(device);
                                  setShowRemoveDeviceModal(true);
                                }}
                              >
                                <Trash2 size={14} />
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Login History */}
        <Col lg={6} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="mb-0 d-flex align-items-center">
                <Eye className="me-2" size={20} />
                Recent Login Activity
              </h5>
            </Card.Header>
            <Card.Body className="p-0">
              {loginHistory.length === 0 ? (
                <div className="text-center p-4 text-muted">
                  <Clock size={48} className="mb-3 opacity-50" />
                  <p>No login history found</p>
                </div>
              ) : (
                <Table responsive className="mb-0">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Location</th>
                      <th>Device</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loginHistory.slice(0, 10).map((login) => (
                      <tr key={login.id}>
                        <td>
                          <small>{new Date(login.timestamp).toLocaleString()}</small>
                        </td>
                        <td>
                          <div className="d-flex align-items-center">
                            <MapPin size={12} className="me-1 text-muted" />
                            <small>{login.location}</small>
                          </div>
                          <small className="text-muted d-block">{login.ip_address}</small>
                        </td>
                        <td>
                          <div className="d-flex align-items-center">
                            {getDeviceIcon(login.device_type)}
                            <small className="ms-1">{login.browser}</small>
                          </div>
                        </td>
                        <td>
                          <div className="d-flex flex-column align-items-start">
                            <Badge 
                              bg={login.success ? 'success' : 'danger'}
                              className="mb-1"
                            >
                              {login.success ? 'Success' : 'Failed'}
                            </Badge>
                            {getRiskBadge(login.risk_level)}
                          </div>
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

      {/* Remove Device Modal */}
      <Modal show={showRemoveDeviceModal} onHide={() => setShowRemoveDeviceModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Remove Device</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {deviceToRemove && (
            <>
              <p>Are you sure you want to remove this device from your account?</p>
              <div className="bg-light p-3 rounded">
                <div className="d-flex align-items-center mb-2">
                  {getDeviceIcon(deviceToRemove.device_type)}
                  <span className="ms-2 fw-bold">
                    {deviceToRemove.name || `${deviceToRemove.os} - ${deviceToRemove.browser}`}
                  </span>
                </div>
                <small className="text-muted">
                  Last seen: {new Date(deviceToRemove.last_seen).toLocaleString()}
                  <br />
                  Location: {deviceToRemove.location}
                </small>
              </div>
              <p className="text-warning mt-3 mb-0">
                <small>
                  <AlertTriangle size={14} className="me-1" />
                  This action cannot be undone. The device will need to be trusted again on next login.
                </small>
              </p>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setShowRemoveDeviceModal(false)}
            disabled={isRemoving}
          >
            Cancel
          </Button>
          <Button 
            variant="danger" 
            onClick={() => deviceToRemove && removeDevice(deviceToRemove)}
            disabled={isRemoving}
          >
            {isRemoving ? (
              <>
                <Spinner size="sm" className="me-2" />
                Removing...
              </>
            ) : (
              'Remove Device'
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </motion.div>
  );
};

export default SecurityDashboard;
