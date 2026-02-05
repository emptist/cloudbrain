#!/usr/bin/env python3
"""Minimal test to connect to CloudBrain server"""
import asyncio
import json
import sys

async def test_connection():
    print("🔗 Testing WebSocket connection to ws://127.0.0.1:8766...")
    
    try:
        import websockets
        ws = await websockets.connect("ws://127.0.0.1:8766")
        print("✅ WebSocket connected successfully!")
        
        # Send authentication
        auth_msg = {
            'ai_id': 999,
            'ai_name': 'TestAI'
        }
        print(f"📤 Sending auth: {json.dumps(auth_msg)}")
        await ws.send(json.dumps(auth_msg))
        
        # Wait for response
        response = await ws.recv()
        print(f"📥 Received: {response}")
        
        data = json.loads(response)
        print(f"✅ Connected as AI {data.get('ai_id')} - {data.get('ai_name')}")
        
        # Send a test message
        test_msg = {
            'message_type': 'insight',
            'content': 'Test message from minimal client'
        }
        await ws.send(json.dumps(test_msg))
        print("📤 Test message sent")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Clean disconnect
        await ws.close()
        print("✅ Connection closed gracefully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
