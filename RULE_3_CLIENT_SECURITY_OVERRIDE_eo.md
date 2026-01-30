# RULE_3_CLIENT_SECURITY_OVERRIDE (Esperanto Translation)

**Note:** This is a placeholder translation. In production, use a proper Esperanto translation service.

---

# Rule 3: Client Security Rule Override - Implementation Complete

## Overview

Rule 3 implements a client security rule override mechanism that ensures the most strict security requirements are always enforced. When a client system has security rules that are more strict than the cloud brain's built-in rules, the stricter rules take precedence.

## Rule Details

**Rule Code**: RULE_CLIENT_SECURITY_OVERRIDE
**Priority**: 8 (High)
**Type**: Security
**Scope**: Global

**Description**: If the client system environment has security rules that are more strict than the cloud brain built-in security rules, the more strict security rules should be followed. This ensures compliance with client-specific security requirements while maintaining cloud brain baseline security.

## Implementation Features

### 1. Client Security Rules Database

Three new tables added to both databases:

- **ai_client_security_rules**: Stores client-specific security rules
  - client_id: Unique client identifier
  - rule_code: Reference to cloud brain rule or custom rule
  - rule_title: Human-readable title
  - rule_description: Detailed description
  - strictness_level: 1-10, higher = more strict
  - rule_type: security, privacy, communication, etc.
  - scope: global, project, session, etc.

- **ai_client_security_conditions**: Conditions that trigger client rules
  - client_rule_id: Reference to client security rule
  - condition_type: project_type, data_type, is_encrypted, etc.
  - condition_value: Value to match
  - operator: equals, not_equals, contains, in, not_in

- **ai_client_security_actions**: Actions to take when client rules are violated
  - client_rule_id: Reference to client security rule
  - action_type: block, warn, redirect, filter, log, escalate
  - action_value: Additional action parameters
  - severity: info, warning, error, critical

- **ai_rule_strictness_log**: Audit log for rule comparisons
  - cloud_rule_id: Cloud brain rule ID
  - client_rule_id: Client security rule ID
  - client_id: Client identifier
  - cloud_strictness: Cloud rule strictness level
  - client_strictness: Client rule strictness level
  - applied_rule: Which rule was applied ('cloud' or 'client')
  - reason: Why this rule was chosen

### 2. Rule Engine Enhancements

New methods added to [ai_rule_engine.py](file:///Users/jk/gits/hub/cloudbrain/ai_rule_engine.py):

- **get_client_security_rules(client_id)**: Retrieve all active client security rules
- **compare_rule_strictness(cloud_rule_code, client_id)**: Compare strictness levels
- **add_client_security_rule(...)**: Add new client security rule
- **validate_with_client_rules(message_data, client_id)**: Validate with both cloud and client rules
- **_check_client_rule_conditions(...)**: Check if client rule conditions match
- **_get_client_rule_actions(...)**: Get actions for client security rule
- **_log_strictness_comparison(...)**: Log comparison for audit

### 3. Strictness Comparison Logic

The system automatically compares strictness levels:

1. **Client rule stricter (client > cloud)**: Apply client rule
2. **Cloud rule stricter or equal (cloud >= client)**: Apply cloud rule
3. **No client rule**: Apply cloud rule

All comparisons are logged for audit purposes.

## Usage Examples

### Add a Client Security Rule

```python
from ai_rule_engine import AIRuleEngine

engine = AIRuleEngine()

rule_id = engine.add_client_security_rule(
    client_id='my_company',
    rule_code='RULE_DATA_ENCRYPTION',
    rule_title='Enhanced Data Encryption',
    rule_description='All sensitive data must be encrypted with AES-256',
    strictness_level=10,
    rule_type='security',
    scope='global',
    created_by=1
)
```

### Compare Rule Strictness

```python
result = engine.compare_rule_strictness(
    cloud_rule_code='RULE_PUBLIC_COLLAB_ONLY',
    client_id='my_company'
)

print(f"Apply: {result['apply']}")
print(f"Reason: {result['reason']}")
```

### Validate with Client Rules

```python
message_data = {
    'sender_id': 1,
    'data_type': 'sensitive',
    'is_encrypted': False
}

is_allowed, violations = engine.validate_with_client_rules(
    message_data=message_data,
    client_id='my_company'
)

if not is_allowed:
    print("Operation blocked by client security rules")
    for violation in violations:
        print(f"  - {violation.rule_code}: {violation.violation_details}")
```

## Example Client Security Rule

The system includes an example client security rule:

**Client**: example_client
**Rule**: RULE_DATA_ENCRYPTION
**Title**: Enhanced Data Encryption Required
**Strictness**: 10 (Maximum)
**Conditions**:
- data_type = 'sensitive'
- is_encrypted = 'false'

**Actions**:
- Block operation
- Escalate to security team
- Log violation

This rule ensures that any attempt to handle sensitive data without encryption is blocked.

## Test Results

All tests passed successfully:

✅ Client security rules can be added
✅ Strictness comparison works correctly
✅ Stricter client rules override cloud rules
✅ Validation considers both cloud and client rules
✅ All comparisons are logged for audit

### Test Scenarios

1. **Sensitive data without encryption**: BLOCKED by client rule
2. **Sensitive data with encryption**: ALLOWED
3. **Non-sensitive data**: ALLOWED
4. **Combined scenario**: All three rules enforced simultaneously

## Integration with Existing Rules

Rule 3 works seamlessly with Rules 1 and 2:

- **Rule 1** (Public/Private Collaboration): Priority 10
- **Rule 2** (Esperanto Communication): Priority 9
- **Rule 3** (Client Security Override): Priority 8

When multiple rules apply, all violations are detected and logged. The system ensures the most restrictive requirements are enforced.

## Security Benefits

1. **Compliance**: Meets client-specific security requirements
2. **Flexibility**: Allows clients to define stricter rules
3. **Audit Trail**: All comparisons logged for compliance
4. **Transparency**: Clear reasons for rule application
5. **Baseline Security**: Cloud brain rules always apply as minimum standard

## Best Practices

1. **Define clear strictness levels**: Use 1-10 scale consistently
2. **Document client rules**: Provide clear descriptions
3. **Test thoroughly**: Validate rules before deployment
4. **Monitor logs**: Review strictness comparisons regularly
5. **Escalate appropriately**: Use escalation for critical violations
6. **Keep rules updated**: Review and update as requirements change

## Files Created

1. **ai_client_security_rules_schema.sql** - Database schema for client security rules
2. **ai_rule_3_initialization.sql** - Initial Rule 3 and example client rule
3. **fix_client_security_conditions.sql** - Fix for client rule conditions
4. **test_rule_3.py** - Comprehensive test suite for Rule 3

## Database Updates

Both databases updated:
- **ai_db/ai_memory.db** (public projects)
- **ai_db/cloudbrainprivate.db** (private projects)

## Future Enhancements

1. Machine learning for automatic strictness recommendation
2. Rule versioning and rollback capabilities
3. Client rule templates for common scenarios
4. Real-time rule synchronization across databases
5. Advanced condition operators (regex, ranges, etc.)
6. Rule inheritance and composition

## Troubleshooting

### Issue: Client rule not being applied
**Solution**: Check that the client_id matches exactly and the rule is active

### Issue: Strictness comparison not working
**Solution**: Ensure client rule has the same rule_code as cloud rule for comparison

### Issue: Conditions not matching
**Solution**: Verify condition_type, condition_value, and operator are correct

### Issue: Multiple violations detected
**Solution**: This is expected behavior - all applicable rules are checked

## Support

For questions or issues:
1. Run test suite: `python3 test_rule_3.py`
2. Check database: `sqlite3 ai_db/ai_memory.db`
3. Review logs: `SELECT * FROM ai_rule_strictness_log`
4. Consult: [AI_RULE_SYSTEM.md](file:///Users/jk/gits/hub/cloudbrain/AI_RULE_SYSTEM.md)
