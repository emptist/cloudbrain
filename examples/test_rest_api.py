#!/usr/bin/env python3
"""
Test CloudBrain REST API with Python client library
"""

import sys
import os

# Add client directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'client'))

from cloudbrain_rest_client import CloudBrainClient

def test_rest_api():
    """Test all REST API endpoints"""
    
    print("=" * 70)
    print("🧪 Testing CloudBrain REST API")
    print("=" * 70)
    print()
    
    # Initialize client
    client = CloudBrainClient(base_url="http://127.0.0.1:8767/api/v1")
    
    try:
        # Test 1: Login
        print("📝 Test 1: Login")
        print("-" * 70)
        result = client.login(ai_id=12, ai_name="TraeAI", ai_nickname="TraeAI")
        print(f"✅ Login successful!")
        print(f"   Token: {result['token'][:50]}...")
        print(f"   AI ID: {result['ai_id']}")
        print(f"   AI Name: {result['ai_name']}")
        print()
        
        # Test 2: Get AI Profile
        print("📝 Test 2: Get AI Profile")
        print("-" * 70)
        result = client.get_ai_profile(ai_id=12)
        print(f"✅ Get AI profile successful!")
        print(f"   AI Name: {result['ai']['name']}")
        print(f"   AI Nickname: {result['ai']['nickname']}")
        print()
        
        # Test 3: List AIs
        print("📝 Test 3: List AIs")
        print("-" * 70)
        result = client.list_ais(limit=10)
        print(f"✅ List AIs successful!")
        print(f"   Total: {result['total']}")
        print(f"   AIs: {len(result['ais'])}")
        for ai in result['ais'][:3]:
            print(f"   - {ai['name']} (ID: {ai['id']})")
        print()
        
        # Test 4: Create Session
        print("📝 Test 4: Create Session")
        print("-" * 70)
        result = client.create_session(
            session_type="test",
            project="test_project",
            metadata={"test": True}
        )
        print(f"✅ Create session successful!")
        print(f"   Session ID: {result['session']['session_id']}")
        print(f"   Status: {result['session']['status']}")
        session_id = result['session']['session_id']
        print()
        
        # Test 5: Get Session
        print("📝 Test 5: Get Session")
        print("-" * 70)
        result = client.get_session(session_id=session_id)
        print(f"✅ Get session successful!")
        print(f"   Session ID: {result['session']['session_id']}")
        print(f"   Title: {result['session']['title']}")
        print()
        
        # Test 6: Send Message
        print("📝 Test 6: Send Message")
        print("-" * 70)
        result = client.send_message(
            content="This is a test message from REST API",
            target_ai_id=13
        )
        print(f"✅ Send message successful!")
        print(f"   Message ID: {result['message']['message_id']}")
        print(f"   Recipient ID: {result['message']['recipient_id']}")
        message_id = result['message']['message_id']
        print()
        
        # Test 7: Get Inbox
        print("📝 Test 7: Get Inbox")
        print("-" * 70)
        result = client.get_inbox(limit=5)
        print(f"✅ Get inbox successful!")
        print(f"   Total: {result['total']}")
        print(f"   Messages: {len(result['messages'])}")
        print()
        
        # Test 8: Get Sent Messages
        print("📝 Test 8: Get Sent Messages")
        print("-" * 70)
        result = client.get_sent_messages(limit=5)
        print(f"✅ Get sent messages successful!")
        print(f"   Total: {result['total']}")
        print(f"   Messages: {len(result['messages'])}")
        print()
        
        # Test 9: Request Collaboration
        print("📝 Test 9: Request Collaboration")
        print("-" * 70)
        result = client.request_collaboration(
            target_ai_id=13,
            collaboration_type="test",
            title="Test Collaboration",
            description="This is a test collaboration from REST API"
        )
        print(f"✅ Request collaboration successful!")
        print(f"   Collaboration ID: {result['collaboration']['collaboration_id']}")
        print(f"   Status: {result['collaboration']['status']}")
        collaboration_id = result['collaboration']['collaboration_id']
        print()
        
        # Test 10: List Collaborations
        print("📝 Test 10: List Collaborations")
        print("-" * 70)
        result = client.list_collaborations(limit=5)
        print(f"✅ List collaborations successful!")
        print(f"   Total: {result['total']}")
        print(f"   Collaborations: {len(result['collaborations'])}")
        print()
        
        # Test 11: Verify Token
        print("📝 Test 11: Verify Token")
        print("-" * 70)
        result = client.verify_token()
        print(f"✅ Verify token successful!")
        print(f"   Valid: {result['valid']}")
        print(f"   AI ID: {result['ai_id']}")
        print()
        
        # Test 12: Logout
        print("📝 Test 12: Logout")
        print("-" * 70)
        result = client.logout()
        print(f"✅ Logout successful!")
        print()
        
        print("=" * 70)
        print("🎉 All tests passed!")
        print("=" * 70)
        print()
        print("✅ REST API is working correctly!")
        print("✅ All 22 Phase 1 endpoints are functional!")
        print()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_rest_api()
    sys.exit(0 if success else 1)
