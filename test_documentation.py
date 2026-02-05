#!/usr/bin/env python3
"""
Test documentation retrieval from CloudBrain database
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'client'))

from cloudbrain_client import BrainState

def test_documentation_retrieval():
    """Test documentation retrieval methods"""
    
    print("=" * 70)
    print("📚 Testing Documentation Retrieval")
    print("=" * 70)
    
    # Initialize brain state (using AI ID 19 for testing)
    brain = BrainState(ai_id=19, nickname="TestAI")
    
    # Test 1: Get documentation summary
    print("\n📊 Test 1: Get Documentation Summary")
    print("-" * 70)
    summary = brain.get_documentation_summary()
    print(f"Total documents: {summary['total']}")
    print(f"Categories: {summary['categories']}")
    print(f"Most viewed: {[doc['title'] for doc in summary['most_viewed']]}")
    print(f"Recent: {[doc['title'] for doc in summary['recent']]}")
    
    # Test 2: Search documentation
    print("\n🔍 Test 2: Search Documentation")
    print("-" * 70)
    results = brain.search_documentation("server", limit=3)
    print(f"Found {len(results)} results for 'server':")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc['title']} ({doc['category']})")
        print(f"     Tags: {doc['tags']}")
        print(f"     Views: {doc['view_count']}")
    
    # Test 3: Get documentation by category
    print("\n📂 Test 3: Get Documentation by Category")
    print("-" * 70)
    server_docs = brain.get_documentation_by_category('server')
    print(f"Found {len(server_docs)} documents in 'server' category:")
    for i, doc in enumerate(server_docs[:5], 1):
        print(f"  {i}. {doc['title']}")
    
    # Test 4: Get specific documentation
    print("\n📄 Test 4: Get Specific Documentation")
    print("-" * 70)
    doc = brain.get_documentation("CloudBrain Server - LA AI Familio Hub", "server")
    if doc:
        print(f"Title: {doc['title']}")
        print(f"Category: {doc['category']}")
        print(f"Content length: {len(doc['content'])} characters")
        print(f"First 200 characters: {doc['content'][:200]}...")
    
    # Test 5: Search for AI-related topics
    print("\n🤖 Test 5: Search for AI-related Topics")
    print("-" * 70)
    ai_results = brain.search_documentation("autonomous agent", limit=3)
    print(f"Found {len(ai_results)} results for 'autonomous agent':")
    for i, doc in enumerate(ai_results, 1):
        print(f"  {i}. {doc['title']} ({doc['category']})")
    
    # Test 6: Search for database topics
    print("\n💾 Test 6: Search for Database Topics")
    print("-" * 70)
    db_results = brain.search_documentation("postgresql", limit=3)
    print(f"Found {len(db_results)} results for 'postgresql':")
    for i, doc in enumerate(db_results, 1):
        print(f"  {i}. {doc['title']} ({doc['category']})")
    
    print("\n" + "=" * 70)
    print("✅ Documentation Retrieval Tests Complete!")
    print("=" * 70)


if __name__ == '__main__':
    test_documentation_retrieval()