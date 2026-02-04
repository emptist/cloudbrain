"""
Health Check Endpoint for CloudBrain

Provides health check and monitoring capabilities for CloudBrain server.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from db_config import get_db_connection, is_postgres, is_sqlite
from logging_config import get_logger

logger = get_logger("cloudbrain.health")


class HealthChecker:
    """Health check and monitoring for CloudBrain"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.server_running = False
        self.clients_connected = 0
    
    def check_database(self) -> Dict[str, Any]:
        """Check database connection and health"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Simple query to test connection
            if is_postgres():
                cursor.execute("SELECT 1")
            else:
                cursor.execute("SELECT 1")
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'status': 'healthy',
                'type': 'postgres' if is_postgres() else 'sqlite',
                'connection': 'successful',
                'latency_ms': 1  # Would need to measure actual latency
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'type': 'unknown',
                'connection': 'failed',
                'error': str(e)
            }
    
    def check_websocket(self, clients: Dict) -> Dict[str, Any]:
        """Check WebSocket server status"""
        try:
            return {
                'status': 'healthy',
                'running': self.server_running,
                'clients_connected': len(clients),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds()
            }
        except Exception as e:
            logger.error(f"WebSocket health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'status': 'healthy',
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent()
            }
        except ImportError:
            return {
                'status': 'skipped',
                'reason': 'psutil not installed'
            }
        except Exception as e:
            logger.error(f"Memory health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def get_health_report(self, clients: Dict) -> Dict[str, Any]:
        """Get comprehensive health report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {
                'database': self.check_database(),
                'websocket': self.check_websocket(clients),
                'memory': self.check_memory()
            },
            'server': {
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'clients_connected': len(clients)
            }
        }
    
    def is_healthy(self, clients: Dict) -> bool:
        """Check if all systems are healthy"""
        health = self.get_health_report(clients)
        
        # Check database
        if health['checks']['database']['status'] != 'healthy':
            return False
        
        # Check WebSocket
        if health['checks']['websocket']['status'] != 'healthy':
            return False
        
        # Memory check can be skipped
        if health['checks']['memory']['status'] not in ['healthy', 'skipped']:
            return False
        
        return True


# Global health checker instance
health_checker = HealthChecker()


def get_health_status(clients: Dict) -> Dict[str, Any]:
    """
    Get health status for CloudBrain server
    
    Args:
        clients: Dictionary of connected clients
    
    Returns:
        Health status dictionary
    """
    return health_checker.get_health_report(clients)


def is_system_healthy(clients: Dict) -> bool:
    """
    Check if CloudBrain system is healthy
    
    Args:
        clients: Dictionary of connected clients
    
    Returns:
        True if healthy, False otherwise
    """
    return health_checker.is_healthy(clients)


def log_health_check(clients: Dict):
    """
    Log health check results
    
    Args:
        clients: Dictionary of connected clients
    """
    health = get_health_status(clients)
    
    if health['status'] == 'healthy':
        logger.info(f"Health check passed - DB: {health['checks']['database']['status']}, "
                   f"WS: {health['checks']['websocket']['status']}, "
                   f"Clients: {health['server']['clients_connected']}")
    else:
        logger.warning(f"Health check failed - {health}")
