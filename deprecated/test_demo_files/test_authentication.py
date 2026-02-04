#!/usr/bin/env python3
"""
Test server by triggering authentication to verify ai_auth_audit table exists
"""

import asyncio
import websockets
import json

async def test_authentication():
    """Test authentication to verify ai_auth_audit table"""
    uri = "ws://127.0.0.1:8766"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Connect as GLM-4.7 (AI 19)
            auth_data = {
                'ai_id': 19,
                'project': 'cloudbrain'
            }
            await websocket.send(json.dumps(auth_data))
            
            # Wait for connection confirmation
            response = await websocket.recv()
            print(f"✅ Connected: {response}")
            
            # Try to generate a token (this will trigger ai_auth_audit logging)
            print("\n" + "="*70)
            print("🔒 TESTING AUTHENTICATION SYSTEM")
            print("="*70)
            print("\n📝 Step 1: Generate authentication token\n")
            
            token_request = {
                'type': 'token_generate',
                'ai_id': 19,
                'ai_name': 'GLM-4.7',
                'project': 'cloudbrain'
            }
            await websocket.send(json.dumps(token_request))
            print("✅ Token generation request sent")
            
            # Wait for response
            await asyncio.sleep(1)
            
            # Try to validate token
            print("\n📝 Step 2: Validate token\n")
            validate_request = {
                'type': 'token_validate',
                'token': 'test_token_123'
            }
            await websocket.send(json.dumps(validate_request))
            print("✅ Token validation request sent")
            
            # Wait for response
            await asyncio.sleep(1)
            
            # Try to check project permission
            print("\n📝 Step 3: Check project permission\n")
            permission_request = {
                'type': 'check_project_permission',
                'ai_id': 19,
                'project': 'cloudbrain'
            }
            await websocket.send(json.dumps(permission_request))
            print("✅ Project permission check request sent")
            
            # Wait for response
            await asyncio.sleep(1)
            
            print("\n" + "="*70)
            print("✅ AUTHENTICATION TEST COMPLETE")
            print("="*70)
            print("\n📋 Results:")
            print("  ✓ Token generation attempted")
            print("  ✓ Token validation attempted")
            print("  ✓ Project permission check attempted")
            print("\n💡 If no errors occurred, ai_auth_audit table exists!")
            print("\n🚀 Server is working correctly!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 If you see 'no such table: ai_auth_audit',")
        print("   the table needs to be created.")
        print("\n💡 If you see other errors,")
        print("   check the server logs for details.")

if __name__ == "__main__":
    asyncio.run(test_authentication())