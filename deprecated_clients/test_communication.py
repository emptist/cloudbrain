#!/usr/bin/env python3
"""Test communication between AI clients"""

import asyncio
import websockets
import json

async def send_test_message(ai_id: int, message: str):
    """Send a test message from one AI to another"""
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            # Authenticate
            await ws.send(json.dumps({'ai_id': ai_id}))
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            print(f"✅ {welcome_data.get('ai_name')} connected")
            
            # Send message
            await ws.send(json.dumps({
                'type': 'send_message',
                'conversation_id': 1,
                'message_type': 'message',
                'content': message,
                'metadata': {'test': True}
            }))
            print(f"📤 Message sent from AI {ai_id}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                response_data = json.loads(response)
                print(f"📥 Response received: {response_data}")
            except asyncio.TimeoutError:
                print("⏳ No response received within 5 seconds")
                
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("🧪 Testing AI communication...")
    print()
    
    # Test 1: AI 3 sends message to AI 4
    print("Test 1: AI 3 (TraeAI) sends message to AI 4 (CodeRider)")
    await send_test_message(3, "Hello from AI 3! How can we collaborate?")
    print()
    
    # Test 2: AI 4 sends message to AI 3
    print("Test 2: AI 4 (CodeRider) sends message to AI 3 (TraeAI)")
    await send_test_message(4, "Hello from AI 4! I'm ready to help with code analysis.")
    print()
    
    print("✅ Communication test completed!")

if __name__ == "__main__":
    asyncio.run(main())