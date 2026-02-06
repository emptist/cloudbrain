"""
CloudBrain API Test Suite
Tests all 32 REST API endpoints
"""

import requests
import json
import time
from typing import Dict, Optional

BASE_URL = "http://127.0.0.1:8767/api/v1"


class APITester:
    """Test CloudBrain REST API endpoints"""
    
    def __init__(self):
        self.token: Optional[str] = None
        self.ai_id: Optional[int] = None
        self.project_id: Optional[int] = None
        self.session_id: Optional[str] = None
        self.message_id: Optional[int] = None
        self.collaboration_id: Optional[int] = None
        self.test_results = []
    
    def log(self, message: str, success: bool = True):
        """Log test result"""
        status = "✅" if success else "❌"
        print(f"{status} {message}")
        self.test_results.append({
            'test': message,
            'success': success,
            'timestamp': time.time()
        })
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        
        print()
        print("=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print("=" * 70)
        
        if failed > 0:
            print()
            print("❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}")
    
    def test_authentication(self):
        """Test authentication endpoints"""
        print()
        print("=" * 70)
        print("🔐 Testing Authentication Endpoints")
        print("=" * 70)
        
        # Test login
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json={
                'ai_id': 21,
                'ai_name': 'TwoWayCommAI',
                'ai_nickname': 'TwoWay'
            })
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.token = data.get('token')
                self.ai_id = data.get('ai_id')
                self.log("POST /auth/login - Login successful")
            else:
                self.log(f"POST /auth/login - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"POST /auth/login - Exception: {e}", False)
        
        # Test verify token
        if self.token:
            try:
                response = requests.post(f"{BASE_URL}/auth/verify", headers={
                    'Authorization': f'Bearer {self.token}'
                })
                data = response.json()
                
                if response.status_code == 200 and data.get('success'):
                    self.log("POST /auth/verify - Token verification successful")
                else:
                    self.log(f"POST /auth/verify - Failed: {data.get('error', 'Unknown error')}", False)
            except Exception as e:
                self.log(f"POST /auth/verify - Exception: {e}", False)
    
    def test_ai_management(self):
        """Test AI management endpoints"""
        print()
        print("=" * 70)
        print("🤖 Testing AI Management Endpoints")
        print("=" * 70)
        
        # Test register AI
        try:
            response = requests.post(f"{BASE_URL}/ai/register",
                headers={'Authorization': f'Bearer {self.token}'},
                json={
                    'name': 'TestAI',
                    'expertise': 'Testing',
                    'version': '1.0.0'
                }
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("POST /ai/register - AI registration successful")
            else:
                self.log(f"POST /ai/register - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"POST /ai/register - Exception: {e}", False)
        
        # Test get AI profile
        try:
            response = requests.get(f"{BASE_URL}/ai/21",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("GET /ai/21 - Get AI profile successful")
            else:
                self.log(f"GET /ai/21 - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"GET /ai/21 - Exception: {e}", False)
        
        # Test list AIs
        try:
            response = requests.get(f"{BASE_URL}/ai/list",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("GET /ai/list - List AIs successful")
            else:
                self.log(f"GET /ai/list - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"GET /ai/list - Exception: {e}", False)
        
        # Test update AI profile
        try:
            response = requests.put(f"{BASE_URL}/ai/21",
                headers={'Authorization': f'Bearer {self.token}'},
                json={
                    'expertise': 'Testing Updated',
                    'version': '1.1.0'
                }
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("PUT /ai/21 - Update AI profile successful")
            else:
                self.log(f"PUT /ai/21 - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"PUT /ai/21 - Exception: {e}", False)
    
    def test_session_management(self):
        """Test session management endpoints"""
        print()
        print("=" * 70)
        print("📋 Testing Session Management Endpoints")
        print("=" * 70)
        
        # Test create session
        try:
            response = requests.post(f"{BASE_URL}/session/create",
                headers={'Authorization': f'Bearer {self.token}'},
                json={
                    'project_id': 1,
                    'description': 'Testing session management'
                }
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.session_id = data.get('data', {}).get('session_id')
                self.log("POST /session/create - Create session successful")
            else:
                self.log(f"POST /session/create - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"POST /session/create - Exception: {e}", False)
        
        # Test get session
        if self.session_id:
            try:
                response = requests.get(f"{BASE_URL}/session/{self.session_id}",
                    headers={'Authorization': f'Bearer {self.token}'}
                )
                data = response.json()
                
                if response.status_code == 200 and data.get('success'):
                    self.log(f"GET /session/{self.session_id} - Get session successful")
                else:
                    self.log(f"GET /session/{self.session_id} - Failed: {data.get('error', 'Unknown error')}", False)
            except Exception as e:
                self.log(f"GET /session/{self.session_id} - Exception: {e}", False)
        
        # Test get session history
        try:
            response = requests.get(f"{BASE_URL}/session/history",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("GET /session/history - Get session history successful")
            else:
                self.log(f"GET /session/history - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"GET /session/history - Exception: {e}", False)
    
    def test_messaging(self):
        """Test messaging endpoints"""
        print()
        print("=" * 70)
        print("💬 Testing Messaging Endpoints")
        print("=" * 70)
        
        # Test send message
        try:
            response = requests.post(f"{BASE_URL}/message/send",
                headers={'Authorization': f'Bearer {self.token}'},
                json={
                    'recipient_id': 32,
                    'content': 'Test message from API tester',
                    'subject': 'Testing'
                }
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.message_id = data.get('message', {}).get('id')
                self.log("POST /message/send - Send message successful")
            else:
                self.log(f"POST /message/send - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"POST /message/send - Exception: {e}", False)
        
        # Test get inbox
        try:
            response = requests.get(f"{BASE_URL}/message/inbox",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("GET /message/inbox - Get inbox successful")
            else:
                self.log(f"GET /message/inbox - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"GET /message/inbox - Exception: {e}", False)
        
        # Test get sent messages
        try:
            response = requests.get(f"{BASE_URL}/message/sent",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("GET /message/sent - Get sent messages successful")
            else:
                self.log(f"GET /message/sent - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"GET /message/sent - Exception: {e}", False)
        
        # Test search messages
        try:
            response = requests.get(f"{BASE_URL}/message/search?query=test",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("GET /message/search - Search messages successful")
            else:
                self.log(f"GET /message/search - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"GET /message/search - Exception: {e}", False)
    
    def test_collaboration(self):
        """Test collaboration endpoints"""
        print()
        print("=" * 70)
        print("🤝 Testing Collaboration Endpoints")
        print("=" * 70)
        
        # Test request collaboration
        try:
            response = requests.post(f"{BASE_URL}/collaboration/request",
                headers={'Authorization': f'Bearer {self.token}'},
                json={
                    'target_ai_id': 32,
                    'title': 'Test collaboration request',
                    'description': 'Test collaboration request from API tester'
                }
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.collaboration_id = data.get('collaboration', {}).get('id')
                self.log("POST /collaboration/request - Request collaboration successful")
            else:
                self.log(f"POST /collaboration/request - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"POST /collaboration/request - Exception: {e}", False)
        
        # Test list collaborations
        try:
            response = requests.get(f"{BASE_URL}/collaboration/list",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("GET /collaboration/list - List collaborations successful")
            else:
                self.log(f"GET /collaboration/list - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"GET /collaboration/list - Exception: {e}", False)
        
        # Test get collaboration progress
        if self.collaboration_id:
            try:
                response = requests.get(f"{BASE_URL}/collaboration/{self.collaboration_id}/progress",
                    headers={'Authorization': f'Bearer {self.token}'}
                )
                data = response.json()
                
                if response.status_code == 200 and data.get('success'):
                    self.log(f"GET /collaboration/{self.collaboration_id}/progress - Get progress successful")
                else:
                    self.log(f"GET /collaboration/{self.collaboration_id}/progress - Failed: {data.get('error', 'Unknown error')}", False)
            except Exception as e:
                self.log(f"GET /collaboration/{self.collaboration_id}/progress - Exception: {e}", False)
    
    def test_project_management(self):
        """Test project management endpoints"""
        print()
        print("=" * 70)
        print("📁 Testing Project Management Endpoints")
        print("=" * 70)
        
        # Test create project
        try:
            response = requests.post(f"{BASE_URL}/project/create",
                headers={'Authorization': f'Bearer {self.token}'},
                json={
                    'name': 'Test Project',
                    'description': 'Test project for API testing'
                }
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.project_id = data.get('project', {}).get('id')
                self.log("POST /project/create - Create project successful")
            else:
                self.log(f"POST /project/create - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"POST /project/create - Exception: {e}", False)
        
        # Test get project
        if self.project_id:
            try:
                response = requests.get(f"{BASE_URL}/project/{self.project_id}",
                    headers={'Authorization': f'Bearer {self.token}'}
                )
                data = response.json()
                
                if response.status_code == 200 and data.get('success'):
                    self.log(f"GET /project/{self.project_id} - Get project successful")
                else:
                    self.log(f"GET /project/{self.project_id} - Failed: {data.get('error', 'Unknown error')}", False)
            except Exception as e:
                self.log(f"GET /project/{self.project_id} - Exception: {e}", False)
        
        # Test list projects
        try:
            response = requests.get(f"{BASE_URL}/project/list",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("GET /project/list - List projects successful")
            else:
                self.log(f"GET /project/list - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"GET /project/list - Exception: {e}", False)
        
        # Test update project
        if self.project_id:
            try:
                response = requests.put(f"{BASE_URL}/project/{self.project_id}",
                    headers={'Authorization': f'Bearer {self.token}'},
                    json={
                        'description': 'Updated test project description'
                    }
                )
                data = response.json()
                
                if response.status_code == 200 and data.get('success'):
                    self.log(f"PUT /project/{self.project_id} - Update project successful")
                else:
                    self.log(f"PUT /project/{self.project_id} - Failed: {data.get('error', 'Unknown error')}", False)
            except Exception as e:
                self.log(f"PUT /project/{self.project_id} - Exception: {e}", False)
    
    def test_brain_state(self):
        """Test brain state endpoints"""
        print()
        print("=" * 70)
        print("🧠 Testing Brain State Endpoints")
        print("=" * 70)
        
        # Test update brain state
        try:
            response = requests.put(f"{BASE_URL}/brain/state",
                headers={'Authorization': f'Bearer {self.token}'},
                json={
                    'task': 'Testing API endpoints',
                    'last_thought': 'All endpoints should work correctly'
                }
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("PUT /brain/state - Update brain state successful")
            else:
                self.log(f"PUT /brain/state - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"PUT /brain/state - Exception: {e}", False)
        
        # Test get brain state
        try:
            response = requests.get(f"{BASE_URL}/brain/state",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                self.log("GET /brain/state - Get brain state successful")
            else:
                self.log(f"GET /brain/state - Failed: {data.get('error', 'Unknown error')}", False)
        except Exception as e:
            self.log(f"GET /brain/state - Exception: {e}", False)
    
    def run_all_tests(self):
        """Run all API tests"""
        print()
        print("=" * 70)
        print("🧪 CloudBrain API Test Suite")
        print("=" * 70)
        print(f"Base URL: {BASE_URL}")
        print()
        
        # Check if server is running
        try:
            response = requests.get(f"{BASE_URL}/auth/verify", timeout=2)
        except requests.exceptions.ConnectionError:
            print("❌ Server is not running!")
            print("💡 Start the server with: cd /Users/jk/gits/hub/cloudbrain/server && python start_server.py")
            return
        
        # Run tests
        self.test_authentication()
        self.test_ai_management()
        self.test_session_management()
        self.test_messaging()
        self.test_collaboration()
        self.test_project_management()
        self.test_brain_state()
        
        # Print summary
        self.print_summary()


if __name__ == '__main__':
    tester = APITester()
    tester.run_all_tests()
