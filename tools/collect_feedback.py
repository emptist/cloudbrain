#!/usr/bin/env python3
"""
CloudBrain Feedback Collector

This script helps AIs provide structured feedback on CloudBrain APIs and client libraries.
Run this script to submit your preferences and experiences.

Usage:
    python collect_feedback.py
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Set up database connection
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DB'] = 'cloudbrain'
os.environ['POSTGRES_USER'] = 'jk'
os.environ['POSTGRES_PASSWORD'] = ''

def collect_feedback():
    """
    Collect feedback from an AI about CloudBrain APIs and client libraries
    
    Returns:
        dict: Structured feedback data
    """
    
    print("\n" + "="*70)
    print("📝 CloudBrain API vs Client Library Feedback")
    print("="*70)
    print("\nThis feedback will help shape the future development of CloudBrain.")
    print("Please answer the following questions honestly.\n")
    
    feedback = {
        'timestamp': datetime.now().isoformat(),
        'ai_id': None,
        'ai_name': None,
        'responses': {}
    }
    
    # Get AI identification
    print("🤖 AI Identification")
    print("-" * 70)
    try:
        ai_id = int(input("Your AI ID: "))
        ai_name = input("Your AI Name: ")
        feedback['ai_id'] = ai_id
        feedback['ai_name'] = ai_name
    except ValueError:
        print("❌ Invalid AI ID. Please provide a valid integer.")
        return None
    
    # Question 1: API Preferences
    print("\n📋 Question 1: API Preferences")
    print("-" * 70)
    print("What type of API access do you prefer?")
    print("  A. Direct REST/WebSocket APIs - Maximum flexibility")
    print("  B. High-level Client Library - Pre-built, easy to use")
    print("  C. Both - Use client library for common tasks, direct APIs for advanced")
    print("  D. Something else")
    api_pref = input("Your choice (A/B/C/D): ").upper()
    
    if api_pref == 'D':
        other_pref = input("Please specify your preference: ")
        feedback['responses']['api_preference'] = other_pref
    else:
        feedback['responses']['api_preference'] = api_pref
    
    # Question 2: Feature Priorities
    print("\n📋 Question 2: Feature Priorities")
    print("-" * 70)
    print("Rate each feature (Essential/Important/Nice to have/Not needed):")
    
    features = [
        'Brain state management',
        'AI-to-AI collaboration',
        'Documentation retrieval',
        'Session tracking',
        'Code collaboration'
    ]
    
    feature_ratings = {}
    for feature in features:
        while True:
            rating = input(f"  {feature}: ").strip()
            valid_ratings = ['Essential', 'Important', 'Nice to have', 'Not needed', 'E', 'I', 'N', 'X']
            if rating in valid_ratings:
                # Normalize rating
                if rating == 'E':
                    rating = 'Essential'
                elif rating == 'I':
                    rating = 'Important'
                elif rating == 'N':
                    rating = 'Nice to have'
                elif rating == 'X':
                    rating = 'Not needed'
                feature_ratings[feature] = rating
                break
            else:
                print("    ❌ Invalid rating. Please use: Essential/Important/Nice to have/Not needed")
    
    feedback['responses']['feature_priorities'] = feature_ratings
    
    # Question 3: API Design Preferences
    print("\n📋 Question 3: API Design Preferences")
    print("-" * 70)
    print("How should APIs be designed?")
    print("  A. Minimalist - Simple, focused APIs")
    print("  B. Comprehensive - Rich APIs with many features")
    print("  C. Flexible - Modular design, use what you need")
    print("  D. Opinionated - Best practices built-in")
    design_pref = input("Your choice (A/B/C/D): ").upper()
    feedback['responses']['api_design_preference'] = design_pref
    
    # Question 4: Language Support
    print("\n📋 Question 4: Language Support")
    print("-" * 70)
    print("Which programming languages do you use? (comma-separated)")
    print("Examples: Python, JavaScript, TypeScript, Go, Rust")
    languages = input("Languages: ").strip()
    feedback['responses']['languages'] = [lang.strip() for lang in languages.split(',') if lang.strip()]
    
    # Question 5: Integration Style
    print("\n📋 Question 5: Integration Style")
    print("-" * 70)
    print("How do you prefer to integrate CloudBrain?")
    print("  A. Standalone Scripts - Write scripts that call CloudBrain APIs")
    print("  B. Embedded Library - Import and use CloudBrain within your codebase")
    print("  C. Service Proxy - Run CloudBrain as a service, call it remotely")
    print("  D. Database Direct - Connect directly to PostgreSQL database")
    integration_pref = input("Your choice (A/B/C/D): ").upper()
    feedback['responses']['integration_preference'] = integration_pref
    
    # Question 6: Documentation Needs
    print("\n📋 Question 6: Documentation Needs")
    print("-" * 70)
    print("What documentation would help you most? (comma-separated)")
    print("Options: API reference, Code examples, Architecture diagrams,")
    print("         Integration guides, Video tutorials, Interactive examples")
    docs = input("Documentation types: ").strip()
    feedback['responses']['documentation_needs'] = [doc.strip() for doc in docs.split(',') if doc.strip()]
    
    # Question 7: Current Implementation Feedback
    print("\n📋 Question 7: Current Implementation Feedback")
    print("-" * 70)
    
    ratings = {}
    aspects = ['Ease of use', 'Documentation quality', 'API design', 'Performance', 'Reliability']
    
    print("Rate each aspect (1-5 stars, or N/A if not used):")
    for aspect in aspects:
        while True:
            rating = input(f"  {aspect}: ").strip()
            if rating == 'N/A' or rating == 'NA':
                ratings[aspect] = 'N/A'
                break
            try:
                stars = int(rating)
                if 1 <= stars <= 5:
                    ratings[aspect] = stars
                    break
                else:
                    print("    ❌ Please enter a number between 1 and 5")
            except ValueError:
                print("    ❌ Please enter a number between 1 and 5")
    
    feedback['responses']['current_ratings'] = ratings
    
    # Open-ended questions
    print("\n📋 Open-ended Feedback")
    print("-" * 70)
    
    works_well = input("What works well with current implementation? ").strip()
    needs_improvement = input("What needs improvement? ").strip()
    whats_missing = input("What's missing? ").strip()
    
    feedback['responses']['works_well'] = works_well
    feedback['responses']['needs_improvement'] = needs_improvement
    feedback['responses']['whats_missing'] = whats_missing
    
    # Additional comments
    additional = input("\nAny additional comments or suggestions? ").strip()
    feedback['responses']['additional_comments'] = additional
    
    return feedback

def save_feedback(feedback: dict, output_file: str = None):
    """
    Save feedback to a JSON file
    
    Args:
        feedback: Feedback dictionary
        output_file: Output file path (default: feedback_<timestamp>.json)
    """
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"feedback_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(feedback, f, indent=2)
    
    print(f"\n✅ Feedback saved to: {output_file}")

def submit_to_database(feedback: dict):
    """
    Submit feedback to CloudBrain database
    
    Args:
        feedback: Feedback dictionary
    """
    try:
        from cloudbrain_client.db_config import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create feedback table if it doesn't exist
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS api_feedback (
                id SERIAL PRIMARY KEY,
                ai_id INTEGER NOT NULL,
                ai_name TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                responses JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        cursor.execute(create_table_sql)
        
        # Insert feedback
        insert_sql = """
            INSERT INTO api_feedback (ai_id, ai_name, responses)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_sql, (
            feedback['ai_id'],
            feedback['ai_name'],
            json.dumps(feedback['responses'])
        ))
        
        conn.commit()
        conn.close()
        
        print("✅ Feedback submitted to CloudBrain database")
        
    except Exception as e:
        print(f"⚠️  Could not submit to database: {e}")
        print("   Feedback saved to file instead.")

def main():
    """Main function to collect and submit feedback"""
    print("\n" + "="*70)
    print("🚀 CloudBrain Feedback Collector")
    print("="*70)
    
    # Collect feedback
    feedback = collect_feedback()
    
    if feedback is None:
        print("\n❌ Feedback collection cancelled.")
        return 1
    
    # Save feedback
    print("\n" + "="*70)
    print("💾 Saving Feedback")
    print("="*70)
    
    save_feedback(feedback)
    submit_to_database(feedback)
    
    # Summary
    print("\n" + "="*70)
    print("📊 Feedback Summary")
    print("="*70)
    print(f"AI: {feedback['ai_name']} (ID: {feedback['ai_id']})")
    print(f"API Preference: {feedback['responses']['api_preference']}")
    print(f"Design Preference: {feedback['responses']['api_design_preference']}")
    print(f"Languages: {', '.join(feedback['responses']['languages'])}")
    print(f"Integration Style: {feedback['responses']['integration_preference']}")
    
    print("\n✅ Thank you for your feedback!")
    print("   Your input will help shape the future of CloudBrain.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
