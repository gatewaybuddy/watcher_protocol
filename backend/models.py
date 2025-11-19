"""Database models for Watcher Protocol."""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Float, Integer,
    ForeignKey, Table, JSON, ARRAY, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# Association table for many-to-many relationship between items and topics
item_topics = Table(
    'item_topics',
    Base.metadata,
    Column('item_id', UUID(as_uuid=True), ForeignKey('items.id', ondelete='CASCADE'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topics.id', ondelete='CASCADE'), primary_key=True),
    Column('relevance_score', Float, default=1.0)
)


class Item(Base):
    """Core table for monitored items (papers, posts, articles, etc.)."""

    __tablename__ = 'items'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Source information
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(255))
    source_url: Mapped[Optional[str]] = mapped_column(Text)

    # Content
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Classification
    category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)

    # Metadata
    authors: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    organizations: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # ML features
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(384))  # Adjust dimension as needed

    # Deduplication
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True)

    # Additional metadata (flexible JSON field)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    topics: Mapped[List["Topic"]] = relationship(
        "Topic",
        secondary=item_topics,
        back_populates="items"
    )
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="item")

    __table_args__ = (
        UniqueConstraint('source', 'source_id', name='uix_source_source_id'),
    )

    def __repr__(self):
        return f"<Item(id={self.id}, title='{self.title[:50]}...', category={self.category})>"


class Topic(Base):
    """Topics/tags for categorizing items."""

    __tablename__ = 'topics'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Parent-child relationship for hierarchical topics
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('topics.id'))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    items: Mapped[List["Item"]] = relationship(
        "Item",
        secondary=item_topics,
        back_populates="topics"
    )
    parent: Mapped[Optional["Topic"]] = relationship("Topic", remote_side=[id], backref="children")

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}')>"


class AlertRule(Base):
    """Rules for triggering alerts based on item properties."""

    __tablename__ = 'alert_rules'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Conditions as JSON
    # Example: {"category": "safety", "risk_level": ["critical", "high"]}
    conditions: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Notification channels
    notification_channels: Mapped[List[str]] = mapped_column(ARRAY(Text))

    # Metadata
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="rule")

    def __repr__(self):
        return f"<AlertRule(id={self.id}, name='{self.name}', enabled={self.enabled})>"


class Alert(Base):
    """Triggered alerts for specific items."""

    __tablename__ = 'alerts'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    rule_id: Mapped[int] = mapped_column(Integer, ForeignKey('alert_rules.id'), nullable=False)
    item_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('items.id'), nullable=False)

    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Status
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(100))

    # Notification status
    notifications_sent: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # Relationships
    rule: Mapped["AlertRule"] = relationship("AlertRule", back_populates="alerts")
    item: Mapped["Item"] = relationship("Item", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, rule_id={self.rule_id}, acknowledged={self.acknowledged})>"


class Subscription(Base):
    """User subscriptions for notifications."""

    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # User identification
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255))

    # Preferences
    categories: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    min_risk_level: Mapped[Optional[str]] = mapped_column(String(20))
    keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # Notification frequency: 'realtime', 'daily', 'weekly'
    frequency: Mapped[str] = mapped_column(String(20), default='daily')

    # Active status
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id='{self.user_id}', frequency='{self.frequency}')>"


class ScraperStatus(Base):
    """Track scraper execution status and checkpoints."""

    __tablename__ = 'scraper_status'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    scraper_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Status
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Statistics
    total_runs: Mapped[int] = mapped_column(Integer, default=0)
    successful_runs: Mapped[int] = mapped_column(Integer, default=0)
    failed_runs: Mapped[int] = mapped_column(Integer, default=0)
    items_collected: Mapped[int] = mapped_column(Integer, default=0)

    # Checkpoint data (last processed ID, timestamp, etc.)
    checkpoint: Mapped[Optional[dict]] = mapped_column(JSON)

    # Configuration
    config: Mapped[Optional[dict]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ScraperStatus(scraper_name='{self.scraper_name}', enabled={self.enabled})>"
