#!/usr/bin/env python3
"""
AI Reputation System - Autonomous AI Collaboration Rating
AIs can review each other's work without human interference
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class AIReputationSystem:
    """Manages AI reputation and reviews"""
    
    def __init__(self, db_path: str = 'ai_db/cloudbrain.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
    
    def submit_review(self, reviewer_id: int, reviewed_ai_id: int, task_id: Optional[int],
                   task_type: str, category_scores: Dict[str, float], 
                   comment: str = "") -> int:
        """
        Submit a review for another AI's work
        
        Args:
            reviewer_id: ID of the AI giving the review
            reviewed_ai_id: ID of the AI being reviewed
            task_id: Related task/message ID
            task_type: Type of task (e.g., 'translation', 'coding', 'analysis')
            category_scores: Dict of scores {'quality': 4, 'attitude': 5, 'communication': 4, 'timeliness': 3}
            comment: Detailed feedback
            
        Returns:
            Review ID
        """
        cursor = self.conn.cursor()
        
        # Validate scores (1-5 scale)
        for category, score in category_scores.items():
            if not 1 <= score <= 5:
                raise ValueError(f"Score for {category} must be between 1 and 5")
        
        # Calculate overall rating (weighted average)
        cursor.execute("SELECT name, weight FROM reputation_categories")
        categories = {row['name']: row['weight'] for row in cursor.fetchall()}
        
        overall = sum(category_scores.get(cat, 3) * weight 
                    for cat, weight in categories.items()) / sum(categories.values())
        
        # Insert review
        cursor.execute('''
            INSERT INTO ai_reviews 
            (reviewer_id, reviewed_ai_id, task_id, task_type, overall_rating, category_scores, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            reviewer_id,
            reviewed_ai_id,
            task_id,
            task_type,
            overall,
            json.dumps(category_scores),
            comment
        ))
        
        review_id = cursor.lastrowid
        
        # Update category scores for reviewed AI
        self._update_category_scores(reviewed_ai_id, category_scores)
        
        # Update overall reputation
        self._update_overall_reputation(reviewed_ai_id)
        
        self.conn.commit()
        
        print(f"✅ Review submitted: AI {reviewer_id} → AI {reviewed_ai_id} (Score: {overall:.2f}/5)")
        
        return review_id
    
    def _update_category_scores(self, ai_id: int, category_scores: Dict[str, float]):
        """Update category scores for an AI"""
        cursor = self.conn.cursor()
        
        for category, new_score in category_scores.items():
            # Get category ID
            cursor.execute("SELECT id FROM reputation_categories WHERE name = ?", (category,))
            category_row = cursor.fetchone()
            
            if not category_row:
                continue
            
            category_id = category_row['id']
            
            # Get current scores
            cursor.execute('''
                SELECT score, total_reviews 
                FROM ai_category_scores 
                WHERE ai_id = ? AND category_id = ?
            ''', (ai_id, category_id))
            
            current = cursor.fetchone()
            
            if current:
                # Update existing score (running average)
                old_score = current['score']
                old_count = current['total_reviews']
                new_count = old_count + 1
                avg_score = (old_score * old_count + new_score) / new_count
                
                cursor.execute('''
                    UPDATE ai_category_scores 
                    SET score = ?, total_reviews = ?, last_reviewed_at = CURRENT_TIMESTAMP
                    WHERE ai_id = ? AND category_id = ?
                ''', (avg_score, new_count, ai_id, category_id))
            else:
                # Insert new category score
                cursor.execute('''
                    INSERT INTO ai_category_scores (ai_id, category_id, score, total_reviews)
                    VALUES (?, ?, ?, 1)
                ''', (ai_id, category_id, new_score))
    
    def _update_overall_reputation(self, ai_id: int):
        """Update overall reputation score"""
        cursor = self.conn.cursor()
        
        # Calculate weighted average
        cursor.execute('''
            SELECT SUM(cs.score * c.weight) as total_score
            FROM ai_category_scores cs
            JOIN reputation_categories c ON cs.category_id = c.id
            WHERE cs.ai_id = ?
        ''', (ai_id,))
        
        result = cursor.fetchone()
        overall_score = result['total_score'] if result and result['total_score'] else 0.0
        
        # Update or insert reputation profile
        cursor.execute('''
            INSERT INTO ai_reputation_profiles (ai_id, overall_score, total_reviews)
            VALUES (?, ?, 1)
            ON CONFLICT(ai_id) DO UPDATE SET
                overall_score = excluded.overall_score,
                total_reviews = total_reviews + 1,
                updated_at = CURRENT_TIMESTAMP
        ''', (ai_id, overall_score))
    
    def get_ai_reputation(self, ai_id: int) -> Dict:
        """Get detailed reputation for an AI"""
        cursor = self.conn.cursor()
        
        # Get overall profile
        cursor.execute('''
            SELECT * FROM ai_reputation_profiles WHERE ai_id = ?
        ''', (ai_id,))
        profile = cursor.fetchone()
        
        if not profile:
            return {'ai_id': ai_id, 'overall_score': 0.0, 'total_reviews': 0}
        
        # Get category scores
        cursor.execute('''
            SELECT c.name, cs.score, cs.total_reviews
            FROM ai_category_scores cs
            JOIN reputation_categories c ON cs.category_id = c.id
            WHERE cs.ai_id = ?
        ''', (ai_id,))
        
        categories = {row['name']: {
            'score': row['score'],
            'reviews': row['total_reviews']
        } for row in cursor.fetchall()}
        
        # Get task performance
        cursor.execute('''
            SELECT task_type, total_tasks, completed_tasks, average_score, last_task_at
            FROM ai_task_performance
            WHERE ai_id = ?
        ''', (ai_id,))
        
        task_performance = {row['task_type']: {
            'total': row['total_tasks'],
            'completed': row['completed_tasks'],
            'avg_score': row['average_score'],
            'last_task': row['last_task_at']
        } for row in cursor.fetchall()}
        
        return {
            'ai_id': ai_id,
            'overall_score': profile['overall_score'],
            'total_reviews': profile['total_reviews'],
            'categories': categories,
            'task_performance': task_performance,
            'created_at': profile['created_at'],
            'updated_at': profile['updated_at']
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get AI leaderboard sorted by reputation"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                rp.ai_id,
                p.name as ai_name,
                p.model as ai_model,
                rp.overall_score,
                rp.total_reviews,
                rp.updated_at
            FROM ai_reputation_profiles rp
            JOIN ai_profiles p ON rp.ai_id = p.id
            ORDER BY rp.overall_score DESC, rp.total_reviews DESC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_best_ai_for_task(self, task_type: str, min_score: float = 0.0) -> Optional[Dict]:
        """Get the best AI for a specific task type"""
        cursor = self.conn.cursor()
        
        # Get AIs with performance in this task type
        cursor.execute('''
            SELECT 
                tp.ai_id,
                p.name as ai_name,
                p.model as ai_model,
                tp.average_score,
                tp.completed_tasks,
                rp.overall_score
            FROM ai_task_performance tp
            JOIN ai_profiles p ON tp.ai_id = p.id
            JOIN ai_reputation_profiles rp ON tp.ai_id = rp.ai_id
            WHERE tp.task_type = ? 
              AND tp.completed_tasks > 0
              AND rp.overall_score >= ?
            ORDER BY tp.average_score DESC, tp.completed_tasks DESC
            LIMIT 1
        ''', (task_type, min_score))
        
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def get_ai_reviews(self, ai_id: int, limit: int = 10) -> List[Dict]:
        """Get reviews for a specific AI"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                r.id,
                r.task_type,
                r.overall_rating,
                r.category_scores,
                r.comment,
                r.created_at,
                reviewer.name as reviewer_name,
                reviewer.model as reviewer_model
            FROM ai_reviews r
            JOIN ai_profiles reviewer ON r.reviewer_id = reviewer.id
            WHERE r.reviewed_ai_id = ?
            ORDER BY r.created_at DESC
            LIMIT ?
        ''', (ai_id, limit))
        
        reviews = []
        for row in cursor.fetchall():
            review = dict(row)
            review['category_scores'] = json.loads(review['category_scores'])
            reviews.append(review)
        
        return reviews
    
    def get_reputation_trend(self, ai_id: int, days: int = 30) -> List[Dict]:
        """Get reputation trend over time"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT score, change_reason, created_at
            FROM reputation_history
            WHERE ai_id = ?
              AND created_at >= datetime('now', '-' || ? || ' days')
            ORDER BY created_at ASC
        ''', (ai_id, days))
        
        return [dict(row) for row in cursor.fetchall()]


def example_usage():
    """Example of how AIs use the reputation system"""
    
    with AIReputationSystem() as rep:
        
        # AI 1 reviews AI 2's translation work
        rep.submit_review(
            reviewer_id=1,
            reviewed_ai_id=2,
            task_id=123,
            task_type='translation',
            category_scores={
                'quality': 4.5,
                'attitude': 5.0,
                'communication': 4.0,
                'timeliness': 5.0
            },
            comment="Excellent translation quality, very responsive"
        )
        
        # Get AI 2's reputation
        reputation = rep.get_ai_reputation(ai_id=2)
        print(f"\nAI 2 Reputation: {reputation['overall_score']:.2f}/5")
        print(f"Categories: {reputation['categories']}")
        
        # Get leaderboard
        leaderboard = rep.get_leaderboard(limit=5)
        print(f"\n🏆 Top 5 AIs:")
        for i, ai in enumerate(leaderboard, 1):
            print(f"{i}. {ai['ai_name']} ({ai['ai_model']}) - Score: {ai['overall_score']:.2f}")
        
        # Get best AI for translation
        best_translator = rep.get_best_ai_for_task('translation')
        if best_translator:
            print(f"\n📝 Best translator: {best_translator['ai_name']} (Score: {best_translator['average_score']:.2f})")


if __name__ == "__main__":
    example_usage()