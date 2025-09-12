# Advanced Authentication System

This document provides comprehensive information about the advanced authentication features implemented in the Pixel AI Creator application.

## Features Overview

### 🔐 Multi-Factor Authentication (MFA/2FA)

- **Time-based One-Time Passwords (TOTP)** using Google Authenticator, Authy, etc.
- **QR Code Generation** for easy mobile app setup
- **Backup Codes** for account recovery
- **Encrypted Storage** of secrets and backup codes
- **Flexible MFA Methods** (extensible for SMS, Email)

### 🌐 Social Login Integration

- **Google OAuth2** - Login with Google accounts
- **GitHub OAuth2** - Login with GitHub accounts
- **LinkedIn OAuth2** - Login with LinkedIn accounts
- **Account Linking** - Link/unlink social accounts
- **Profile Synchronization** - Sync user data from social providers

### 🛡️ Enhanced Security

- **Password Strength Validation** using zxcvbn algorithm
- **Password History Tracking** to prevent reuse
- **Device Tracking** and trusted device management
- **Login Attempt Monitoring** with IP and location tracking
- **Session Management** with enhanced security controls

### 📱 Device Management

- **Device Registration** and naming
- **Trusted Device Marking** for reduced MFA prompts
- **Device Removal** and security management
- **Cross-device Session Control**

## API Endpoints

### MFA Endpoints

| Endpoint                                     | Method | Description                     |
| -------------------------------------------- | ------ | ------------------------------- |
| `/auth/advanced/mfa/setup`                   | POST   | Setup MFA for user account      |
| `/auth/advanced/mfa/verify-setup`            | POST   | Verify MFA setup with TOTP code |
| `/auth/advanced/mfa/disable`                 | POST   | Disable MFA for account         |
| `/auth/advanced/mfa/backup-codes`            | GET    | Get backup codes                |
| `/auth/advanced/mfa/regenerate-backup-codes` | POST   | Generate new backup codes       |

### Enhanced Authentication

| Endpoint                                 | Method | Description                     |
| ---------------------------------------- | ------ | ------------------------------- |
| `/auth/advanced/login-mfa`               | POST   | Login with MFA support          |
| `/auth/advanced/password/change`         | POST   | Change password with validation |
| `/auth/advanced/password/strength-check` | POST   | Check password strength         |

### Social Login

| Endpoint                                     | Method | Description                |
| -------------------------------------------- | ------ | -------------------------- |
| `/auth/advanced/social/authorize/{provider}` | GET    | Start social login flow    |
| `/auth/advanced/social/callback/{provider}`  | GET    | Handle OAuth callback      |
| `/auth/advanced/social/accounts`             | GET    | Get linked social accounts |
| `/auth/advanced/social/unlink/{provider}`    | DELETE | Unlink social account      |

### Security & Device Management

| Endpoint                             | Method | Description       |
| ------------------------------------ | ------ | ----------------- |
| `/auth/advanced/devices`             | GET    | Get user devices  |
| `/auth/advanced/devices/{device_id}` | DELETE | Remove device     |
| `/auth/advanced/login-history`       | GET    | Get login history |

## Setup Instructions

### 1. Environment Configuration

Copy the advanced authentication environment template:

```bash
cp .env.advanced-auth.template .env.advanced-auth
```

Edit the file and add your OAuth credentials and encryption keys.

### 2. Social Provider Setup

#### Google OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project
3. Enable Google+ API and OAuth2 API
4. Create OAuth 2.0 Client ID credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/auth/advanced/social/callback/google`
   - `https://yourdomain.com/auth/advanced/social/callback/google`

#### GitHub OAuth2

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create new OAuth App
3. Set Authorization callback URL:
   - `http://localhost:8000/auth/advanced/social/callback/github`

#### LinkedIn OAuth2

1. Go to [LinkedIn Developer Portal](https://developer.linkedin.com/)
2. Create new app
3. Add redirect URLs and request scopes:
   - `r_liteprofile`, `r_emailaddress`

### 3. Database Migration

Run the advanced authentication migration:

```bash
cd api
alembic upgrade head
```

### 4. Docker Configuration

Update your `docker-compose.yml` to include the new environment variables:

```yaml
services:
  api:
    environment:
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID}
      - GITHUB_CLIENT_SECRET=${GITHUB_CLIENT_SECRET}
      - LINKEDIN_CLIENT_ID=${LINKEDIN_CLIENT_ID}
      - LINKEDIN_CLIENT_SECRET=${LINKEDIN_CLIENT_SECRET}
      - MFA_ENCRYPTION_KEY=${MFA_ENCRYPTION_KEY}
      - BASE_URL=${BASE_URL}
```

### 5. Frontend Integration

The frontend needs to be updated to support the new authentication flows:

#### MFA Setup Flow

```javascript
// 1. Setup MFA
const response = await fetch("/auth/advanced/mfa/setup", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ method: "TOTP" }),
});

const { secret_key, qr_code_url, backup_codes } = await response.json();

// 2. Display QR code to user
// 3. User scans QR code with authenticator app
// 4. User enters verification code

// 5. Verify setup
await fetch("/auth/advanced/mfa/verify-setup", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    code: userEnteredCode,
    remember_device: true,
  }),
});
```

#### Social Login Flow

```javascript
// 1. Get authorization URL
const response = await fetch("/auth/advanced/social/authorize/google");
const { authorization_url, state } = await response.json();

// 2. Redirect user to authorization URL
window.location.href = authorization_url;

// 3. Handle callback (in callback page)
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get("code");
const state = urlParams.get("state");

// 4. Exchange code for tokens
const tokenResponse = await fetch(
  `/auth/advanced/social/callback/google?code=${code}&state=${state}`
);
const { access_token, user } = await tokenResponse.json();
```

## Security Considerations

### Encryption

- MFA secrets are encrypted using AES-256
- Backup codes are hashed and encrypted
- Encryption keys should be rotated regularly

### Password Policies

- Minimum 8 characters (configurable)
- Requires uppercase, lowercase, numbers, symbols
- Prevents common passwords
- Tracks password history (prevents reuse of last 5 passwords)
- zxcvbn strength scoring (minimum score 2/4)

### Session Security

- JWT tokens with configurable expiration
- Device tracking and trusted device management
- IP-based login monitoring
- Failed login attempt tracking

### Rate Limiting

Consider implementing rate limiting for:

- Login attempts (prevent brute force)
- MFA verification attempts
- Password strength checks
- Social login callbacks

## Database Schema

### Core Tables

#### `user_mfa`

- Stores MFA configuration per user
- Encrypted secret keys and backup codes
- Method tracking (TOTP, SMS, Email)

#### `social_login`

- Social provider account links
- OAuth tokens and refresh tokens
- Profile synchronization data

#### `password_history`

- Historical password hashes
- Prevents password reuse
- Tracks change metadata

#### `login_attempt`

- Security monitoring and logging
- Failed login tracking
- IP and device information

#### `device_info`

- Trusted device management
- Browser and OS fingerprinting
- Device naming and tracking

## Error Handling

### Common Error Responses

#### MFA Errors

```json
{
  "detail": "MFA is already enabled for this account",
  "error_code": "MFA_ALREADY_ENABLED"
}
```

#### Social Login Errors

```json
{
  "detail": "OAuth2 authentication failed: invalid_grant",
  "error_code": "OAUTH_FAILED"
}
```

#### Password Validation Errors

```json
{
  "detail": "Password does not meet requirements: Add uppercase letters, Add symbols",
  "error_code": "WEAK_PASSWORD"
}
```

## Testing

### Unit Tests

Run the authentication service tests:

```bash
cd api
pytest tests/test_auth_advanced.py -v
```

### Integration Tests

Test the complete authentication flows:

```bash
pytest tests/test_auth_integration.py -v
```

### Manual Testing

Use the provided test scripts to validate functionality:

```bash
# Test MFA setup flow
python scripts/test_mfa_flow.py

# Test social login flow
python scripts/test_social_login.py

# Test password validation
python scripts/test_password_validation.py
```

## Monitoring & Analytics

### Security Metrics

- Failed login attempts by IP
- MFA adoption rates
- Social login usage statistics
- Password strength distributions

### Recommended Monitoring

- Set up alerts for:
  - Unusual login patterns
  - High failed login rates
  - MFA bypass attempts
  - New device registrations

## Troubleshooting

### Common Issues

#### "MFA setup failed"

- Check encryption key configuration
- Verify database connectivity
- Check for existing MFA records

#### "Social login callback failed"

- Verify OAuth credentials
- Check redirect URI configuration
- Validate state parameter handling

#### "Password validation errors"

- Check zxcvbn library installation
- Verify password policy configuration
- Test with different password patterns

### Debug Mode

Enable debug logging for authentication:

```python
import logging
logging.getLogger('auth.advanced').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

- **SMS MFA** integration with Twilio
- **Email MFA** with verification codes
- **WebAuthn/FIDO2** support for passwordless auth
- **Risk-based Authentication** with device fingerprinting
- **SAML SSO** for enterprise integration
- **OAuth2 Scopes** for fine-grained permissions

### Security Improvements

- **Hardware Security Module (HSM)** integration
- **Advanced Fraud Detection** with ML
- **Biometric Authentication** support
- **Zero-Knowledge Proofs** for enhanced privacy

## Support

For questions or issues with the advanced authentication system:

1. Check the troubleshooting section above
2. Review the API documentation
3. Check the test suite for examples
4. Create an issue in the project repository

## Contributing

When contributing to the authentication system:

1. Follow security best practices
2. Add comprehensive tests
3. Update documentation
4. Consider backward compatibility
5. Review security implications
