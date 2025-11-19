# Watcher Protocol Architecture

## System Overview

Watcher Protocol is a distributed system designed for real-time monitoring and analysis of AI research and alignment developments.

## Core Components

### 1. Data Collection Layer

#### Scrapers
Each scraper is a modular component responsible for collecting data from a specific source:

```python
class BaseScraper:
    """Base class for all data scrapers"""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.rate_limiter = RateLimiter(config.requests_per_minute)

    async def fetch(self) -> List[RawItem]:
        """Fetch new items from source"""
        pass

    async def parse(self, raw_data) -> List[ParsedItem]:
        """Parse raw data into structured format"""
        pass

    async def run(self) -> List[ParsedItem]:
        """Main execution method"""
        raw_data = await self.fetch()
        return await self.parse(raw_data)
```

**Implemented Scrapers:**
- `ArxivScraper`: Polls arXiv API for new papers in relevant categories
- `AlignmentForumScraper`: RSS feed parser for Alignment Forum
- `LessWrongScraper`: API integration for LessWrong posts
- `GitHubScraper`: Monitors trending repositories and specific orgs
- `RSSFeedScraper`: Generic RSS/Atom feed parser

**Planned Scrapers:**
- `TwitterScraper`: Monitor key researchers and organizations
- `BlogScraper`: AI lab blogs (OpenAI, Anthropic, DeepMind)
- `RedditScraper`: Relevant subreddits
- `ConferenceScraper`: Proceedings from major conferences
- `NewsScraper`: General news about AI incidents

### 2. Processing Pipeline

```
Raw Data → Deduplication → Classification → Enrichment → Storage
```

#### Deduplication
- Content hashing (SHA-256 of normalized text)
- Fuzzy matching for similar titles
- URL canonicalization
- Cross-reference checking

#### Classification

**Category Classification:**
Uses a fine-tuned text classification model to categorize items:
- Alignment Research
- Capabilities Research
- Safety & Security
- Policy & Governance
- Incidents & Concerns
- General AI Research

**Risk Assessment:**
Scores items on potential safety relevance:
- `critical`: Immediate safety concerns
- `high`: Significant safety implications
- `medium`: Noteworthy for safety researchers
- `low`: General research interest
- `info`: Informational only

**Topic Extraction:**
- Named entity recognition (organizations, researchers, models)
- Keyword extraction
- Technical concept identification
- Citation network analysis

#### Enrichment
- Fetch full-text content when available
- Extract metadata (authors, affiliations, citations)
- Generate embeddings for semantic search
- Calculate relevance scores
- Link related items

### 3. Storage Layer

#### PostgreSQL Schema

```sql
-- Core items table
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL,
    source_id VARCHAR(255),
    title TEXT NOT NULL,
    content TEXT,
    url TEXT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Classification
    category VARCHAR(50),
    risk_level VARCHAR(20),
    confidence_score FLOAT,

    -- Metadata
    authors TEXT[],
    organizations TEXT[],
    keywords TEXT[],
    embedding VECTOR(1536),

    -- Indexing
    UNIQUE(source, source_id)
);

CREATE INDEX idx_items_published ON items(published_at DESC);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_items_risk ON items(risk_level);
CREATE INDEX idx_items_embedding ON items USING ivfflat (embedding);

-- Topics/tags
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    description TEXT
);

CREATE TABLE item_topics (
    item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    relevance_score FLOAT,
    PRIMARY KEY (item_id, topic_id)
);

-- Alerts
CREATE TABLE alert_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT true,

    -- Conditions (JSON)
    conditions JSONB NOT NULL,

    -- Actions
    notification_channels TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id INTEGER REFERENCES alert_rules(id),
    item_id UUID REFERENCES items(id),
    triggered_at TIMESTAMP DEFAULT NOW(),
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100)
);

-- User subscriptions
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    email VARCHAR(255),

    -- Preferences
    categories TEXT[],
    min_risk_level VARCHAR(20),
    keywords TEXT[],
    frequency VARCHAR(20), -- realtime, daily, weekly

    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Redis Cache
- Recent items cache (last 24h)
- Rate limiting counters
- Scraper state/checkpoints
- Session management
- Real-time feed data

#### Object Storage (S3/MinIO)
- Full-text PDFs
- Archived HTML snapshots
- Generated reports
- Exported datasets

### 4. API Layer

**FastAPI Application Structure:**

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Watcher Protocol API", version="1.0.0")

# Routes
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["statistics"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
```

**Key Endpoints:**

```
# Items
GET    /api/v1/items?category={cat}&risk={level}&limit={n}
GET    /api/v1/items/{id}
GET    /api/v1/items/{id}/related
POST   /api/v1/items/{id}/flag

# Search
GET    /api/v1/search?q={query}&filters={json}
POST   /api/v1/search/semantic    # Embedding-based search
GET    /api/v1/search/suggest     # Auto-complete suggestions

# Timeline
GET    /api/v1/timeline?category={cat}&start={date}&end={date}
GET    /api/v1/timeline/trends

# Alerts
GET    /api/v1/alerts
POST   /api/v1/alerts/rules
PUT    /api/v1/alerts/rules/{id}
POST   /api/v1/alerts/{id}/acknowledge

# Subscriptions
POST   /api/v1/subscriptions
GET    /api/v1/subscriptions/{id}
PUT    /api/v1/subscriptions/{id}
DELETE /api/v1/subscriptions/{id}

# Stats
GET    /api/v1/stats/overview
GET    /api/v1/stats/sources
GET    /api/v1/stats/trends

# Admin
GET    /api/v1/admin/scrapers/status
POST   /api/v1/admin/scrapers/{name}/trigger
GET    /api/v1/admin/health
```

### 5. Frontend Application

**Tech Stack:**
- Next.js 14 (React framework)
- TypeScript
- TailwindCSS (styling)
- Recharts (data visualization)
- SWR (data fetching)
- Zustand (state management)

**Key Pages:**

1. **Dashboard** (`/`)
   - Recent high-priority items
   - Trend graphs
   - Quick stats
   - Active alerts

2. **Timeline** (`/timeline`)
   - Chronological view
   - Filter by category/risk
   - Interactive charts
   - Trend analysis

3. **Search** (`/search`)
   - Full-text search
   - Advanced filters
   - Semantic search
   - Saved searches

4. **Alerts** (`/alerts`)
   - Active alerts list
   - Alert rule management
   - Notification settings
   - Alert history

5. **Item Detail** (`/items/[id]`)
   - Full content view
   - Related items
   - Citation network
   - Discussion/notes

6. **Settings** (`/settings`)
   - Notification preferences
   - Subscription management
   - API key management
   - Data export

### 6. Background Jobs

**Scheduler (APScheduler/Celery):**

```python
# Continuous scraping jobs
@scheduler.scheduled_job('interval', minutes=60)
async def scrape_arxiv():
    scraper = ArxivScraper()
    items = await scraper.run()
    await process_items(items)

@scheduler.scheduled_job('interval', minutes=30)
async def scrape_alignment_forum():
    scraper = AlignmentForumScraper()
    items = await scraper.run()
    await process_items(items)

# Periodic analysis
@scheduler.scheduled_job('cron', hour=0)  # Daily at midnight
async def generate_daily_digest():
    items = await get_items_last_24h()
    report = await create_digest_report(items)
    await send_digest_emails(report)

@scheduler.scheduled_job('cron', day_of_week='mon', hour=8)
async def generate_weekly_report():
    await create_weekly_analysis()

# Maintenance
@scheduler.scheduled_job('cron', hour=3)  # Daily at 3 AM
async def cleanup_old_cache():
    await redis.delete_old_entries(days=7)

@scheduler.scheduled_job('cron', day_of_week='sun', hour=2)
async def recompute_embeddings():
    # Update embeddings for items with new model
    await batch_update_embeddings()
```

### 7. Notification System

**Alert Engine:**

```python
class AlertEngine:
    """Evaluates rules and triggers notifications"""

    async def evaluate_item(self, item: Item):
        # Get all active rules
        rules = await get_active_alert_rules()

        for rule in rules:
            if self.matches_conditions(item, rule.conditions):
                await self.trigger_alert(item, rule)

    def matches_conditions(self, item: Item, conditions: dict) -> bool:
        # Evaluate JSON conditions
        # Examples:
        # {"category": "safety", "risk_level": ["critical", "high"]}
        # {"keywords": ["AGI", "superintelligence"], "match": "any"}
        # {"authors": ["specific_researcher@org.com"]}
        pass

    async def trigger_alert(self, item: Item, rule: AlertRule):
        alert = Alert.create(item=item, rule=rule)

        for channel in rule.notification_channels:
            if channel.startswith('email:'):
                await send_email_notification(channel, alert)
            elif channel.startswith('slack:'):
                await send_slack_notification(channel, alert)
            elif channel.startswith('webhook:'):
                await send_webhook(channel, alert)
```

**Notification Channels:**
- Email (SMTP)
- Slack webhooks
- Discord webhooks
- Custom webhooks (JSON POST)
- RSS feed generation
- Telegram bot (planned)

## Data Flow

```
1. Scraper fetches data from source
   ↓
2. Deduplication check (hash + fuzzy match)
   ↓
3. Classification (category, risk, topics)
   ↓
4. Enrichment (embeddings, metadata extraction)
   ↓
5. Storage (PostgreSQL + Redis cache)
   ↓
6. Alert evaluation (check rules)
   ↓
7. Notification dispatch (if triggered)
   ↓
8. Frontend update (WebSocket push or polling)
```

## Scaling Considerations

### Current Design (MVP)
- Single backend instance
- PostgreSQL (single instance)
- Redis (single instance)
- Suitable for: <100k items, <1k users

### Horizontal Scaling
- Multiple backend instances (load balanced)
- Scraper workers (dedicated instances)
- Read replicas for PostgreSQL
- Redis cluster
- Suitable for: <1M items, <10k users

### Large Scale
- Microservices architecture
- Message queue (RabbitMQ/Kafka) for scraper results
- Distributed task processing (Celery cluster)
- PostgreSQL sharding
- Elasticsearch for search
- CDN for frontend
- Object storage for content
- Suitable for: >1M items, >10k users

## Security

### API Security
- API key authentication
- Rate limiting (per key)
- CORS configuration
- Input validation/sanitization
- SQL injection prevention (parameterized queries)

### Data Security
- Encrypted database connections
- Secrets management (environment variables)
- No storage of personal data without consent
- GDPR compliance for EU users

### Operational Security
- Regular dependency updates
- Security scanning (Snyk, Dependabot)
- Access logging
- Intrusion detection

## Monitoring & Observability

### Metrics (Prometheus)
- Scraper success/failure rates
- API response times
- Database query performance
- Alert triggering frequency
- Storage usage

### Logging (Structured JSON)
- Application logs (Python logging)
- Access logs (nginx)
- Error tracking (Sentry)

### Dashboards (Grafana)
- System health overview
- Scraper performance
- User activity
- Data growth trends

## Deployment

### Docker Compose (Development)
```yaml
services:
  backend:
    build: ./docker/Dockerfile.backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./docker/Dockerfile.frontend
    ports:
      - "3000:3000"

  postgres:
    image: pgvector/pgvector:pg16
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
```

### Kubernetes (Production)
- Backend deployment (replicas: 3)
- Frontend deployment (replicas: 2)
- PostgreSQL StatefulSet
- Redis StatefulSet
- Ingress for HTTPS
- Cert-manager for TLS

### Cloud Providers
- **AWS**: ECS/EKS, RDS, ElastiCache, S3
- **Azure**: AKS, Azure Database, Azure Cache, Blob Storage
- **GCP**: GKE, Cloud SQL, Memorystore, Cloud Storage

## Future Enhancements

1. **Machine Learning**
   - Custom alignment topic classifier
   - Anomaly detection for unusual research patterns
   - Trend prediction
   - Automated summarization

2. **Collaboration Features**
   - User annotations and notes
   - Shared collections
   - Discussion threads
   - Expert reviews

3. **Advanced Analytics**
   - Citation network analysis
   - Researcher collaboration graphs
   - Topic evolution tracking
   - Impact prediction

4. **Integration**
   - Zotero/Mendeley export
   - Roam Research/Obsidian sync
   - API for third-party tools
   - Browser extension
