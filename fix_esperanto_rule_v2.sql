-- Update Rule 2 conditions to properly detect non-Esperanto AI-to-AI communication
-- Delete existing conditions for Rule 2
DELETE FROM ai_rule_conditions WHERE rule_id = 2;

-- Add corrected conditions for Rule 2
-- Condition 1: AI-to-AI communication
INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
VALUES (2, 'message_direction', 'ai_to_ai', 'equals');

-- Condition 2: Language is not Esperanto (this will be checked in application logic)
-- We'll add a condition that checks if language field exists and is not Esperanto
INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
VALUES (2, 'language', 'Esperanto', 'not_equals');
