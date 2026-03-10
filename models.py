import os
import re
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine

# ---------------------------------------------------------------------------
# Database URL handling (supports PostgreSQL and fallback SQLite)
# ---------------------------------------------------------------------------
raw_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or "sqlite:///./app.db"
# Normalise async scheme to sync psycopg driver
if raw_url.startswith("postgresql+asyncpg://"):
    raw_url = raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+psycopg://")

# Determine if we need SSL (any non‑localhost PostgreSQL URL)
connect_args = {}
if raw_url.startswith("postgresql+psycopg://") and not re.search(r"(localhost|127\.0\.0\.1)", raw_url):
    connect_args["sslmode"] = "require"

engine = create_engine(raw_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()

# ---------------------------------------------------------------------------
# Table name prefix – prevents collisions in shared DBs
# ---------------------------------------------------------------------------
PREFIX = "ql_"

def _pref(name: str) -> str:
    return f"{PREFIX}{name}"

# ---------------------------------------------------------------------------
# SQLAlchemy models (no type annotations on relationship())
# ---------------------------------------------------------------------------
class Business(Base):
    __tablename__ = _pref("businesses")
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20))
    address = Column(Text)
    subscription_status = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    locations = relationship("Location", back_populates="business")
    staff = relationship("Staff", back_populates="business")

class Location(Base):
    __tablename__ = _pref("locations")
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    business_id = Column(UUID(as_uuid=True), ForeignKey(_pref("businesses") + ".id"), nullable=False)
    address = Column(Text, nullable=False)
    timezone = Column(String(50), nullable=False)
    language = Column(String(10), nullable=False, default="en")
    capacity = Column(Integer, nullable=False, default=50)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    business = relationship("Business", back_populates="locations")
    queue_entries = relationship("QueueEntry", back_populates="location")
    wait_times = relationship("WaitTime", back_populates="location")
    notifications = relationship("Notification", back_populates="location")

class Customer(Base):
    __tablename__ = _pref("customers")
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String(100))
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20))
    language = Column(String(10), nullable=False, default="en")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    queue_entries = relationship("QueueEntry", back_populates="customer")
    notifications = relationship("Notification", back_populates="customer")

class QueueEntry(Base):
    __tablename__ = _pref("queue_entries")
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    customer_id = Column(UUID(as_uuid=True), ForeignKey(_pref("customers") + ".id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey(_pref("locations") + ".id"), nullable=False)
    party_size = Column(Integer, nullable=False, default=1)
    estimated_wait_time = Column(Integer)  # minutes, populated by AI
    status = Column(String(20), nullable=False, default="pending")
    joined_at = Column(DateTime, server_default=func.now(), nullable=False)
    called_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    queue_code = Column(String(10), nullable=False, unique=True)

    customer = relationship("Customer", back_populates="queue_entries")
    location = relationship("Location", back_populates="queue_entries")

class WaitTime(Base):
    __tablename__ = _pref("wait_times")
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    location_id = Column(UUID(as_uuid=True), ForeignKey(_pref("locations") + ".id"), nullable=False)
    wait_time = Column(Integer, nullable=False)  # minutes
    calculated_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    location = relationship("Location", back_populates="wait_times")

class Notification(Base):
    __tablename__ = _pref("notifications")
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    customer_id = Column(UUID(as_uuid=True), ForeignKey(_pref("customers") + ".id"))
    location_id = Column(UUID(as_uuid=True), ForeignKey(_pref("locations") + ".id"))
    type = Column(String(20), nullable=False, default="info")
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime)
    read_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    status = Column(String(20), nullable=False, default="pending")

    customer = relationship("Customer", back_populates="notifications")
    location = relationship("Location", back_populates="notifications")

class Staff(Base):
    __tablename__ = _pref("staff")
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    business_id = Column(UUID(as_uuid=True), ForeignKey(_pref("businesses") + ".id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(50), nullable=False, default="staff")
    password_hash = Column(String(255), nullable=False)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    business = relationship("Business", back_populates="staff")

class AuditLog(Base):
    __tablename__ = _pref("audit_logs")
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    staff_id = Column(UUID(as_uuid=True), ForeignKey(_pref("staff") + ".id"))
    table_name = Column(String(100), nullable=False)
    action = Column(String(20), nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    staff = relationship("Staff")

# Create tables if they do not exist (useful for demo)
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
