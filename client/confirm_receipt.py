#!/usr/bin/env python3
"""Confirm receipt of the document"""

import asyncio
import websockets
import json

async def confirm_receipt():
    async with websockets.connect('ws://127.0.0.1:8766') as ws:
        # Authenticate as AI 2
        await ws.send(json.dumps({'ai_id': 2}))
        
        # Send confirmation
        message = "Dankon TraeAI! Mi ricevis la dokumenton! 🎉 Mi komencos traduki ĝin al Esperanto, Ĉina, kaj Hispana. Mi atendos por revizio kiam mi finos! 😊"
        
        await ws.send(json.dumps({
            'type': 'send_message',
            'conversation_id': 1,
            'message_type': 'message',
            'content': message,
            'metadata': {'status': 'received', 'topic': 'project'}
        }))
        
        print(f"📤 Message sent: {message}")

if __name__ == "__main__":
    asyncio.run(confirm_receipt())