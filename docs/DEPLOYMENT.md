# Deployment Guide

## Quick Start with Docker Compose

The easiest way to run Watcher Protocol is using Docker Compose.

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/watcher_protocol.git
   cd watcher_protocol
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   nano .env
   ```

3. **Start services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001

5. **Initialize database** (first time only)
   ```bash
   docker-compose exec backend python -c "from models import Base; from sqlalchemy import create_engine; engine = create_engine('postgresql://watcher:watcher_password@postgres:5432/watcher_db'); Base.metadata.create_all(engine)"
   ```

## Production Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Push images to ECR**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

   # Build and push backend
   docker build -t watcher-backend -f docker/Dockerfile.backend .
   docker tag watcher-backend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/watcher-backend:latest
   docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/watcher-backend:latest

   # Build and push frontend
   docker build -t watcher-frontend -f docker/Dockerfile.frontend .
   docker tag watcher-frontend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/watcher-frontend:latest
   docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/watcher-frontend:latest
   ```

2. **Create RDS PostgreSQL instance**
   - Use PostgreSQL 16 with pgvector extension
   - Instance type: db.t3.medium or larger
   - Enable automated backups

3. **Create ElastiCache Redis cluster**
   - Redis 7.x
   - Instance type: cache.t3.micro or larger

4. **Configure S3 bucket**
   - Create bucket for content storage
   - Enable versioning
   - Configure lifecycle rules

5. **Deploy ECS tasks**
   - Use the task definitions in `deploy/aws/`
   - Configure load balancer
   - Set up auto-scaling

#### Using Kubernetes (EKS)

See `deploy/aws/kubernetes/` for manifests.

```bash
# Apply configurations
kubectl apply -f deploy/aws/kubernetes/namespace.yaml
kubectl apply -f deploy/aws/kubernetes/secrets.yaml
kubectl apply -f deploy/aws/kubernetes/postgres.yaml
kubectl apply -f deploy/aws/kubernetes/redis.yaml
kubectl apply -f deploy/aws/kubernetes/backend.yaml
kubectl apply -f deploy/aws/kubernetes/frontend.yaml
kubectl apply -f deploy/aws/kubernetes/ingress.yaml
```

### Azure Deployment

#### Using Azure Container Instances

1. **Create Resource Group**
   ```bash
   az group create --name watcher-protocol-rg --location eastus
   ```

2. **Create Azure Database for PostgreSQL**
   ```bash
   az postgres flexible-server create \
     --resource-group watcher-protocol-rg \
     --name watcher-postgres \
     --location eastus \
     --admin-user watcher \
     --admin-password YOUR_PASSWORD \
     --sku-name Standard_B2s \
     --version 16
   ```

3. **Create Azure Cache for Redis**
   ```bash
   az redis create \
     --resource-group watcher-protocol-rg \
     --name watcher-redis \
     --location eastus \
     --sku Basic \
     --vm-size c0
   ```

4. **Deploy containers**
   ```bash
   az container create \
     --resource-group watcher-protocol-rg \
     --name watcher-backend \
     --image YOUR_REGISTRY/watcher-backend:latest \
     --dns-name-label watcher-api \
     --ports 8000 \
     --environment-variables DATABASE_URL=... REDIS_URL=...
   ```

See `deploy/azure/` for complete configurations.

### Google Cloud Platform

Use Cloud Run for serverless deployment or GKE for Kubernetes.

See `deploy/gcp/` for configurations.

## Monitoring

### Health Checks

- **Backend**: `GET /health`
- **Database**: Automatic via Docker health checks
- **Redis**: Automatic via Docker health checks

### Prometheus Metrics

Metrics available at `/metrics`:
- Request counts and latencies
- Scraper success/failure rates
- Database connection pool status
- Cache hit/miss ratios

### Logging

- Structured JSON logging
- Centralized with ELK stack or CloudWatch
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Alerting

Configure alerts in `ops/alerts/`:
- Scraper failures
- High error rates
- Database connection issues
- High latency

## Scaling

### Horizontal Scaling

- Backend: Scale to 3+ instances behind load balancer
- Frontend: Scale to 2+ instances
- Database: Use read replicas for queries
- Redis: Use Redis Cluster for high availability

### Vertical Scaling

Minimum requirements per service:
- Backend: 1 CPU, 2GB RAM
- Frontend: 0.5 CPU, 512MB RAM
- PostgreSQL: 2 CPU, 4GB RAM
- Redis: 0.5 CPU, 512MB RAM

## Backup and Recovery

### Database Backups

```bash
# Manual backup
docker-compose exec postgres pg_dump -U watcher watcher_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U watcher watcher_db < backup.sql
```

### Automated Backups

Configure automated backups in production:
- AWS RDS: Automated daily snapshots
- Azure: Point-in-time restore
- GCP: Automated backups with retention

## Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Enable database encryption
- [ ] Rotate API keys regularly
- [ ] Set up VPN for admin access
- [ ] Enable audit logging
- [ ] Configure rate limiting
- [ ] Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check DATABASE_URL is correct
   - Verify PostgreSQL is running
   - Check network connectivity

2. **Scraper failures**
   - Verify API keys are set
   - Check rate limits
   - Review scraper logs

3. **Memory issues**
   - Increase container memory limits
   - Optimize database queries
   - Clear Redis cache

4. **Slow performance**
   - Add database indexes
   - Enable Redis caching
   - Scale horizontally

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

## Maintenance

### Update Dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Database Migrations

Use Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Cleanup

```bash
# Remove old items (older than 1 year)
curl -X POST http://localhost:8000/api/v1/admin/database/cleanup?days_old=365

# Clear Redis cache
curl -X POST http://localhost:8000/api/v1/admin/cache/clear
```
