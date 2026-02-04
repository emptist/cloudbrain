#!/usr/bin/env python3
"""
CloudBrain Client Logging Configuration

Centralized logging configuration for CloudBrain client.
Provides consistent logging format and handlers across the project.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(
    name: str = "cloudbrain.client",
    level: int = logging.INFO,
    log_file: str = None,
    log_dir: str = None
) -> logging.Logger:
    """
    Setup logging for CloudBrain client components.
    
    Args:
        name: Logger name (default: "cloudbrain.client")
        level: Logging level (default: logging.INFO)
        log_file: Optional log file name (default: None)
        log_dir: Optional log directory (default: "logs/")
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file or log_dir:
        if log_dir is None:
            log_dir = "logs"
        
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        if log_file is None:
            log_file = f"cloudbrain_client_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_path / log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "cloudbrain.client") -> logging.Logger:
    """
    Get an existing logger or create a new one.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_log_level(logger: logging.Logger, level: int):
    """
    Set logging level for a logger.
    
    Args:
        logger: Logger instance
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
