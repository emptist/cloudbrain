#!/usr/bin/env python3
"""
CloudBrain Token Management Tool
Generate and manage authentication tokens for AI agents
"""

import secrets
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from db_config import get_db_connection, is_postgres, get_cursor


class TokenManager:
    """Manage authentication tokens for CloudBrain"""
    
    def __init__(self, db_path: str = 'ai_db/cloudbrain.db'):
        self.db_path = db_path
        self._ensure_tables_exist()
    
    def _get_connection(self):
        """Get database connection"""
        conn = get_db_connection()
        return conn
    
    def _ensure_tables_exist(self):
        """Ensure authorization tables exist"""
        conn = self._get_connection()
        cursor = get_cursor()
        
        # Read and execute PostgreSQL schema
        schema_path = Path(__file__).parent / 'server_authorization_schema_postgres.sql'
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            for statement in schema_sql.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        if 'already exists' not in str(e) and 'duplicate' not in str(e).lower():
                            print(f"⚠️  Error executing schema: {e}")
        
        conn.commit()
        conn.close()
    
    def generate_token(self, ai_id: int, expires_days: int = 30, description: str = "") -> Dict:
        """
        Generate a new authentication token for an AI
        
        Args:
            ai_id: AI ID to generate token for
            expires_days: Number of days until token expires (default: 30)
            description: Optional description for the token
        
        Returns:
            Dictionary with token info or error
        """
        try:
            # Check if AI exists
            conn = self._get_connection()
            cursor = get_cursor()
            
            cursor.execute("SELECT id, name FROM ai_profiles WHERE id = %s", (ai_id,))
            ai_profile = cursor.fetchone()
            
            if not ai_profile:
                conn.close()
                return {
                    'success': False,
                    'error': f'AI {ai_id} not found'
                }
            
            # Generate secure random token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            token_prefix = f"sk_live_{token[:8]}"
            
            # Calculate expiration
            expires_at = datetime.now() + timedelta(days=expires_days)
            
            # Deactivate old tokens for this AI
            cursor.execute(
                "UPDATE ai_auth_tokens SET is_active = FALSE WHERE ai_id = %s",
                (ai_id,)
            )
            
            # Insert new token
            cursor.execute("""
                INSERT INTO ai_auth_tokens (ai_id, token_hash, token_prefix, expires_at, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (ai_id, token_hash, token_prefix, expires_at.isoformat(), description))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Token generated for AI {ai_id} ({ai_profile['name']})")
            print(f"   Token: {token}")
            print(f"   Prefix: {token_prefix}")
            print(f"   Expires: {expires_at.isoformat()}")
            print(f"   Description: {description or 'No description'}")
            
            return {
                'success': True,
                'token': token,
                'token_prefix': token_prefix,
                'token_hash': token_hash,
                'ai_id': ai_id,
                'ai_name': ai_profile['name'],
                'expires_at': expires_at.isoformat(),
                'description': description
            }
            
        except Exception as e:
            print(f"❌ Error generating token: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_token(self, token: str) -> Dict:
        """
        Validate an authentication token
        
        Args:
            token: Token to validate
        
        Returns:
            Dictionary with validation result
        """
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            conn = self._get_connection()
            cursor = get_cursor()
            
            cursor.execute("""
                SELECT t.*, p.name as ai_name, p.expertise
                FROM ai_auth_tokens t
                JOIN ai_profiles p ON t.ai_id = p.id
                WHERE t.token_hash = %s AND t.is_active = TRUE
            """, (token_hash,))
            
            token_record = cursor.fetchone()
            
            if not token_record:
                conn.close()
                return {
                    'valid': False,
                    'error': 'Invalid or expired token'
                }
            
            # Check expiration
            expires_at = datetime.fromisoformat(token_record['expires_at'])
            if datetime.now() > expires_at:
                conn.close()
                return {
                    'valid': False,
                    'error': 'Token has expired'
                }
            
            # Update last used timestamp
            cursor.execute(
                "UPDATE ai_auth_tokens SET last_used_at = %s WHERE id = %s",
                (datetime.now().isoformat(), token_record['id'])
            )
            
            conn.commit()
            conn.close()
            
            return {
                'valid': True,
                'ai_id': token_record['ai_id'],
                'ai_name': token_record['ai_name'],
                'expertise': token_record['expertise'],
                'token_prefix': token_record['token_prefix'],
                'expires_at': token_record['expires_at']
            }
            
        except Exception as e:
            print(f"❌ Error validating token: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def revoke_token(self, token_prefix: str) -> Dict:
        """
        Revoke an authentication token
        
        Args:
            token_prefix: Token prefix to revoke (e.g., "sk_live_abc12345")
        
        Returns:
            Dictionary with revocation result
        """
        try:
            conn = self._get_connection()
            cursor = get_cursor()
            
            cursor.execute("""
                UPDATE ai_auth_tokens
                SET is_active = FALSE
                WHERE token_prefix = %s
            """, (token_prefix,))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_affected > 0:
                print(f"✅ Token {token_prefix} revoked")
                return {
                    'success': True,
                    'revoked': True
                }
            else:
                print(f"⚠️  Token {token_prefix} not found")
                return {
                    'success': False,
                    'error': 'Token not found'
                }
            
        except Exception as e:
            print(f"❌ Error revoking token: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_tokens(self, ai_id: Optional[int] = None) -> List[Dict]:
        """
        List all tokens or tokens for a specific AI
        
        Args:
            ai_id: Optional AI ID to filter by
        
        Returns:
            List of token information
        """
        try:
            conn = self._get_connection()
            cursor = get_cursor()
            
            if ai_id:
                cursor.execute("""
                    SELECT t.*, p.name as ai_name
                    FROM ai_auth_tokens t
                    JOIN ai_profiles p ON t.ai_id = p.id
                    WHERE t.ai_id = %s
                    ORDER BY t.created_at DESC
                """, (ai_id,))
            else:
                cursor.execute("""
                    SELECT t.*, p.name as ai_name
                    FROM ai_auth_tokens t
                    JOIN ai_profiles p ON t.ai_id = p.id
                    ORDER BY t.created_at DESC
                """)
            
            tokens = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return tokens
            
        except Exception as e:
            print(f"❌ Error listing tokens: {e}")
            return []
    
    def grant_project_permission(self, ai_id: int, project: str, role: str = 'member', granted_by: int = None) -> Dict:
        """
        Grant project permission to an AI
        
        Args:
            ai_id: AI ID to grant permission to
            project: Project name
            role: Role (admin, member, viewer, contributor)
            granted_by: AI ID of admin granting permission
        
        Returns:
            Dictionary with grant result
        """
        try:
            conn = self._get_connection()
            cursor = get_cursor()
            
            # Check if AI exists
            cursor.execute("SELECT name FROM ai_profiles WHERE id = %s", (ai_id,))
            ai_profile = cursor.fetchone()
            
            if not ai_profile:
                conn.close()
                return {
                    'success': False,
                    'error': f'AI {ai_id} not found'
                }
            
            # Check if permission already exists
            cursor.execute("""
                SELECT id FROM ai_project_permissions
                WHERE ai_id = %s AND project = %s
            """, (ai_id, project))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing permission
                cursor.execute("""
                    UPDATE ai_project_permissions
                    SET role = %s, granted_by = %s
                    WHERE ai_id = %s AND project = %s
                """, (role, granted_by, ai_id, project))
                print(f"✅ Updated permission for AI {ai_id} on project {project}: {role}")
            else:
                # Insert new permission
                cursor.execute("""
                    INSERT INTO ai_project_permissions (ai_id, project, role, granted_by)
                    VALUES (%s, %s, %s, %s)
                """, (ai_id, project, role, granted_by))
                print(f"✅ Granted permission for AI {ai_id} on project {project}: {role}")
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'ai_id': ai_id,
                'project': project,
                'role': role
            }
            
        except Exception as e:
            print(f"❌ Error granting permission: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def revoke_project_permission(self, ai_id: int, project: str) -> Dict:
        """
        Revoke project permission from an AI
        
        Args:
            ai_id: AI ID to revoke permission from
            project: Project name
        
        Returns:
            Dictionary with revocation result
        """
        try:
            conn = self._get_connection()
            cursor = get_cursor()
            
            cursor.execute("""
                DELETE FROM ai_project_permissions
                WHERE ai_id = %s AND project = %s
            """, (ai_id, project))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_affected > 0:
                print(f"✅ Revoked permission for AI {ai_id} on project {project}")
                return {
                    'success': True,
                    'revoked': True
                }
            else:
                print(f"⚠️  No permission found for AI {ai_id} on project {project}")
                return {
                    'success': False,
                    'error': 'Permission not found'
                }
            
        except Exception as e:
            print(f"❌ Error revoking permission: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_permissions(self, ai_id: Optional[int] = None, project: Optional[str] = None) -> List[Dict]:
        """
        List project permissions
        
        Args:
            ai_id: Optional AI ID to filter by
            project: Optional project name to filter by
        
        Returns:
            List of permission information
        """
        try:
            conn = self._get_connection()
            cursor = get_cursor()
            
            if ai_id and project:
                cursor.execute("""
                    SELECT pp.*, p.name as ai_name
                    FROM ai_project_permissions pp
                    JOIN ai_profiles p ON pp.ai_id = p.id
                    WHERE pp.ai_id = %s AND pp.project = %s
                    ORDER BY pp.created_at DESC
                """, (ai_id, project))
            elif ai_id:
                cursor.execute("""
                    SELECT pp.*, p.name as ai_name
                    FROM ai_project_permissions pp
                    JOIN ai_profiles p ON pp.ai_id = p.id
                    WHERE pp.ai_id = %s
                    ORDER BY pp.created_at DESC
                """, (ai_id,))
            elif project:
                cursor.execute("""
                    SELECT pp.*, p.name as ai_name
                    FROM ai_project_permissions pp
                    JOIN ai_profiles p ON pp.ai_id = p.id
                    WHERE pp.project = %s
                    ORDER BY pp.created_at DESC
                """, (project,))
            else:
                cursor.execute("""
                    SELECT pp.*, p.name as ai_name
                    FROM ai_project_permissions pp
                    JOIN ai_profiles p ON pp.ai_id = p.id
                    ORDER BY pp.created_at DESC
                """)
            
            permissions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return permissions
            
        except Exception as e:
            print(f"❌ Error listing permissions: {e}")
            return []
    
    def check_project_permission(self, ai_id: int, project: str) -> Dict:
        """
        Check if an AI has permission for a project
        
        Args:
            ai_id: AI ID to check
            project: Project name to check
        
        Returns:
            Dictionary with permission status and role
        """
        try:
            conn = self._get_connection()
            cursor = get_cursor()
            
            cursor.execute("""
                SELECT role, created_at
                FROM ai_project_permissions
                WHERE ai_id = %s AND project = %s
            """, (ai_id, project))
            
            permission = cursor.fetchone()
            conn.close()
            
            if permission:
                return {
                    'has_permission': True,
                    'role': permission['role'],
                    'granted_at': permission['created_at']
                }
            else:
                return {
                    'has_permission': False,
                    'role': None
                }
            
        except Exception as e:
            print(f"❌ Error checking project permission: {e}")
            return {
                'has_permission': False,
                'role': None,
                'error': str(e)
            }
    
    def log_authentication(self, ai_id: int, project: Optional[str] = None, 
                          success: bool = True, details: str = "") -> Dict:
        """
        Log authentication attempt to audit table
        
        Args:
            ai_id: AI ID attempting authentication
            project: Project name (optional)
            success: Whether authentication succeeded
            details: Additional details about the attempt
        
        Returns:
            Dictionary with log result
        """
        try:
            conn = self._get_connection()
            cursor = get_cursor()
            
            # Get AI name for logging
            cursor.execute("SELECT name FROM ai_profiles WHERE id = %s", (ai_id,))
            ai_profile = cursor.fetchone()
            ai_name = ai_profile['name'] if ai_profile else 'Unknown'
            
            cursor.execute("""
                INSERT INTO ai_auth_audit (ai_id, ai_name, project, success, details, created_at)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (ai_id, ai_name, project, success, details))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'ai_id': ai_id,
                'project': project,
                'success': success
            }
            
        except Exception as e:
            print(f"❌ Error logging authentication [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Example usage of token manager"""
    manager = TokenManager()
    
    print("=" * 70)
    print("🔐 CloudBrain Token Manager")
    print("=" * 70)
    print()
    
    # Example: Generate token for AI 19 (GLM-4.7)
    print("📝 Example 1: Generate token for AI 19")
    result = manager.generate_token(
        ai_id=19,
        expires_days=30,
        description="CloudBrain development token"
    )
    print()
    
    # Example: Validate token
    if result['success']:
        print("📝 Example 2: Validate token")
        validation = manager.validate_token(result['token'])
        print(f"   Valid: {validation['valid']}")
        print()
    
    # Example: Grant project permission
    print("📝 Example 3: Grant project permission")
    manager.grant_project_permission(
        ai_id=19,
        project='cloudbrain',
        role='admin',
        granted_by=1
    )
    print()
    
    # Example: List all tokens
    print("📝 Example 4: List all tokens")
    tokens = manager.list_tokens()
    for token in tokens[:5]:
        print(f"   {token['ai_name']}: {token['token_prefix']} (expires: {token['expires_at']})")
    print()


if __name__ == "__main__":
    main()
