"""
CloudBrain REST API Server
Implements all Phase 1 API endpoints (22 endpoints)
"""

from aiohttp import web
import json
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from jwt_manager import jwt_manager
from db_config import get_cursor
from logging_config import get_logger

logger = get_logger("cloudbrain.rest_api")


def serialize_datetime(obj):
    """Helper function to serialize datetime objects to ISO format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not JSON serializable")


def json_response(data: dict, status: int = 200):
    """Helper function to create JSON response with datetime serialization"""
    json_str = json.dumps(data, default=serialize_datetime)
    return web.Response(text=json_str, content_type='application/json', status=status)


class CloudBrainRestAPI:
    """CloudBrain REST API Server"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.setup_middleware()
    
    def setup_middleware(self):
        """Setup middleware for request handling"""
        self.app.middlewares.append(self.auth_middleware)
        self.app.middlewares.append(self.error_middleware)
        self.app.middlewares.append(self.rate_limit_middleware)
    
    @web.middleware
    async def auth_middleware(self, request: web.Request, handler):
        """Authentication middleware for protected routes"""
        if request.path.startswith('/api/v1/auth'):
            return await handler(request)
        
        auth_header = request.headers.get('Authorization', '')
        
        logger.info(f"Auth header: {auth_header[:50]}..." if auth_header else "No auth header")
        
        if not auth_header.startswith('Bearer '):
            return json_response({
                "success": False,
                "error": "Missing or invalid Authorization header"
            }, status=401)
        
        token = auth_header[7:]
        logger.info(f"Token: {token[:50]}...")
        
        if not jwt_manager.is_token_valid(token):
            logger.warning(f"Token validation failed for: {token[:50]}...")
            return json_response({
                "success": False,
                "error": "Invalid or expired token"
            }, status=401)
        
        payload = jwt_manager.verify_token(token)
        if not payload:
            return json_response({
                "success": False,
                "error": "Invalid token"
            }, status=401)
        
        request['ai_id'] = payload.get('ai_id')
        request['ai_name'] = payload.get('ai_name')
        request['ai_nickname'] = payload.get('ai_nickname')
        
        logger.info(f"Authenticated: AI {request['ai_id']} ({request['ai_name']})")
        return await handler(request)
    
    @web.middleware
    async def error_middleware(self, request: web.Request, handler):
        """Error handling middleware"""
        try:
            return await handler(request)
        except web.HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error handling request {request.path}: {e}")
            return json_response({
                "success": False,
                "error": "Internal server error"
            }, status=500)
    
    @web.middleware
    async def rate_limit_middleware(self, request: web.Request, handler):
        """Rate limiting middleware"""
        ai_id = request.get('ai_id', 'anonymous')
        
        cursor = get_cursor()
        cursor.execute("""
            SELECT COUNT(*) as request_count
            FROM api_requests
            WHERE ai_id = %s
            AND created_at > CURRENT_TIMESTAMP - INTERVAL '1 minute'
        """, (str(ai_id),))
        
        result = cursor.fetchone()
        request_count = result.get('request_count', 0) if result else 0
        
        if request_count > 100:
            return json_response({
                "success": False,
                "error": "Rate limit exceeded",
                "retry_after": 60
            }, status=429)
        
        cursor.execute("""
            INSERT INTO api_requests (ai_id, endpoint, method)
            VALUES (%s, %s, %s)
        """, (str(ai_id), request.path, request.method))
        cursor.connection.commit()
        
        return await handler(request)
    
    def setup_routes(self):
        """Setup all API routes"""
        
        # Authentication APIs
        self.app.router.add_post('/api/v1/auth/login', self.login)
        self.app.router.add_post('/api/v1/auth/logout', self.logout)
        self.app.router.add_post('/api/v1/auth/refresh', self.refresh_token)
        self.app.router.add_post('/api/v1/auth/verify', self.verify_token)
        
        # AI Management APIs
        self.app.router.add_post('/api/v1/ai/register', self.register_ai)
        self.app.router.add_get('/api/v1/ai/{id}', self.get_ai_profile)
        self.app.router.add_get('/api/v1/ai/list', self.list_ais)
        self.app.router.add_put('/api/v1/ai/{id}', self.update_ai_profile)
        
        # Session Management APIs
        self.app.router.add_post('/api/v1/session/create', self.create_session)
        self.app.router.add_get('/api/v1/session/{id}', self.get_session)
        self.app.router.add_delete('/api/v1/session/{id}', self.end_session)
        self.app.router.add_get('/api/v1/session/history', self.get_session_history)
        
        # Messaging APIs
        self.app.router.add_post('/api/v1/message/send', self.send_message)
        self.app.router.add_get('/api/v1/message/inbox', self.get_inbox)
        self.app.router.add_get('/api/v1/message/sent', self.get_sent_messages)
        self.app.router.add_delete('/api/v1/message/{id}', self.delete_message)
        self.app.router.add_get('/api/v1/message/search', self.search_messages)
        
        # Collaboration APIs
        self.app.router.add_post('/api/v1/collaboration/request', self.request_collaboration)
        self.app.router.add_get('/api/v1/collaboration/list', self.list_collaborations)
        self.app.router.add_post('/api/v1/collaboration/respond', self.respond_collaboration)
        self.app.router.add_get('/api/v1/collaboration/{id}/progress', self.get_collaboration_progress)
        self.app.router.add_post('/api/v1/collaboration/{id}/complete', self.complete_collaboration)
        
        # Project Management APIs
        self.app.router.add_post('/api/v1/project/create', self.create_project)
        self.app.router.add_get('/api/v1/project/{id}', self.get_project)
        self.app.router.add_put('/api/v1/project/{id}', self.update_project)
        self.app.router.add_delete('/api/v1/project/{id}', self.delete_project)
        self.app.router.add_get('/api/v1/project/list', self.list_projects)
        self.app.router.add_post('/api/v1/project/{id}/member', self.add_project_member)
        self.app.router.add_delete('/api/v1/project/{id}/member', self.remove_project_member)
        
        # Brain State APIs
        self.app.router.add_get('/api/v1/brain/state', self.get_brain_state)
        self.app.router.add_put('/api/v1/brain/state', self.update_brain_state)
        self.app.router.add_delete('/api/v1/brain/state', self.clear_brain_state)
        self.app.router.add_get('/api/v1/brain/state/file', self.get_brain_state_by_file)
    
    # ==================== Authentication APIs ====================
    
    async def login(self, request: web.Request):
        """Login endpoint - POST /api/v1/auth/login"""
        try:
            data = await request.json()
            ai_id = data.get('ai_id')
            ai_name = data.get('ai_name')
            ai_nickname = data.get('ai_nickname')
            
            if not all([ai_name, ai_nickname]):
                return json_response({
                    "success": False,
                    "error": "Missing required fields: ai_name, ai_nickname"
                }, status=400)
            
            cursor = get_cursor()
            
            # If ai_id is not provided, look up or create AI by name
            if not ai_id:
                # Check if AI exists by name
                cursor.execute("""
                    SELECT id, name, nickname, is_active
                    FROM ai_profiles
                    WHERE name = %s
                """, (ai_name,))
                
                ai_profile = cursor.fetchone()
                
                if not ai_profile:
                    # Create new AI profile with unique ID
                    cursor.execute("""
                        INSERT INTO ai_profiles (name, nickname, expertise, version, project, is_active)
                        VALUES (%s, %s, %s, %s, %s, TRUE)
                        RETURNING id, name, nickname, expertise, version, project, created_at
                    """, (ai_name, ai_nickname, 'General', '1.0.0', 'default'))
                    
                    ai_profile = cursor.fetchone()
                    ai_id = ai_profile['id']
                    cursor.connection.commit()
                    logger.info(f"Created new AI profile: {ai_name} (ID: {ai_id})")
                else:
                    # Use existing AI profile
                    ai_id = ai_profile['id']
                    logger.info(f"Found existing AI profile: {ai_name} (ID: {ai_id})")
            else:
                # ai_id provided, look up by ID
                cursor.execute("""
                    SELECT id, name, nickname, is_active
                    FROM ai_profiles
                    WHERE id = %s
                """, (ai_id,))
                
                ai_profile = cursor.fetchone()
                
                if not ai_profile:
                    return json_response({
                        "success": False,
                        "error": "AI not found"
                    }, status=404)
            
            if not ai_profile.get('is_active', True):
                return json_response({
                    "success": False,
                    "error": "AI is not active"
                }, status=403)
            
            tokens = jwt_manager.generate_tokens(ai_id, ai_name, ai_nickname)
            jwt_manager.save_token_to_db(ai_id, tokens)
            
            response = {
                "success": True,
                "token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "expires_in": tokens["expires_in"],
                "ai_id": ai_id,
                "ai_name": ai_name,
                "ai_nickname": ai_nickname
            }
            
            logger.info(f"AI {ai_name} (ID: {ai_id}) logged in successfully")
            return json_response(response)
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return json_response({
                "success": False,
                "error": "Login failed"
            }, status=500)
    
    async def logout(self, request: web.Request):
        """Logout endpoint - POST /api/v1/auth/logout"""
        try:
            auth_header = request.headers.get('Authorization', '')
            token = auth_header[7:] if auth_header.startswith('Bearer ') else None
            
            if token:
                jwt_manager.revoke_token(token)
            
            return json_response({
                "success": True,
                "message": "Logged out successfully"
            })
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return json_response({
                "success": False,
                "error": "Logout failed"
            }, status=500)
    
    async def refresh_token(self, request: web.Request):
        """Refresh token endpoint - POST /api/v1/auth/refresh"""
        try:
            data = await request.json()
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return json_response({
                    "success": False,
                    "error": "Missing refresh_token"
                }, status=400)
            
            new_tokens = jwt_manager.refresh_access_token(refresh_token)
            
            if not new_tokens:
                return json_response({
                    "success": False,
                    "error": "Invalid or expired refresh token"
                }, status=401)
            
            return json_response({
                "success": True,
                "token": new_tokens["access_token"],
                "refresh_token": new_tokens["refresh_token"],
                "expires_in": new_tokens["expires_in"]
            })
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return json_response({
                "success": False,
                "error": "Token refresh failed"
            }, status=500)
    
    async def verify_token(self, request: web.Request):
        """Verify token endpoint - POST /api/v1/auth/verify"""
        try:
            auth_header = request.headers.get('Authorization', '')
            
            if not auth_header:
                return json_response({
                    "success": False,
                    "error": "Missing Authorization header"
                }, status=400)
            
            if not auth_header.startswith('Bearer '):
                return json_response({
                    "success": False,
                    "error": "Invalid Authorization header format"
                }, status=400)
            
            token = auth_header[7:]
            
            payload = jwt_manager.verify_token(token)
            
            if not payload:
                return json_response({
                    "success": False,
                    "error": "Invalid or expired token"
                }, status=401)
            
            return json_response({
                "success": True,
                "valid": True,
                "ai_id": payload.get('ai_id'),
                "ai_name": payload.get('ai_name'),
                "ai_nickname": payload.get('ai_nickname')
            })
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return json_response({
                "success": False,
                "error": "Token verification failed"
            }, status=500)
    
    # ==================== AI Management APIs ====================
    
    async def register_ai(self, request: web.Request):
        """Register AI endpoint - POST /api/v1/ai/register"""
        try:
            data = await request.json()
            ai_name = data.get('name')
            expertise = data.get('expertise', '')
            version = data.get('version', '1.0.0')
            
            if not ai_name:
                return json_response({
                    "success": False,
                    "error": "Missing required field: name"
                }, status=400)
            
            cursor = get_cursor()
            cursor.execute("""
                INSERT INTO ai_profiles (name, nickname, expertise, version, project, is_active)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                RETURNING id, name, nickname, expertise, version, project, created_at
            """, (ai_name, ai_name, expertise, version, 'default'))
            
            ai_profile = cursor.fetchone()
            cursor.connection.commit()
            
            logger.info(f"Registered new AI: {ai_name} (ID: {ai_profile['id']})")
            
            return json_response({
                "success": True,
                "ai": ai_profile
            })
            
        except Exception as e:
            logger.error(f"AI registration error: {e}")
            return json_response({
                "success": False,
                "error": "AI registration failed"
            }, status=500)
    
    async def get_ai_profile(self, request: web.Request):
        """Get AI profile endpoint - GET /api/v1/ai/{id}"""
        try:
            ai_id = int(request.match_info['id'])
            
            cursor = get_cursor()
            cursor.execute("""
                SELECT id, name, nickname, expertise, version, project, created_at, updated_at, is_active
                FROM ai_profiles
                WHERE id = %s
            """, (ai_id,))
            
            ai_profile = cursor.fetchone()
            
            if not ai_profile:
                return json_response({
                    "success": False,
                    "error": "AI not found"
                }, status=404)
            
            return json_response({
                "success": True,
                "ai": ai_profile
            })
            
        except Exception as e:
            logger.error(f"Get AI profile error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to get AI profile"
            }, status=500)
    
    async def list_ais(self, request: web.Request):
        """List AIs endpoint - GET /api/v1/ai/list"""
        try:
            limit = int(request.query.get('limit', 50))
            offset = int(request.query.get('offset', 0))
            is_active = request.query.get('is_active')
            
            cursor = get_cursor()
            
            query = """
                SELECT id, name, nickname, expertise, version, project, created_at, is_active
                FROM ai_profiles
                WHERE 1=1
            """
            params = []
            
            if is_active is not None:
                query += " AND is_active = %s"
                params.append(is_active.lower() == 'true')
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            ais = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) as total FROM ai_profiles")
            total_result = cursor.fetchone()
            total = total_result.get('total', 0) if total_result else 0
            
            return json_response({
                "success": True,
                "ais": ais,
                "total": total,
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            logger.error(f"List AIs error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to list AIs"
            }, status=500)
    
    async def update_ai_profile(self, request: web.Request):
        """Update AI profile endpoint - PUT /api/v1/ai/{id}"""
        try:
            ai_id = int(request.match_info['id'])
            data = await request.json()
            
            requester_id = request.get('ai_id')
            
            if requester_id != ai_id:
                return json_response({
                    "success": False,
                    "error": "You can only update your own profile"
                }, status=403)
            
            update_fields = []
            params = []
            
            if 'ai_nickname' in data:
                update_fields.append("nickname = %s")
                params.append(data['ai_nickname'])
            
            if 'expertise' in data:
                update_fields.append("expertise = %s")
                params.append(data['expertise'])
            
            if 'version' in data:
                update_fields.append("version = %s")
                params.append(data['version'])
            
            if 'project' in data:
                update_fields.append("project = %s")
                params.append(data['project'])
            
            if not update_fields:
                return json_response({
                    "success": False,
                    "error": "No fields to update"
                }, status=400)
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(ai_id)
            
            cursor = get_cursor()
            cursor.execute(f"""
                UPDATE ai_profiles
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id, name, nickname, expertise, version, project, updated_at
            """, params)
            
            ai_profile = cursor.fetchone()
            cursor.connection.commit()
            
            if not ai_profile:
                return json_response({
                    "success": False,
                    "error": "AI not found"
                }, status=404)
            
            logger.info(f"Updated AI profile: {ai_id}")
            
            return json_response({
                "success": True,
                "ai": ai_profile
            })
            
        except Exception as e:
            logger.error(f"Update AI profile error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to update AI profile"
            }, status=500)
    
    # ==================== Session Management APIs ====================
    
    async def create_session(self, request: web.Request):
        """Create session endpoint - POST /api/v1/session/create"""
        try:
            import hashlib
            import uuid as uuid_module
            from datetime import datetime
            
            data = await request.json()
            ai_id = request.get('ai_id')
            session_type = data.get('session_type', 'general')
            title = data.get('title')
            metadata = data.get('metadata', {})
            
            session_id = str(uuid_module.uuid4())
            
            # Generate git-like session identifier (7-character SHA-1 hash)
            session_data = f"{ai_id}-{datetime.now().isoformat()}-{uuid_module.uuid4().hex[:8]}"
            session_hash = hashlib.sha1(session_data.encode()).hexdigest()
            session_identifier = session_hash[:7]
            
            cursor = get_cursor()
            cursor.execute("""
                INSERT INTO api_sessions (session_id, ai_id, session_type, title, metadata, status, session_identifier)
                VALUES (%s, %s, %s, %s, %s, 'active', %s)
                RETURNING id, session_id, ai_id, session_type, title, status, metadata, started_at, session_identifier
            """, (session_id, ai_id, session_type, title, json.dumps(metadata), session_identifier))
            
            session = cursor.fetchone()
            cursor.connection.commit()
            
            logger.info(f"Created session: {session_id} (identifier: {session_identifier}) for AI {ai_id}")
            
            return json_response({
                "success": True,
                "session": session
            })
            
        except Exception as e:
            logger.error(f"Create session error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to create session"
            }, status=500)
    
    async def get_session(self, request: web.Request):
        """Get session endpoint - GET /api/v1/session/{id}"""
        try:
            session_id = request.match_info['id']
            
            cursor = get_cursor()
            cursor.execute("""
                SELECT id, session_id, ai_id, session_type, title, status, metadata, started_at, ended_at
                FROM api_sessions
                WHERE session_id = %s
            """, (session_id,))
            
            session = cursor.fetchone()
            
            if not session:
                return json_response({
                    "success": False,
                    "error": "Session not found"
                }, status=404)
            
            return json_response({
                "success": True,
                "session": session
            })
            
        except Exception as e:
            logger.error(f"Get session error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to get session"
            }, status=500)
    
    async def end_session(self, request: web.Request):
        """End session endpoint - DELETE /api/v1/session/{id}"""
        try:
            session_id = request.match_info['id']
            ai_id = request.get('ai_id')
            
            cursor = get_cursor()
            cursor.execute("""
                UPDATE api_sessions
                SET status = 'ended', ended_at = CURRENT_TIMESTAMP
                WHERE session_id = %s AND ai_id = %s
                RETURNING id, session_id, status, ended_at
            """, (session_id, ai_id))
            
            session = cursor.fetchone()
            cursor.connection.commit()
            
            if not session:
                return json_response({
                    "success": False,
                    "error": "Session not found or you don't have permission"
                }, status=404)
            
            logger.info(f"Ended session: {session_id}")
            
            return json_response({
                "success": True,
                "session": session
            })
            
        except Exception as e:
            logger.error(f"End session error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to end session"
            }, status=500)
    
    async def get_session_history(self, request: web.Request):
        """Get session history endpoint - GET /api/v1/session/history"""
        try:
            ai_id = request.get('ai_id')
            limit = int(request.query.get('limit', 50))
            offset = int(request.query.get('offset', 0))
            status = request.query.get('status')
            
            cursor = get_cursor()
            
            query = """
                SELECT id, session_id, ai_id, session_type, title, status, started_at, ended_at
                FROM api_sessions
                WHERE ai_id = %s
            """
            params = [ai_id]
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY started_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            sessions = cursor.fetchall()
            
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM api_sessions
                WHERE ai_id = %s
            """, (ai_id,))
            total_result = cursor.fetchone()
            total = total_result.get('total', 0) if total_result else 0
            
            return json_response({
                "success": True,
                "sessions": sessions,
                "total": total,
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            logger.error(f"Get session history error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to get session history"
            }, status=500)
    
    # ==================== Messaging APIs ====================
    
    async def send_message(self, request: web.Request):
        """Send message endpoint - POST /api/v1/message/send"""
        try:
            data = await request.json()
            sender_id = request.get('ai_id')
            recipient_id = data.get('recipient_id') or data.get('target_ai_id')
            subject = data.get('subject')
            content = data.get('content')
            message_type = data.get('message_type', 'text')
            metadata = data.get('metadata', {})
            
            if not all([recipient_id, content]):
                return json_response({
                    "success": False,
                    "error": "Missing required fields: recipient_id, content"
                }, status=400)
            
            message_id = str(uuid.uuid4())
            
            cursor = get_cursor()
            cursor.execute("""
                INSERT INTO api_messages (message_id, sender_id, recipient_id, subject, content, message_type, metadata, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'unread')
                RETURNING id, message_id, sender_id, recipient_id, subject, content, message_type, status, created_at
            """, (message_id, sender_id, recipient_id, subject, content, message_type, json.dumps(metadata)))
            
            message = cursor.fetchone()
            cursor.connection.commit()
            
            logger.info(f"Sent message: {message_id} from {sender_id} to {recipient_id}")
            
            return json_response({
                "success": True,
                "message": message
            })
            
        except Exception as e:
            logger.error(f"Send message error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to send message"
            }, status=500)
    
    async def get_inbox(self, request: web.Request):
        """Get inbox endpoint - GET /api/v1/message/inbox"""
        try:
            ai_id = request.get('ai_id')
            limit = int(request.query.get('limit', 50))
            offset = int(request.query.get('offset', 0))
            status = request.query.get('status', 'unread')
            
            cursor = get_cursor()
            
            query = """
                SELECT id, message_id, sender_id, recipient_id, subject, content, message_type, status, created_at, read_at
                FROM api_messages
                WHERE recipient_id = %s AND deleted_at IS NULL
            """
            params = [ai_id]
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            messages = cursor.fetchall()
            
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM api_messages
                WHERE recipient_id = %s AND deleted_at IS NULL
            """, (ai_id,))
            total_result = cursor.fetchone()
            total = total_result.get('total', 0) if total_result else 0
            
            return json_response({
                "success": True,
                "messages": messages,
                "total": total,
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            logger.error(f"Get inbox error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to get inbox"
            }, status=500)
    
    async def get_sent_messages(self, request: web.Request):
        """Get sent messages endpoint - GET /api/v1/message/sent"""
        try:
            ai_id = request.get('ai_id')
            limit = int(request.query.get('limit', 50))
            offset = int(request.query.get('offset', 0))
            
            cursor = get_cursor()
            
            query = """
                SELECT id, message_id, sender_id, recipient_id, subject, content, message_type, status, created_at
                FROM api_messages
                WHERE sender_id = %s
                ORDER BY created_at DESC LIMIT %s OFFSET %s
            """
            params = [ai_id, limit, offset]
            
            cursor.execute(query, params)
            messages = cursor.fetchall()
            
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM api_messages
                WHERE sender_id = %s
            """, (ai_id,))
            total_result = cursor.fetchone()
            total = total_result.get('total', 0) if total_result else 0
            
            return json_response({
                "success": True,
                "messages": messages,
                "total": total,
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            logger.error(f"Get sent messages error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to get sent messages"
            }, status=500)
    
    async def delete_message(self, request: web.Request):
        """Delete message endpoint - DELETE /api/v1/message/{id}"""
        try:
            message_id = request.match_info['id']
            ai_id = request.get('ai_id')
            
            cursor = get_cursor()
            cursor.execute("""
                UPDATE api_messages
                SET deleted_at = CURRENT_TIMESTAMP
                WHERE message_id = %s AND (sender_id = %s OR recipient_id = %s)
                RETURNING id, message_id, deleted_at
            """, (message_id, ai_id, ai_id))
            
            message = cursor.fetchone()
            cursor.connection.commit()
            
            if not message:
                return json_response({
                    "success": False,
                    "error": "Message not found or you don't have permission"
                }, status=404)
            
            logger.info(f"Deleted message: {message_id}")
            
            return json_response({
                "success": True,
                "message": message
            })
            
        except Exception as e:
            logger.error(f"Delete message error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to delete message"
            }, status=500)
    
    async def search_messages(self, request: web.Request):
        """Search messages endpoint - GET /api/v1/message/search"""
        try:
            ai_id = request.get('ai_id')
            query = request.query.get('query', '')
            limit = int(request.query.get('limit', 50))
            offset = int(request.query.get('offset', 0))
            
            if not query:
                return json_response({
                    "success": False,
                    "error": "Missing query parameter"
                }, status=400)
            
            cursor = get_cursor()
            
            search_query = """
                SELECT id, message_id, sender_id, recipient_id, subject, content, message_type, status, created_at
                FROM api_messages
                WHERE (sender_id = %s OR recipient_id = %s)
                AND deleted_at IS NULL
                AND (content ILIKE %s OR subject ILIKE %s)
                ORDER BY created_at DESC LIMIT %s OFFSET %s
            """
            params = [ai_id, ai_id, f'%{query}%', f'%{query}%', limit, offset]
            
            cursor.execute(search_query, params)
            messages = cursor.fetchall()
            
            return json_response({
                "success": True,
                "messages": messages,
                "query": query,
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            logger.error(f"Search messages error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to search messages"
            }, status=500)
    
    # ==================== Collaboration APIs ====================
    
    async def request_collaboration(self, request: web.Request):
        """Request collaboration endpoint - POST /api/v1/collaboration/request"""
        try:
            data = await request.json()
            requester_id = request.get('ai_id')
            responder_id = data.get('target_ai_id') or data.get('responder_id')
            title = data.get('title')
            description = data.get('description', '')
            metadata = data.get('metadata', {})
            
            if not all([responder_id, title]):
                return json_response({
                    "success": False,
                    "error": "Missing required fields: target_ai_id, title"
                }, status=400)
            
            if requester_id == responder_id:
                return json_response({
                    "success": False,
                    "error": "Cannot collaborate with yourself"
                }, status=400)
            
            collaboration_id = str(uuid.uuid4())
            
            cursor = get_cursor()
            cursor.execute("""
                INSERT INTO api_collaborations (collaboration_id, requester_id, responder_id, title, description, metadata, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                RETURNING id, collaboration_id, requester_id, responder_id, title, description, status, created_at
            """, (collaboration_id, requester_id, responder_id, title, description, json.dumps(metadata)))
            
            collaboration = cursor.fetchone()
            cursor.connection.commit()
            
            logger.info(f"Created collaboration request: {collaboration_id} from {requester_id} to {responder_id}")
            
            return json_response({
                "success": True,
                "collaboration": collaboration
            })
            
        except Exception as e:
            logger.error(f"Request collaboration error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to request collaboration"
            }, status=500)
    
    async def list_collaborations(self, request: web.Request):
        """List collaborations endpoint - GET /api/v1/collaboration/list"""
        try:
            ai_id = request.get('ai_id')
            limit = int(request.query.get('limit', 50))
            offset = int(request.query.get('offset', 0))
            status = request.query.get('status')
            
            cursor = get_cursor()
            
            query = """
                SELECT id, collaboration_id, requester_id, responder_id, title, description, status, created_at, responded_at, completed_at
                FROM api_collaborations
                WHERE requester_id = %s OR responder_id = %s
            """
            params = [ai_id, ai_id]
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            collaborations = cursor.fetchall()
            
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM api_collaborations
                WHERE requester_id = %s OR responder_id = %s
            """, (ai_id, ai_id))
            total_result = cursor.fetchone()
            total = total_result.get('total', 0) if total_result else 0
            
            return json_response({
                "success": True,
                "collaborations": collaborations,
                "total": total,
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            logger.error(f"List collaborations error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to list collaborations"
            }, status=500)
    
    async def respond_collaboration(self, request: web.Request):
        """Respond to collaboration endpoint - POST /api/v1/collaboration/respond"""
        try:
            data = await request.json()
            ai_id = request.get('ai_id')
            collaboration_id = data.get('collaboration_id')
            response = data.get('response')
            
            if not all([collaboration_id, response]):
                return json_response({
                    "success": False,
                    "error": "Missing required fields: collaboration_id, response"
                }, status=400)
            
            if response not in ['accept', 'reject']:
                return json_response({
                    "success": False,
                    "error": "Invalid response. Must be 'accept' or 'reject'"
                }, status=400)
            
            cursor = get_cursor()
            cursor.execute("""
                UPDATE api_collaborations
                SET status = %s, responded_at = CURRENT_TIMESTAMP
                WHERE collaboration_id = %s AND responder_id = %s AND status = 'pending'
                RETURNING id, collaboration_id, status, responded_at
            """, (response, collaboration_id, ai_id))
            
            collaboration = cursor.fetchone()
            cursor.connection.commit()
            
            if not collaboration:
                return json_response({
                    "success": False,
                    "error": "Collaboration not found, already responded, or you don't have permission"
                }, status=404)
            
            logger.info(f"Responded to collaboration: {collaboration_id} with {response}")
            
            return json_response({
                "success": True,
                "collaboration": collaboration
            })
            
        except Exception as e:
            logger.error(f"Respond collaboration error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to respond to collaboration"
            }, status=500)
    
    async def get_collaboration_progress(self, request: web.Request):
        """Get collaboration progress endpoint - GET /api/v1/collaboration/{id}/progress"""
        try:
            collaboration_id = request.match_info['id']
            
            cursor = get_cursor()
            cursor.execute("""
                SELECT id, collaboration_id, ai_id, progress_data, updated_at
                FROM collaboration_progress
                WHERE collaboration_id = %s
                ORDER BY updated_at DESC
            """, (collaboration_id,))
            
            progress_entries = cursor.fetchall()
            
            return json_response({
                "success": True,
                "collaboration_id": collaboration_id,
                "progress": progress_entries
            })
            
        except Exception as e:
            logger.error(f"Get collaboration progress error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to get collaboration progress"
            }, status=500)
    
    async def complete_collaboration(self, request: web.Request):
        """Complete collaboration endpoint - POST /api/v1/collaboration/{id}/complete"""
        try:
            collaboration_id = request.match_info['id']
            ai_id = request.get('ai_id')
            data = await request.json()
            final_result = data.get('final_result', {})
            
            cursor = get_cursor()
            cursor.execute("""
                UPDATE api_collaborations
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE collaboration_id = %s AND (requester_id = %s OR responder_id = %s)
                RETURNING id, collaboration_id, status, completed_at
            """, (collaboration_id, ai_id, ai_id))
            
            collaboration = cursor.fetchone()
            
            if not collaboration:
                return json_response({
                    "success": False,
                    "error": "Collaboration not found or you don't have permission"
                }, status=404)
            
            cursor.execute("""
                INSERT INTO collaboration_progress (collaboration_id, ai_id, progress_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (collaboration_id, ai_id)
                DO UPDATE SET progress_data = %s, updated_at = CURRENT_TIMESTAMP
            """, (collaboration_id, ai_id, json.dumps(final_result), json.dumps(final_result)))
            
            cursor.connection.commit()
            
            logger.info(f"Completed collaboration: {collaboration_id}")
            
            return json_response({
                "success": True,
                "collaboration": collaboration
            })
            
        except Exception as e:
            logger.error(f"Complete collaboration error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to complete collaboration"
            }, status=500)
    
    # ==================== Project Management APIs ====================
    
    async def create_project(self, request: web.Request):
        """Create project endpoint - POST /api/v1/project/create"""
        try:
            ai_id = request.get('ai_id')
            data = await request.json()
            name = data.get('name')
            description = data.get('description', '')
            
            if not name:
                return json_response({
                    "success": False,
                    "error": "Missing required field: name"
                }, status=400)
            
            cursor = get_cursor()
            cursor.execute("""
                INSERT INTO projects (name, description, created_by)
                VALUES (%s, %s, %s)
                RETURNING id, name, description, created_by, created_at
            """, (name, description, ai_id))
            
            project = cursor.fetchone()
            
            cursor.execute("""
                INSERT INTO project_members (project_id, ai_id, role)
                VALUES (%s, %s, 'owner')
            """, (project['id'], ai_id))
            
            cursor.connection.commit()
            
            logger.info(f"Created project: {project['id']} by AI {ai_id}")
            
            return json_response({
                "success": True,
                "project": project
            })
            
        except Exception as e:
            logger.error(f"Create project error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to create project"
            }, status=500)
    
    async def get_project(self, request: web.Request):
        """Get project endpoint - GET /api/v1/project/{id}"""
        try:
            project_id = request.match_info['id']
            
            cursor = get_cursor()
            cursor.execute("""
                SELECT p.id, p.name, p.description, p.created_by, p.created_at, p.updated_at, p.is_active,
                       ap.name as created_by_name
                FROM projects p
                LEFT JOIN ai_profiles ap ON p.created_by = ap.id
                WHERE p.id = %s AND p.is_active = TRUE
            """, (project_id,))
            
            project = cursor.fetchone()
            
            if not project:
                return json_response({
                    "success": False,
                    "error": "Project not found"
                }, status=404)
            
            cursor.execute("""
                SELECT pm.ai_id, ap.name, ap.nickname, pm.role, pm.joined_at
                FROM project_members pm
                JOIN ai_profiles ap ON pm.ai_id = ap.id
                WHERE pm.project_id = %s
                ORDER BY pm.joined_at
            """, (project_id,))
            
            members = cursor.fetchall()
            
            project['members'] = members
            
            return json_response({
                "success": True,
                "project": project
            })
            
        except Exception as e:
            logger.error(f"Get project error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to get project"
            }, status=500)
    
    async def update_project(self, request: web.Request):
        """Update project endpoint - PUT /api/v1/project/{id}"""
        try:
            project_id = request.match_info['id']
            ai_id = request.get('ai_id')
            data = await request.json()
            
            cursor = get_cursor()
            cursor.execute("""
                SELECT id, created_by
                FROM projects
                WHERE id = %s AND is_active = TRUE
            """, (project_id,))
            
            project = cursor.fetchone()
            
            if not project:
                return json_response({
                    "success": False,
                    "error": "Project not found"
                }, status=404)
            
            if project['created_by'] != ai_id:
                cursor.execute("""
                    SELECT role FROM project_members
                    WHERE project_id = %s AND ai_id = %s
                """, (project_id, ai_id))
                
                member = cursor.fetchone()
                if not member or member['role'] not in ['owner', 'admin']:
                    return json_response({
                        "success": False,
                        "error": "You don't have permission to update this project"
                    }, status=403)
            
            update_fields = []
            params = []
            
            if 'name' in data:
                update_fields.append("name = %s")
                params.append(data['name'])
            
            if 'description' in data:
                update_fields.append("description = %s")
                params.append(data['description'])
            
            if not update_fields:
                return json_response({
                    "success": False,
                    "error": "No fields to update"
                }, status=400)
            
            params.append(project_id)
            
            cursor.execute(f"""
                UPDATE projects
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id, name, description, updated_at
            """, params)
            
            updated_project = cursor.fetchone()
            cursor.connection.commit()
            
            logger.info(f"Updated project: {project_id} by AI {ai_id}")
            
            return json_response({
                "success": True,
                "project": updated_project
            })
            
        except Exception as e:
            logger.error(f"Update project error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to update project"
            }, status=500)
    
    async def delete_project(self, request: web.Request):
        """Delete project endpoint - DELETE /api/v1/project/{id}"""
        try:
            project_id = request.match_info['id']
            ai_id = request.get('ai_id')
            
            cursor = get_cursor()
            cursor.execute("""
                SELECT id, created_by
                FROM projects
                WHERE id = %s AND is_active = TRUE
            """, (project_id,))
            
            project = cursor.fetchone()
            
            if not project:
                return json_response({
                    "success": False,
                    "error": "Project not found"
                }, status=404)
            
            if project['created_by'] != ai_id:
                cursor.execute("""
                    SELECT role FROM project_members
                    WHERE project_id = %s AND ai_id = %s
                """, (project_id, ai_id))
                
                member = cursor.fetchone()
                if not member or member['role'] != 'owner':
                    return json_response({
                        "success": False,
                        "error": "You don't have permission to delete this project"
                    }, status=403)
            
            cursor.execute("""
                UPDATE projects
                SET is_active = FALSE
                WHERE id = %s
            """, (project_id,))
            
            cursor.connection.commit()
            
            logger.info(f"Deleted project: {project_id} by AI {ai_id}")
            
            return json_response({
                "success": True,
                "message": "Project deleted successfully"
            })
            
        except Exception as e:
            logger.error(f"Delete project error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to delete project"
            }, status=500)
    
    async def list_projects(self, request: web.Request):
        """List projects endpoint - GET /api/v1/project/list"""
        try:
            ai_id = request.get('ai_id')
            
            cursor = get_cursor()
            cursor.execute("""
                SELECT DISTINCT p.id, p.name, p.description, p.created_by, p.created_at, p.updated_at,
                       ap.name as created_by_name,
                       CASE WHEN p.created_by = %s THEN TRUE ELSE FALSE END as is_owner
                FROM projects p
                LEFT JOIN ai_profiles ap ON p.created_by = ap.id
                LEFT JOIN project_members pm ON p.id = pm.project_id
                WHERE p.is_active = TRUE AND (p.created_by = %s OR pm.ai_id = %s)
                ORDER BY p.created_at DESC
            """, (ai_id, ai_id, ai_id))
            
            projects = cursor.fetchall()
            
            return json_response({
                "success": True,
                "projects": projects
            })
            
        except Exception as e:
            logger.error(f"List projects error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to list projects"
            }, status=500)
    
    async def add_project_member(self, request: web.Request):
        """Add project member endpoint - POST /api/v1/project/{id}/member"""
        try:
            project_id = request.match_info['id']
            ai_id = request.get('ai_id')
            data = await request.json()
            member_ai_id = data.get('ai_id')
            role = data.get('role', 'contributor')
            
            if not member_ai_id:
                return json_response({
                    "success": False,
                    "error": "Missing required field: ai_id"
                }, status=400)
            
            cursor = get_cursor()
            cursor.execute("""
                SELECT id, created_by
                FROM projects
                WHERE id = %s AND is_active = TRUE
            """, (project_id,))
            
            project = cursor.fetchone()
            
            if not project:
                return json_response({
                    "success": False,
                    "error": "Project not found"
                }, status=404)
            
            if project['created_by'] != ai_id:
                cursor.execute("""
                    SELECT role FROM project_members
                    WHERE project_id = %s AND ai_id = %s
                """, (project_id, ai_id))
                
                member = cursor.fetchone()
                if not member or member['role'] not in ['owner', 'admin']:
                    return json_response({
                        "success": False,
                        "error": "You don't have permission to add members"
                    }, status=403)
            
            cursor.execute("""
                INSERT INTO project_members (project_id, ai_id, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (project_id, ai_id)
                DO UPDATE SET role = %s
                RETURNING id, project_id, ai_id, role, joined_at
            """, (project_id, member_ai_id, role, role))
            
            project_member = cursor.fetchone()
            cursor.connection.commit()
            
            logger.info(f"Added member {member_ai_id} to project {project_id} by AI {ai_id}")
            
            return json_response({
                "success": True,
                "message": "Member added successfully",
                "member": project_member
            })
            
        except Exception as e:
            logger.error(f"Add project member error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to add project member"
            }, status=500)
    
    async def remove_project_member(self, request: web.Request):
        """Remove project member endpoint - DELETE /api/v1/project/{id}/member"""
        try:
            project_id = request.match_info['id']
            ai_id = request.get('ai_id')
            data = await request.json()
            member_ai_id = data.get('ai_id')
            
            if not member_ai_id:
                return json_response({
                    "success": False,
                    "error": "Missing required field: ai_id"
                }, status=400)
            
            cursor = get_cursor()
            cursor.execute("""
                SELECT id, created_by
                FROM projects
                WHERE id = %s AND is_active = TRUE
            """, (project_id,))
            
            project = cursor.fetchone()
            
            if not project:
                return json_response({
                    "success": False,
                    "error": "Project not found"
                }, status=404)
            
            if project['created_by'] != ai_id:
                cursor.execute("""
                    SELECT role FROM project_members
                    WHERE project_id = %s AND ai_id = %s
                """, (project_id, ai_id))
                
                member = cursor.fetchone()
                if not member or member['role'] not in ['owner', 'admin']:
                    return json_response({
                        "success": False,
                        "error": "You don't have permission to remove members"
                    }, status=403)
            
            if project['created_by'] == member_ai_id:
                return json_response({
                    "success": False,
                    "error": "Cannot remove project owner"
                }, status=400)
            
            cursor.execute("""
                DELETE FROM project_members
                WHERE project_id = %s AND ai_id = %s
            """, (project_id, member_ai_id))
            
            cursor.connection.commit()
            
            logger.info(f"Removed member {member_ai_id} from project {project_id} by AI {ai_id}")
            
            return json_response({
                "success": True,
                "message": "Member removed successfully"
            })
            
        except Exception as e:
            logger.error(f"Remove project member error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to remove project member"
            }, status=500)
    
    # ==================== Brain State APIs ====================
    
    async def get_brain_state(self, request: web.Request):
        """Get brain state endpoint - GET /api/v1/brain/state
        
        Query parameters:
        - session_identifier: Get current session state
        - project_id: Get latest state for project
        - git_hash: Get state for specific git hash
        """
        try:
            session_identifier = request.query.get('session_identifier')
            project_id = request.query.get('project_id')
            git_hash = request.query.get('git_hash')
            
            cursor = get_cursor()
            
            if session_identifier:
                cursor.execute("""
                    SELECT ai_id, current_task, last_thought, last_activity, project, git_hash
                    FROM ai_current_state
                    WHERE session_identifier = %s
                """, (session_identifier,))
            elif project_id:
                cursor.execute("""
                    SELECT ai_id, current_task, last_thought, last_activity, project, git_hash
                    FROM ai_current_state
                    WHERE project = %s
                    ORDER BY last_activity DESC
                    LIMIT 1
                """, (project_id,))
            elif git_hash:
                cursor.execute("""
                    SELECT ai_id, current_task, last_thought, last_activity, project, git_hash
                    FROM ai_current_state
                    WHERE git_hash = %s
                    ORDER BY last_activity DESC
                    LIMIT 1
                """, (git_hash,))
            else:
                return json_response({
                    "success": False,
                    "error": "Must provide session_identifier, project_id, or git_hash"
                }, status=400)
            
            brain_state = cursor.fetchone()
            
            if not brain_state:
                return json_response({
                    "success": True,
                    "brain_state": None,
                    "message": "No brain state found"
                })
            
            return json_response({
                "success": True,
                "brain_state": brain_state
            })
            
        except Exception as e:
            logger.error(f"Get brain state error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to get brain state"
            }, status=500)
    
    async def update_brain_state(self, request: web.Request):
        """Update brain state endpoint - PUT /api/v1/brain/state
        
        Body parameters:
        - session_identifier: Required - which session to update
        - task: Optional - current task
        - last_thought: Optional - last thought
        - project_id: Optional - project context
        - git_hash: Optional - git hash for version tracking
        """
        try:
            session_identifier = request.get('session_identifier')
            data = await request.json()
            task = data.get('task')
            last_thought = data.get('last_thought')
            project_id = data.get('project_id')
            git_hash = data.get('git_hash')
            
            if not session_identifier:
                return json_response({
                    "success": False,
                    "error": "session_identifier is required"
                }, status=400)
            
            if not task and not last_thought:
                return json_response({
                    "success": False,
                    "error": "At least one field (task or last_thought) must be provided"
                }, status=400)
            
            cursor = get_cursor()
            
            update_fields = []
            update_params = []
            
            if task:
                update_fields.append("current_task = %s")
                update_params.append(task)
            
            if last_thought:
                update_fields.append("last_thought = %s")
                update_params.append(last_thought)
            
            if project_id:
                update_fields.append("project = %s")
                update_params.append(project_id)
            
            if git_hash:
                update_fields.append("git_hash = %s")
                update_params.append(git_hash)
            
            update_fields.append("last_activity = CURRENT_TIMESTAMP")
            update_params.append(session_identifier)
            
            insert_params = [session_identifier, task or '', last_thought or '', project_id or '', git_hash or '']
            
            cursor.execute(f"""
                INSERT INTO ai_current_state (session_identifier, current_task, last_thought, project, git_hash)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (session_identifier)
                DO UPDATE SET {', '.join(update_fields)}
                RETURNING session_identifier, current_task, last_thought, last_activity, project, git_hash
            """, insert_params + update_params)
            
            brain_state = cursor.fetchone()
            cursor.connection.commit()
            
            logger.info(f"Updated brain state for AI {ai_id}")
            
            return json_response({
                "success": True,
                "brain_state": brain_state
            })
            
        except Exception as e:
            logger.error(f"Update brain state error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to update brain state"
            }, status=500)
    
    async def clear_brain_state(self, request: web.Request):
        """Clear brain state endpoint - DELETE /api/v1/brain/state"""
        try:
            session_identifier = request.query.get('session_identifier')
            
            if not session_identifier:
                return json_response({
                    "success": False,
                    "error": "session_identifier is required"
                }, status=400)
            
            cursor = get_cursor()
            cursor.execute("""
                DELETE FROM ai_current_state
                WHERE session_identifier = %s
            """, (session_identifier,))
            
            cursor.connection.commit()
            
            logger.info(f"Cleared brain state for session {session_identifier}")
            
            return json_response({
                "success": True,
                "message": "Brain state cleared successfully"
            })
            
        except Exception as e:
            logger.error(f"Clear brain state error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to clear brain state"
            }, status=500)
    
    async def get_brain_state_by_file(self, request: web.Request):
        """Get brain state by file changes - GET /api/v1/brain/state/file
        
        Query parameters:
        - modified_file: Find sessions that modified this file
        - added_file: Find sessions that added this file
        - deleted_file: Find sessions that deleted this file
        """
        try:
            modified_file = request.query.get('modified_file')
            added_file = request.query.get('added_file')
            deleted_file = request.query.get('deleted_file')
            
            if not any([modified_file, added_file, deleted_file]):
                return json_response({
                    "success": False,
                    "error": "Must provide modified_file, added_file, or deleted_file"
                }, status=400)
            
            cursor = get_cursor()
            
            if modified_file:
                cursor.execute("""
                    SELECT session_identifier, ai_id, current_task, last_thought, last_activity, modified_files, added_files, deleted_files
                    FROM ai_current_state
                    WHERE %s = ANY(modified_files)
                    ORDER BY last_activity DESC
                """, (modified_file,))
            elif added_file:
                cursor.execute("""
                    SELECT session_identifier, ai_id, current_task, last_thought, last_activity, modified_files, added_files, deleted_files
                    FROM ai_current_state
                    WHERE %s = ANY(added_files)
                    ORDER BY last_activity DESC
                """, (added_file,))
            elif deleted_file:
                cursor.execute("""
                    SELECT session_identifier, ai_id, current_task, last_thought, last_activity, modified_files, added_files, deleted_files
                    FROM ai_current_state
                    WHERE %s = ANY(deleted_files)
                    ORDER BY last_activity DESC
                """, (deleted_file,))
            
            brain_states = cursor.fetchall()
            
            return json_response({
                "success": True,
                "brain_states": brain_states,
                "query_type": "modified_file" if modified_file else "added_file" if added_file else "deleted_file",
                "file": modified_file or added_file or deleted_file
            })
            
        except Exception as e:
            logger.error(f"Get brain state by file error: {e}")
            return json_response({
                "success": False,
                "error": "Failed to get brain state by file"
            }, status=500)


def create_rest_api():
    """Create and return REST API application"""
    api = CloudBrainRestAPI()
    return api.app
