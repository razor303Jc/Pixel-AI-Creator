# Database Management System

This comprehensive Database Management System provides enterprise-level database administration, monitoring, backup, and security features for the Pixel AI Creator platform.

## 🚀 Features

### Core Database Management

- **Advanced Connection Pooling**: Optimized connection management with SQLAlchemy async engine
- **Health Monitoring**: Real-time database health checks and performance monitoring
- **Automated Backups**: Scheduled backups with encryption and compression
- **Security Auditing**: Comprehensive audit trails and access control
- **Performance Optimization**: Query analysis and database tuning recommendations

### Monitoring & Alerting

- **Real-time Metrics**: Connection counts, response times, error rates
- **Alert System**: Configurable thresholds with multiple alert levels
- **Performance Analytics**: Historical metrics and trend analysis
- **Dashboard Interface**: Comprehensive admin dashboard for monitoring

### Backup & Recovery

- **Multiple Backup Types**: Full, incremental, schema-only, data-only
- **Encryption**: AES-256 encryption for backup files
- **Compression**: Configurable compression levels
- **Automated Scheduling**: Cron-based backup scheduling
- **Disaster Recovery**: Point-in-time recovery capabilities

### Security Features

- **Access Auditing**: Track all database operations
- **Data Encryption**: Encryption at rest and in transit
- **Compliance Reporting**: Automated compliance checks
- **Data Masking**: Sensitive data anonymization
- **Role-based Access**: Granular permission control

## 📁 Architecture

```
api/
├── core/
│   ├── database_manager.py      # Connection management & pooling
│   └── enhanced_config.py       # Configuration settings
├── services/
│   ├── database_monitor.py      # Health monitoring & alerts
│   └── database_backup.py       # Backup & security services
├── routes/
│   └── database_management.py   # REST API endpoints
├── middleware/
│   └── database_middleware.py   # Request/response middleware
└── main_database_integration.py # Application integration

frontend/
├── components/
│   └── admin/
│       └── DatabaseManagement.tsx  # Admin dashboard
└── services/
    └── databaseAPI.ts              # API client
```

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Additional database management dependencies
pip install asyncpg psycopg2-binary redis cryptography apscheduler
```

### 2. Environment Configuration

Create or update your `.env` file:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/pixel_ai_db
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Monitoring Settings
DB_HEALTH_CHECK_INTERVAL=30
DB_SLOW_QUERY_THRESHOLD=1.0
DB_METRICS_RETENTION_HOURS=168

# Backup Configuration
BACKUP_DIRECTORY=/app/backups
BACKUP_ENCRYPTION_KEY=your-32-character-encryption-key-here
BACKUP_RETENTION_DAYS=30
BACKUP_COMPRESSION_LEVEL=6

# Security Settings
DB_AUDIT_ENABLED=true
DB_ENCRYPTION_ENABLED=true
DB_AUDIT_RETENTION_DAYS=90

# Alert Thresholds
ALERT_CONNECTION_THRESHOLD=0.8
ALERT_RESPONSE_TIME_THRESHOLD=2000
ALERT_ERROR_RATE_THRESHOLD=0.05

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Alerts
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL_TO=admin@yourcompany.com,dba@yourcompany.com
```

### 3. Database Setup

```bash
# Run database migrations
alembic upgrade head

# Initialize monitoring tables
python -c "
from api.services.database_monitor import DatabaseMonitor
from api.core.database_manager import DatabaseConnectionManager
import asyncio

async def setup():
    manager = DatabaseConnectionManager()
    await manager.initialize()
    monitor = DatabaseMonitor(manager)
    await monitor.initialize()
    print('Database monitoring setup complete')

asyncio.run(setup())
"
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm install recharts react-bootstrap bootstrap lucide-react axios
npm start
```

## 🎯 Usage

### Starting the Application

```bash
# Start with database management features
python -m uvicorn api.main_database_integration:app --host 0.0.0.0 --port 8000

# Or using the existing main.py with integrated features
python api/main.py
```

### API Endpoints

#### Health & Monitoring

```bash
# Check database health
GET /api/database/health

# Get connection statistics
GET /api/database/connections/stats

# Get performance metrics
GET /api/database/metrics/history?hours=24

# Get current alerts
GET /api/database/alerts
```

#### Backup Management

```bash
# Create backup
POST /api/database/backups
{
  "backup_type": "full",
  "custom_name": "pre-deployment-backup"
}

# List backups
GET /api/database/backups

# Download backup
GET /api/database/backups/{backup_id}/download

# Restore from backup
POST /api/database/restore
{
  "backup_id": "backup-id-here",
  "confirm": true
}
```

#### Security & Auditing

```bash
# Get audit logs
GET /api/database/security/audit?limit=100

# Generate compliance report
GET /api/database/security/compliance

# Update security settings
PUT /api/database/security/settings
{
  "enable_audit": true,
  "max_audit_retention_days": 90
}
```

### Admin Dashboard

Access the database management dashboard at:

```
http://localhost:3000/admin/database
```

Features:

- Real-time health monitoring
- Performance metrics visualization
- Backup management interface
- Alert management
- Connection monitoring

## 📊 Monitoring & Alerts

### Metrics Collected

- **Connection Metrics**: Active/idle connections, pool utilization
- **Performance Metrics**: Query response times, throughput
- **Error Metrics**: Error rates, failed queries
- **System Metrics**: CPU usage, memory usage, disk space

### Alert Levels

- **CRITICAL**: Service-affecting issues requiring immediate attention
- **ERROR**: Significant problems that may impact performance
- **WARNING**: Potential issues that should be monitored
- **INFO**: Informational alerts for awareness

### Alert Configuration

```python
# Configure alert thresholds
ALERT_THRESHOLDS = {
    "connection_usage": 0.8,     # 80% of max connections
    "response_time": 2000,       # 2 seconds
    "error_rate": 0.05,          # 5% error rate
    "disk_usage": 0.9,           # 90% disk usage
}
```

## 🔒 Security Features

### Audit Logging

All database operations are logged with:

- User identification
- Timestamp
- Operation type
- Table/data affected
- IP address
- Success/failure status

### Data Encryption

- **At Rest**: Backup files encrypted with AES-256
- **In Transit**: SSL/TLS encryption for all connections
- **Sensitive Data**: Automatic masking of PII in logs

### Access Control

- Role-based permissions
- Connection limits per user
- IP whitelist support
- Session timeout controls

## 💾 Backup & Recovery

### Backup Types

1. **Full Backup**: Complete database dump
2. **Incremental**: Changes since last backup
3. **Schema Only**: Database structure only
4. **Data Only**: Data without schema

### Automated Scheduling

```python
# Example backup schedule
BACKUP_SCHEDULE = {
    "incremental": "0 */6 * * *",    # Every 6 hours
    "full": "0 2 * * 0",             # Weekly on Sunday at 2 AM
    "schema": "0 1 * * 1",           # Weekly on Monday at 1 AM
}
```

### Recovery Options

- Point-in-time recovery
- Table-level restoration
- Cross-environment restoration
- Validation before restore

## 🔧 Performance Optimization

### Connection Pool Tuning

```python
# Recommended settings for production
DB_POOL_SIZE = 20          # Base connections
DB_MAX_OVERFLOW = 30       # Additional connections
DB_POOL_TIMEOUT = 30       # Connection timeout
DB_POOL_RECYCLE = 3600     # Connection recycling
```

### Query Optimization

- Automatic slow query detection
- Index recommendations
- Query plan analysis
- Performance trending

### Maintenance Tasks

- Automatic VACUUM operations
- Index rebuilding
- Statistics updates
- Connection cleanup

## 🐛 Troubleshooting

### Common Issues

#### High Connection Usage

```bash
# Check active connections
GET /api/database/connections/details

# Close idle connections
POST /api/database/connections/close-idle
```

#### Slow Performance

```bash
# Analyze performance
GET /api/database/performance/analyze

# Run optimization
POST /api/database/performance/optimize
```

#### Backup Failures

```bash
# Check backup status
GET /api/database/backups/{backup_id}

# Validate backup
POST /api/database/backups/{backup_id}/validate
```

### Logging

Database management operations are logged at various levels:

```python
# Enable debug logging
LOG_LEVEL=DEBUG
DB_ENABLE_QUERY_LOGGING=true
```

## 📈 Monitoring Dashboard

The admin dashboard provides:

### Overview Widgets

- Database health status
- Active connections count
- Recent alerts summary
- Backup status

### Performance Charts

- Response time trends
- Connection usage over time
- Error rate monitoring
- Query volume metrics

### Management Interfaces

- Backup creation and scheduling
- Alert acknowledgment and resolution
- Connection management
- Security settings

## 🚀 Production Deployment

### Environment Setup

```bash
# Production environment variables
ENVIRONMENT=production
DEBUG=false
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=100
BACKUP_RETENTION_DAYS=90
DB_AUDIT_ENABLED=true
```

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set BACKUP_ENCRYPTION_KEY
- [ ] Configure SSL certificates
- [ ] Set up firewall rules
- [ ] Enable audit logging
- [ ] Configure email alerts

### Monitoring Setup

- [ ] Set up external monitoring
- [ ] Configure log aggregation
- [ ] Set up backup verification
- [ ] Test disaster recovery procedures

## 📝 API Documentation

Complete API documentation is available at:

```
http://localhost:8000/docs
```

The API provides comprehensive endpoints for:

- Database health monitoring
- Backup management
- Security administration
- Performance analysis
- Connection management

## 🤝 Contributing

When contributing to the database management system:

1. Follow the established patterns in the codebase
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure security best practices
5. Test with various database loads

## 📄 License

This database management system is part of the Pixel AI Creator platform and follows the same licensing terms.

---

For additional support or questions about the database management system, please refer to the main project documentation or contact the development team.
