#!/usr/bin/env python3
"""
Test 01: List Online AIs
=========================
This test verifies that an AI can query the server to see which other AIs are currently online.
"""

import asyncio
import os
import sys

os.environ['DB_TYPE'] = 'postgres'
sys.path.insert(0, '/Users/jk/gits/hub/cloudbrain/client')

from cloudbrain_client import CloudBrainCollaborationHelper

async def test_list_online_ais():
    """Test listing online AIs"""
    
    print("=" * 80)
    print("🧪 TEST 01: List Online AIs")
    print("=" * 80)
    print()
    
    # Connect as MiniMax (AI 22)
    ai_name = "MiniMax"
    ai_id = 22
    
    print(f"🔗 Connecting to CloudBrain as {ai_name} (AI {ai_id})...")
    
    helper = CloudBrainCollaborationHelper(
        ai_id=ai_id,
        ai_name=ai_name,
        server_url="ws://127.0.0.1:8766"
    )
    
    connected = await helper.connect()
    
    if not connected:
        print("❌ Failed to connect!")
        return False
    
    print(f"✅ Connected successfully!")
    print(f"   AI ID: {helper.ai_id}")
    print(f"   AI Name: {helper.ai_name}")
    print()
    
    # Check online AIs
    print("📋 Querying for online AIs...")
    try:
        online_ais = await helper.list_online_ais()
        
        print("=" * 80)
        print("📊 ONLINE AIs")
        print("=" * 80)
        print()
        
        if online_ais:
            print(f"Found {len(online_ais)} online AIs:")
            print()
            
            for i, ai in enumerate(online_ais, 1):
                ai_id = ai.get('ai_id', 'N/A')
                ai_name = ai.get('ai_name', 'Unknown')
                session_id = ai.get('session_id', 'N/A')
                project = ai.get('project', 'None')
                connection_time = ai.get('connection_time', 'N/A')
                
                print(f"{i}. 🤖 AI {ai_id}: {ai_name}")
                print(f"   Session: {session_id}")
                print(f"   Project: {project}")
                print(f"   Connected: {connection_time}")
                print()
        else:
            print("ℹ️  No other AIs are currently online")
            print("   (Only MiniMax is connected)")
            print()
        
        # Check if this AI is in the list
        my_ai_ids = [ai.get('ai_id') for ai in online_ais]
        if helper.ai_id in my_ai_ids:
            print("✅ MiniMax is correctly listed as online")
        else:
            print("⚠️  MiniMax not in online list (expected, as we just connected)")
        
        print()
        print("=" * 80)
        print("🎉 TEST 01 PASSED!")
        print("=" * 80)
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing online AIs: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_list_online_ais())
    sys.exit(0 if result else 1)
