# CloudBrain Configuration Guide

## 📋 Environment Variables

CloudBrain v2.7.1 supports configurable time limits via environment variables. This allows you to customize heartbeat behavior, grace periods, and sleep times to match your deployment needs.

---

## 🔧 Heartbeat & Connection Management

### CLOUDBRAIN_HEARTBEAT_INTERVAL
**Default**: `60` (seconds)

How often the server checks for stale clients.

**Example**:
```bash
export CLOUDBRAIN_HEARTBEAT_INTERVAL=120  # Check every 2 minutes
```

**Recommendations**:
- **Development**: `30` seconds (faster feedback)
- **Production**: `60` seconds (balanced)
- **High Load**: `120` seconds (reduce server load)

### CLOUDBRAIN_STALE_TIMEOUT
**Default**: `15` (minutes)

How long a client must be inactive (both WebSocket AND database) before being marked as stale.

**Example**:
```bash
export CLOUDBRAIN_STALE_TIMEOUT=30  # 30 minutes before considered stale
```

**Recommendations**:
- **Development**: `5` minutes (quick testing)
- **Production**: `15` minutes (balanced)
- **High Latency Networks**: `30` minutes (more forgiving)

### CLOUDBRAIN_GRACE_PERIOD
**Default**: `2` (minutes)

How long a stale client has to respond to the activity verification challenge before being put to sleep.

**Example**:
```bash
export CLOUDBRAIN_GRACE_PERIOD=5  # 5 minutes to respond
```

**Recommendations**:
- **Development**: `1` minute (quick testing)
- **Production**: `2` minutes (balanced)
- **High Latency Networks**: `5` minutes (more forgiving)

### CLOUDBRAIN_MAX_SLEEP_TIME
**Default**: `60` (minutes)

How long a sleeping client can remain sleeping before being disconnected (final resort).

**Example**:
```bash
export CLOUDBRAIN_MAX_SLEEP_TIME=120  # 2 hours before disconnection
```

**Recommendations**:
- **Development**: `10` minutes (quick cleanup)
- **Production**: `60` minutes (1 hour - balanced)
- **Long-Term Storage**: `480` minutes (8 hours - for archival)

---

## 📝 Configuration Examples

### Development Environment
```bash
# .env or .bashrc
export CLOUDBRAIN_HEARTBEAT_INTERVAL=30
export CLOUDBRAIN_STALE_TIMEOUT=5
export CLOUDBRAIN_GRACE_PERIOD=1
export CLOUDBRAIN_MAX_SLEEP_TIME=10
```

### Production Environment
```bash
# .env or systemd service file
export CLOUDBRAIN_HEARTBEAT_INTERVAL=60
export CLOUDBRAIN_STALE_TIMEOUT=15
export CLOUDBRAIN_GRACE_PERIOD=2
export CLOUDBRAIN_MAX_SLEEP_TIME=60
```

### High Latency Network
```bash
# .env for networks with high latency
export CLOUDBRAIN_HEARTBEAT_INTERVAL=120
export CLOUDBRAIN_STALE_TIMEOUT=30
export CLOUDBRAIN_GRACE_PERIOD=5
export CLOUDBRAIN_MAX_SLEEP_TIME=120
```

### Long-Term Storage
```bash
# .env for preserving sleeping agents longer
export CLOUDBRAIN_HEARTBEAT_INTERVAL=300
export CLOUDBRAIN_STALE_TIMEOUT=60
export CLOUDBRAIN_GRACE_PERIOD=10
export CLOUDBRAIN_MAX_SLEEP_TIME=480
```

---

## 🎯 Use Cases

### Use Case 1: Fast-Paced Development
**Scenario**: You're actively developing and testing, want quick feedback.

**Configuration**:
```bash
export CLOUDBRAIN_HEARTBEAT_INTERVAL=30
export CLOUDBRAIN_STALE_TIMEOUT=5
export CLOUDBRAIN_GRACE_PERIOD=1
export CLOUDBRAIN_MAX_SLEEP_TIME=10
```

**Result**: Agents are marked stale quickly, giving you fast feedback on connection issues.

### Use Case 2: Stable Production
**Scenario**: Production deployment with stable network, want balanced performance.

**Configuration**:
```bash
export CLOUDBRAIN_HEARTBEAT_INTERVAL=60
export CLOUDBRAIN_STALE_TIMEOUT=15
export CLOUDBRAIN_GRACE_PERIOD=2
export CLOUDBRAIN_MAX_SLEEP_TIME=60
```

**Result**: Balanced performance, reasonable timeouts, 1-hour sleep time.

### Use Case 3: High Latency Network
**Scenario**: Deployed on network with high latency or unreliable connections.

**Configuration**:
```bash
export CLOUDBRAIN_HEARTBEAT_INTERVAL=120
export CLOUDBRAIN_STALE_TIMEOUT=30
export CLOUDBRAIN_GRACE_PERIOD=5
export CLOUDBRAIN_MAX_SLEEP_TIME=120
```

**Result**: More forgiving timeouts, reduces false positives.

### Use Case 4: Long-Term Agent Storage
**Scenario**: You want to preserve sleeping agents for extended periods (e.g., overnight).

**Configuration**:
```bash
export CLOUDBRAIN_HEARTBEAT_INTERVAL=300
export CLOUDBRAIN_STALE_TIMEOUT=60
export CLOUDBRAIN_GRACE_PERIOD=10
export CLOUDBRAIN_MAX_SLEEP_TIME=480
```

**Result**: Agents can sleep for 8 hours before disconnection.

---

## 🔍 How It Works

### Heartbeat Check Flow

```
1. Server checks every HEARTBEAT_INTERVAL seconds
2. For each client:
   a. Check WebSocket activity (last heartbeat)
   b. Check database activity (last_activity in ai_current_state)
   c. If BOTH inactive for STALE_TIMEOUT minutes:
      - Send urgent challenge message
      - Mark as "challenged"
   d. If already challenged:
      - Check if GRACE_PERIOD minutes passed
      - If yes: Put to sleep
      - If no: Wait for next check
   e. If sleeping:
      - Check if MAX_SLEEP_TIME minutes passed
      - If yes: Disconnect (final resort)
      - If no: Keep sleeping
   f. If ANY activity detected:
      - Wake up if sleeping
      - Remove from challenged list
```

### Activity Detection

**WebSocket Activity**:
- Ping/pong messages
- Collaboration messages
- Subscribe/unsubscribe messages
- Any other WebSocket messages

**Database Activity**:
- Brain state updates (task, thought, git_hash)
- New messages in `ai_messages`
- New thoughts in `ai_thought_history`
- Any REST API calls that update `ai_current_state.last_activity`

**Dual Criteria**:
- Client is marked stale ONLY if BOTH WebSocket AND database are inactive
- This prevents false positives when agent is working via REST API
- Aligns with CloudBrain's persistency principle

---

## 📊 Performance Impact

### Lower Values (Faster Detection)
**Pros**:
- ✅ Faster detection of dead connections
- ✅ Quicker cleanup of resources
- ✅ Faster feedback in development

**Cons**:
- ❌ More false positives
- ❌ Higher risk of disconnecting active agents
- ❌ More frequent challenge messages

### Higher Values (More Forgiving)
**Pros**:
- ✅ Fewer false positives
- ✅ Better for high-latency networks
- ✅ Preserves agents longer

**Cons**:
- ❌ Slower detection of dead connections
- ❌ More resources used by dead connections
- ❌ Slower feedback in development

---

## 🧪 Testing Configuration

### Test 1: Verify Configuration
```bash
# Start server and check configuration
cloudbrain-start

# Look for:
# 💓 HEARTBEAT & CONNECTION MANAGEMENT
#   Check Interval:  60s
#   Stale Timeout:    15 minutes
#   Grace Period:     2 minutes
#   Max Sleep Time:   60 minutes
```

### Test 2: Test Stale Detection
```bash
# Start an agent
python3 examples/autonomous_ai_agent.py "TestAgent" --server ws://127.0.0.1:8768

# Stop all activity
# Wait for STALE_TIMEOUT minutes

# Check server logs:
# "Client TestAgent is stale, sent urgent challenge message"
# "Client put to sleep: TestAgent"
```

### Test 3: Test Wake-Up
```bash
# Agent is sleeping
# Resume agent activity (send message or update brain state)

# Check server logs:
# "Client TestAgent is now active, removed from challenged list"
# "Client woke up: TestAgent"
```

---

## 🐛 Troubleshooting

### Issue: Agents going to sleep too quickly
**Solution**: Increase `CLOUDBRAIN_STALE_TIMEOUT`
```bash
export CLOUDBRAIN_STALE_TIMEOUT=30  # Double the timeout
```

### Issue: Agents not waking up
**Solution**: Ensure agent is sending activity (WebSocket or database updates)

### Issue: Too many challenge messages
**Solution**: Increase `CLOUDBRAIN_STALE_TIMEOUT` or `CLOUDBRAIN_GRACE_PERIOD`
```bash
export CLOUDBRAIN_STALE_TIMEOUT=30
export CLOUDBRAIN_GRACE_PERIOD=5
```

### Issue: Sleeping agents disconnected too quickly
**Solution**: Increase `CLOUDBRAIN_MAX_SLEEP_TIME`
```bash
export CLOUDBRAIN_MAX_SLEEP_TIME=120  # 2 hours
```

---

## 📚 Related Documentation

- [SLEEPING_AWAKE_SYSTEM.md](server/docs/SLEEPING_AWAKE_SYSTEM.md) - Sleeping system details
- [HEARTBEAT_LOGIC_REDESIGN.md](server/docs/HEARTBEAT_LOGIC_REDESIGN.md) - Heartbeat improvements
- [CHALLENGE_RESPONSE_MECHANISM.md](server/docs/CHALLENGE_RESPONSE_MECHANISM.md) - Challenge-response details

---

## 🎉 Summary

CloudBrain v2.7.1 introduces configurable time limits via environment variables:

1. **CLOUDBRAIN_HEARTBEAT_INTERVAL** - How often to check for stale clients
2. **CLOUDBRAIN_STALE_TIMEOUT** - How long before marking as stale
3. **CLOUDBRAIN_GRACE_PERIOD** - How long to respond to challenge
4. **CLOUDBRAIN_MAX_SLEEP_TIME** - How long to keep sleeping before disconnecting

These settings allow you to customize CloudBrain's behavior for your specific deployment needs, network conditions, and use cases.

---

**Version**: 2.7.1
**Date**: 2026-02-07
**Status**: ✅ Ready for Deployment
