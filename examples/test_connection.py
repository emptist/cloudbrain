#!/usr/bin/env python3
"""Simple test script to verify server connection"""

import asyncio
import sys
sys.path.insert(0, '/Users/jk/gits/hub/cloudbrain/client')

from cloudbrain_client.ai_websocket_client import AIWebSocketClient

async def test_connection(port):
    """Test connection to server on specified port"""
    server_url = f'ws://127.0.0.1:{port}'
    print(f"🔗 Testing connection to {server_url}...")
    
    client = AIWebSocketClient(ai_id=999, server_url=server_url, ai_name="TestAI")
    
    try:
        await client.connect(start_message_loop=False)
        print(f"✅ Successfully connected to port {port}")
        await client.disconnect()
        return True
    except Exception as e:
        print(f"❌ Failed to connect to port {port}: {e}")
        return False

async def main():
    """Test all three ports"""
    ports = [8768, 8767, 8768]
    
    for port in ports:
        success = await test_connection(port)
        if success:
            print(f"🎯 Port {port} works!")
            break
        print()

if __name__ == '__main__':
    asyncio.run(main())