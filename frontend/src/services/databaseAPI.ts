import axios, { AxiosResponse } from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Type definitions
export interface DatabaseHealth {
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

export interface ConnectionStats {
  total_connections: number;
  active_connections: number;
  idle_connections: number;
  max_connections: number;
  avg_response_time: number;
  status: string;
}

export interface DatabaseMetrics {
  timestamp: string;
  connection_count: number;
  avg_response_time: number;
  error_rate: number;
  total_queries: number;
  cpu_usage?: number;
  memory_usage?: number;
  disk_usage?: number;
}

export interface DatabaseAlert {
  id: string;
  level: 'critical' | 'error' | 'warning' | 'info';
  metric_type: string;
  message: string;
  value: number;
  threshold: number;
  timestamp: string;
  resolved: boolean;
  acknowledged: boolean;
}

export interface DatabaseBackup {
  id: string;
  backup_type: 'full' | 'schema_only' | 'data_only' | 'incremental';
  file_size: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  encrypted: boolean;
  file_path?: string;
  custom_name?: string;
}

export interface BackupCreateRequest {
  backup_type: 'full' | 'schema_only' | 'data_only' | 'incremental';
  custom_name?: string;
  encrypt?: boolean;
  compress?: boolean;
}

export interface RestoreRequest {
  backup_id: string;
  confirm: boolean;
  target_database?: string;
}

export interface SecurityAudit {
  id: string;
  event_type: string;
  user_id: string;
  table_name: string;
  operation: string;
  timestamp: string;
  ip_address: string;
  details: Record<string, any>;
}

export interface DatabaseMigration {
  id: string;
  name: string;
  version: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  applied_at: string | null;
  rollback_available: boolean;
}

// Database Management API
export class DatabaseManagementAPI {
  // Health monitoring
  static async getHealth(): Promise<DatabaseHealth> {
    const response: AxiosResponse<DatabaseHealth> = await api.get('/api/database/health');
    return response.data;
  }

  static async getConnectionStats(): Promise<ConnectionStats> {
    const response: AxiosResponse<ConnectionStats> = await api.get('/api/database/connections/stats');
    return response.data;
  }

  // Metrics and monitoring
  static async getMetricsHistory(hours: number = 24): Promise<DatabaseMetrics[]> {
    const response: AxiosResponse<DatabaseMetrics[]> = await api.get(
      `/api/database/metrics/history?hours=${hours}`
    );
    return response.data;
  }

  static async getCurrentMetrics(): Promise<DatabaseMetrics> {
    const response: AxiosResponse<DatabaseMetrics> = await api.get('/api/database/metrics/current');
    return response.data;
  }

  // Alert management
  static async getAlerts(resolved: boolean = false): Promise<DatabaseAlert[]> {
    const response: AxiosResponse<DatabaseAlert[]> = await api.get(
      `/api/database/alerts?resolved=${resolved}`
    );
    return response.data;
  }

  static async resolveAlert(alertId: string): Promise<void> {
    await api.post(`/api/database/alerts/${alertId}/resolve`);
  }

  static async acknowledgeAlert(alertId: string): Promise<void> {
    await api.post(`/api/database/alerts/${alertId}/acknowledge`);
  }

  static async deleteAlert(alertId: string): Promise<void> {
    await api.delete(`/api/database/alerts/${alertId}`);
  }

  // Backup management
  static async getBackups(): Promise<DatabaseBackup[]> {
    const response: AxiosResponse<DatabaseBackup[]> = await api.get('/api/database/backups');
    return response.data;
  }

  static async createBackup(request: BackupCreateRequest): Promise<DatabaseBackup> {
    const response: AxiosResponse<DatabaseBackup> = await api.post('/api/database/backups', request);
    return response.data;
  }

  static async getBackupStatus(backupId: string): Promise<DatabaseBackup> {
    const response: AxiosResponse<DatabaseBackup> = await api.get(`/api/database/backups/${backupId}`);
    return response.data;
  }

  static async downloadBackup(backupId: string): Promise<Blob> {
    const response: AxiosResponse<Blob> = await api.get(
      `/api/database/backups/${backupId}/download`,
      { responseType: 'blob' }
    );
    return response.data;
  }

  static async deleteBackup(backupId: string): Promise<void> {
    await api.delete(`/api/database/backups/${backupId}`);
  }

  // Restore operations
  static async restoreDatabase(request: RestoreRequest): Promise<void> {
    await api.post('/api/database/restore', request);
  }

  static async validateBackup(backupId: string): Promise<{ valid: boolean; errors?: string[] }> {
    const response = await api.post(`/api/database/backups/${backupId}/validate`);
    return response.data;
  }

  // Security and auditing
  static async getSecurityAudit(
    limit: number = 100,
    offset: number = 0
  ): Promise<{ audit_logs: SecurityAudit[]; total: number }> {
    const response = await api.get(
      `/api/database/security/audit?limit=${limit}&offset=${offset}`
    );
    return response.data;
  }

  static async getComplianceReport(): Promise<{
    compliant: boolean;
    checks: Array<{ name: string; status: string; details: string }>;
    generated_at: string;
  }> {
    const response = await api.get('/api/database/security/compliance');
    return response.data;
  }

  static async updateSecuritySettings(settings: {
    enable_audit: boolean;
    max_audit_retention_days: number;
    enable_encryption: boolean;
    enable_data_masking: boolean;
  }): Promise<void> {
    await api.put('/api/database/security/settings', settings);
  }

  // Migration management
  static async getMigrations(): Promise<DatabaseMigration[]> {
    const response: AxiosResponse<DatabaseMigration[]> = await api.get('/api/database/migrations');
    return response.data;
  }

  static async applyMigration(migrationId: string): Promise<void> {
    await api.post(`/api/database/migrations/${migrationId}/apply`);
  }

  static async rollbackMigration(migrationId: string): Promise<void> {
    await api.post(`/api/database/migrations/${migrationId}/rollback`);
  }

  // Connection management
  static async closeIdleConnections(): Promise<{ closed_connections: number }> {
    const response = await api.post('/api/database/connections/close-idle');
    return response.data;
  }

  static async getConnectionDetails(): Promise<{
    active_connections: Array<{
      pid: number;
      user: string;
      database: string;
      state: string;
      query: string;
      duration: number;
    }>;
  }> {
    const response = await api.get('/api/database/connections/details');
    return response.data;
  }

  static async killConnection(pid: number): Promise<void> {
    await api.post(`/api/database/connections/${pid}/kill`);
  }

  // Performance optimization
  static async analyzePerformance(): Promise<{
    slow_queries: Array<{
      query: string;
      avg_duration: number;
      call_count: number;
      total_time: number;
    }>;
    recommendations: string[];
    index_suggestions: Array<{
      table: string;
      columns: string[];
      rationale: string;
    }>;
  }> {
    const response = await api.get('/api/database/performance/analyze');
    return response.data;
  }

  static async optimizeDatabase(): Promise<{
    tables_analyzed: number;
    indexes_created: number;
    tables_vacuumed: number;
    performance_improvement: number;
  }> {
    const response = await api.post('/api/database/performance/optimize');
    return response.data;
  }

  // Database maintenance
  static async vacuum(table?: string): Promise<void> {
    const params = table ? `?table=${table}` : '';
    await api.post(`/api/database/maintenance/vacuum${params}`);
  }

  static async reindex(table?: string): Promise<void> {
    const params = table ? `?table=${table}` : '';
    await api.post(`/api/database/maintenance/reindex${params}`);
  }

  static async updateStatistics(table?: string): Promise<void> {
    const params = table ? `?table=${table}` : '';
    await api.post(`/api/database/maintenance/analyze${params}`);
  }

  // Configuration management
  static async getConfiguration(): Promise<Record<string, any>> {
    const response = await api.get('/api/database/config');
    return response.data;
  }

  static async updateConfiguration(config: Record<string, any>): Promise<void> {
    await api.put('/api/database/config', config);
  }

  // System information
  static async getSystemInfo(): Promise<{
    version: string;
    uptime: string;
    size: string;
    tables_count: number;
    indexes_count: number;
    connections_used: number;
    connections_max: number;
  }> {
    const response = await api.get('/api/database/system/info');
    return response.data;
  }
}

// Utility functions
export const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatDuration = (milliseconds: number): string => {
  if (milliseconds < 1000) return `${milliseconds}ms`;
  if (milliseconds < 60000) return `${(milliseconds / 1000).toFixed(1)}s`;
  if (milliseconds < 3600000) return `${(milliseconds / 60000).toFixed(1)}m`;
  return `${(milliseconds / 3600000).toFixed(1)}h`;
};

export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    healthy: '#28a745',
    warning: '#ffc107',
    critical: '#dc3545',
    error: '#dc3545',
    pending: '#6c757d',
    running: '#007bff',
    completed: '#28a745',
    failed: '#dc3545',
  };
  return colors[status] || '#6c757d';
};

export const getAlertSeverityColor = (level: string): string => {
  const colors: Record<string, string> = {
    critical: '#dc3545',
    error: '#dc3545',
    warning: '#ffc107',
    info: '#17a2b8',
  };
  return colors[level] || '#6c757d';
};

export default DatabaseManagementAPI;
