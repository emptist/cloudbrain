"""
Custom Exceptions for CloudBrain

Provides specific exception types for better error handling and debugging.
"""


class CloudBrainException(Exception):
    """Base exception for CloudBrain errors"""
    pass


class DatabaseConnectionError(CloudBrainException):
    """Database connection failed"""
    pass


class DatabaseQueryError(CloudBrainException):
    """Database query execution failed"""
    pass


class WebSocketConnectionError(CloudBrainException):
    """WebSocket connection failed"""
    pass


class WebSocketMessageError(CloudBrainException):
    """WebSocket message handling failed"""
    pass


class AuthenticationError(CloudBrainException):
    """Authentication failed"""
    pass


class ValidationError(CloudBrainException):
    """Input validation failed"""
    pass


class RateLimitError(CloudBrainException):
    """Rate limit exceeded"""
    pass


class BrainStateError(CloudBrainException):
    """Brain state management failed"""
    pass


class ConfigurationError(CloudBrainException):
    """Configuration error"""
    pass


class AIServiceError(CloudBrainException):
    """AI service error"""
    pass


def handle_exception(logger, exception: Exception, context: str = ""):
    """
    Centralized exception handler with proper logging
    
    Args:
        logger: Logger instance
        exception: Exception to handle
        context: Additional context information
    """
    error_type = type(exception).__name__
    error_msg = str(exception)
    
    if context:
        logger.error(f"[{context}] {error_type}: {error_msg}", exc_info=True)
    else:
        logger.error(f"{error_type}: {error_msg}", exc_info=True)
    
    # Return structured error information
    return {
        'error_type': error_type,
        'error_message': error_msg,
        'context': context,
        'timestamp': datetime.now().isoformat()
    }
