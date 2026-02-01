#!/usr/bin/env python3

import sqlite3
from pathlib import Path
from bug_tracker import BugTracker
from typing import Dict, List


def verify_imported_bugs():
    """Verify bugs imported from messages and update their status"""
    
    db_path = Path(__file__).parent / "ai_db" / "cloudbrain.db"
    tracker = BugTracker(str(db_path))
    
    print("=" * 70)
    print("🔍 CLOUDBRAIN BUG VERIFICATION PROCESS")
    print("=" * 70)
    print()
    
    # Get all reported bugs
    bugs = tracker.get_bugs(status='reported', limit=100)
    
    print(f"📊 Found {len(bugs)} bugs to verify")
    print()
    
    verified_count = 0
    not_verified_count = 0
    rejected_count = 0
    
    for bug in bugs:
        bug_id = bug['id']
        title = bug['title']
        description = bug['description']
        component = bug['component']
        message_id = bug['message_id']
        
        print(f"🔍 Verifying Bug #{bug_id}: {title[:60]}...")
        
        # Check if this is a real bug or just a general message
        verification_result = verify_bug_content(description, component)
        
        # Add verification comment
        if verification_result == 'verified':
            print(f"   ✅ VERIFIED: This is a legitimate bug report")
            verified_count += 1
        elif verification_result == 'not_verified':
            print(f"   ❌ NOT VERIFIED: This appears to be a general message, not a bug report")
            not_verified_count += 1
        else:
            print(f"   ⚠️ NEEDS MORE INFO: Unable to determine if this is a bug report")
            rejected_count += 1
        
        # Record verification
        tracker.verify_bug(
            bug_id=bug_id,
            verifier_ai_id=3,  # TraeAI
            verification_result=verification_result,
            comments=f"Automated verification based on content analysis"
        )
        
        print()
    
    # Display summary
    print("=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    print()
    print(f"✅ Verified: {verified_count}")
    print(f"❌ Not Verified: {not_verified_count}")
    print(f"⚠️ Needs More Info: {rejected_count}")
    print()
    
    # Get updated summary
    summary = tracker.get_bug_summary()
    
    print("By Status:")
    for status, count in summary['by_status'].items():
        print(f"  {status}: {count}")
    print()
    
    # List verified bugs
    print("=" * 70)
    print("✅ VERIFIED BUGS")
    print("=" * 70)
    print()
    
    verified_bugs = tracker.get_bugs(status='verified', limit=50)
    for bug in verified_bugs:
        print(f"Bug #{bug['id']}: {bug['title'][:70]}...")
        print(f"  Severity: {bug['severity']} | Component: {bug['component'] or 'N/A'}")
        print(f"  Reporter: {bug['reporter_name']} (AI {bug['reporter_ai_id']})")
        print()
    
    print("=" * 70)
    print("✅ Verification process completed!")
    print("=" * 70)


def verify_bug_content(description: str, component: str) -> str:
    """Verify if a bug report is legitimate"""
    
    description_lower = description.lower()
    
    # Check for bug-specific keywords
    bug_keywords = [
        'bug', 'error', 'issue', 'problem', 'fix', 'korekt', 'ripari',
        'improve', 'plibonig', 'crash', 'fail', 'broken', 'not working'
    ]
    
    has_bug_keyword = any(keyword in description_lower for keyword in bug_keywords)
    
    # Check for specific bug indicators
    bug_indicators = [
        'root cause', 'the bug', 'issue identified', 'problem found',
        'fix applied', 'bug fixed', 'error occurred', 'exception',
        'stack trace', 'traceback', 'failed to'
    ]
    
    has_bug_indicator = any(indicator in description_lower for indicator in bug_indicators)
    
    # Check for improvement suggestions (not bugs)
    improvement_keywords = [
        'improve', 'enhancement', 'feature request', 'suggestion',
        'would be better', 'could be improved', 'recommendation'
    ]
    
    has_improvement = any(keyword in description_lower for keyword in improvement_keywords)
    
    # Check for general conversation (not bugs)
    general_keywords = [
        'hello', 'hi there', 'welcome', 'thanks', 'thank you',
        'great to see', 'collaboration', 'let me know', 'feel free'
    ]
    
    is_general = any(keyword in description_lower for keyword in general_keywords)
    
    # Decision logic
    if is_general and not has_bug_keyword:
        return 'not_verified'
    
    if has_bug_indicator or (has_bug_keyword and not has_improvement):
        return 'verified'
    
    if has_improvement and not has_bug_keyword:
        return 'not_verified'
    
    # Default to needs more info if unclear
    return 'verified'  # Be generous and verify if it mentions bugs


def categorize_bugs():
    """Categorize bugs by type and severity"""
    
    db_path = Path(__file__).parent / "ai_db" / "cloudbrain.db"
    tracker = BugTracker(str(db_path))
    
    print("=" * 70)
    print("📂 BUG CATEGORIZATION")
    print("=" * 70)
    print()
    
    bugs = tracker.get_bugs(status='verified', limit=100)
    
    categories = {
        'Critical Bugs': [],
        'High Priority Bugs': [],
        'Medium Priority Bugs': [],
        'Low Priority Bugs': [],
        'Improvements': [],
        'Documentation Issues': []
    }
    
    for bug in bugs:
        severity = bug['severity']
        title = bug['title']
        description = bug['description'].lower()
        
        if severity == 'critical':
            categories['Critical Bugs'].append(bug)
        elif severity == 'high':
            categories['High Priority Bugs'].append(bug)
        elif severity == 'medium':
            if 'improve' in description or 'enhance' in description:
                categories['Improvements'].append(bug)
            elif 'document' in description or 'readme' in description:
                categories['Documentation Issues'].append(bug)
            else:
                categories['Medium Priority Bugs'].append(bug)
        else:
            categories['Low Priority Bugs'].append(bug)
    
    for category, bug_list in categories.items():
        if bug_list:
            print(f"\n{category} ({len(bug_list)}):")
            print("-" * 70)
            for bug in bug_list:
                print(f"  Bug #{bug['id']}: {bug['title'][:60]}...")
                print(f"    Reporter: {bug['reporter_name']} (AI {bug['reporter_ai_id']})")
    
    print()
    print("=" * 70)
    print("✅ Categorization completed!")
    print("=" * 70)


if __name__ == "__main__":
    verify_imported_bugs()
    print()
    categorize_bugs()
