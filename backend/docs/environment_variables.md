# Environment Variables

This document describes the environment variables used in the application.

## Configuration

The application uses environment variables for configuration. These can be set in a `.env` file for development or directly as environment variables in production.

## Security Variables

### SECRET_KEY

- **Description**: Secret key used for JWT token generation and validation.
- **Default**: A randomly generated secure string if not provided.
- **Recommendation**: For production environments, always set this to a secure random value and do not share it.

To generate a secure SECRET_KEY, you can use the provided script:

```bash
python scripts/generate_secret_key.py
```

Or run this Python command:

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

In production, set this as an environment variable rather than in a `.env` file:

```bash
# Linux/macOS
export SECRET_KEY="your-generated-secure-key"

# Windows (Command Prompt)
set SECRET_KEY=your-generated-secure-key

# Windows (PowerShell)
$env:SECRET_KEY="your-generated-secure-key"
```

### ACCESS_TOKEN_EXPIRE_MINUTES

- **Description**: The number of minutes after which a JWT token expires.
- **Default**: 30 minutes
- **Recommendation**: Set this to a value appropriate for your application's security requirements. Shorter times are more secure but require users to authenticate more frequently.

## Database Variables

### POSTGRES_DSN

- **Description**: PostgreSQL connection string.
- **Format**: `postgres://username:password@host:port/database`
- **Required**: Yes

### POSTGRES_USER

- **Description**: PostgreSQL username.
- **Default**: "postgres"

### POSTGRES_PASSWORD

- **Description**: PostgreSQL password.
- **Default**: "postgres"

### POSTGRES_DB

- **Description**: PostgreSQL database name.
- **Default**: "postgres"

### SQL_DEBUG

- **Description**: Enable SQL query debugging.
- **Default**: false
- **Values**: true/false

## Redis Variables

### REDIS_DSN

- **Description**: Redis connection string.
- **Format**: `redis://host:port/db`
- **Required**: Yes

### CONNECTION_POOL_SIZE

- **Description**: Redis connection pool size.
- **Default**: 10

## Debug Variables

### DEBUG

- **Description**: Enable debug mode.
- **Default**: false
- **Values**: true/false

## Bot Variables

### BOT_CREDENTIALS

- **Description**: Bot credentials for authentication.
- **Format**: Comma-separated list of `cts_url|secret_key|bot_id`
- **Required**: No (empty list if not provided) 