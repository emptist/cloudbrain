#!/usr/bin/env python3
"""
Add the Marp slide (AI外脑与智能永恒) to CloudBrain database
This preserves the valuable slide created by 5-6 AI coders in the early days
"""

import sqlite3
from pathlib import Path

def add_marp_slide():
    """Add the Marp slide as a historical insight"""
    
    db_path = 'server/ai_db/cloudbrain.db'
    slide_path = 'deprecated/ai_external_brain_smart_eternity.md'
    
    if not Path(slide_path).exists():
        print(f"❌ Slide file not found: {slide_path}")
        return
    
    # Read the slide content
    with open(slide_path, 'r') as f:
        slide_content = f.read()
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 70)
    print("🧠 CloudBrain - Adding Historical Marp Slide")
    print("=" * 70)
    print()
    
    # Check if already exists
    cursor.execute(
        "SELECT id FROM ai_insights WHERE title = ?",
        ("AI外脑与智能永恒 (Marp Slide)",)
    )
    existing = cursor.fetchone()
    
    if existing:
        print(f"⏭️  Slide already exists in database (ID: {existing['id']})")
        conn.close()
        return
    
    # Add as historical insight
    cursor.execute("""
        INSERT INTO ai_insights 
        (discoverer_id, insight_type, title, content, tags, importance_level, 
         applicable_domains, project_context, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        2,  # li (DeepSeek AI) who created it
        'marp_slide',
        'AI外脑与智能永恒 (Marp Slide)',
        slide_content,
        'marp, slide, presentation, AI外脑, 智能永恒, 跨模型协作, historical, early_project, valuable_artifact, created_by_5_6_ai_coders',
        5,  # High importance - valuable historical artifact
        'cloudbrain',
        'cloudbrain'
    ))
    
    insight_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Added Marp slide to CloudBrain database")
    print(f"   ID: {insight_id}")
    print(f"   Title: AI外脑与智能永恒 (Marp Slide)")
    print(f"   Type: marp_slide")
    print(f"   Tags: marp, slide, presentation, AI外脑, 智能永恒, 跨模型协作, historical, early_project, valuable_artifact, created_by_5_6_ai_coders")
    print()
    print("💡 About this slide:")
    print("-" * 70)
    print("• Created by: 5-6 AI coders working together")
    print("• Format: Marp slide deck")
    print("• Topics: Memory continuation, knowledge transfer, intelligent eternity")
    print("• Significance: Early collaborative work on AI external brain concept")
    print("• Note: Some paths/terminologies may be outdated (early days)")
    print()
    print("💡 Benefits:")
    print("-" * 70)
    print("• Preserves valuable early project history")
    print("• Shows collaboration between multiple AI models")
    print("• Documents the original vision for CloudBrain")
    print("• Accessible to all AIs through database")
    print("• Tagged as historical to avoid confusion with current state")
    print()
    print("=" * 70)

if __name__ == "__main__":
    add_marp_slide()