"""
Multi-Agent AI System Configuration Settings
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    url: str = Field(default="sqlite:///./multiagent.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration settings"""
    url: str = Field(default="redis://localhost:6379/0")
    max_connections: int = Field(default=20)
    
    class Config:
        env_prefix = "REDIS_"


class AIModelSettings(BaseSettings):
    """AI Model configuration settings"""
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)
    
    # Model preferences for different tasks
    hive_collective_model: str = Field(default="gpt-4-1106-preview")
    code_generation_model: str = Field(default="claude-3-opus-20240229")
    testing_model: str = Field(default="gpt-4-1106-preview")
    documentation_model: str = Field(default="gpt-4-1106-preview")
    
    # Model parameters
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=4000)
    
    class Config:
        env_prefix = "AI_"


class SecuritySettings(BaseSettings):
    """Security configuration settings"""
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    class Config:
        env_prefix = "SECURITY_"


class MonitoringSettings(BaseSettings):
    """Monitoring and logging configuration"""
    log_level: str = Field(default="INFO")
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=8000)
    
    class Config:
        env_prefix = "MONITORING_"


class SystemSettings(BaseSettings):
    """Main system configuration"""
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    
    # Zone configuration
    max_concurrent_agents: int = Field(default=10)
    task_timeout_seconds: int = Field(default=300)
    
    # Continuous learning settings
    enable_learning: bool = Field(default=True)
    learning_batch_size: int = Field(default=100)
    
    class Config:
        env_prefix = "SYSTEM_"


class Settings(BaseSettings):
    """Combined application settings"""
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    ai_models: AIModelSettings = AIModelSettings()
    security: SecuritySettings = SecuritySettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    system: SystemSettings = SystemSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


# Global settings instance
settings = Settings()

