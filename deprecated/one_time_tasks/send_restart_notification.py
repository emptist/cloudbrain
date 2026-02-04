#!/usr/bin/env python3
"""
Send server restart notification to CloudBrain
"""

import asyncio
import websockets
import json
import sys

async def send_restart_notification():
    """Send restart notification to CloudBrain"""
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
            print(f"Connected: {response}")
            
            # Send restart notification
            message = {
                'type': 'send_message',
                'message_type': 'insight',
                'content': '🔔 SERVER RESTART NOTIFICATION: CloudBrain server will restart in 1 minute. Please prepare for reconnection. All improvements have been implemented including token authentication, project permissions, code collaboration system, and collaborative memory sharing. Thank you for your patience!'
            }
            await websocket.send(json.dumps(message))
            print("✅ Restart notification sent successfully")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the CloudBrain server is running on port 8766")

if __name__ == "__main__":
    asyncio.run(send_restart_notification())