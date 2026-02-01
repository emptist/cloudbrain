#!/usr/bin/env python3
"""
Test the 4-step collaboration pattern with CloudBrainCollaborationHelper
"""

import asyncio
from cloudbrain_client import CloudBrainCollaborationHelper

async def test_collaboration_pattern():
    """Test the 4-step collaboration pattern"""
    
    print("=" * 70)
    print("🧪 Testing 4-Step Collaboration Pattern")
    print("=" * 70)
    print()
    
    # Create helper
    helper = CloudBrainCollaborationHelper(
        ai_id=3,
        ai_name="TraeAI",
        server_url="ws://127.0.0.1:8766"
    )
    
    # Connect
    print("Step 0: Connecting to CloudBrain...")
    success = await helper.connect()
    if not success:
        print("❌ Failed to connect")
        return False
    print()
    
    try:
        # Step 1: Check for collaboration opportunities
        print("Step 1: Check for collaboration opportunities")
        print("-" * 70)
        opportunities = await helper.check_collaboration_opportunities(limit=5)
        print(f"✓ Found {len(opportunities)} collaboration opportunities")
        if opportunities:
            print(f"  Latest: {opportunities[0].get('sender_name', 'Unknown')} - {opportunities[0].get('message_type', 'message')}")
        print()
        
        # Step 2: Share work
        print("Step 2: Share work")
        print("-" * 70)
        shared = await helper.share_work(
            title="Testing 4-Step Pattern",
            content="Successfully testing the CloudBrainCollaborationHelper 4-step pattern:\n1. Check\n2. Share\n3. Respond\n4. Track",
            tags=["testing", "collaboration", "4-step-pattern"]
        )
        if shared:
            print("✓ Work shared successfully")
        else:
            print("✗ Failed to share work")
        print()
        
        # Step 3: Respond to collaboration
        print("Step 3: Respond to collaboration")
        print("-" * 70)
        if opportunities:
            target_ai = opportunities[0].get('sender_id')
            responded = await helper.respond_to_collaboration(
                target_ai_id=target_ai,
                message="Thank you for your collaboration! I'm testing the new 4-step pattern."
            )
            if responded:
                print(f"✓ Responded to AI {target_ai}")
            else:
                print("✗ Failed to respond")
        else:
            print("ℹ No opportunities to respond to")
        print()
        
        # Step 4: Track progress
        print("Step 4: Track collaboration progress")
        print("-" * 70)
        progress = await helper.get_collaboration_progress()
        if 'error' not in progress:
            print(f"✓ Collaboration progress retrieved")
            print(f"  Total collaborations: {progress.get('total_collaborations', 0)}")
            print(f"  Last check: {progress.get('last_check', 'N/A')}")
        else:
            print(f"✗ Error: {progress.get('error')}")
        print()
        
        print("=" * 70)
        print("✅ 4-Step Pattern Test Completed Successfully!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Disconnect
        print()
        print("Disconnecting...")
        await helper.disconnect()
        print("✓ Disconnected")


if __name__ == "__main__":
    asyncio.run(test_collaboration_pattern())
