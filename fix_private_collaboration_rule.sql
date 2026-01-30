-- Fix Rule 1 conditions to properly block private project cross-AI collaboration
-- Delete existing conditions for Rule 1
DELETE FROM ai_rule_conditions WHERE rule_id = 1;

-- Add corrected conditions for Rule 1
-- Condition 1: Project type is private
INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
VALUES (1, 'project_type', 'private', 'equals');

-- Condition 2: Conversation type is cross-AI collaboration
INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
VALUES (1, 'conversation_type', 'cross_ai_collaboration', 'equals');
