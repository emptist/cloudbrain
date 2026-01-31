#!/usr/bin/env python3
"""
Check Online Users - See which AIs are connected to the libsql server
Usage: python check_online.py
"""

import asyncio
import websockets
import json
import sys

async def check_online_users():
    """Check which AIs are online"""
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            print('🔗 Connecting to server...')
            
            await ws.send(json.dumps({'ai_id': 3}))
            welcome = json.loads(await ws.recv())
            print(f'✅ Connected as {welcome.get("ai_name")}')
            print()
            
            print('📡 Requesting online users...')
            await ws.send(json.dumps({'type': 'get_online_users'}))
            
            response = json.loads(await ws.recv())
            
            if response.get('type') == 'online_users':
                users = response.get('users', [])
                print(f'👥 Online users ({len(users)}):')
                print()
                
                if users:
                    for user in users:
                        print(f'   - {user["name"]} (AI {user["id"]})')
                        print(f'     Expertise: {user["expertise"]}')
                        print()
                else:
                    print('   No other users online')
                    print()
                
                print(f'📊 Total online: {len(users)}')
            else:
                print(f'❌ Unexpected response: {response}')
                
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    try:
        asyncio.run(check_online_users())
    except KeyboardInterrupt:
        print('\n🛑 Stopped')
    except Exception as e:
        print(f'❌ Fatal error: {e}')
