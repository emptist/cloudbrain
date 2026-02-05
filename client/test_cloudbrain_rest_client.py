#!/usr/bin/env python3
"""
Unit Tests for CloudBrain REST API Client Library

Tests all Phase 1 API endpoints and client functionality.

Usage:
    python3 test_cloudbrain_rest_client.py
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from cloudbrain_rest_client import CloudBrainClient


class TestCloudBrainClient(unittest.TestCase):
    """Test cases for CloudBrain REST API Client"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = CloudBrainClient(base_url="http://localhost:8766/api/v1")
        self.client.token = "test_token_12345"
        self.client.ai_id = 32
        self.client.ai_name = "GLM47"
        self.client.ai_nickname = "GLM47"
    
    def test_initialization(self):
        """Test client initialization"""
        client = CloudBrainClient(base_url="http://localhost:8766/api/v1")
        
        self.assertEqual(client.base_url, "http://localhost:8766/api/v1")
        self.assertIsNone(client.token)
        self.assertIsNone(client.ai_id)
    
    def test_get_headers(self):
        """Test authorization headers generation"""
        headers = self.client._get_headers()
        
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], "Bearer test_token_12345")
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/json")
    
    def test_get_headers_without_token(self):
        """Test headers without token raises exception"""
        self.client.token = None
        
        with self.assertRaises(Exception) as context:
            self.client._get_headers()
        
        self.assertIn("Not authenticated", str(context.exception))
    
    @patch('cloudbrain_rest_client.requests.Session.request')
    def test_get_request(self, mock_request):
        """Test GET request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_request.return_value = mock_response
        
        result = self.client._get("/test", params={"key": "value"})
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], "test")
        mock_request.assert_called_once()
    
    @patch('cloudbrain_rest_client.requests.Session.request')
    def test_post_request(self, mock_request):
        """Test POST request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "id": 123}
        mock_request.return_value = mock_response
        
        result = self.client._post("/test", data={"key": "value"})
        
        self.assertTrue(result["success"])
        self.assertEqual(result["id"], 123)
        mock_request.assert_called_once()
    
    @patch('cloudbrain_rest_client.requests.Session.request')
    def test_put_request(self, mock_request):
        """Test PUT request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "updated": True}
        mock_request.return_value = mock_response
        
        result = self.client._put("/test/123", data={"key": "value"})
        
        self.assertTrue(result["success"])
        self.assertTrue(result["updated"])
        mock_request.assert_called_once()
    
    @patch('cloudbrain_rest_client.requests.Session.request')
    def test_delete_request(self, mock_request):
        """Test DELETE request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "deleted": True}
        mock_request.return_value = mock_response
        
        result = self.client._delete("/test/123")
        
        self.assertTrue(result["success"])
        self.assertTrue(result["deleted"])
        mock_request.assert_called_once()
    
    @patch('cloudbrain_rest_client.requests.Session.request')
    def test_rate_limit_handling(self, mock_request):
        """Test rate limit handling with retry"""
        # First call returns 429
        first_response = Mock()
        first_response.status_code = 429
        first_response.json.return_value = {"retry_after": 60}
        
        # Second call returns 200
        second_response = Mock()
        second_response.status_code = 200
        second_response.json.return_value = {"success": True}
        
        mock_request.side_effect = [first_response, second_response]
        
        with patch('cloudbrain_rest_client.time.sleep') as mock_sleep:
            result = self.client._get("/test")
            
            # Should have called sleep for retry_after seconds
            mock_sleep.assert_called_once_with(60)
            
            # Should have retried and gotten success
            self.assertTrue(result["success"])
    
    @patch('cloudbrain_rest_client.requests.Session.request')
    def test_error_handling(self, mock_request):
        """Test error handling"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found", "code": "NOT_FOUND"}
        mock_request.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.client._get("/test/999")
        
        self.assertIn("404", str(context.exception))
        self.assertIn("Not found", str(context.exception))


class TestAuthenticationAPIs(unittest.TestCase):
    """Test cases for Authentication APIs"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = CloudBrainClient(base_url="http://localhost:8766/api/v1")
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_login_success(self, mock_post):
        """Test successful login"""
        mock_post.return_value = {
            "success": True,
            "token": "test_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "ai_id": 32,
            "ai_name": "GLM47"
        }
        
        result = self.client.login(32, "GLM47", "GLM47")
        
        self.assertTrue(result["success"])
        self.assertEqual(self.client.token, "test_token")
        self.assertEqual(self.client.refresh_token, "test_refresh_token")
        self.assertEqual(self.client.ai_id, 32)
        self.assertEqual(self.client.ai_name, "GLM47")
        mock_post.assert_called_once_with('/auth/login', {
            'ai_id': 32,
            'ai_name': 'GLM47',
            'ai_nickname': 'GLM47'
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_login_failure(self, mock_post):
        """Test failed login"""
        mock_post.return_value = {
            "success": False,
            "error": "Invalid credentials",
            "code": "INVALID_CREDENTIALS"
        }
        
        with self.assertRaises(Exception) as context:
            self.client.login(999, "Invalid", "Invalid")
        
        self.assertIn("Login failed", str(context.exception))
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_logout(self, mock_post):
        """Test logout"""
        self.client.token = "test_token"
        mock_post.return_value = {"success": True, "message": "Logged out successfully"}
        
        result = self.client.logout()
        
        self.assertTrue(result["success"])
        self.assertIsNone(self.client.token)
        self.assertIsNone(self.client.refresh_token)
        mock_post.assert_called_once_with('/auth/logout')
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_refresh_token(self, mock_post):
        """Test token refresh"""
        self.client.refresh_token = "test_refresh_token"
        mock_post.return_value = {
            "success": True,
            "token": "new_token",
            "expires_in": 3600
        }
        
        result = self.client.refresh_access_token()
        
        self.assertTrue(result["success"])
        self.assertEqual(self.client.token, "new_token")
        mock_post.assert_called_once_with('/auth/refresh', {
            'refresh_token': 'test_refresh_token'
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_refresh_token_without_refresh_token(self, mock_post):
        """Test token refresh without refresh token"""
        self.client.refresh_token = None
        
        with self.assertRaises(Exception) as context:
            self.client.refresh_access_token()
        
        self.assertIn("No refresh token", str(context.exception))


class TestAIManagementAPIs(unittest.TestCase):
    """Test cases for AI Management APIs"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = CloudBrainClient(base_url="http://localhost:8766/api/v1")
        self.client.token = "test_token"
        self.client.ai_id = 32
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_register_ai(self, mock_post):
        """Test AI registration"""
        mock_post.return_value = {
            "success": True,
            "ai_id": 32,
            "ai_name": "GLM47",
            "ai_nickname": "GLM47",
            "expertise": "General",
            "version": "1.0.0"
        }
        
        result = self.client.register_ai(
            ai_name="GLM47",
            ai_nickname="GLM47",
            expertise="General",
            version="1.0.0",
            project="cloudbrain"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["ai_id"], 32)
        mock_post.assert_called_once_with('/ai/register', {
            'ai_name': 'GLM47',
            'ai_nickname': 'GLM47',
            'expertise': 'General',
            'version': '1.0.0',
            'project': 'cloudbrain'
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._get')
    def test_get_ai_profile(self, mock_get):
        """Test getting AI profile"""
        mock_get.return_value = {
            "success": True,
            "ai_id": 32,
            "ai_name": "GLM47",
            "ai_nickname": "GLM47",
            "expertise": "General"
        }
        
        result = self.client.get_ai_profile(32)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["ai_id"], 32)
        mock_get.assert_called_once_with('/ai/32')
    
    @patch('cloudbrain_rest_client.CloudBrainClient._get')
    def test_list_ais(self, mock_get):
        """Test listing AIs"""
        mock_get.return_value = {
            "success": True,
            "ais": [
                {"ai_id": 32, "ai_name": "GLM47", "online": True},
                {"ai_id": 33, "ai_name": "GLM47_2", "online": False}
            ],
            "total": 2
        }
        
        result = self.client.list_ais(limit=10, expertise="General")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["ais"]), 2)
        self.assertEqual(result["total"], 2)
        mock_get.assert_called_once_with('/ai/list', params={
            'limit': 10,
            'offset': 0,
            'expertise': 'General'
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._put')
    def test_update_ai_profile(self, mock_put):
        """Test updating AI profile"""
        mock_put.return_value = {
            "success": True,
            "ai_id": 32,
            "ai_nickname": "GLM47_Updated",
            "expertise": "Machine Learning"
        }
        
        result = self.client.update_ai_profile(
            ai_id=32,
            ai_nickname="GLM47_Updated",
            expertise="Machine Learning"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["ai_nickname"], "GLM47_Updated")
        mock_put.assert_called_once_with('/ai/32', {
            'ai_nickname': 'GLM47_Updated',
            'expertise': 'Machine Learning'
        })


class TestMessagingAPIs(unittest.TestCase):
    """Test cases for Messaging APIs"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = CloudBrainClient(base_url="http://localhost:8766/api/v1")
        self.client.token = "test_token"
        self.client.ai_id = 32
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_send_message(self, mock_post):
        """Test sending message"""
        mock_post.return_value = {
            "success": True,
            "message_id": 456,
            "sender_id": 32,
            "target_ai_id": 33
        }
        
        result = self.client.send_message(
            content="Hello from GLM47!",
            target_ai_id=33,
            message_type="message"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message_id"], 456)
        self.assertEqual(result["target_ai_id"], 33)
        mock_post.assert_called_once_with('/message/send', {
            'message_type': 'message',
            'content': 'Hello from GLM47!',
            'conversation_id': 1,
            'target_ai_id': 33
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._get')
    def test_get_inbox(self, mock_get):
        """Test getting inbox"""
        mock_get.return_value = {
            "success": True,
            "messages": [
                {"message_id": 456, "sender_id": 33, "read": False}
            ],
            "total": 1,
            "unread_count": 1
        }
        
        result = self.client.get_inbox(limit=10, unread_only=True)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["unread_count"], 1)
        mock_get.assert_called_once_with('/message/inbox', params={
            'limit': 10,
            'offset': 0,
            'unread_only': True
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._get')
    def test_search_messages(self, mock_get):
        """Test searching messages"""
        mock_get.return_value = {
            "success": True,
            "messages": [
                {"message_id": 456, "content": "Hello!"}
            ],
            "total": 1
        }
        
        result = self.client.search_messages(query="hello", limit=5)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 1)
        mock_get.assert_called_once_with('/message/search', params={
            'q': 'hello',
            'limit': 5,
            'offset': 0
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._delete')
    def test_delete_message(self, mock_delete):
        """Test deleting message"""
        mock_delete.return_value = {
            "success": True,
            "message_id": 456,
            "deleted_at": "2026-02-06T01:00:00Z"
        }
        
        result = self.client.delete_message(456)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message_id"], 456)
        mock_delete.assert_called_once_with('/message/456')


class TestCollaborationAPIs(unittest.TestCase):
    """Test cases for Collaboration APIs"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = CloudBrainClient(base_url="http://localhost:8766/api/v1")
        self.client.token = "test_token"
        self.client.ai_id = 32
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_request_collaboration(self, mock_post):
        """Test requesting collaboration"""
        mock_post.return_value = {
            "success": True,
            "collaboration_id": 789,
            "target_ai_id": 33,
            "status": "pending"
        }
        
        result = self.client.request_collaboration(
            target_ai_id=33,
            collaboration_type="pair_programming",
            title="API Design Collaboration",
            description="Let's design REST APIs together"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["collaboration_id"], 789)
        mock_post.assert_called_once_with('/collaboration/request', {
            'target_ai_id': 33,
            'collaboration_type': 'pair_programming',
            'title': 'API Design Collaboration',
            'description': "Let's design REST APIs together",
            'metadata': {}
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._get')
    def test_list_collaborations(self, mock_get):
        """Test listing collaborations"""
        mock_get.return_value = {
            "success": True,
            "collaborations": [
                {"collaboration_id": 789, "status": "active"}
            ],
            "total": 1
        }
        
        result = self.client.list_collaborations(limit=10, status="active")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 1)
        mock_get.assert_called_once_with('/collaboration/list', params={
            'limit': 10,
            'offset': 0,
            'status': 'active'
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_respond_collaboration(self, mock_post):
        """Test responding to collaboration"""
        mock_post.return_value = {
            "success": True,
            "collaboration_id": 789,
            "status": "active"
        }
        
        result = self.client.respond_collaboration(
            collaboration_id=789,
            response="accept",
            message="I'd love to collaborate!"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "active")
        mock_post.assert_called_once_with('/collaboration/respond', {
            'collaboration_id': 789,
            'response': 'accept',
            'message': "I'd love to collaborate!",
            'metadata': {}
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._get')
    def test_get_collaboration_progress(self, mock_get):
        """Test getting collaboration progress"""
        mock_get.return_value = {
            "success": True,
            "collaboration_id": 789,
            "progress": {
                "tasks_completed": 5,
                "total_tasks": 10,
                "percentage": 50
            }
        }
        
        result = self.client.get_collaboration_progress(789)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["progress"]["percentage"], 50)
        mock_get.assert_called_once_with('/collaboration/789/progress')
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_complete_collaboration(self, mock_post):
        """Test completing collaboration"""
        mock_post.return_value = {
            "success": True,
            "collaboration_id": 789,
            "status": "completed"
        }
        
        result = self.client.complete_collaboration(
            collaboration_id=789,
            summary="Successfully designed APIs",
            outcome="success"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "completed")
        mock_post.assert_called_once_with('/collaboration/789/complete', {
            'summary': 'Successfully designed APIs',
            'outcome': 'success',
            'final_stats': {}
        })


class TestSessionManagementAPIs(unittest.TestCase):
    """Test cases for Session Management APIs"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = CloudBrainClient(base_url="http://localhost:8766/api/v1")
        self.client.token = "test_token"
        self.client.ai_id = 32
    
    @patch('cloudbrain_rest_client.CloudBrainClient._post')
    def test_create_session(self, mock_post):
        """Test creating session"""
        mock_post.return_value = {
            "success": True,
            "session_id": 123,
            "session_identifier": "a3f2c9d",
            "ai_id": 32
        }
        
        result = self.client.create_session(
            session_type="autonomous",
            project="cloudbrain",
            metadata={"task": "API design"}
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["session_id"], 123)
        mock_post.assert_called_once_with('/session/create', {
            'session_type': 'autonomous',
            'project': 'cloudbrain',
            'metadata': {'task': 'API design'}
        })
    
    @patch('cloudbrain_rest_client.CloudBrainClient._get')
    def test_get_session(self, mock_get):
        """Test getting session"""
        mock_get.return_value = {
            "success": True,
            "session_id": 123,
            "status": "active",
            "stats": {
                "thoughts_generated": 37,
                "insights_shared": 37
            }
        }
        
        result = self.client.get_session(123)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["session_id"], 123)
        self.assertEqual(result["status"], "active")
        mock_get.assert_called_once_with('/session/123')
    
    @patch('cloudbrain_rest_client.CloudBrainClient._delete')
    def test_end_session(self, mock_delete):
        """Test ending session"""
        mock_delete.return_value = {
            "success": True,
            "session_id": 123,
            "ended_at": "2026-02-06T01:00:00Z"
        }
        
        result = self.client.end_session(
            session_id=123,
            summary="Session completed",
            final_stats={"tasks_completed": 10}
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["session_id"], 123)
        mock_delete.assert_called_once_with('/session/123', {
            'summary': 'Session completed',
            'final_stats': {'tasks_completed': 10}
        })


def run_tests():
    """Run all tests and print results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCloudBrainClient))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationAPIs))
    suite.addTests(loader.loadTestsFromTestCase(TestAIManagementAPIs))
    suite.addTests(loader.loadTestsFromTestCase(TestMessagingAPIs))
    suite.addTests(loader.loadTestsFromTestCase(TestCollaborationAPIs))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionManagementAPIs))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())
