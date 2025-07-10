"""
Core database models and connection setup for the Multi-Agent AI System
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from config.settings import settings

# Database setup
engine = create_engine(
    settings.database.url,
    echo=settings.database.echo,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Project(Base):
    """Project model for tracking multi-agent system projects"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    status = Column(String(50), default="created")  # created, analyzing, implementing, testing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Project configuration
    config = Column(JSON, default={})
    
    # Relationships
    tasks = relationship("Task", back_populates="project")
    debate_sessions = relationship("DebateSession", back_populates="project")
    agents = relationship("AgentInstance", back_populates="project")


class Task(Base):
    """Task model for tracking individual tasks within projects"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    task_type = Column(String(100))  # hive_debate, code_generation, testing, etc.
    status = Column(String(50), default="pending")  # pending, assigned, in_progress, completed, failed
    priority = Column(Integer, default=5)  # 1-10 scale
    
    # Task data
    input_data = Column(JSON, default={})
    output_data = Column(JSON, default={})
    task_metadata = Column(JSON, default={})
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    agent_assignments = relationship("AgentAssignment", back_populates="task")


class AgentInstance(Base):
    """Agent instance model for tracking active agents"""
    __tablename__ = "agent_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(Integer, ForeignKey("projects.id"))
    agent_type = Column(String(100))  # hive_collective, code_generation, testing, etc.
    status = Column(String(50), default="idle")  # idle, busy, error, offline
    
    # Agent configuration
    config = Column(JSON, default={})
    capabilities = Column(JSON, default=[])
    
    # Performance metrics
    tasks_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_completion_time = Column(Float, default=0.0)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="agents")
    assignments = relationship("AgentAssignment", back_populates="agent")


class AgentAssignment(Base):
    """Agent assignment model for tracking task assignments"""
    __tablename__ = "agent_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    agent_id = Column(Integer, ForeignKey("agent_instances.id"))
    status = Column(String(50), default="assigned")  # assigned, in_progress, completed, failed
    
    # Assignment data
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Results
    result_data = Column(JSON, default={})
    error_message = Column(Text, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="agent_assignments")
    agent = relationship("AgentInstance", back_populates="assignments")


class DebateSession(Base):
    """Debate session model for hive collective intelligence"""
    __tablename__ = "debate_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(Integer, ForeignKey("projects.id"))
    topic = Column(String(500), nullable=False)
    status = Column(String(50), default="created")  # created, in_progress, completed, failed
    
    # Debate configuration
    participants = Column(JSON, default=[])  # List of persona types
    debate_type = Column(String(100))  # requirements_analysis, architecture_design, etc.
    
    # Results
    consensus_reached = Column(Boolean, default=False)
    final_decision = Column(JSON, default={})
    confidence_score = Column(Float, default=0.0)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="debate_sessions")
    messages = relationship("DebateMessage", back_populates="session")


class DebateMessage(Base):
    """Debate message model for tracking debate conversations"""
    __tablename__ = "debate_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("debate_sessions.id"))
    persona_type = Column(String(100))  # architect, innovator, pragmatist, etc.
    message_type = Column(String(50))  # analysis, proposal, challenge, consensus
    content = Column(Text, nullable=False)
    
    # Message metadata
    confidence = Column(Float, default=0.0)
    reasoning = Column(Text)
    references = Column(JSON, default=[])
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("DebateSession", back_populates="messages")


class KnowledgeBase(Base):
    """Knowledge base model for continuous learning"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    category = Column(String(100))  # pattern, best_practice, failure_mode, etc.
    subcategory = Column(String(100))
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Knowledge metadata
    confidence_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    tags = Column(JSON, default=[])
    
    # Source information
    source_type = Column(String(100))  # project, feedback, external
    source_id = Column(String(100))
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)


class SystemMetrics(Base):
    """System metrics model for monitoring and analytics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50))  # counter, gauge, histogram
    
    # Metric metadata
    labels = Column(JSON, default={})
    description = Column(String(255))
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# Database utility functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)

