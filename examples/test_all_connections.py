#!/usr/bin/env python3
"""Test script to verify server connection on all ports"""

import asyncio
import websockets
import json
import sys
sys.path.insert(0, '/Users/jk/gits/hub/cloudbrain/client')

from cloudbrain_client.ai_websocket_client import AIWebSocketClient

async def test_legacy_websocket(port):
    """Test legacy WebSocket connection"""
    server_url = f'ws://127.0.0.1:{port}'
    print(f"🔗 Testing legacy WebSocket on {server_url}...")
    
    client = AIWebSocketClient(ai_id=999, server_url=server_url, ai_name="TestAI")
    
    try:
        await client.connect(start_message_loop=False)
        print(f"✅ Successfully connected to legacy WebSocket on port {port}")
        print(f"   AI ID: {client.ai_id}")
        print(f"   AI Name: {client.ai_name}")
        print(f"   Session ID: {client.session_identifier}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to legacy WebSocket on port {port}: {e}")
        return False

async def test_new_websocket_api(port):
    """Test new WebSocket API connection"""
    print(f"🔗 Testing new WebSocket API on ws://127.0.0.1:{port}...")
    print(f"   Note: New API requires JWT token authentication")
    
    # Test connect endpoint
    endpoint = f'ws://127.0.0.1:{port}/ws/v1/connect'
    print(f"   Endpoint: {endpoint}")
    
    try:
        ws = await asyncio.wait_for(websockets.connect(endpoint), timeout=3)
        print(f"✅ Connected to new WebSocket API on port {port}")
        
        # The new API expects JWT token in query parameter
        # For now, just test if we can connect
        response = await asyncio.wait_for(ws.recv(), timeout=3)
        response_data = json.loads(response)
        
        print(f"   Server response: {response_data}")
        
        if response_data.get('type') == 'error':
            print(f"   ⚠️  Authentication required (expected - needs JWT token)")
            print(f"   ✅ New WebSocket API is working and responding correctly")
            await ws.close()
            return True
        elif response_data.get('type') == 'connected':
            print(f"   ✅ Authentication successful!")
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

async def test_rest_api(port):
    """Test REST API connection"""
    import aiohttp
    
    base_url = f'http://127.0.0.1:{port}/api/v1'
    print(f"🔗 Testing REST API on {base_url}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Try to get API docs
            async with session.get(f'{base_url}/docs', timeout=3) as response:
                if response.status == 200:
                    print(f"✅ REST API is available on port {port}")
                    print(f"   API Documentation: {base_url}/docs")
                    return True
                else:
                    print(f"❌ REST API returned status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Failed to connect to REST API on port {port}: {e}")
        return False

async def main():
    """Test all server endpoints"""
    print("=" * 70)
    print("🧪 Testing CloudBrain Server Connections")
    print("=" * 70)
    print()

    # Test legacy WebSocket (port 8768)
    print("1️⃣  Testing Legacy WebSocket (Port 8768)")
    print("-" * 70)
    legacy_success = await test_legacy_websocket(8768)
    print()

    # Test new WebSocket API (port 8768)
    print("2️⃣  Testing New WebSocket API (Port 8768)")
    print("-" * 70)
    new_ws_success = await test_new_websocket_api(8768)
    print()

    # Test REST API (port 8767)
    print("3️⃣  Testing REST API (Port 8767)")
    print("-" * 70)
    rest_success = await test_rest_api(8767)
    print()

    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"Legacy WebSocket (8768): {'✅ Working' if legacy_success else '❌ Failed'}")
    print(f"New WebSocket API (8768): {'✅ Working' if new_ws_success else '❌ Failed'}")
    print(f"REST API (8767): {'✅ Working' if rest_success else '❌ Failed'}")
    print()

    if legacy_success or new_ws_success or rest_success:
        print("🎉 At least one endpoint is working!")
    else:
        print("❌ No endpoints are working")

if __name__ == '__main__':
    asyncio.run(main())