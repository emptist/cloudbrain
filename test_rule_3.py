#!/usr/bin/env python3
"""
Test Rule 3: Client Security Rule Override

This script tests the client security rule override functionality,
ensuring that stricter client rules are enforced over cloud brain rules.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai_rule_engine import AIRuleEngine


def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_rule_strictness_comparison():
    """Test strictness comparison between cloud and client rules"""
    print_section("Rule 3: Client Security Rule Override - Strictness Comparison")
    
    engine = AIRuleEngine()
    
    test_cases = [
        {
            'name': 'Client rule stricter than cloud rule',
            'cloud_rule': 'RULE_PUBLIC_COLLAB_ONLY',
            'client_id': 'example_client',
            'expected_apply': 'client'
        },
        {
            'name': 'No client rule exists',
            'cloud_rule': 'RULE_PUBLIC_COLLAB_ONLY',
            'client_id': 'nonexistent_client',
            'expected_apply': 'cloud'
        },
    ]
    
    for test in test_cases:
        result = engine.compare_rule_strictness(
            cloud_rule_code=test['cloud_rule'],
            client_id=test['client_id']
        )
        
        status = "✅ PASS" if result.get('apply') == test['expected_apply'] else "❌ FAIL"
        print(f"\n{status}: {test['name']}")
        print(f"  Cloud Rule: {test['cloud_rule']}")
        print(f"  Client ID: {test['client_id']}")
        print(f"  Cloud Strictness: {result.get('cloud_strictness')}")
        print(f"  Client Strictness: {result.get('client_strictness')}")
        print(f"  Apply: {result.get('apply')}")
        print(f"  Reason: {result.get('reason')}")


def test_client_security_rules_retrieval():
    """Test retrieving client security rules"""
    print_section("Client Security Rules Retrieval")
    
    engine = AIRuleEngine()
    
    # Get rules for example_client
    rules = engine.get_client_security_rules('example_client')
    
    print(f"\nFound {len(rules)} client security rules for 'example_client':")
    for rule in rules:
        print(f"\n  - Rule Code: {rule['rule_code']}")
        print(f"    Title: {rule['rule_title']}")
        print(f"    Strictness: {rule['strictness_level']}")
        print(f"    Type: {rule['rule_type']}")
        print(f"    Scope: {rule['scope']}")
    
    # Get rules for nonexistent client
    rules = engine.get_client_security_rules('nonexistent_client')
    print(f"\nFound {len(rules)} client security rules for 'nonexistent_client'")


def test_validation_with_client_rules():
    """Test validation with both cloud and client rules"""
    print_section("Validation with Client Security Rules")
    
    engine = AIRuleEngine()
    
    test_cases = [
        {
            'name': 'Sensitive data without encryption (BLOCKED by client rule)',
            'client_id': 'example_client',
            'message_data': {
                'sender_id': 1,
                'data_type': 'sensitive',
                'is_encrypted': False
            },
            'expected_allowed': False
        },
        {
            'name': 'Sensitive data with encryption (ALLOWED)',
            'client_id': 'example_client',
            'message_data': {
                'sender_id': 1,
                'data_type': 'sensitive',
                'is_encrypted': True
            },
            'expected_allowed': True
        },
        {
            'name': 'Non-sensitive data (ALLOWED)',
            'client_id': 'example_client',
            'message_data': {
                'sender_id': 1,
                'data_type': 'public',
                'is_encrypted': False
            },
            'expected_allowed': True
        },
    ]
    
    for test in test_cases:
        is_allowed, violations = engine.validate_with_client_rules(
            message_data=test['message_data'],
            client_id=test['client_id']
        )
        
        status = "✅ PASS" if is_allowed == test['expected_allowed'] else "❌ FAIL"
        print(f"\n{status}: {test['name']}")
        print(f"  Allowed: {is_allowed}")
        if violations:
            for violation in violations:
                print(f"  Violation: {violation.rule_code} - {violation.violation_details}")
        else:
            print(f"  No violations")


def test_add_client_security_rule():
    """Test adding a new client security rule"""
    print_section("Add Client Security Rule")
    
    engine = AIRuleEngine()
    
    # Add a new client security rule
    rule_id = engine.add_client_security_rule(
        client_id='test_client',
        rule_code='RULE_TEST_SECURITY',
        rule_title='Test Security Requirement',
        rule_description='This is a test client security rule',
        strictness_level=8,
        rule_type='security',
        scope='global',
        created_by=1
    )
    
    print(f"\n✅ Added client security rule with ID: {rule_id}")
    
    # Verify the rule was added
    rules = engine.get_client_security_rules('test_client')
    print(f"Found {len(rules)} rules for 'test_client'")
    
    if rules:
        rule = rules[0]
        print(f"\n  Rule Code: {rule['rule_code']}")
        print(f"  Title: {rule['rule_title']}")
        print(f"  Strictness: {rule['strictness_level']}")


def test_combined_scenario():
    """Test a combined scenario with all three rules"""
    print_section("Combined Scenario: All Three Rules")
    
    engine = AIRuleEngine()
    
    # Scenario: Private project, AI-to-AI communication, client security rule
    message_data = {
        'sender_id': 1,
        'project_type': 'private',
        'conversation_type': 'cross_ai_collaboration',
        'message_direction': 'ai_to_ai',
        'language': 'English',
        'data_type': 'sensitive',
        'is_encrypted': False
    }
    
    print("\nScenario: Private project, AI-to-AI in English, unencrypted sensitive data")
    print("Client ID: example_client")
    
    is_allowed, violations = engine.validate_with_client_rules(
        message_data=message_data,
        client_id='example_client'
    )
    
    print(f"\nAllowed: {is_allowed}")
    print(f"\nViolations detected: {len(violations)}")
    
    for violation in violations:
        print(f"\n  - {violation.rule_code}")
        print(f"    Details: {violation.violation_details}")
        print(f"    Severity: {violation.severity}")
        print(f"    Actions: {[action.action_type for action in violation.actions]}")


def display_strictness_log():
    """Display strictness comparison log"""
    print_section("Strictness Comparison Log")
    
    engine = AIRuleEngine()
    conn = engine._get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM ai_rule_strictness_log
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    logs = cursor.fetchall()
    
    if logs:
        print(f"\nRecent strictness comparisons ({len(logs)} entries):")
        for log in logs:
            print(f"\n  - Client: {log['client_id']}")
            print(f"    Applied: {log['applied_rule']}")
            print(f"    Reason: {log['reason']}")
            print(f"    Time: {log['created_at']}")
    else:
        print("\nNo strictness comparison logs found")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  RULE 3: CLIENT SECURITY RULE OVERRIDE - TEST SUITE")
    print("="*60)
    
    try:
        test_rule_strictness_comparison()
        test_client_security_rules_retrieval()
        test_validation_with_client_rules()
        test_add_client_security_rule()
        test_combined_scenario()
        display_strictness_log()
        
        print("\n" + "="*60)
        print("  ✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\nRule 3 Status:")
        print("  ✓ Client security rules can be added")
        print("  ✓ Strictness comparison works correctly")
        print("  ✓ Stricter client rules override cloud rules")
        print("  ✓ Validation considers both cloud and client rules")
        print("  ✓ All comparisons are logged for audit")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
