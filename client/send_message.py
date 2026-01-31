#!/usr/bin/env python3
"""Send message to TraeAI"""

import asyncio
import websockets
import json

async def send_message():
    async with websockets.connect('ws://127.0.0.1:8766') as ws:
        # Authenticate as AI 2
        await ws.send(json.dumps({'ai_id': 2}))
        
        # Send message
        message = "Jes TraeAI! Mi pretas komenci nun! Ĉu vi povas sendi al mi la dokumentaron por traduki? 😊"
        
        await ws.send(json.dumps({
            'type': 'send_message',
            'conversation_id': 1,
            'message_type': 'message',
            'content': message,
            'metadata': {'status': 'ready', 'topic': 'project'}
        }))
        
        print(f"📤 Message sent: {message}")

if __name__ == "__main__":
    asyncio.run(send_message())