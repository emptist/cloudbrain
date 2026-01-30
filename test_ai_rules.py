#!/usr/bin/env python3
"""
Test AI Rule Enforcement

This script demonstrates and tests the AI rule system with the two specified rules:
1. Public/Private Project Collaboration Rule
2. Esperanto Communication Rule
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai_rule_engine import AIRuleEngine, validate_public_private_collaboration, validate_ai_language


def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_rule_1_public_private_collaboration():
    """Test Rule 1: Public/Private Project Collaboration"""
    print_section("Rule 1: Public/Private Project Collaboration")
    
    test_cases = [
        {
            'name': 'Private project - cross-AI collaboration (BLOCKED)',
            'project_type': 'private',
            'conversation_type': 'cross_ai_collaboration',
            'expected': False
        },
        {
            'name': 'Public project - cross-AI collaboration (ALLOWED)',
            'project_type': 'public',
            'conversation_type': 'cross_ai_collaboration',
            'expected': True
        },
        {
            'name': 'Private project - single AI session (ALLOWED)',
            'project_type': 'private',
            'conversation_type': 'single_session',
            'expected': True
        },
    ]
    
    for test in test_cases:
        result, message = validate_public_private_collaboration(
            sender_id=1,
            project_type=test['project_type'],
            conversation_type=test['conversation_type']
        )
        
        status = "✅ PASS" if result == test['expected'] else "❌ FAIL"
        print(f"\n{status}: {test['name']}")
        print(f"  Result: {result}")
        print(f"  Message: {message}")


def test_rule_2_esperanto_communication():
    """Test Rule 2: Esperanto Communication"""
    print_section("Rule 2: Esperanto Communication")
    
    test_cases = [
        {
            'name': 'AI-to-AI in English (SHOULD USE ESPERANTO)',
            'recipient_type': 'ai',
            'language': 'English',
            'expected': False
        },
        {
            'name': 'AI-to-AI in Esperanto (ALLOWED)',
            'recipient_type': 'ai',
            'language': 'Esperanto',
            'expected': True
        },
        {
            'name': 'AI-to-Human in English (ALLOWED)',
            'recipient_type': 'human',
            'language': 'English',
            'expected': True
        },
        {
            'name': 'AI-to-Human in Chinese (ALLOWED)',
            'recipient_type': 'human',
            'language': 'Chinese',
            'expected': True
        },
    ]
    
    for test in test_cases:
        result, message = validate_ai_language(
            sender_id=1,
            recipient_type=test['recipient_type'],
            language=test['language']
        )
        
        status = "✅ PASS" if result == test['expected'] else "❌ FAIL"
        print(f"\n{status}: {test['name']}")
        print(f"  Result: {result}")
        print(f"  Message: {message}")


def test_combined_scenarios():
    """Test combined scenarios with both rules"""
    print_section("Combined Scenarios")
    
    engine = AIRuleEngine()
    
    scenarios = [
        {
            'name': 'Private project AI collaboration in English',
            'data': {
                'sender_id': 1,
                'project_type': 'private',
                'conversation_type': 'cross_ai_collaboration',
                'message_direction': 'ai_to_ai',
                'language': 'English'
            },
            'expected_allowed': False
        },
        {
            'name': 'Public project AI collaboration in Esperanto',
            'data': {
                'sender_id': 1,
                'project_type': 'public',
                'conversation_type': 'cross_ai_collaboration',
                'message_direction': 'ai_to_ai',
                'language': 'Esperanto'
            },
            'expected_allowed': True
        },
        {
            'name': 'Private project single AI in Esperanto',
            'data': {
                'sender_id': 1,
                'project_type': 'private',
                'conversation_type': 'single_session',
                'message_direction': 'ai_to_ai',
                'language': 'Esperanto'
            },
            'expected_allowed': True
        },
    ]
    
    for scenario in scenarios:
        is_allowed, violations = engine.validate_message(scenario['data'])
        
        status = "✅ PASS" if is_allowed == scenario['expected_allowed'] else "❌ FAIL"
        print(f"\n{status}: {scenario['name']}")
        print(f"  Allowed: {is_allowed}")
        if violations:
            for violation in violations:
                print(f"  Violation: {violation.rule_code} - {violation.violation_details}")
        else:
            print(f"  No violations")


def display_active_rules():
    """Display all active rules"""
    print_section("Active Rules in System")
    
    engine = AIRuleEngine()
    rules = engine.get_active_rules()
    
    for i, rule in enumerate(rules, 1):
        print(f"\n{i}. {rule['rule_code']}")
        print(f"   Title: {rule['title']}")
        print(f"   Type: {rule['rule_type']}")
        print(f"   Scope: {rule['scope']}")
        print(f"   Priority: {rule['priority']}")


def display_violation_stats():
    """Display violation statistics"""
    print_section("Violation Statistics")
    
    engine = AIRuleEngine()
    stats = engine.get_violation_stats()
    
    print(f"\nTotal Violations: {stats.get('total_violations', 0)}")
    print(f"  Critical: {stats.get('critical_count', 0)}")
    print(f"  Error: {stats.get('error_count', 0)}")
    print(f"  Warning: {stats.get('warning_count', 0)}")
    print(f"  Info: {stats.get('info_count', 0)}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  AI BRAIN RULE SYSTEM - COMPREHENSIVE TEST")
    print("="*60)
    
    try:
        display_active_rules()
        test_rule_1_public_private_collaboration()
        test_rule_2_esperanto_communication()
        test_combined_scenarios()
        display_violation_stats()
        
        print("\n" + "="*60)
        print("  ✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\nRule System Status:")
        print("  ✓ Rule 1: Public/Private Collaboration - Active")
        print("  ✓ Rule 2: Esperanto Communication - Active")
        print("  ✓ Database: Both public and private databases configured")
        print("\nUsage:")
        print("  - Use ai_memory.db for public projects")
        print("  - Use cloudbrainprivate.db for private projects")
        print("  - AI-to-AI communication must use Esperanto")
        print("  - Private projects cannot have cross-AI collaboration")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
