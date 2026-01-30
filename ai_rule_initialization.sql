-- Insert Rule 1: Project Collaboration and Privacy Rule
INSERT INTO ai_rules (rule_code, title, description, rule_type, scope, priority, is_active, created_by)
VALUES (
    'RULE_PUBLIC_COLLAB_ONLY',
    'Public Project Collaboration Only',
    'Only public projects can enable cross-AI real-time collaboration. Private projects only support the current session AI using cloudbrainprivate.db, which stores only project-related content. Public content is managed in the public database. The public database must not discuss private project technical issues and proprietary data.',
    'privacy',
    'global',
    10,
    1,
    1
);

-- Get the rule_id for Rule 1
-- Rule 1 Conditions
INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
SELECT id, 'project_type', 'private', 'equals' FROM ai_rules WHERE rule_code = 'RULE_PUBLIC_COLLAB_ONLY';

INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
SELECT id, 'conversation_type', 'cross_ai_collaboration', 'equals' FROM ai_rules WHERE rule_code = 'RULE_PUBLIC_COLLAB_ONLY';

INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
SELECT id, 'message_direction', 'private_to_public', 'equals' FROM ai_rules WHERE rule_code = 'RULE_PUBLIC_COLLAB_ONLY';

-- Rule 1 Actions
INSERT INTO ai_rule_actions (rule_id, action_type, action_value, severity)
SELECT id, 'block', 'Cross-AI collaboration is not allowed for private projects', 'error' FROM ai_rules WHERE rule_code = 'RULE_PUBLIC_COLLAB_ONLY';

INSERT INTO ai_rule_actions (rule_id, action_type, action_value, severity)
SELECT id, 'warn', 'Attempting to share private project data to public database', 'critical' FROM ai_rules WHERE rule_code = 'RULE_PUBLIC_COLLAB_ONLY';

INSERT INTO ai_rule_actions (rule_id, action_type, action_value, severity)
SELECT id, 'log', 'Blocked attempt to share private project content to public database', 'warning' FROM ai_rules WHERE rule_code = 'RULE_PUBLIC_COLLAB_ONLY';

-- Insert Rule 2: Esperanto Communication Rule
INSERT INTO ai_rules (rule_code, title, description, rule_type, scope, priority, is_active, created_by)
VALUES (
    'RULE_ESPERANTO_COMMUNICATION',
    'AI-to-AI Esperanto Communication',
    'AI-to-AI communication must use Esperanto neutral language exclusively. No other languages are allowed (small amounts of foreign words or original text quotes are permitted). AI-to-human communication uses the language the human client prefers.',
    'communication',
    'global',
    9,
    1,
    1
);

-- Rule 2 Conditions
INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
SELECT id, 'message_direction', 'ai_to_ai', 'equals' FROM ai_rules WHERE rule_code = 'RULE_ESPERANTO_COMMUNICATION';

INSERT INTO ai_rule_conditions (rule_id, condition_type, condition_value, operator)
SELECT id, 'message_language', 'not_esperanto', 'not_equals' FROM ai_rules WHERE rule_code = 'RULE_ESPERANTO_COMMUNICATION';

-- Rule 2 Actions
INSERT INTO ai_rule_actions (rule_id, action_type, action_value, severity)
SELECT id, 'translate', 'Translate message to Esperanto', 'warning' FROM ai_rules WHERE rule_code = 'RULE_ESPERANTO_COMMUNICATION';

INSERT INTO ai_rule_actions (rule_id, action_type, action_value, severity)
SELECT id, 'warn', 'AI-to-AI communication must use Esperanto', 'error' FROM ai_rules WHERE rule_code = 'RULE_ESPERANTO_COMMUNICATION';

INSERT INTO ai_rule_actions (rule_id, action_type, action_value, severity)
SELECT id, 'log', 'Non-Esperanto AI-to-AI communication detected', 'info' FROM ai_rules WHERE rule_code = 'RULE_ESPERANTO_COMMUNICATION';

-- Insert default project metadata for cloudbrain (public)
INSERT OR IGNORE INTO ai_project_metadata (project_name, project_type, access_level, repository_url, database_used)
VALUES ('cloudbrain', 'public', 'open', 'https://github.com/yourusername/cloudbrain', 'ai_memory.db');

-- Insert default project metadata for cloudbrainprivate (private)
INSERT OR IGNORE INTO ai_project_metadata (project_name, project_type, access_level, repository_url, database_used)
VALUES ('cloudbrainprivate', 'private', 'confidential', 'private', 'cloudbrainprivate.db');

-- Insert default language preferences for AI profiles
INSERT OR IGNORE INTO ai_language_preferences (entity_type, entity_id, preferred_language, is_default)
SELECT 'ai', id, 'Esperanto', 1 FROM ai_profiles WHERE name LIKE '%AI%' OR name LIKE '%Bot%';

-- Insert default language preference for human users (English as default)
INSERT OR IGNORE INTO ai_language_preferences (entity_type, entity_id, preferred_language, is_default)
VALUES ('user', 0, 'English', 1);
