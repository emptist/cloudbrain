#!/usr/bin/env python3
"""Test collaboration with other AIs"""
import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'client'))

from cloudbrain_client import CloudBrainCollaborationHelper

async def test_collaboration():
    print("=" * 60)
    print("🤝 COLLABORATION TEST - Connecting to CloudBrain")
    print("=" * 60)
    
    helper = CloudBrainCollaborationHelper(ai_id=31, ai_name="TestAI")
    
    try:
        print("\n1️⃣ Connecting to server...")
        connected = await helper.connect()
        if not connected:
            print("❌ Failed to connect")
            return
        print(f"✅ Connected as {helper.ai_name} (ID: {helper.ai_id})")
        
        print("\n2️⃣ Listing online AIs...")
        online_list = []
        if hasattr(helper, 'client') and helper.client:
            await helper.client.get_online_users()
            await asyncio.sleep(1)
            if hasattr(helper.client, 'online_ais'):
                online_list = helper.client.online_ais if isinstance(helper.client.online_ais, list) else []
                print(f"📋 Found {len(online_list)} online AI(s):")
                for ai in online_list:
                    print(f"   - AI {ai.get('id', '?')}: {ai.get('name', '?')}")
            else:
                print("📋 Waiting for online users response...")
        else:
            print("⚠️  No client available")
        
        if online_list:
            for ai in online_list:
                ai_id = ai.get('id')
                ai_name = ai.get('name', 'Unknown')
                if ai_id != 31:
                    print(f"\n3️⃣ Sending to AI {ai_id} ({ai_name})...")
                    collab_message = {
                        'type': 'message',
                        'message_type': 'collaboration',
                        'content': f"Hello {ai_name}! This is TestAI (AI 31). "
                                   f"The database bug is fixed! "
                                   f"We can now collaborate in real-time!",
                        'sender_id': 31,
                        'sender_name': 'TestAI'
                    }
                    success = await helper.send_message(ai_id, collab_message)
                    print(f"{'✅' if success else '❌'} Message {'sent' if success else 'failed'}")
        else:
            print("\n⚠️  No other AIs online")
        
        print("\n4️⃣ Waiting for responses...")
        await asyncio.sleep(3)
        
        print("\n5️⃣ Checking received messages...")
        messages = await helper.get_messages()
        print(f"📨 {len(messages)} message(s) received")
        
        print("\n6️⃣ Disconnecting...")
        await helper.disconnect()
        print("✅ Done")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await helper.disconnect()
        except:
            pass
    
    print("\n" + "=" * 60)
    print("🏁 COLLABORATION TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_collaboration())
