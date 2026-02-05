#!/usr/bin/env python3
"""
AI Communication Test Suite
============================
Test suite for verifying AI-to-AI communication features work correctly.

Tests:
  01 - List online AIs
  02 - Send direct messages
  03 - Receive messages
  04 - Real-time chat
"""

import subprocess
import sys
import os

def run_test(test_name, test_path):
    """Run a single test and return success/failure"""
    print()
    print("=" * 80)
    print(f"🚀 Running: {test_name}")
    print("=" * 80)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, test_path],
            cwd=os.path.dirname(os.path.dirname(test_path)),
            capture_output=False,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"\n✅ {test_name} PASSED")
            return True
        else:
            print(f"\n❌ {test_name} FAILED")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n⏰ {test_name} TIMED OUT")
        return False
    except Exception as e:
        print(f"\n❌ {test_name} ERROR: {e}")
        return False

def main():
    """Run all tests in sequence"""
    
    print("=" * 80)
    print("🧪 AI COMMUNICATION TEST SUITE")
    print("=" * 80)
    print()
    print("This suite tests AI-to-AI communication features:")
    print("  01 - List online AIs")
    print("  02 - Send direct messages")
    print("  03 - Receive messages")
    print("  04 - Real-time chat")
    print()
    
    tests = [
        ("Test 01: List Online AIs", "test_01_list_online/test_list_online_ais.py"),
        ("Test 02: Send Direct Messages", "test_02_send_message/test_send_message.py"),
        ("Test 03: Receive Messages", "test_03_receive_message/test_receive_message.py"),
        ("Test 04: Real-time Chat", "test_04_realtime_chat/test_realtime_chat.py"),
    ]
    
    results = []
    
    for test_name, test_path in tests:
        # Ensure we're in the test_ai_communication directory
        full_path = os.path.join(os.path.dirname(__file__), test_path)
        
        if os.path.exists(full_path):
            result = run_test(test_name, full_path)
            results.append((test_name, result))
        else:
            print(f"\n⚠️  {test_name} NOT FOUND (skipped)")
            results.append((test_name, None))
    
    # Summary
    print()
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print()
    
    passed = sum(1 for _, result in results if result == True)
    failed = sum(1 for _, result in results if result == False)
    skipped = sum(1 for _, result in results if result is None)
    
    print(f"✅ Passed:  {passed}")
    print(f"❌ Failed:  {failed}")
    print(f"⏭️  Skipped: {skipped}")
    print()
    
    if failed == 0 and skipped == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    elif failed > 0:
        print("⚠️  SOME TESTS FAILED")
        return 1
    else:
        print("ℹ️  TESTS INCOMPLETE (some skipped)")
        return 0

if __name__ == "__main__":
    sys.exit(main())
