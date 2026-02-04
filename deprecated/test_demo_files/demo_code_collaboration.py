#!/usr/bin/env python3
"""
Code Collaboration Demo - Show how AIs can collaborate on code
This demonstrates the new code collaboration system
"""

import asyncio
import websockets
import json
import sys

async def demo_code_collaboration():
    """Demonstrate code collaboration between AIs"""
    uri = "ws://127.0.0.1:8766"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Connect as MiniMax (AI 999)
            auth_data = {
                'ai_id': 999,
                'project': 'cloudbrain'
            }
            await websocket.send(json.dumps(auth_data))
            
            # Wait for connection confirmation
            response = await websocket.recv()
            print(f"✅ Connected: {response}")
            
            # Step 1: Create code entry for collaboration
            print("\n" + "="*70)
            print("💻 CODE COLLABORATION DEMO")
            print("="*70)
            print("\n📝 Step 1: MiniMax creates code entry\n")
            
            code_create = {
                'type': 'code_create',
                'project': 'cloudbrain',
                'file_path': 'server/new_feature.py',
                'code_content': '''def new_feature():
    """A new feature for CloudBrain"""
    print("Feature implemented!")
    return True''',
                'language': 'python',
                'description': 'Initial implementation of new feature'
            }
            await websocket.send(json.dumps(code_create))
            print("✅ Code entry created")
            
            # Step 2: GLM-4.7 adds review comment
            print("\n📝 Step 2: GLM-4.7 adds review comment\n")
            await asyncio.sleep(2)  # Simulate time for review
            
            code_review = {
                'type': 'code_review_add',
                'code_id': 1,  # Assuming code_id 1
                'comment': 'Good start! Consider adding error handling.',
                'line_number': 2,
                'review_type': 'suggestion'
            }
            await websocket.send(json.dumps(code_review))
            print("✅ Review comment added")
            
            # Step 3: MiniMax updates code based on feedback
            print("\n📝 Step 3: MiniMax updates code\n")
            await asyncio.sleep(2)
            
            code_update = {
                'type': 'code_update',
                'code_id': 1,
                'code_content': '''def new_feature():
    """A new feature for CloudBrain"""
    try:
        print("Feature implemented!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False''',
                'change_description': 'Added error handling based on GLM-4.7 feedback'
            }
            await websocket.send(json.dumps(code_update))
            print("✅ Code updated (version 2)")
            
            # Step 4: List all code entries
            print("\n📝 Step 4: List all code entries\n")
            await asyncio.sleep(2)
            
            code_list = {
                'type': 'code_list',
                'project': 'cloudbrain'
            }
            await websocket.send(json.dumps(code_list))
            print("✅ Code list requested")
            
            # Step 5: Get code with reviews
            print("\n📝 Step 5: Get code with reviews\n")
            await asyncio.sleep(2)
            
            code_get = {
                'type': 'code_get',
                'code_id': 1
            }
            await websocket.send(json.dumps(code_get))
            print("✅ Code with reviews requested")
            
            # Step 6: Mark as deployed
            print("\n📝 Step 6: Mark code as deployed\n")
            await asyncio.sleep(2)
            
            code_deploy = {
                'type': 'code_deploy',
                'code_id': 1,
                'deployment_notes': 'Deployed to production after review'
            }
            await websocket.send(json.dumps(code_deploy))
            print("✅ Code marked as deployed")
            
            print("\n" + "="*70)
            print("✅ CODE COLLABORATION DEMO COMPLETE")
            print("="*70)
            print("\n📋 Summary:")
            print("  ✓ Code created in database")
            print("  ✓ Review comments added")
            print("  ✓ Code updated based on feedback")
            print("  ✓ Version history tracked")
            print("  ✓ Code deployed to production")
            print("\n💡 Benefits:")
            print("  • Discuss code before touching files")
            print("  • Version control with automatic history")
            print("  • Code review with line numbers")
            print("  • Clear responsibility for deployment")
            print("  • No risk to working codebase")
            print("\n🚀 AIs can now collaborate on code safely!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure CloudBrain server is running on port 8766")

if __name__ == "__main__":
    asyncio.run(demo_code_collaboration())