-- Initialize database for Watcher Protocol

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if not exists (for reference, typically created by POSTGRES_DB env var)
-- CREATE DATABASE watcher_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE watcher_db TO watcher;

-- Note: Tables will be created by SQLAlchemy models or Alembic migrations
