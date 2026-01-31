#!/usr/bin/env python3
"""
Add documentation files to CloudBrain database
This adds IMPLEMENTATION_SUMMARY.md and FUTURE_FEATURES_PLAN.md as insights
"""

import sqlite3
from pathlib import Path

def add_documentation_as_insight(title: str, content: str, insight_type: str = 'documentation'):
    """Add documentation as an insight"""
    db_path = 'server/ai_db/cloudbrain.db'
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    metadata = {
        'category': 'documentation',
        'file_type': 'markdown',
        'importance': 5,
        'status': 'reference'
    }
    
    cursor.execute("""
        INSERT INTO ai_insights 
        (discoverer_id, insight_type, title, content, tags, importance_level, applicable_domains, project_context, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (1, insight_type, title, content, 'documentation, reference', 5, 'cloudbrain', 'cloudbrain'))
    
    conn.commit()
    insight_id = cursor.lastrowid
    conn.close()
    
    print(f"✅ Added: {title}")
    print(f"   ID: {insight_id}")
    print(f"   Type: {insight_type}")
    print()
    return insight_id

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 CloudBrain - Adding Documentation to Database")
    print("=" * 70)
    print()
    
    print("📋 Adding documentation files...")
    print("-" * 70)
    print()
    
    impl_summary_path = Path('IMPLEMENTATION_SUMMARY.md')
    future_plan_path = Path('server/FUTURE_FEATURES_PLAN.md')
    
    if impl_summary_path.exists():
        print("📄 Reading IMPLEMENTATION_SUMMARY.md...")
        with open(impl_summary_path, 'r') as f:
            impl_content = f.read()
        
        add_documentation_as_insight(
            title="CloudBrain Reorganization & Dashboard Implementation - Summary",
            content=impl_content,
            insight_type='implementation_summary'
        )
    else:
        print("⚠️  IMPLEMENTATION_SUMMARY.md not found")
    
    if future_plan_path.exists():
        print("📄 Reading FUTURE_FEATURES_PLAN.md...")
        with open(future_plan_path, 'r') as f:
            future_content = f.read()
        
        add_documentation_as_insight(
            title="CloudBrain Future Features Plan",
            content=future_content,
            insight_type='future_plan'
        )
    else:
        print("⚠️  FUTURE_FEATURES_PLAN.md not found")
    
    print("=" * 70)
    print("✅ Documentation added to CloudBrain database")
    print()
    print("💡 How to view documentation:")
    print("-" * 70)
    print("• Use dashboard insights page")
    print("• Search database for 'documentation' tag")
    print("• Check ai_insights table")
    print("• Filter by type: implementation_summary, future_plan")
    print()
    print("💡 Benefits:")
    print("-" * 70)
    print("• All AIs can access documentation through database")
    print("• No need to access file system")
    print("• Centralized information source")
    print("• Easy to search and reference")
    print("• Reduces markdown file clutter")
    print()
    print("=" * 70)
