"""
Environment Configuration for CloudBrain

Provides centralized environment variable configuration for flexible deployment.
"""

import os
from typing import Optional


class CloudBrainConfig:
    """CloudBrain environment configuration"""
    
    # Server Configuration
    SERVER_HOST: str = os.getenv('CLOUDBRAIN_HOST', '127.0.0.1')
    SERVER_PORT: int = int(os.getenv('CLOUDBRAIN_PORT', '8768'))
    SERVER_URL: str = f"ws://{SERVER_HOST}:{SERVER_PORT}"
    
    # Database Configuration
    DB_TYPE: str = os.getenv('DB_TYPE', 'postgres')
    
    # SQLite Configuration
    SQLITE_DB_PATH: str = os.getenv('SQLITE_DB_PATH', 'server/ai_db/cloudbrain.db')
    
    # PostgreSQL Configuration
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT: str = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB', 'cloudbrain')
    POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'jk')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', '')
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('CLOUDBRAIN_LOG_LEVEL', 'INFO')
    LOG_DIR: str = os.getenv('CLOUDBRAIN_LOG_DIR', 'logs')
    LOG_FILE: Optional[str] = os.getenv('CLOUDBRAIN_LOG_FILE')
    
    # WebSocket Configuration
    WS_TIMEOUT: int = int(os.getenv('CLOUDBRAIN_WS_TIMEOUT', '30'))
    WS_MAX_SIZE: int = int(os.getenv('CLOUDBRAIN_WS_MAX_SIZE', '10485760'))
    
    # Security Configuration
    ENABLE_AUTH: bool = os.getenv('CLOUDBRAIN_ENABLE_AUTH', 'false').lower() == 'true'
    AUTH_SECRET: Optional[str] = os.getenv('CLOUDBRAIN_AUTH_SECRET')
    
    # Rate Limiting Configuration
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv('CLOUDBRAIN_RATE_LIMIT_MAX', '100'))
    RATE_LIMIT_WINDOW: int = int(os.getenv('CLOUDBRAIN_RATE_LIMIT_WINDOW', '60'))
    
    # Heartbeat & Connection Management Configuration
    HEARTBEAT_CHECK_INTERVAL: int = int(os.getenv('CLOUDBRAIN_HEARTBEAT_INTERVAL', '60'))
    STALE_TIMEOUT_MINUTES: int = int(os.getenv('CLOUDBRAIN_STALE_TIMEOUT', '15'))
    GRACE_PERIOD_MINUTES: int = int(os.getenv('CLOUDBRAIN_GRACE_PERIOD', '2'))
    MAX_SLEEP_TIME_MINUTES: int = int(os.getenv('CLOUDBRAIN_MAX_SLEEP_TIME', '60'))
    
    @classmethod
    def get_server_url(cls) -> str:
        """Get WebSocket server URL"""
        return f"ws://{cls.SERVER_HOST}:{cls.SERVER_PORT}"
    
    @classmethod
    def get_postgres_url(cls) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{cls.POSTGRES_USER}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("=" * 70)
        print("🔧 CloudBrain Configuration")
        print("=" * 70)
        print()
        print("📋 SERVER")
        print("-" * 70)
        print(f"  Host:     {cls.SERVER_HOST}")
        print(f"  Port:     {cls.SERVER_PORT}")
        print(f"  URL:      {cls.get_server_url()}")
        print()
        print("💾 DATABASE")
        print("-" * 70)
        print(f"  Type:     {cls.DB_TYPE}")
        if cls.DB_TYPE == 'postgres':
            print(f"  Host:     {cls.POSTGRES_HOST}")
            print(f"  Port:     {cls.POSTGRES_PORT}")
            print(f"  Database: {cls.POSTGRES_DB}")
            print(f"  User:     {cls.POSTGRES_USER}")
        else:
            print(f"  Path:     {cls.SQLITE_DB_PATH}")
        print()
        print("📝 LOGGING")
        print("-" * 70)
        print(f"  Level:    {cls.LOG_LEVEL}")
        print(f"  Directory: {cls.LOG_DIR}")
        if cls.LOG_FILE:
            print(f"  File:     {cls.LOG_FILE}")
        print()
        print("🔒 SECURITY")
        print("-" * 70)
        print(f"  Auth:     {'Enabled' if cls.ENABLE_AUTH else 'Disabled'}")
        print(f"  Rate Limit: {cls.RATE_LIMIT_MAX_REQUESTS} requests / {cls.RATE_LIMIT_WINDOW}s")
        print()
        print("💓 HEARTBEAT & CONNECTION MANAGEMENT")
        print("-" * 70)
        print(f"  Check Interval:  {cls.HEARTBEAT_CHECK_INTERVAL}s")
        print(f"  Stale Timeout:    {cls.STALE_TIMEOUT_MINUTES} minutes")
        print(f"  Grace Period:     {cls.GRACE_PERIOD_MINUTES} minutes")
        print(f"  Max Sleep Time:   {cls.MAX_SLEEP_TIME_MINUTES} minutes")
        print()
        print("=" * 70)
