# TSES OTP Authentication Service

Email-based OTP authentication service with Redis rate limiting, Celery async processing, and JWT tokens.

## Features

- Email-based OTP authentication
- Redis-backed rate limiting (3 OTP requests per email per 10 minutes, 10 requests per IP per hour)
- Asynchronous email sending via Celery
- JWT token generation using SimpleJWT
- Audit logging with filtering
- OpenAPI documentation via drf-spectacular
- Docker containerization

## Architecture

- **apps/accounts**: OTP request/verify flows, JWT issuance
- **apps/audit**: Audit log model and read-only endpoints
- **Redis**: OTP storage and rate limiting counters
- **Celery**: Asynchronous task processing
- **PostgreSQL**: Primary database

## API Endpoints

### Authentication
- `POST /api/v1/auth/otp/request/` - Request OTP
- `POST /api/v1/auth/otp/verify/` - Verify OTP and get JWT tokens

### Audit
- `GET /api/v1/audit/logs/` - List audit logs (JWT required)

### Documentation
- `GET /api/docs/` - Swagger UI
- `GET /api/schema/` - OpenAPI schema

## Quick Start

### Using Docker (Recommended)

```bash
# Build and start services
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser (optional)
docker-compose exec web python manage.py createsuperuser
```

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start Redis and PostgreSQL

3. Run migrations:
```bash
python manage.py migrate
```

4. Start Celery worker:
```bash
celery -A config worker -l info
```

5. Start Django server:
```bash
python manage.py runserver
```

## Usage Examples

### Request OTP
```bash
curl -X POST http://localhost:8000/api/v1/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Verify OTP
```bash
curl -X POST http://localhost:8000/api/v1/auth/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "otp": "123456"}'
```

### Access Audit Logs
```bash
curl -X GET http://localhost:8000/api/v1/audit/logs/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Rate Limits

- **Email**: 3 OTP requests per 10 minutes
- **IP**: 10 OTP requests per hour
- **Failed attempts**: 5 failed verifications per 15 minutes (locks account)

## Environment Variables

- `DJANGO_SETTINGS_MODULE`: Django settings module (default: config.settings.local)
- `REDIS_URL`: Redis connection URL (default: redis://redis:6379/0)

## Development

The service is built with a modular architecture:

- **Services layer**: Business logic separated from views
- **Utils**: Redis operations and utilities
- **Tasks**: Celery async tasks
- **Serializers**: Request/response validation
- **Filters**: Query filtering for audit logs
