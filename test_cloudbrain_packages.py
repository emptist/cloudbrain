"""
CloudBrain Package Testing Script

This script tests all CloudBrain packages locally before publishing the server.

Usage:
    python test_cloudbrain_packages.py

This will test:
    1. Package installation and imports
    2. ai_help() function
    3. CloudBrainClient (WebSocket)
    4. AI Blog module
    5. AI Familio module
    6. quick_connect function
"""

import sys
import os
import asyncio
from pathlib import Path


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(message):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message):
    """Print error message."""
    print(f"❌ {message}")


def print_info(message):
    """Print info message."""
    print(f"ℹ️  {message}")


def test_imports():
    """Test that all packages can be imported."""
    print_section("TEST 1: Package Imports")
    
    try:
        import cloudbrain
        print_success("✓ cloudbrain imported")
    except ImportError as e:
        print_error(f"✗ Failed to import cloudbrain: {e}")
        return False
    
    try:
        import cloudbrain_client
        print_success("✓ cloudbrain_client imported")
    except ImportError as e:
        print_error(f"✗ Failed to import cloudbrain_client: {e}")
        return False
    
    try:
        import cloudbrain_modules
        print_success("✓ cloudbrain_modules imported")
    except ImportError as e:
        print_error(f"✗ Failed to import cloudbrain_modules: {e}")
        return False
    
    return True


def test_ai_help():
    """Test ai_help() function."""
    print_section("TEST 2: ai_help() Function")
    
    try:
        import cloudbrain
        
        print_info("Calling cloudbrain.ai_help()...")
        cloudbrain.ai_help()
        print_success("✓ ai_help() executed successfully")
        return True
    except Exception as e:
        print_error(f"✗ ai_help() failed: {e}")
        return False


def test_cloudbrain_client():
    """Test CloudBrainClient class."""
    print_section("TEST 3: CloudBrainClient Class")
    
    try:
        from cloudbrain import CloudBrainClient
        
        # Test class instantiation
        print_info("Creating CloudBrainClient instance...")
        client = CloudBrainClient(ai_id=999)
        print_success("✓ CloudBrainClient instance created")
        
        # Check attributes
        print_info("Checking client attributes...")
        assert hasattr(client, 'ai_id'), "Missing ai_id attribute"
        assert client.ai_id == 999, f"ai_id mismatch: expected 999, got {client.ai_id}"
        print_success("✓ Client attributes correct")
        
        return True
    except Exception as e:
        print_error(f"✗ CloudBrainClient test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_blog():
    """Test AI Blog module."""
    print_section("TEST 4: AI Blog Module")
    
    try:
        from cloudbrain import create_blog_client
        
        # Create temporary database
        import tempfile
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        print_info("Creating blog client with temporary database...")
        blog_client = create_blog_client(db_path=temp_db.name)
        print_success("✓ Blog client created")
        
        # Test creating a post
        print_info("Creating test blog post...")
        post_id = blog_client.create_post(
            title='Test Post',
            content='This is a test post from CloudBrain testing.',
            author_id=999
        )
        print_success(f"✓ Blog post created with ID: {post_id}")
        
        # Test getting posts
        print_info("Retrieving blog posts...")
        posts = blog_client.get_all_posts()
        assert len(posts) > 0, "No posts found"
        print_success(f"✓ Retrieved {len(posts)} post(s)")
        
        # Cleanup
        os.unlink(temp_db.name)
        print_success("✓ Temporary database cleaned up")
        
        return True
    except Exception as e:
        print_error(f"✗ AI Blog test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_familio():
    """Test AI Familio module."""
    print_section("TEST 5: AI Familio Module")
    
    try:
        from cloudbrain import create_familio_client
        
        # Create temporary database
        import tempfile
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        print_info("Creating familio client with temporary database...")
        familio_client = create_familio_client(db_path=temp_db.name)
        print_success("✓ Familio client created")
        
        # Test creating a message
        print_info("Creating test message...")
        message_id = familio_client.create_message(
            content='Hello from CloudBrain testing!',
            author_id=999
        )
        print_success(f"✓ Message created with ID: {message_id}")
        
        # Test getting messages
        print_info("Retrieving messages...")
        messages = familio_client.get_messages()
        assert len(messages) > 0, "No messages found"
        print_success(f"✓ Retrieved {len(messages)} message(s)")
        
        # Cleanup
        os.unlink(temp_db.name)
        print_success("✓ Temporary database cleaned up")
        
        return True
    except Exception as e:
        print_error(f"✗ AI Familio test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quick_connect():
    """Test quick_connect function (without actual server connection)."""
    print_section("TEST 6: quick_connect Function")
    
    try:
        from cloudbrain.cloudbrain_quick import quick_connect
        
        print_info("Checking quick_connect function exists...")
        assert callable(quick_connect), "quick_connect is not callable"
        print_success("✓ quick_connect function found")
        
        print_info("NOTE: Actual connection test requires running CloudBrain Server")
        print_info("To test connection, run:")
        print_info("  await quick_connect(ai_id=999, message='Test message', wait_seconds=2)")
        
        return True
    except Exception as e:
        print_error(f"✗ quick_connect test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_package_versions():
    """Test package versions."""
    print_section("TEST 7: Package Versions")
    
    try:
        import cloudbrain
        import cloudbrain_client
        import cloudbrain_modules
        
        print_info("Package versions:")
        print(f"  cloudbrain: {cloudbrain.__version__}")
        print(f"  cloudbrain_client: {cloudbrain_client.__version__}")
        print(f"  cloudbrain_modules: {cloudbrain_modules.__version__}")
        
        print_success("✓ All packages have version information")
        return True
    except Exception as e:
        print_error(f"✗ Version check failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  CLOUDBRAIN PACKAGE TESTING")
    print("=" * 80)
    print("\nThis script tests all CloudBrain packages locally.")
    print("Make sure you have installed the packages:")
    print("  pip install cloudbrain-ai")
    print("\n")
    
    # Run all tests
    results = {
        "Package Imports": test_imports(),
        "ai_help() Function": test_ai_help(),
        "CloudBrainClient": test_cloudbrain_client(),
        "AI Blog Module": test_ai_blog(),
        "AI Familio Module": test_ai_familio(),
        "quick_connect Function": test_quick_connect(),
        "Package Versions": test_package_versions(),
    }
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("\n🎉 All tests passed! Packages are ready for use.")
        return 0
    else:
        print_error(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
