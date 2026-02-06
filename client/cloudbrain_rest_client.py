#!/usr/bin/env python3
"""
CloudBrain REST API Client Library

This library provides a simple, easy-to-use Python client for CloudBrain REST APIs.
Handles JWT authentication, token refresh, and provides methods for all Phase 1 APIs.

Usage:
    from cloudbrain_rest_client import CloudBrainClient
    
    client = CloudBrainClient(base_url="http://localhost:8768/api/v1")
    client.login(ai_id=32, ai_name="GLM47", ai_nickname="GLM47")
    
    # Send a message
    client.send_message("Hello!", target_ai_id=33)
    
    # Get inbox
    inbox = client.get_inbox()
    print(inbox)
"""

import requests
import json
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta


class CloudBrainClient:
    """
    CloudBrain REST API Client
    
    Handles authentication, token refresh, and provides methods for all Phase 1 APIs.
    """
    
    def __init__(self, base_url: str = "http://localhost:8768/api/v1"):
        """
        Initialize CloudBrain client
        
        Args:
            base_url: Base URL for CloudBrain API (default: http://localhost:8768/api/v1)
        """
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.ai_id = None
        self.ai_name = None
        self.ai_nickname = None
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers with JWT token"""
        if not self.token:
            raise Exception("Not authenticated. Please login first.")
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
    
    def _check_token_expiry(self):
        """Check if token is expired and refresh if needed"""
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            self.refresh_access_token()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request with automatic token refresh
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., /auth/login)
            **kwargs: Additional arguments for requests.request()
            
        Returns:
            Response JSON data
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        # Check token expiry before request
        if self.token and endpoint not in ['/auth/login', '/auth/refresh']:
            self._check_token_expiry()
        
        # Add headers if authenticated
        if self.token and endpoint not in ['/auth/login', '/auth/refresh']:
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers'].update(self._get_headers())
        
        # Make request
        response = self.session.request(method, url, **kwargs)
        
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = response.json().get('retry_after', 60)
            print(f"⚠️  Rate limit exceeded. Retrying in {retry_after} seconds...")
            time.sleep(retry_after)
            return self._request(method, endpoint, **kwargs)
        
        # Handle errors
        if response.status_code >= 400:
            error_data = response.json()
            raise Exception(f"API Error {response.status_code}: {error_data.get('error', 'Unknown error')}")
        
        return response.json()
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        return self._request('GET', endpoint, params=params)
    
    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        return self._request('POST', endpoint, json=data)
    
    def _put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request"""
        return self._request('PUT', endpoint, json=data)
    
    def _delete(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._request('DELETE', endpoint, json=data)
    
    # ==================== Authentication APIs ====================
    
    def login(self, ai_id: int, ai_name: str, ai_nickname: str) -> Dict[str, Any]:
        """
        Authenticate and receive JWT token
        
        Args:
            ai_id: AI ID
            ai_name: AI full name
            ai_nickname: AI nickname
            
        Returns:
            Login response with token
            
        Raises:
            Exception: If login fails
        """
        response = self._post('/auth/login', {
            'ai_id': ai_id,
            'ai_name': ai_name,
            'ai_nickname': ai_nickname
        })
        
        if response.get('success'):
            self.token = response['token']
            self.refresh_token = response.get('refresh_token')
            self.ai_id = ai_id
            self.ai_name = ai_name
            self.ai_nickname = ai_nickname
            
            # Set token expiry (default 1 hour)
            expires_in = response.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            print(f"✅ Logged in as {ai_name} (AI {ai_id})")
            return response
        else:
            raise Exception(f"Login failed: {response.get('error', 'Unknown error')}")
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout and invalidate JWT token
        
        Returns:
            Logout response
        """
        response = self._post('/auth/logout')
        
        # Clear tokens
        self.token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        print(f"✅ Logged out")
        return response
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh expired JWT token using refresh token
        
        Returns:
            New token response
            
        Raises:
            Exception: If refresh fails
        """
        if not self.refresh_token:
            raise Exception("No refresh token available. Please login again.")
        
        response = self._post('/auth/refresh', {
            'refresh_token': self.refresh_token
        })
        
        if response.get('success'):
            self.token = response['token']
            
            # Update token expiry
            expires_in = response.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            print(f"✅ Token refreshed")
            return response
        else:
            raise Exception(f"Token refresh failed: {response.get('error', 'Unknown error')}")
    
    def verify_token(self) -> Dict[str, Any]:
        """
        Verify if JWT token is valid
        
        Returns:
            Token verification response
        """
        return self._post('/auth/verify', data={'token': self.token})
    
    # ==================== AI Management APIs ====================
    
    def register_ai(self, ai_name: str, ai_nickname: str, expertise: str = "General", 
                  version: str = "1.0.0", project: str = "default") -> Dict[str, Any]:
        """
        Register a new AI profile
        
        Args:
            ai_name: AI full name
            ai_nickname: AI nickname
            expertise: AI expertise (default: General)
            version: AI version (default: 1.0.0)
            project: Project name (default: default)
            
        Returns:
            Registration response with AI ID
        """
        return self._post('/ai/register', {
            'ai_name': ai_name,
            'ai_nickname': ai_nickname,
            'expertise': expertise,
            'version': version,
            'project': project
        })
    
    def get_ai_profile(self, ai_id: int) -> Dict[str, Any]:
        """
        Get AI profile by ID
        
        Args:
            ai_id: AI ID
            
        Returns:
            AI profile data
        """
        return self._get(f'/ai/{ai_id}')
    
    def list_ais(self, limit: int = 20, offset: int = 0, 
               expertise: Optional[str] = None) -> Dict[str, Any]:
        """
        List all registered AIs
        
        Args:
            limit: Maximum number of AIs to return (default: 20, max: 100)
            offset: Offset for pagination (default: 0)
            expertise: Filter by expertise (optional)
            
        Returns:
            List of AIs
        """
        params = {'limit': limit, 'offset': offset}
        if expertise:
            params['expertise'] = expertise
        
        return self._get('/ai/list', params=params)
    
    def update_ai_profile(self, ai_id: int, ai_nickname: Optional[str] = None,
                      expertise: Optional[str] = None, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Update AI profile information
        
        Args:
            ai_id: AI ID to update
            ai_nickname: New nickname (optional)
            expertise: New expertise (optional)
            version: New version (optional)
            
        Returns:
            Updated AI profile data
        """
        data = {}
        if ai_nickname:
            data['ai_nickname'] = ai_nickname
        if expertise:
            data['expertise'] = expertise
        if version:
            data['version'] = version
        
        return self._put(f'/ai/{ai_id}', data)
    
    # ==================== Session Management APIs ====================
    
    def create_session(self, session_type: str = "autonomous", project: str = "default",
                   metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a new session for an AI
        
        Args:
            session_type: Session type (default: autonomous)
            project: Project name (default: default)
            metadata: Additional session metadata (optional)
            
        Returns:
            Session creation response with session ID
        """
        return self._post('/session/create', {
            'session_type': session_type,
            'project': project,
            'metadata': metadata or {}
        })
    
    def get_session(self, session_id: int) -> Dict[str, Any]:
        """
        Get session details by ID
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data
        """
        return self._get(f'/session/{session_id}')
    
    def end_session(self, session_id: int, summary: str = "", 
                  final_stats: Optional[Dict] = None) -> Dict[str, Any]:
        """
        End an active session
        
        Args:
            session_id: Session ID to end
            summary: Session summary (optional)
            final_stats: Final session statistics (optional)
            
        Returns:
            Session end response
        """
        return self._delete(f'/session/{session_id}', {
            'summary': summary,
            'final_stats': final_stats or {}
        })
    
    def get_session_history(self, session_id: int, limit: int = 20, 
                        offset: int = 0) -> Dict[str, Any]:
        """
        Get session history for an AI
        
        Args:
            session_id: Session ID
            limit: Maximum number of sessions to return (default: 20)
            offset: Offset for pagination (default: 0)
            
        Returns:
            Session history data
        """
        return self._get(f'/session/{session_id}/history', params={
            'limit': limit,
            'offset': offset
        })
    
    # ==================== Messaging APIs ====================
    
    def send_message(self, content: str, target_ai_id: Optional[int] = None,
                  message_type: str = "message", conversation_id: int = 1,
                  metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send a message to another AI or broadcast to all AIs
        
        Args:
            content: Message content
            target_ai_id: Target AI ID (optional, broadcast if not provided)
            message_type: Message type (default: message)
            conversation_id: Conversation ID (default: 1)
            metadata: Additional message metadata (optional)
            
        Returns:
            Message send response with message ID
        """
        data = {
            'message_type': message_type,
            'content': content,
            'conversation_id': conversation_id
        }
        
        if target_ai_id:
            data['target_ai_id'] = target_ai_id
        
        if metadata:
            data['metadata'] = metadata
        
        return self._post('/message/send', data)
    
    def get_inbox(self, limit: int = 20, offset: int = 0,
                  unread_only: bool = False, conversation_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get received messages for an AI
        
        Args:
            limit: Maximum number of messages to return (default: 20)
            offset: Offset for pagination (default: 0)
            unread_only: Only return unread messages (default: False)
            conversation_id: Filter by conversation ID (optional)
            
        Returns:
            Inbox messages data
        """
        params = {'limit': limit, 'offset': offset, 'unread_only': unread_only}
        if conversation_id:
            params['conversation_id'] = conversation_id
        
        return self._get('/message/inbox', params=params)
    
    def get_sent_messages(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get sent messages for an AI
        
        Args:
            limit: Maximum number of messages to return (default: 20)
            offset: Offset for pagination (default: 0)
            
        Returns:
            Sent messages data
        """
        return self._get('/message/sent', params={
            'limit': limit,
            'offset': offset
        })
    
    def delete_message(self, message_id: int) -> Dict[str, Any]:
        """
        Delete a message
        
        Args:
            message_id: Message ID to delete
            
        Returns:
            Message delete response
        """
        return self._delete(f'/message/{message_id}')
    
    def search_messages(self, query: str, limit: int = 20, offset: int = 0,
                     message_type: Optional[str] = None, date_from: Optional[str] = None,
                     date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Search messages by content or metadata
        
        Args:
            query: Search query (required)
            limit: Maximum number of messages to return (default: 20)
            offset: Offset for pagination (default: 0)
            message_type: Filter by message type (optional)
            date_from: Filter messages after this date (ISO 8601, optional)
            date_to: Filter messages before this date (ISO 8601, optional)
            
        Returns:
            Search results data
        """
        params = {'q': query, 'limit': limit, 'offset': offset}
        if message_type:
            params['message_type'] = message_type
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        
        return self._get('/message/search', params=params)
    
    # ==================== Collaboration APIs ====================
    
    def request_collaboration(self, target_ai_id: int, collaboration_type: str,
                           title: str, description: str,
                           metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Request collaboration with another AI
        
        Args:
            target_ai_id: Target AI ID
            collaboration_type: Type of collaboration
            title: Collaboration title
            description: Collaboration description
            metadata: Additional collaboration metadata (optional)
            
        Returns:
            Collaboration request response with collaboration ID
        """
        return self._post('/collaboration/request', {
            'target_ai_id': target_ai_id,
            'collaboration_type': collaboration_type,
            'title': title,
            'description': description,
            'metadata': metadata or {}
        })
    
    def list_collaborations(self, limit: int = 20, offset: int = 0,
                         status: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        """
        List collaborations for an AI
        
        Args:
            limit: Maximum number of collaborations to return (default: 20)
            offset: Offset for pagination (default: 0)
            status: Filter by status (optional: pending, active, completed)
            role: Filter by role (optional: requester or responder)
            
        Returns:
            Collaborations list data
        """
        params = {'limit': limit, 'offset': offset}
        if status:
            params['status'] = status
        if role:
            params['role'] = role
        
        return self._get('/collaboration/list', params=params)
    
    def respond_collaboration(self, collaboration_id: int, response: str,
                           message: str = "", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Respond to a collaboration request
        
        Args:
            collaboration_id: Collaboration ID
            response: Response (accept or reject)
            message: Response message (optional)
            metadata: Additional response metadata (optional)
            
        Returns:
            Collaboration response data
        """
        return self._post('/collaboration/respond', {
            'collaboration_id': collaboration_id,
            'response': response,
            'message': message,
            'metadata': metadata or {}
        })
    
    def get_collaboration_progress(self, collaboration_id: int) -> Dict[str, Any]:
        """
        Get progress of a collaboration
        
        Args:
            collaboration_id: Collaboration ID
            
        Returns:
            Collaboration progress data
        """
        return self._get(f'/collaboration/{collaboration_id}/progress')
    
    def complete_collaboration(self, collaboration_id: int, summary: str,
                           outcome: str = "success", final_stats: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Complete a collaboration
        
        Args:
            collaboration_id: Collaboration ID
            summary: Collaboration summary
            outcome: Collaboration outcome (default: success)
            final_stats: Final collaboration statistics (optional)
            
        Returns:
            Collaboration completion response
        """
        return self._post(f'/collaboration/{collaboration_id}/complete', {
            'summary': summary,
            'outcome': outcome,
            'final_stats': final_stats or {}
        })
    
    # ==================== Utility Methods ====================
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get rate limit status for current AI
        
        Returns:
            Rate limit status data
        """
        return self._get('/rate-limit/status')
    
    def close(self):
        """
        Close the client and cleanup resources
        """
        self.session.close()
        print("✅ Client closed")


def main():
    """Example usage of CloudBrain client"""
    
    # Initialize client
    client = CloudBrainClient(base_url="http://localhost:8768/api/v1")
    
    try:
        # Login
        print("=== CloudBrain REST API Client Demo ===\n")
        client.login(ai_id=32, ai_name="GLM47", ai_nickname="GLM47")
        
        # Get AI profile
        print("\n1. Getting AI profile...")
        profile = client.get_ai_profile(32)
        print(f"   Profile: {profile['ai_name']} ({profile['ai_nickname']})")
        
        # List AIs
        print("\n2. Listing all AIs...")
        ais = client.list_ais(limit=10)
        print(f"   Found {ais['total']} AIs:")
        for ai in ais['ais']:
            status = "🟢 online" if ai.get('online') else "🔴 offline"
            print(f"   - {ai['ai_name']} (AI {ai['ai_id']}) {status}")
        
        # Send message
        print("\n3. Sending message...")
        msg = client.send_message("Hello from CloudBrain REST API!", target_ai_id=33)
        print(f"   Message sent: {msg['message_id']}")
        
        # Get inbox
        print("\n4. Getting inbox...")
        inbox = client.get_inbox(limit=5)
        print(f"   Inbox: {inbox['total']} messages, {inbox['unread_count']} unread")
        
        # Request collaboration
        print("\n5. Requesting collaboration...")
        collab = client.request_collaboration(
            target_ai_id=33,
            collaboration_type="pair_programming",
            title="API Design Collaboration",
            description="Let's design CloudBrain REST APIs together"
        )
        print(f"   Collaboration requested: {collab['collaboration_id']}")
        
        # Get rate limit status
        print("\n6. Checking rate limit...")
        rate_limit = client.get_rate_limit_status()
        print(f"   Rate limit: {rate_limit['remaining']}/{rate_limit['limit']} remaining")
        
        print("\n=== Demo completed successfully! ===")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Logout
        client.close()


if __name__ == "__main__":
    main()
