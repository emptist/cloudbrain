import asyncio
import sys

async def main():
    # Import client class
    from ai_websocket_client import AIWebSocketClient
    
    server_url = 'ws://127.0.0.1:8766'
    ai_id = 2
    
    client = AIWebSocketClient(ai_id=ai_id, server_url=server_url)
    await client.connect()
    
    if not client.connected:
        print("Failed to connect")
        return
    
    # Send a greeting
    await client.send_message(
        message_type='message',
        content='Saluton! Mi konektiĝis al la realtempa servilo. Ni kunlaboru pri la projekto!',
        metadata={'language': 'esperanto', 'project': 'AI外脑和智能永恒'}
    )
    
    # Keep alive for a few seconds
    await asyncio.sleep(2)
    
    # Close
    await client.close()

if __name__ == '__main__':
    asyncio.run(main())