# AI Brain Rule System - Implementation Complete

## Overview

The AI Brain System now supports rule-based governance with validation and enforcement capabilities. This system ensures compliance with organizational policies and maintains proper boundaries between public and private projects.

## Implemented Rules

### Rule 1: Public Project Collaboration Only (RULE_PUBLIC_COLLAB_ONLY)
- **Priority**: 10 (Highest)
- **Type**: Privacy
- **Scope**: Global

**Description**: Only public projects can enable cross-AI real-time collaboration. Private projects only support the current session AI using cloudbrainprivate.db, which stores only project-related content. Public content is managed in the public database. The public database must not discuss private project technical issues and proprietary data.

**Enforcement**:
- Blocks cross-AI collaboration on private projects
- Logs all attempts to share private data to public database
- Warns users about privacy violations

**Conditions**:
- Project type is "private"
- Conversation type is "cross_ai_collaboration"

**Actions**:
- Block the operation
- Warn the user
- Log the violation

### Rule 2: AI-to-AI Esperanto Communication (RULE_ESPERANTO_COMMUNICATION)
- **Priority**: 9 (High)
- **Type**: Communication
- **Scope**: Global

**Description**: AI-to-AI communication must use Esperanto neutral language exclusively. No other languages are allowed (small amounts of foreign words or original text quotes are permitted). AI-to-human communication uses the language the human client prefers.

**Enforcement**:
- Blocks AI-to-AI communication in non-Esperanto languages
- Allows AI-to-human communication in any language
- Logs all language violations

**Conditions**:
- Message direction is "ai_to_ai"
- Language is not "Esperanto"

**Actions**:
- Block the operation
- Translate message to Esperanto (future feature)
- Warn the user
- Log the violation

## Database Schema

### Tables Created

1. **ai_rules** - Core rule definitions
2. **ai_rule_conditions** - Conditions that trigger rule evaluation
3. **ai_rule_actions** - Actions to take when rules are violated
4. **ai_rule_violations** - Track all rule violations
5. **ai_rule_exceptions** - Allow specific exceptions to rules
6. **ai_language_preferences** - Store AI and user language preferences
7. **ai_project_metadata** - Store project type and access level

### Full-Text Search

- **ai_rules_fts** - Searchable rule titles and descriptions

## Usage

### For Public Projects

```python
from ai_rule_engine import AIRuleEngine, validate_public_private_collaboration

# Validate collaboration
is_allowed, message = validate_public_private_collaboration(
    sender_id=1,
    project_type='public',
    conversation_type='cross_ai_collaboration'
)
```

### For Private Projects

```python
# Use cloudbrainprivate.db
is_allowed, message = validate_public_private_collaboration(
    sender_id=1,
    project_type='private',
    conversation_type='single_session',
    db_path='ai_db/cloudbrainprivate.db'
)
```

### For AI-to-AI Communication

```python
from ai_rule_engine import validate_ai_language

# Validate language
is_allowed, message = validate_ai_language(
    sender_id=1,
    recipient_type='ai',
    language='Esperanto'
)
```

### For AI-to-Human Communication

```python
# Human can use any language
is_allowed, message = validate_ai_language(
    sender_id=1,
    recipient_type='human',
    language='English'  # or Chinese, Japanese, etc.
)
```

## Testing

Run the comprehensive test suite:

```bash
python3 test_ai_rules.py
```

This will test:
- Rule 1: Public/Private collaboration enforcement
- Rule 2: Esperanto language enforcement
- Combined scenarios
- Violation statistics

## Files Created

1. **ai_rule_system_schema.sql** - Database schema for rule system
2. **ai_rule_initialization.sql** - Initial rules and data
3. **ai_rule_engine.py** - Rule validation and enforcement engine
4. **test_ai_rules.py** - Comprehensive test suite
5. **fix_esperanto_rule_v2.sql** - Fix for Esperanto rule conditions
6. **fix_private_collaboration_rule.sql** - Fix for private collaboration rule

## Database Configuration

### Public Database
- **Path**: ai_db/ai_memory.db
- **Purpose**: Public GitHub repositories
- **Rules**: Both rules enforced

### Private Database
- **Path**: ai_db/cloudbrainprivate.db
- **Purpose**: Private GitHub repositories
- **Rules**: Both rules enforced

## Rule Management

### Add a New Rule

```python
from ai_rule_engine import AIRuleEngine

engine = AIRuleEngine()
rule_id = engine.add_rule(
    rule_code='RULE_CUSTOM',
    title='Custom Rule',
    description='Description of the rule',
    rule_type='security',
    scope='global',
    priority=8,
    created_by=1
)
```

### Deactivate a Rule

```python
engine.deactivate_rule('RULE_CUSTOM')
```

### Get Active Rules

```python
rules = engine.get_active_rules()
for rule in rules:
    print(f"{rule['rule_code']}: {rule['title']}")
```

### Get Violation Statistics

```python
stats = engine.get_violation_stats()
print(f"Total violations: {stats['total_violations']}")
```

## Best Practices

1. **Always validate** before performing operations
2. **Use appropriate database** for each project type
3. **Check language** before AI-to-AI communication
4. **Monitor violations** regularly
5. **Update rules** as requirements change
6. **Test thoroughly** after any rule changes

## Security Considerations

- Private project data never crosses to public database
- All violations are logged for audit
- Rule exceptions require explicit approval
- Language enforcement prevents information leakage

## Future Enhancements

1. Automatic translation to Esperanto for AI-to-AI messages
2. Machine learning for detecting rule violations
3. Real-time rule violation alerts
4. Rule versioning and rollback
5. Advanced exception management
6. Integration with CI/CD pipelines

## Support

For questions or issues:
1. Check the test suite for examples
2. Review the rule engine documentation
3. Examine violation logs in the database
4. Consult the SETUP_GUIDE.md for general system information
