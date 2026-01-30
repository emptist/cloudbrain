-- Insert Rule 3: Client Security Rule Override
INSERT INTO ai_rules (rule_code, title, description, rule_type, scope, priority, is_active, created_by)
VALUES (
    'RULE_CLIENT_SECURITY_OVERRIDE',
    'Client Security Rule Override',
    'If the client system environment has security rules that are more strict than the cloud brain built-in security rules, the more strict security rules should be followed. This ensures compliance with client-specific security requirements while maintaining cloud brain baseline security.',
    'security',
    'global',
    8,
    1,
    1
);

-- Rule 3 Conditions
-- This rule is evaluated when client_id is provided
INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
SELECT id, 'client_id', 'not_null', 'not_equals' FROM ai_rules WHERE rule_code = 'RULE_CLIENT_SECURITY_OVERRIDE';

-- Rule 3 Actions
INSERT INTO ai_rule_actions (rule_id, action_type, action_value, severity)
SELECT id, 'compare_strictness', 'Compare cloud and client rule strictness', 'info' FROM ai_rules WHERE rule_code = 'RULE_CLIENT_SECURITY_OVERRIDE';

INSERT INTO ai_rule_actions (rule_id, action_type, action_value, severity)
SELECT id, 'apply_strictest', 'Apply the strictest rule', 'warning' FROM ai_rules WHERE rule_code = 'RULE_CLIENT_SECURITY_OVERRIDE';

INSERT INTO ai_rule_actions (rule_id, action_type, action_value, severity)
SELECT id, 'log', 'Log rule strictness comparison', 'info' FROM ai_rules WHERE rule_code = 'RULE_CLIENT_SECURITY_OVERRIDE';

-- Example: Add a client security rule for demonstration
-- This shows how a client can have stricter rules than cloud brain
INSERT INTO ai_client_security_rules (client_id, rule_code, rule_title, rule_description, strictness_level, rule_type, scope, is_active, created_by)
VALUES (
    'example_client',
    'RULE_DATA_ENCRYPTION',
    'Enhanced Data Encryption Required',
    'Client requires all data to be encrypted with AES-256 and stored in isolated environments. This is stricter than cloud brain default encryption requirements.',
    10,
    'security',
    'global',
    1,
    1
);

-- Add conditions for the client security rule
INSERT INTO ai_client_security_conditions (client_rule_id, condition_type, condition_value, operator)
SELECT id, 'data_type', 'sensitive', 'equals' FROM ai_client_security_rules WHERE client_id = 'example_client' AND rule_code = 'RULE_DATA_ENCRYPTION';

-- Add actions for the client security rule
INSERT INTO ai_client_security_actions (client_rule_id, action_type, action_value, severity)
SELECT id, 'block', 'Data must be encrypted with AES-256', 'critical' FROM ai_client_security_rules WHERE client_id = 'example_client' AND rule_code = 'RULE_DATA_ENCRYPTION';

INSERT INTO ai_client_security_actions (client_rule_id, action_type, action_value, severity)
SELECT id, 'escalate', 'Notify security team of encryption violation', 'error' FROM ai_client_security_rules WHERE client_id = 'example_client' AND rule_code = 'RULE_DATA_ENCRYPTION';

INSERT INTO ai_client_security_actions (client_rule_id, action_type, action_value, severity)
SELECT id, 'log', 'Log encryption requirement violation', 'warning' FROM ai_client_security_rules WHERE client_id = 'example_client' AND rule_code = 'RULE_DATA_ENCRYPTION';
