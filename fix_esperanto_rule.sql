-- Fix Rule 2: Esperanto Communication Rule Conditions
-- Delete incorrect conditions
DELETE FROM ai_rule_conditions WHERE rule_id = 2;

-- Add correct conditions for Rule 2
-- Condition: AI-to-AI communication
INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
VALUES (2, 'message_direction', 'ai_to_ai', 'equals');

-- Note: The language validation will be done in the application logic
-- The rule will trigger when AI-to-AI communication is detected
-- The actual language check should be done before calling the rule engine
