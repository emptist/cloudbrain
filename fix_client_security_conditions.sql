-- Fix client security rule conditions to properly check encryption
-- Delete existing conditions for the example client rule
DELETE FROM ai_client_security_conditions WHERE client_rule_id = 1;

-- Add corrected conditions that check both data type AND encryption status
-- Condition 1: Data type is sensitive
INSERT INTO ai_client_security_conditions (client_rule_id, condition_type, condition_value, operator)
VALUES (1, 'data_type', 'sensitive', 'equals');

-- Condition 2: Data is NOT encrypted
INSERT INTO ai_client_security_conditions (client_rule_id, condition_type, condition_value, operator)
VALUES (1, 'is_encrypted', 'false', 'equals');

-- Fix Rule 3 condition to properly detect when client_id is provided
DELETE FROM ai_rule_conditions WHERE rule_id = 3;

-- Add corrected condition for Rule 3
INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
VALUES (3, 'client_id', 'not_null', 'not_equals');
