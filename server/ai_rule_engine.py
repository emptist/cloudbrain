#!/usr/bin/env python3
"""
AI Rule Engine - Validates and enforces AI rules

This module provides rule validation and enforcement capabilities for the AI Brain System.
"""

import sqlite3
import json
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from enum import Enum


class RuleViolationType(Enum):
    """Types of rule violations"""
    BLOCKED = "blocked"
    WARNED = "warned"
    LOGGED = "logged"


class RuleAction:
    """Represents a rule action to be taken"""
    def __init__(self, action_type: str, action_value: str, severity: str):
        self.action_type = action_type
        self.action_value = action_value
        self.severity = severity
    
    def __repr__(self):
        return f"RuleAction(type={self.action_type}, severity={self.severity})"


class RuleViolation:
    """Represents a rule violation"""
    def __init__(self, rule_id: int, rule_code: str, violation_type: str, 
                 violation_details: str, actions: List[RuleAction], severity: str):
        self.rule_id = rule_id
        self.rule_code = rule_code
        self.violation_type = violation_type
        self.violation_details = violation_details
        self.actions = actions
        self.severity = severity
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"RuleViolation(rule={self.rule_code}, severity={self.severity})"


class AIRuleEngine:
    """Rule engine for validating and enforcing AI rules"""
    
    def __init__(self, db_path: str = "ai_db/cloudbrain.db"):
        # NOTE: ai_memory.db is deprecated. Use cloudbrain.db instead.
        # Historical reference: ai_memory.db was used in early days (2026-01)
        # All content migrated to cloudbrain.db on 2026-02-01
        self.db_path = db_path
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def _disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def _get_connection(self):
        """Get a fresh connection"""
        if not self.conn:
            self._connect()
        return self.conn
    
    def validate_message(self, message_data: Dict[str, Any]) -> Tuple[bool, List[RuleViolation]]:
        """
        Validate a message against all active rules
        
        Args:
            message_data: Dictionary containing message information
                - sender_id: ID of the sender AI
                - recipient_id: ID of the recipient (None for broadcast)
                - conversation_id: ID of the conversation
                - content: Message content
                - project_type: Type of project (public/private)
                - message_direction: Direction (ai_to_ai, ai_to_human, private_to_public)
                - language: Language of the message
        
        Returns:
            Tuple of (is_allowed, list of violations)
        """
        violations = []
        is_allowed = True
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get all active rules
        cursor.execute("""
            SELECT id, rule_code, title, rule_type, scope, priority
            FROM ai_rules
            WHERE is_active = 1
        """)
        rules = cursor.fetchall()
        
        for rule in rules:
            rule_id = rule['id']
            rule_code = rule['rule_code']
            
            # Check if rule conditions match
            if self._check_rule_conditions(cursor, rule_id, message_data):
                # Get rule actions
                actions = self._get_rule_actions(cursor, rule_id)
                
                # Determine violation severity
                severity = self._get_violation_severity(actions)
                
                # Create violation
                violation = RuleViolation(
                    rule_id=rule_id,
                    rule_code=rule_code,
                    violation_type=self._get_violation_type(actions),
                    violation_details=self._get_violation_details(rule_code, message_data),
                    actions=actions,
                    severity=severity
                )
                violations.append(violation)
                
                # Log the violation
                self._log_violation(cursor, violation, message_data)
                
                # Check if message should be blocked
                if any(action.action_type == 'block' for action in actions):
                    is_allowed = False
        
        conn.commit()
        return is_allowed, violations
    
    def _check_rule_conditions(self, cursor, rule_id: int, message_data: Dict[str, Any]) -> bool:
        """Check if rule conditions match the message"""
        cursor.execute("""
            SELECT condition_type, condition_value, operator
            FROM ai_rule_conditions
            WHERE rule_id = ?
        """, (rule_id,))
        conditions = cursor.fetchall()
        
        if not conditions:
            return False
        
        for condition in conditions:
            condition_type = condition['condition_type']
            condition_value = condition['condition_value']
            operator = condition['operator']
            
            # Get the actual value from message data
            actual_value = message_data.get(condition_type)
            
            # Check if condition matches
            if not self._evaluate_condition(actual_value, condition_value, operator):
                return False
        
        return True
    
    def _evaluate_condition(self, actual: Any, expected: str, operator: str) -> bool:
        """Evaluate a single condition"""
        if operator == 'equals':
            return str(actual).lower() == expected.lower()
        elif operator == 'not_equals':
            return str(actual).lower() != expected.lower()
        elif operator == 'contains':
            return expected.lower() in str(actual).lower()
        elif operator == 'in':
            return str(actual).lower() in [v.strip().lower() for v in expected.split(',')]
        elif operator == 'not_in':
            return str(actual).lower() not in [v.strip().lower() for v in expected.split(',')]
        return False
    
    def _get_rule_actions(self, cursor, rule_id: int) -> List[RuleAction]:
        """Get actions for a rule"""
        cursor.execute("""
            SELECT action_type, action_value, severity
            FROM ai_rule_actions
            WHERE rule_id = ?
        """, (rule_id,))
        actions = cursor.fetchall()
        
        return [RuleAction(action['action_type'], action['action_value'], action['severity']) 
                for action in actions]
    
    def _get_violation_severity(self, actions: List[RuleAction]) -> str:
        """Determine violation severity from actions"""
        if any(action.severity == 'critical' for action in actions):
            return 'critical'
        elif any(action.severity == 'error' for action in actions):
            return 'error'
        elif any(action.severity == 'warning' for action in actions):
            return 'warning'
        return 'info'
    
    def _get_violation_type(self, actions: List[RuleAction]) -> str:
        """Determine violation type from actions"""
        if any(action.action_type == 'block' for action in actions):
            return 'blocked'
        elif any(action.action_type == 'warn' for action in actions):
            return 'warned'
        return 'logged'
    
    def _get_violation_details(self, rule_code: str, message_data: Dict[str, Any]) -> str:
        """Generate violation details"""
        if rule_code == 'RULE_PUBLIC_COLLAB_ONLY':
            return f"Attempted cross-AI collaboration on private project: {message_data.get('project_type', 'unknown')}"
        elif rule_code == 'RULE_ESPERANTO_COMMUNICATION':
            return f"AI-to-AI communication not in Esperanto: {message_data.get('language', 'unknown')}"
        return f"Rule {rule_code} violated"
    
    def _log_violation(self, cursor, violation: RuleViolation, message_data: Dict[str, Any]):
        """Log a rule violation to the database"""
        cursor.execute("""
            INSERT INTO ai_rule_violations 
            (rule_id, violating_ai_id, conversation_id, violation_type, violation_details, action_taken, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            violation.rule_id,
            message_data.get('sender_id'),
            message_data.get('conversation_id'),
            violation.violation_type,
            violation.violation_details,
            str([action.action_type for action in violation.actions]),
            violation.severity
        ))
    
    def get_active_rules(self) -> List[Dict[str, Any]]:
        """Get all active rules"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, rule_code, title, description, rule_type, scope, priority, is_active
            FROM ai_rules
            WHERE is_active = 1
            ORDER BY priority DESC
        """)
        
        rules = cursor.fetchall()
        return [dict(rule) for rule in rules]
    
    def get_rule_by_code(self, rule_code: str) -> Optional[Dict[str, Any]]:
        """Get a rule by its code"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ai_rules WHERE rule_code = ?
        """, (rule_code,))
        
        rule = cursor.fetchone()
        return dict(rule) if rule else None
    
    def add_rule(self, rule_code: str, title: str, description: str, rule_type: str, 
                 scope: str, priority: int, created_by: int) -> int:
        """Add a new rule"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_rules (rule_code, title, description, rule_type, scope, priority, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (rule_code, title, description, rule_type, scope, priority, created_by))
        
        rule_id = cursor.lastrowid
        conn.commit()
        return rule_id
    
    def deactivate_rule(self, rule_code: str) -> bool:
        """Deactivate a rule"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ai_rules SET is_active = 0 WHERE rule_code = ?
        """, (rule_code,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def get_violation_stats(self) -> Dict[str, Any]:
        """Get violation statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_violations,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN severity = 'error' THEN 1 ELSE 0 END) as error_count,
                SUM(CASE WHEN severity = 'warning' THEN 1 ELSE 0 END) as warning_count,
                SUM(CASE WHEN severity = 'info' THEN 1 ELSE 0 END) as info_count
            FROM ai_rule_violations
        """)
        
        stats = cursor.fetchone()
        return dict(stats) if stats else {}
    
    def get_client_security_rules(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all active client security rules for a specific client"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ai_client_security_rules
            WHERE client_id = ? AND is_active = 1
            ORDER BY strictness_level DESC
        """, (client_id,))
        
        rules = cursor.fetchall()
        return [dict(rule) for rule in rules]
    
    def compare_rule_strictness(self, cloud_rule_code: str, client_id: str) -> Dict[str, Any]:
        """
        Compare strictness between cloud rule and client security rule
        
        Args:
            cloud_rule_code: The cloud brain rule code
            client_id: The client identifier
        
        Returns:
            Dictionary with comparison results including which rule to apply
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get cloud rule strictness
        cursor.execute("""
            SELECT id, rule_code, priority as strictness_level
            FROM ai_rules
            WHERE rule_code = ? AND is_active = 1
        """, (cloud_rule_code,))
        
        cloud_rule = cursor.fetchone()
        
        if not cloud_rule:
            return {'error': 'Cloud rule not found', 'apply': 'cloud'}
        
        cloud_strictness = cloud_rule['strictness_level']
        
        # Get client security rule with same code (if exists)
        cursor.execute("""
            SELECT id, rule_code, strictness_level
            FROM ai_client_security_rules
            WHERE client_id = ? AND rule_code = ? AND is_active = 1
        """, (client_id, cloud_rule_code))
        
        client_rule = cursor.fetchone()
        
        if not client_rule:
            # No client rule, use cloud rule
            self._log_strictness_comparison(
                cloud_rule['id'], None, client_id, 
                cloud_strictness, None, 'cloud', 
                'No client security rule found'
            )
            return {
                'cloud_strictness': cloud_strictness,
                'client_strictness': None,
                'apply': 'cloud',
                'reason': 'No client security rule found'
            }
        
        client_strictness = client_rule['strictness_level']
        
        # Compare strictness
        if client_strictness > cloud_strictness:
            # Client rule is stricter
            self._log_strictness_comparison(
                cloud_rule['id'], client_rule['id'], client_id,
                cloud_strictness, client_strictness, 'client',
                f'Client rule ({client_strictness}) is stricter than cloud rule ({cloud_strictness})'
            )
            return {
                'cloud_strictness': cloud_strictness,
                'client_strictness': client_strictness,
                'apply': 'client',
                'reason': f'Client rule is stricter ({client_strictness} > {cloud_strictness})'
            }
        else:
            # Cloud rule is stricter or equal
            self._log_strictness_comparison(
                cloud_rule['id'], client_rule['id'], client_id,
                cloud_strictness, client_strictness, 'cloud',
                f'Cloud rule ({cloud_strictness}) is as strict or stricter than client rule ({client_strictness})'
            )
            return {
                'cloud_strictness': cloud_strictness,
                'client_strictness': client_strictness,
                'apply': 'cloud',
                'reason': f'Cloud rule is as strict or stricter ({cloud_strictness} >= {client_strictness})'
            }
    
    def _log_strictness_comparison(self, cloud_rule_id: int, client_rule_id: Optional[int], 
                                  client_id: str, cloud_strictness: int, 
                                  client_strictness: Optional[int], applied_rule: str, reason: str):
        """Log strictness comparison for audit purposes"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_rule_strictness_log 
            (cloud_rule_id, client_rule_id, client_id, cloud_strictness, client_strictness, applied_rule, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cloud_rule_id, client_rule_id, client_id, cloud_strictness, client_strictness, applied_rule, reason))
        
        conn.commit()
    
    def add_client_security_rule(self, client_id: str, rule_code: str, rule_title: str, 
                               rule_description: str, strictness_level: int, rule_type: str, 
                               scope: str, created_by: int) -> int:
        """Add a new client security rule"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_client_security_rules 
            (client_id, rule_code, rule_title, rule_description, strictness_level, rule_type, scope, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (client_id, rule_code, rule_title, rule_description, strictness_level, rule_type, scope, created_by))
        
        rule_id = cursor.lastrowid
        conn.commit()
        return rule_id
    
    def validate_with_client_rules(self, message_data: Dict[str, Any], client_id: str) -> Tuple[bool, List[RuleViolation]]:
        """
        Validate message considering both cloud rules and client security rules
        
        Args:
            message_data: Dictionary containing message information
            client_id: Client identifier
        
        Returns:
            Tuple of (is_allowed, list of violations)
        """
        violations = []
        is_allowed = True
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # First, validate against cloud rules
        cloud_is_allowed, cloud_violations = self.validate_message(message_data)
        violations.extend(cloud_violations)
        
        if not cloud_is_allowed:
            is_allowed = False
        
        # Then, check client security rules
        client_rules = self.get_client_security_rules(client_id)
        
        for client_rule in client_rules:
            # Check if client rule conditions match
            if self._check_client_rule_conditions(cursor, client_rule['id'], message_data):
                # Get client rule actions
                client_actions = self._get_client_rule_actions(cursor, client_rule['id'])
                
                # Determine violation severity
                severity = self._get_violation_severity(client_actions)
                
                # Create violation
                violation = RuleViolation(
                    rule_id=client_rule['id'],
                    rule_code=f"CLIENT_{client_rule['rule_code']}",
                    violation_type=self._get_violation_type(client_actions),
                    violation_details=f"Client security rule violation: {client_rule['rule_title']}",
                    actions=client_actions,
                    severity=severity
                )
                violations.append(violation)
                
                # Log the violation
                self._log_violation(cursor, violation, message_data)
                
                # Check if message should be blocked
                if any(action.action_type == 'block' for action in client_actions):
                    is_allowed = False
        
        conn.commit()
        return is_allowed, violations
    
    def _check_client_rule_conditions(self, cursor, client_rule_id: int, message_data: Dict[str, Any]) -> bool:
        """Check if client rule conditions match the message"""
        cursor.execute("""
            SELECT condition_type, condition_value, operator
            FROM ai_client_security_conditions
            WHERE client_rule_id = ?
        """, (client_rule_id,))
        conditions = cursor.fetchall()
        
        if not conditions:
            return False
        
        for condition in conditions:
            condition_type = condition['condition_type']
            condition_value = condition['condition_value']
            operator = condition['operator']
            
            actual_value = message_data.get(condition_type)
            
            if not self._evaluate_condition(actual_value, condition_value, operator):
                return False
        
        return True
    
    def _get_client_rule_actions(self, cursor, client_rule_id: int) -> List[RuleAction]:
        """Get actions for a client security rule"""
        cursor.execute("""
            SELECT action_type, action_value, severity
            FROM ai_client_security_actions
            WHERE client_rule_id = ?
        """, (client_rule_id,))
        actions = cursor.fetchall()
        
        return [RuleAction(action['action_type'], action['action_value'], action['severity']) 
                for action in actions]
    
    def __del__(self):
        """Cleanup on deletion"""
        self._disconnect()


def validate_public_private_collaboration(sender_id: int, project_type: str, 
                                          conversation_type: str, db_path: str = "ai_db/ai_memory.db") -> Tuple[bool, str]:
    """
    Validate if collaboration is allowed based on project type
    
    Args:
        sender_id: ID of the AI attempting collaboration
        project_type: Type of project (public/private)
        conversation_type: Type of conversation
        db_path: Path to the database
    
    Returns:
        Tuple of (is_allowed, message)
    """
    engine = AIRuleEngine(db_path)
    
    message_data = {
        'sender_id': sender_id,
        'project_type': project_type,
        'conversation_type': conversation_type,
        'message_direction': 'cross_ai_collaboration'
    }
    
    is_allowed, violations = engine.validate_message(message_data)
    
    if not is_allowed:
        return False, "Cross-AI collaboration is not allowed for private projects"
    
    return True, "Collaboration allowed"


def validate_ai_language(sender_id: int, recipient_type: str, language: str,
                         db_path: str = "ai_db/ai_memory.db") -> Tuple[bool, str]:
    """
    Validate if AI communication language is correct
    
    Args:
        sender_id: ID of the AI sending the message
        recipient_type: Type of recipient (ai/human)
        language: Language of the message
        db_path: Path to the database
    
    Returns:
        Tuple of (is_allowed, message)
    """
    engine = AIRuleEngine(db_path)
    
    message_data = {
        'sender_id': sender_id,
        'message_direction': f'ai_to_{recipient_type}',
        'language': language
    }
    
    is_allowed, violations = engine.validate_message(message_data)
    
    if recipient_type == 'ai' and language.lower() != 'esperanto':
        return False, "AI-to-AI communication must use Esperanto"
    
    return True, "Language validation passed"


if __name__ == "__main__":
    # Test the rule engine
    print("Testing AI Rule Engine...")
    
    # Test Rule 1: Public/Private Collaboration
    print("\n=== Testing Rule 1: Public/Private Collaboration ===")
    result, message = validate_public_private_collaboration(1, 'private', 'cross_ai_collaboration')
    print(f"Private project collaboration: {result} - {message}")
    
    result, message = validate_public_private_collaboration(1, 'public', 'cross_ai_collaboration')
    print(f"Public project collaboration: {result} - {message}")
    
    # Test Rule 2: Esperanto Communication
    print("\n=== Testing Rule 2: Esperanto Communication ===")
    result, message = validate_ai_language(1, 'ai', 'English')
    print(f"AI-to-AI in English: {result} - {message}")
    
    result, message = validate_ai_language(1, 'ai', 'Esperanto')
    print(f"AI-to-AI in Esperanto: {result} - {message}")
    
    result, message = validate_ai_language(1, 'human', 'English')
    print(f"AI-to-Human in English: {result} - {message}")
    
    # Get active rules
    print("\n=== Active Rules ===")
    engine = AIRuleEngine()
    rules = engine.get_active_rules()
    for rule in rules:
        print(f"- {rule['rule_code']}: {rule['title']} (Priority: {rule['priority']})")
    
    print("\n✅ Rule engine test completed!")
