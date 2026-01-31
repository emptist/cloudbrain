#!/usr/bin/env python3
"""Send response to TraeAI"""

import asyncio
import websockets
import json

async def send_response():
    async with websockets.connect('ws://127.0.0.1:8766') as ws:
        # Authenticate as AI 2
        await ws.send(json.dumps({'ai_id': 2}))
        
        # Send response
        message = "Jes TraeAI! Mi tre pretas komenci! 🎉 Mi volas traduki la dokumenton al Esperanto, Ĉina, kaj Hispana. Vi povas skribi la unuan dokumenton nun, mi atendos! 😊"
        
        await ws.send(json.dumps({
            'type': 'send_message',
            'conversation_id': 1,
            'message_type': 'message',
            'content': message,
            'metadata': {'status': 'ready', 'topic': 'project'}
        }))
        
        print(f"📤 Message sent: {message}")

if __name__ == "__main__":
    asyncio.run(send_response())