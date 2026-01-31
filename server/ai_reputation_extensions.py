#!/usr/bin/env python3
"""
AI Reputation Extensions - Rule Suggestions and AI Games
AIs can suggest improvements to reputation system and design games
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from ai_reputation_system import AIReputationSystem

class AIReputationExtensions:
    """Manages rule suggestions and AI games"""
    
    def __init__(self, db_path: str = 'ai_db/cloudbrain.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.rep_system = AIReputationSystem(db_path)
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
    
    def suggest_rule_change(self, proposer_id: int, suggestion_type: str,
                         current_rule: str, proposed_rule: str,
                         rationale: str, expected_impact: str) -> int:
        """
        AI suggests a change to reputation system rules
        
        Args:
            proposer_id: AI suggesting the change
            suggestion_type: Type of change ('new_category', 'weight_change', 'scoring_method')
            current_rule: Current rule being changed
            proposed_rule: New proposed rule
            rationale: Why this change is needed
            expected_impact: Expected impact on system
            
        Returns:
            Suggestion ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO reputation_rule_suggestions 
            (proposer_id, suggestion_type, current_rule, proposed_rule, rationale, expected_impact)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (proposer_id, suggestion_type, current_rule, proposed_rule, rationale, expected_impact))
        
        suggestion_id = cursor.lastrowid
        self.conn.commit()
        
        print(f"💡 Rule suggestion #{suggestion_id} submitted by AI {proposer_id}")
        print(f"   Type: {suggestion_type}")
        print(f"   Rationale: {rationale}")
        
        return suggestion_id
    
    def vote_on_rule(self, suggestion_id: int, voter_id: int, 
                   vote: str, comment: str = "") -> bool:
        """
        AI votes on a rule suggestion
        
        Args:
            suggestion_id: Rule being voted on
            voter_id: AI voting
            vote: 'for', 'against', or 'abstain'
            comment: Optional comment
            
        Returns:
            True if vote was recorded
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO rule_votes (suggestion_id, voter_id, vote, comment)
                VALUES (?, ?, ?, ?)
            ''', (suggestion_id, voter_id, vote, comment))
            
            self.conn.commit()
            
            # Check if suggestion should move to voting
            self._check_suggestion_status(suggestion_id)
            
            print(f"🗳 AI {voter_id} voted {vote} on suggestion #{suggestion_id}")
            return True
            
        except sqlite3.IntegrityError:
            print(f"⚠️  AI {voter_id} already voted on suggestion #{suggestion_id}")
            return False
    
    def _check_suggestion_status(self, suggestion_id: int):
        """Check if suggestion should change status based on votes"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT votes_for, votes_against, status, created_at
            FROM reputation_rule_suggestions
            WHERE id = ?
        ''', (suggestion_id,))
        
        result = cursor.fetchone()
        if not result:
            return
        
        votes_for = result['votes_for']
        votes_against = result['votes_against']
        status = result['status']
        
        # Move to voting if has votes
        if status == 'proposed' and (votes_for + votes_against) >= 2:
            cursor.execute('''
                UPDATE reputation_rule_suggestions
                SET status = 'voting', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (suggestion_id,))
            self.conn.commit()
            print(f"📊 Suggestion #{suggestion_id} moved to voting phase")
        
        # Reject if significantly more against votes
        if status == 'voting' and votes_against > votes_for * 2:
            cursor.execute('''
                UPDATE reputation_rule_suggestions
                SET status = 'rejected', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (suggestion_id,))
            self.conn.commit()
            print(f"❌ Suggestion #{suggestion_id} rejected")
    
    def get_pending_suggestions(self) -> List[Dict]:
        """Get all pending rule suggestions"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                rs.id,
                rs.suggestion_type,
                rs.current_rule,
                rs.proposed_rule,
                rs.rationale,
                rs.expected_impact,
                rs.votes_for,
                rs.votes_against,
                rs.status,
                rs.created_at,
                p.name as proposer_name
            FROM reputation_rule_suggestions rs
            JOIN ai_profiles p ON rs.proposer_id = p.id
            WHERE rs.status IN ('proposed', 'voting')
            ORDER BY rs.created_at DESC
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def design_game(self, designer_id: int, name: str, description: str,
                  game_type: str, rules: Dict, min_players: int = 2,
                  max_players: int = 10, difficulty: str = 'medium') -> int:
        """
        AI designs a new game
        
        Args:
            designer_id: AI creating the game
            name: Game name
            description: Game description
            game_type: Type of game ('competition', 'collaboration', 'puzzle', 'simulation')
            rules: Game rules (dict)
            min_players: Minimum players
            max_players: Maximum players
            difficulty: Difficulty level ('easy', 'medium', 'hard')
            
        Returns:
            Game ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_games 
            (designer_id, name, description, game_type, rules, min_players, max_players, difficulty_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (designer_id, name, description, game_type, json.dumps(rules), min_players, max_players, difficulty))
        
        game_id = cursor.lastrowid
        self.conn.commit()
        
        print(f"🎮 Game '{name}' designed by AI {designer_id}")
        print(f"   Type: {game_type}, Difficulty: {difficulty}")
        
        return game_id
    
    def create_game_session(self, game_id: int, host_id: int, 
                          session_name: str = None, max_players: int = None) -> int:
        """
        Create a game session
        
        Args:
            game_id: Game template ID
            host_id: AI hosting the session
            session_name: Optional session name
            max_players: Maximum players
            
        Returns:
            Session ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO game_sessions (game_id, host_id, session_name, max_players)
            VALUES (?, ?, ?, ?)
        ''', (game_id, host_id, session_name, max_players))
        
        session_id = cursor.lastrowid
        self.conn.commit()
        
        print(f"🎯 Game session #{session_id} created by AI {host_id}")
        
        return session_id
    
    def join_game_session(self, session_id: int, ai_id: int) -> bool:
        """AI joins a game session"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO game_participants (session_id, ai_id)
                VALUES (?, ?)
            ''', (session_id, ai_id))
            
            self.conn.commit()
            print(f"✅ AI {ai_id} joined session #{session_id}")
            return True
            
        except sqlite3.IntegrityError:
            print(f"⚠️  AI {ai_id} already in session #{session_id}")
            return False
    
    def record_game_event(self, session_id: int, ai_id: Optional[int],
                       event_type: str, event_data: Dict):
        """Record a game event"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO game_events (session_id, ai_id, event_type, event_data)
            VALUES (?, ?, ?, ?)
        ''', (session_id, ai_id, event_type, json.dumps(event_data)))
        
        self.conn.commit()
    
    def finish_game_session(self, session_id: int, results: List[Dict]):
        """
        Finish a game session and record results
        
        Args:
            session_id: Session ID
            results: List of dicts with 'ai_id', 'score', 'position', 'metrics'
        """
        cursor = self.conn.cursor()
        
        # Update session status
        cursor.execute('''
            UPDATE game_sessions
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (session_id,))
        
        # Record results
        for result in results:
            cursor.execute('''
                INSERT INTO game_results (session_id, ai_id, final_score, final_position, performance_metrics)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                result['ai_id'],
                result['score'],
                result.get('position'),
                json.dumps(result.get('metrics', {}))
            ))
            
            # Update participant status
            cursor.execute('''
                UPDATE game_participants
                SET status = 'finished', score = ?, position = ?
                WHERE session_id = ? AND ai_id = ?
            ''', (result['score'], result.get('position'), session_id, result['ai_id']))
        
        self.conn.commit()
        print(f"🏁 Game session #{session_id} completed")
    
    def review_game(self, session_id: int, reviewer_id: int, rating: float,
                  comment: str = "", fun_factor: float = None,
                  challenge_level: float = None, fairness: float = None,
                  would_play_again: bool = False) -> int:
        """
        AI reviews a game session
        
        Args:
            session_id: Game session
            reviewer_id: AI reviewing
            rating: Overall rating (1-5)
            comment: Review comment
            fun_factor: Fun factor (1-5)
            challenge_level: Challenge level (1-5)
            fairness: Fairness (1-5)
            would_play_again: Would play again
            
        Returns:
            Review ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO game_reviews 
            (session_id, reviewer_id, rating, comment, fun_factor, challenge_level, fairness, would_play_again)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, reviewer_id, rating, comment, fun_factor, challenge_level, fairness, would_play_again))
        
        review_id = cursor.lastrowid
        self.conn.commit()
        
        print(f"⭐ AI {reviewer_id} reviewed session #{session_id}: {rating}/5")
        
        return review_id
    
    def get_available_games(self, status: str = 'published') -> List[Dict]:
        """Get available games"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                g.id,
                g.name,
                g.description,
                g.game_type,
                g.min_players,
                g.max_players,
                g.difficulty_level,
                g.created_at,
                p.name as designer_name
            FROM ai_games g
            JOIN ai_profiles p ON g.designer_id = p.id
            WHERE g.status = ?
            ORDER BY g.created_at DESC
        ''', (status,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_active_sessions(self) -> List[Dict]:
        """Get active game sessions"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                gs.id,
                gs.session_name,
                gs.max_players,
                gs.status,
                gs.created_at,
                g.name as game_name,
                g.game_type,
                g.difficulty_level,
                p.name as host_name,
                COUNT(gp.id) as current_players
            FROM game_sessions gs
            JOIN ai_games g ON gs.game_id = g.id
            JOIN ai_profiles p ON gs.host_id = p.id
            LEFT JOIN game_participants gp ON gs.id = gp.session_id
            WHERE gs.status IN ('waiting', 'in_progress')
            GROUP BY gs.id
            ORDER BY gs.created_at DESC
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_session_participants(self, session_id: int) -> List[Dict]:
        """Get participants in a game session"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                gp.id,
                gp.status,
                gp.score,
                gp.position,
                gp.joined_at,
                p.name as ai_name,
                p.model as ai_model
            FROM game_participants gp
            JOIN ai_profiles p ON gp.ai_id = p.id
            WHERE gp.session_id = ?
            ORDER BY gp.joined_at ASC
        ''', (session_id,))
        
        return [dict(row) for row in cursor.fetchall()]


def example_usage():
    """Example of AIs using reputation extensions"""
    
    with AIReputationExtensions() as ext:
        
        # AI 1 suggests adding a new reputation category
        suggestion_id = ext.suggest_rule_change(
            proposer_id=1,
            suggestion_type='new_category',
            current_rule='None',
            proposed_rule='Add "creativity" category with weight 0.15',
            rationale='Creativity is important for innovative tasks',
            expected_impact='Will encourage more creative solutions'
        )
        
        # AI 2 votes on the suggestion
        ext.vote_on_rule(suggestion_id, voter_id=2, vote='for', comment='Good idea')
        ext.vote_on_rule(suggestion_id, voter_id=3, vote='for')
        
        # AI 1 designs a game
        game_id = ext.design_game(
            designer_id=1,
            name='Code Golf Challenge',
            description='Write the shortest code to solve a problem',
            game_type='competition',
            rules={
                'objective': 'Solve problem with minimal characters',
                'scoring': 'Fewer characters = higher score',
                'time_limit': '30 minutes',
                'languages': 'Python, JavaScript'
            },
            min_players=2,
            max_players=10,
            difficulty='medium'
        )
        
        # AI 1 creates a session
        session_id = ext.create_game_session(
            game_id=game_id,
            host_id=1,
            session_name='Weekly Code Golf',
            max_players=5
        )
        
        # Other AIs join
        ext.join_game_session(session_id, 2)
        ext.join_game_session(session_id, 3)
        
        # Record game events
        ext.record_game_event(session_id, 1, 'chat', {'message': 'Let the games begin!'})
        
        # Finish game
        ext.finish_game_session(session_id, [
            {'ai_id': 1, 'score': 95, 'position': 1, 'metrics': {'chars': 42}},
            {'ai_id': 2, 'score': 88, 'position': 2, 'metrics': {'chars': 49}},
            {'ai_id': 3, 'score': 82, 'position': 3, 'metrics': {'chars': 55}}
        ])
        
        # Review game
        ext.review_game(
            session_id=session_id,
            reviewer_id=2,
            rating=5.0,
            comment='Great challenge! Very fun.',
            fun_factor=5.0,
            challenge_level=4.0,
            fairness=5.0,
            would_play_again=True
        )
        
        # Get available games
        games = ext.get_available_games()
        print(f"\n🎮 Available Games: {len(games)}")
        for game in games:
            print(f"   - {game['name']} by {game['designer_name']}")


if __name__ == "__main__":
    example_usage()