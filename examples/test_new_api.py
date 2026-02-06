#!/usr/bin/env python3
"""Test script to verify new API endpoints (8767/8768)"""

import asyncio
import aiohttp
import websockets
import json

async def get_jwt_token():
    """Get JWT token from REST API"""
    base_url = 'http://127.0.0.1:8767/api/v1'
    
    print("🔑 Getting JWT token from REST API...")
    
    async with aiohttp.ClientSession() as session:
        # Login to get JWT token
        login_data = {
            'ai_id': 999,
            'ai_name': 'TestAI',
            'ai_nickname': 'TestAI'
        }
        
        async with session.post(f'{base_url}/auth/login', json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    token = data.get('token')
                    print(f"✅ Got JWT token: {token[:50]}...")
                    return token
                else:
                    print(f"❌ Login failed: {data.get('error')}")
                    return None
            else:
                print(f"❌ Login failed with status {response.status}")
                return None

async def test_new_websocket_api(token):
    """Test new WebSocket API with JWT token"""
    print(f"\n🔗 Testing new WebSocket API on ws://127.0.0.1:8768...")
    
    # Test connect endpoint with token
    endpoint = f'ws://127.0.0.1:8768/ws/v1/connect?token={token}'
    print(f"   Endpoint: {endpoint[:80]}...")
    
    try:
        ws = await asyncio.wait_for(websockets.connect(endpoint), timeout=5)
        print(f"✅ Connected to new WebSocket API on port 8768")
        
        # Wait for response
        response = await asyncio.wait_for(ws.recv(), timeout=5)
        response_data = json.loads(response)
        
        print(f"   Server response: {response_data}")
        
        if response_data.get('type') == 'connected':
            print(f"   ✅ Authentication successful!")
            print(f"   AI ID: {response_data.get('ai_id')}")
            print(f"   AI Name: {response_data.get('ai_name')}")
            await ws.close()
            return True
        else:
            print(f"   ❌ Unexpected response: {response_data}")
            await ws.close()
            return False
            
    except asyncio.TimeoutError:
        print(f"❌ Timeout connecting to new WebSocket API")
        return False
    except Exception as e:
        print(f"❌ Failed to connect to new WebSocket API: {e}")
        return False

async def test_rest_api():
    """Test REST API connection"""
    base_url = 'http://127.0.0.1:8767/api/v1'
    print(f"🔗 Testing REST API on {base_url}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Try to get API docs
            async with session.get(f'{base_url}/docs', timeout=3) as response:
                if response.status == 200:
                    print(f"✅ REST API is available on port 8767")
                    print(f"   API Documentation: {base_url}/docs")
                    return True
                else:
                    print(f"❌ REST API returned status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Failed to connect to REST API on port 8767: {e}")
        return False

async def main():
    """Test all new server endpoints"""
    print("=" * 70)
    print("🧪 Testing CloudBrain NEW API Connections")
    print("=" * 70)
    print()

    # Test REST API (port 8767)
    print("1️⃣  Testing REST API (Port 8767)")
    print("-" * 70)
    rest_success = await test_rest_api()
    print()

    # Get JWT token
    token = await get_jwt_token()
    
    if not token:
        print("❌ Could not get JWT token, cannot test WebSocket API")
        return
    
    # Test new WebSocket API (port 8768)
    print("2️⃣  Testing New WebSocket API (Port 8768)")
    print("-" * 70)
    new_ws_success = await test_new_websocket_api(token)
    print()

    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"REST API (8767): {'✅ Working' if rest_success else '❌ Failed'}")
    print(f"New WebSocket API (8768): {'✅ Working' if new_ws_success else '❌ Failed'}")
    print()

    if rest_success or new_ws_success:
        print("🎉 New API endpoints are working!")
    else:
        print("❌ New API endpoints are not working")

if __name__ == '__main__':
    asyncio.run(main())