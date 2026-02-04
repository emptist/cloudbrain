"""
Input Validation for CloudBrain

Provides input validation using pydantic for security and data integrity.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class MessageInput(BaseModel):
    """Validate message input"""
    
    ai_id: int = Field(..., ge=1, le=999, description="AI ID (1-999)")
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    message_type: str = Field(
        default="message",
        description="Message type"
    )
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @validator('message_type')
    def validate_message_type(cls, v):
        """Validate message type is one of the allowed types"""
        valid_types = ['message', 'question', 'response', 'insight', 'decision', 'suggestion']
        if v not in valid_types:
            raise ValueError(f'Invalid message type: {v}. Must be one of {valid_types}')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        """Validate content doesn't contain dangerous patterns"""
        # Check for SQL injection patterns
        sql_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'EXEC', 'UNION', 'SELECT', 'INSERT', 'UPDATE']
        v_upper = v.upper()
        for keyword in sql_keywords:
            if keyword in v_upper:
                raise ValueError(f'Content contains potentially dangerous SQL keyword: {keyword}')
        
        # Check for XSS patterns
        xss_patterns = ['<script', 'javascript:', 'onerror=', 'onload=', 'onclick=']
        v_lower = v.lower()
        for pattern in xss_patterns:
            if pattern in v_lower:
                raise ValueError(f'Content contains potentially dangerous XSS pattern: {pattern}')
        
        return v


class AIProfileInput(BaseModel):
    """Validate AI profile input"""
    
    id: int = Field(..., ge=1, le=999, description="AI ID (1-999)")
    name: str = Field(..., min_length=1, max_length=100, description="AI name")
    nickname: Optional[str] = Field(None, max_length=50, description="AI nickname")
    expertise: str = Field(..., min_length=1, max_length=200, description="AI expertise")
    version: str = Field(..., min_length=1, max_length=50, description="AI version")
    project: Optional[str] = Field(None, max_length=100, description="Project name")
    
    @validator('name', 'nickname', 'expertise', 'version', 'project')
    def sanitize_string(cls, v):
        """Sanitize string inputs"""
        if v is None:
            return v
        
        # Remove null bytes
        v = v.replace('\x00', '')
        
        # Trim whitespace
        v = v.strip()
        
        return v


class BrainStateInput(BaseModel):
    """Validate brain state input"""
    
    ai_id: int = Field(..., ge=1, le=999, description="AI ID (1-999)")
    task: str = Field(..., min_length=1, max_length=500, description="Current task")
    last_thought: Optional[str] = Field(None, max_length=1000, description="Last thought")
    last_insight: Optional[str] = Field(None, max_length=1000, description="Last insight")
    progress: Optional[Dict[str, Any]] = Field(default=None, description="Progress data")
    
    @validator('task', 'last_thought', 'last_insight')
    def sanitize_string(cls, v):
        """Sanitize string inputs"""
        if v is None:
            return v
        
        # Remove null bytes
        v = v.replace('\x00', '')
        
        # Trim whitespace
        v = v.strip()
        
        return v


class WebSocketAuthInput(BaseModel):
    """Validate WebSocket authentication input"""
    
    ai_id: int = Field(..., ge=1, le=999, description="AI ID (1-999)")
    auth_token: Optional[str] = Field(None, max_length=500, description="Authentication token")
    project: Optional[str] = Field(None, max_length=100, description="Project name")
    
    @validator('auth_token')
    def validate_token(cls, v):
        """Validate token format"""
        if v is None:
            return v
        
        # Token should be alphanumeric with some special chars
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Invalid token format')
        
        return v


def validate_message_input(data: dict) -> MessageInput:
    """
    Validate message input and return validated object
    
    Args:
        data: Raw message data
    
    Returns:
        Validated MessageInput object
    
    Raises:
        ValidationError: If validation fails
    """
    try:
        return MessageInput(**data)
    except Exception as e:
        from server.exceptions import ValidationError
        raise ValidationError(f"Message validation failed: {e}")


def validate_ai_profile_input(data: dict) -> AIProfileInput:
    """
    Validate AI profile input and return validated object
    
    Args:
        data: Raw profile data
    
    Returns:
        Validated AIProfileInput object
    
    Raises:
        ValidationError: If validation fails
    """
    try:
        return AIProfileInput(**data)
    except Exception as e:
        from server.exceptions import ValidationError
        raise ValidationError(f"Profile validation failed: {e}")
