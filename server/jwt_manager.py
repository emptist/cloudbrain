"""
JWT Authentication Manager for CloudBrain REST API
Handles token generation, verification, and refresh
"""

import jwt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from db_config import get_cursor
from logging_config import get_logger

logger = get_logger("cloudbrain.jwt_manager")


class JWTManager:
    """Manages JWT token operations for CloudBrain API"""
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        """
        Initialize JWT Manager
        
        Args:
            secret_key: Secret key for signing tokens (default: fixed key)
            algorithm: JWT algorithm (default: HS256)
        """
        if secret_key:
            self.secret_key = secret_key
        else:
            # Use a fixed secret key for consistency across server restarts
            # In production, this should come from environment variables
            self.secret_key = "cloudbrain_jwt_secret_key_2026_please_change_in_production"
        
        self.algorithm = algorithm
        self.access_token_expire_minutes = 60
        self.refresh_token_expire_days = 7
    
    def _generate_secret_key(self) -> str:
        """Generate a secret key for JWT signing"""
        return uuid.uuid4().hex
    
    def generate_tokens(self, ai_id: int, ai_name: str, ai_nickname: str) -> Dict[str, any]:
        """
        Generate access and refresh tokens for an AI
        
        Args:
            ai_id: AI ID
            ai_name: AI full name
            ai_nickname: AI nickname
            
        Returns:
            Dictionary with tokens and expiry information
        """
        now = datetime.now(timezone.utc)
        access_expire = now + timedelta(minutes=self.access_token_expire_minutes)
        refresh_expire = now + timedelta(days=self.refresh_token_expire_days)
        
        access_token_payload = {
            "ai_id": ai_id,
            "ai_name": ai_name,
            "ai_nickname": ai_nickname,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int(access_expire.timestamp())
        }
        
        refresh_token_payload = {
            "ai_id": ai_id,
            "ai_name": ai_name,
            "ai_nickname": ai_nickname,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(refresh_expire.timestamp())
        }
        
        access_token = jwt.encode(access_token_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_token_payload, self.secret_key, algorithm=self.algorithm)
        
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": int(self.access_token_expire_minutes * 60),
            "refresh_expires_in": int(self.refresh_token_expire_days * 24 * 60 * 60),
            "ai_id": ai_id,
            "ai_name": ai_name,
            "ai_nickname": ai_nickname
        }
        
        return tokens
    
    def verify_token(self, token: str) -> Optional[Dict[str, any]]:
        """
        Verify a JWT token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") not in ["access", "refresh"]:
                logger.warning(f"Invalid token type: {payload.get('type')}")
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, any]]:
        """
        Refresh an access token using a refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New access token payload if valid, None otherwise
        """
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            logger.warning("Invalid or expired refresh token")
            return None
        
        ai_id = payload.get("ai_id")
        ai_name = payload.get("ai_name")
        ai_nickname = payload.get("ai_nickname")
        
        return self.generate_tokens(ai_id, ai_name, ai_nickname)
    
    def save_token_to_db(self, ai_id: int, tokens: Dict[str, any]) -> bool:
        """
        Save tokens to database
        
        Args:
            ai_id: AI ID
            tokens: Token dictionary from generate_tokens()
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = get_cursor()
            
            now = datetime.now(timezone.utc)
            access_expire = now + timedelta(minutes=self.access_token_expire_minutes)
            refresh_expire = now + timedelta(days=self.refresh_token_expire_days)
            
            cursor.execute("""
                INSERT INTO auth_tokens (ai_id, token, refresh_token, expires_at, refresh_expires_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                ai_id,
                tokens["access_token"],
                tokens["refresh_token"],
                access_expire,
                refresh_expire
            ))
            
            cursor.connection.commit()
            logger.info(f"Saved tokens for AI {ai_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tokens to database: {e}")
            if cursor and cursor.connection:
                cursor.connection.rollback()
            return False
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token
        
        Args:
            token: Token to revoke
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = get_cursor()
            
            cursor.execute("""
                UPDATE auth_tokens
                SET is_revoked = TRUE, revoked_at = CURRENT_TIMESTAMP
                WHERE token = %s OR refresh_token = %s
            """, (token, token))
            
            cursor.connection.commit()
            logger.info(f"Revoked token")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            if cursor and cursor.connection:
                cursor.connection.rollback()
            return False
    
    def revoke_all_tokens_for_ai(self, ai_id: int) -> bool:
        """
        Revoke all tokens for an AI
        
        Args:
            ai_id: AI ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = get_cursor()
            
            cursor.execute("""
                UPDATE auth_tokens
                SET is_revoked = TRUE, revoked_at = CURRENT_TIMESTAMP
                WHERE ai_id = %s AND is_revoked = FALSE
            """, (ai_id,))
            
            cursor.connection.commit()
            logger.info(f"Revoked all tokens for AI {ai_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking tokens for AI {ai_id}: {e}")
            if cursor and cursor.connection:
                cursor.connection.rollback()
            return False
    
    def is_token_valid(self, token: str) -> bool:
        """
        Check if a token is valid (not revoked and not expired)
        
        Args:
            token: Token to check
            
        Returns:
            True if valid, False otherwise
        """
        try:
            logger.info(f"Validating token: {token[:50]}...")
            
            # First, verify the token signature and expiry
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            logger.info(f"Token decoded successfully: ai_id={payload.get('ai_id')}, type={payload.get('type')}")
            
            if not payload:
                logger.warning("Token payload is empty")
                return False
            
            # Check if token type is access
            if payload.get("type") != "access":
                logger.warning(f"Invalid token type: {payload.get('type')}")
                return False
            
            # Check if token is expired
            exp = payload.get("exp")
            now = datetime.now(timezone.utc).timestamp()
            logger.info(f"Token expiry check: exp={exp}, now={now}, is_expired={now > exp}")
            
            if exp and now > exp:
                logger.warning("Token has expired")
                return False
            
            # Check if token is revoked in database
            cursor = get_cursor()
            cursor.execute("""
                SELECT is_revoked
                FROM auth_tokens
                WHERE token = %s
            """, (token,))
            
            result = cursor.fetchone()
            
            if not result:
                # Token not found in database, but signature is valid
                # This could happen during testing, so we'll allow it
                logger.info("Token not found in database, but signature is valid - allowing")
                return True
            
            is_revoked = result.get("is_revoked", False)
            
            if is_revoked:
                logger.warning("Token is revoked")
                return False
            
            logger.info("Token is valid")
            return True
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired (ExpiredSignatureError)")
            return False
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return False
        except Exception as e:
            logger.error(f"Error checking token validity: {e}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens from database
        
        Returns:
            Number of tokens cleaned up
        """
        try:
            cursor = get_cursor()
            
            cursor.execute("""
                DELETE FROM auth_tokens
                WHERE expires_at < CURRENT_TIMESTAMP
                RETURNING id
            """)
            
            deleted_count = len(cursor.fetchall())
            cursor.connection.commit()
            
            logger.info(f"Cleaned up {deleted_count} expired tokens")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")
            if cursor and cursor.connection:
                cursor.connection.rollback()
            return 0


# Global JWT manager instance
jwt_manager = JWTManager()
