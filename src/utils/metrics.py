"""
Metrics collection and monitoring utilities
"""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from core.database import SessionLocal, SystemMetrics

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Metrics collector for system monitoring"""
    
    def __init__(self):
        # Prometheus metrics
        self.project_counter = Counter('projects_total', 'Total number of projects', ['status'])
        self.task_counter = Counter('tasks_total', 'Total number of tasks', ['type', 'status'])
        self.agent_counter = Counter('agents_total', 'Total number of agents', ['type', 'status'])
        
        self.project_duration = Histogram('project_duration_seconds', 'Project completion time')
        self.task_duration = Histogram('task_duration_seconds', 'Task completion time', ['type'])
        self.debate_duration = Histogram('debate_duration_seconds', 'Debate session duration')
        
        self.active_projects = Gauge('active_projects', 'Number of active projects')
        self.active_agents = Gauge('active_agents', 'Number of active agents')
        self.system_health = Gauge('system_health', 'System health score (0-1)')
        
        self.metrics_server_port = 9090
        self.initialized = False
    
    async def initialize(self):
        """Initialize metrics collection"""
        try:
            # Start Prometheus metrics server
            start_http_server(self.metrics_server_port)
            logger.info(f"Metrics server started on port {self.metrics_server_port}")
            
            # Start background metrics collection
            asyncio.create_task(self._collect_system_metrics())
            
            self.initialized = True
            logger.info("Metrics collector initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics collector: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown metrics collection"""
        self.initialized = False
        logger.info("Metrics collector shutdown")
    
    def record_project_created(self):
        """Record project creation"""
        self.project_counter.labels(status='created').inc()
    
    def record_project_completed(self, duration_seconds: float):
        """Record project completion"""
        self.project_counter.labels(status='completed').inc()
        self.project_duration.observe(duration_seconds)
    
    def record_project_failed(self):
        """Record project failure"""
        self.project_counter.labels(status='failed').inc()
    
    def record_task_created(self, task_type: str):
        """Record task creation"""
        self.task_counter.labels(type=task_type, status='created').inc()
    
    def record_task_completed(self, task_type: str, duration_seconds: float):
        """Record task completion"""
        self.task_counter.labels(type=task_type, status='completed').inc()
        self.task_duration.labels(type=task_type).observe(duration_seconds)
    
    def record_task_failed(self, task_type: str):
        """Record task failure"""
        self.task_counter.labels(type=task_type, status='failed').inc()
    
    def record_agent_started(self, agent_type: str):
        """Record agent start"""
        self.agent_counter.labels(type=agent_type, status='started').inc()
    
    def record_agent_stopped(self, agent_type: str):
        """Record agent stop"""
        self.agent_counter.labels(type=agent_type, status='stopped').inc()
    
    def record_debate_completed(self, duration_seconds: float):
        """Record debate session completion"""
        self.debate_duration.observe(duration_seconds)
    
    def update_active_projects(self, count: int):
        """Update active projects gauge"""
        self.active_projects.set(count)
    
    def update_active_agents(self, count: int):
        """Update active agents gauge"""
        self.active_agents.set(count)
    
    def update_system_health(self, health_score: float):
        """Update system health gauge"""
        self.system_health.set(health_score)
    
    async def _collect_system_metrics(self):
        """Background task to collect system metrics"""
        while self.initialized:
            try:
                await self._update_system_metrics()
                await asyncio.sleep(30)  # Collect metrics every 30 seconds
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _update_system_metrics(self):
        """Update system-wide metrics"""
        try:
            db = SessionLocal()
            
            # Count active projects
            from core.database import Project
            active_projects_count = db.query(Project).filter(
                Project.status.in_(['created', 'analyzing', 'implementing', 'testing'])
            ).count()
            self.update_active_projects(active_projects_count)
            
            # Count active agents
            from core.database import AgentInstance
            active_agents_count = db.query(AgentInstance).filter(
                AgentInstance.status == 'busy'
            ).count()
            self.update_active_agents(active_agents_count)
            
            # Calculate system health score
            health_score = await self._calculate_system_health()
            self.update_system_health(health_score)
            
            # Store metrics in database
            await self._store_metrics_in_db(db, {
                'active_projects': active_projects_count,
                'active_agents': active_agents_count,
                'system_health': health_score
            })
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    async def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""
        try:
            # Simple health calculation based on various factors
            health_factors = []
            
            # Check if all zones are responsive (placeholder)
            health_factors.append(1.0)  # Assume healthy for now
            
            # Check error rates (placeholder)
            health_factors.append(0.9)  # Assume 90% healthy
            
            # Check resource utilization (placeholder)
            health_factors.append(0.95)  # Assume 95% healthy
            
            # Calculate average health score
            return sum(health_factors) / len(health_factors) if health_factors else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating system health: {e}")
            return 0.0
    
    async def _store_metrics_in_db(self, db, metrics: Dict[str, Any]):
        """Store metrics in database for historical tracking"""
        try:
            timestamp = datetime.utcnow()
            
            for metric_name, metric_value in metrics.items():
                metric = SystemMetrics(
                    metric_name=metric_name,
                    metric_value=float(metric_value),
                    metric_type='gauge',
                    timestamp=timestamp
                )
                db.add(metric)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error storing metrics in database: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        return {
            "active_projects": self.active_projects._value._value,
            "active_agents": self.active_agents._value._value,
            "system_health": self.system_health._value._value,
            "metrics_server_port": self.metrics_server_port,
            "initialized": self.initialized
        }

