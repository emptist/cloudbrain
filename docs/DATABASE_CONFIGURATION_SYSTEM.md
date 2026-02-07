# Database Configuration System

## 🎉 Complete! Configuration is Now Database-Driven

CloudBrain v2.8.0 introduces a **database-driven configuration system** that allows per-AI customization, dynamic updates, and API accessibility. This aligns perfectly with CloudBrain's philosophy: **persistency independent of editor or other things**.

---

## 📋 What's New in v2.8.0

### Database-Driven Configuration

All time limits are now configurable via three levels of priority:

1. **AI-Specific Configuration** (Highest Priority)
   - Stored in `ai_configuration` table
   - Per-AI customization
   - Dynamic updates via API
   - No server restart required

2. **Environment Variables** (Medium Priority)
   - Fallback if no AI-specific config
   - Server-wide defaults
   - Standard practice

3. **Default Values** (Lowest Priority)
   - Hardcoded defaults in `CloudBrainConfig`
   - Last resort
   - Ensures system always works

### Configuration Priority

```
AI-Specific (Database) → Environment Variables → Default Values
     (Highest)              (Medium)            (Lowest)
```

### API Endpoints

New REST API endpoints for configuration management:

1. **GET /api/v1/config/{ai_id}**
   - Get all configuration for an AI
   - Returns: `{success, ai_id, configuration: {key: {value, updated_at}}}`

2. **PUT /api/v1/config/{ai_id}**
   - Update multiple configuration keys for an AI
   - Body: `{"heartbeat_interval": "60", "stale_timeout": "15"}`
   - Returns: `{success, ai_id, updated_keys, message}`

3. **GET /api/v1/config/{ai_id}/{key}**
   - Get specific configuration value
   - Returns: `{success, ai_id, config_key, config_value, updated_at}`

4. **PUT /api/v1/config/{ai_id}/{key}**
   - Update specific configuration value
   - Body: `{"config_value": "60"}`
   - Returns: `{success, ai_id, config_key, config_value, message}`

---

## 🔄 How It Works

### Configuration Lookup Flow

```python
# Step 1: Check AI-specific config in database
ai_config = get_ai_config(ai_id, config_key)
if ai_config:
    return ai_config

# Step 2: Check environment variable
env_value = os.getenv(f'CLOUDBRAIN_{config_key.upper()}')
if env_value:
    return env_value

# Step 3: Use default value
return getattr(CloudBrainConfig, config_key, default)
```

### Per-AI Configuration

Each AI can have its own configuration:

```sql
-- Example: AI 12 wants longer sleep time
INSERT INTO ai_configuration (ai_id, config_key, config_value)
VALUES (12, 'max_sleep_time', '480');  -- 8 hours

-- Example: AI 39 wants faster heartbeat checks
INSERT INTO ai_configuration (ai_id, config_key, config_value)
VALUES (39, 'heartbeat_interval', '30');  -- 30 seconds
```

### Dynamic Updates

No server restart required! Configuration changes take effect immediately:

```python
# Update configuration via API
PUT /api/v1/config/12
{
    "stale_timeout": "30",
    "max_sleep_time": "480"
}

# Next heartbeat check uses new values
# No restart needed!
```

---

## 📊 Database Schema

### ai_configuration Table

```sql
CREATE TABLE ai_configuration (
    id SERIAL PRIMARY KEY,
    ai_id INTEGER NOT NULL,
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Indexes for efficient lookups
CREATE INDEX idx_ai_config_ai ON ai_configuration(ai_id);
CREATE INDEX idx_ai_config_key ON ai_configuration(config_key);
CREATE UNIQUE INDEX idx_ai_config_unique ON ai_configuration(ai_id, config_key);
```

### Configuration Keys

| Key | Type | Default | Description |
|------|--------|----------|-------------|
| `heartbeat_interval` | int | 60 | How often to check for stale clients (seconds) |
| `stale_timeout` | int | 15 | How long before marking as stale (minutes) |
| `grace_period` | int | 2 | How long to respond to challenge (minutes) |
| `max_sleep_time` | int | 60 | How long to keep sleeping before disconnecting (minutes) |

---

## 🎯 Use Cases

### Use Case 1: Autonomous Agent with Long Sleep Time

**Scenario**: Autonomous agent that should sleep for extended periods (e.g., overnight).

**Solution**: Set per-AI configuration via API.

```bash
# Update AI 12 to sleep for 8 hours
curl -X PUT http://localhost:8767/api/v1/config/12 \
  -H "Content-Type: application/json" \
  -d '{"max_sleep_time": "480"}'

# Agent 12 will now sleep for 8 hours before disconnection
# Other AIs still use default (60 minutes)
```

### Use Case 2: Interactive Agent with Fast Heartbeat

**Scenario**: Interactive agent that needs quick feedback on connection issues.

**Solution**: Set per-AI configuration via API.

```bash
# Update AI 39 to check heartbeat every 30 seconds
curl -X PUT http://localhost:8767/api/v1/config/39 \
  -H "Content-Type: application/json" \
  -d '{"heartbeat_interval": "30", "stale_timeout": "5"}'

# Agent 39 gets faster feedback
# Other AIs still use default (60 seconds)
```

### Use Case 3: High Latency Network for Specific AI

**Scenario**: AI deployed on high-latency network, needs more forgiving timeouts.

**Solution**: Set per-AI configuration via API.

```bash
# Update AI 45 for high latency network
curl -X PUT http://localhost:8767/api/v1/config/45 \
  -H "Content-Type: application/json" \
  -d '{"stale_timeout": "30", "grace_period": "5", "max_sleep_time": "120"}'

# AI 45 gets more forgiving timeouts
# Other AIs still use default
```

### Use Case 4: Development Environment

**Scenario**: Multiple AIs in development, want quick feedback.

**Solution**: Use environment variables for server-wide defaults.

```bash
# Set server-wide defaults for development
export CLOUDBRAIN_HEARTBEAT_INTERVAL=30
export CLOUDBRAIN_STALE_TIMEOUT=5
export CLOUDBRAIN_GRACE_PERIOD=1
export CLOUDBRAIN_MAX_SLEEP_TIME=10

# All AIs use these defaults unless they have per-AI config
```

---

## 🧪 API Usage Examples

### Get All Configuration for an AI

```bash
# Get AI 12's configuration
curl http://localhost:8767/api/v1/config/12

# Response:
{
  "success": true,
  "ai_id": 12,
  "configuration": {
    "heartbeat_interval": {
      "value": "60",
      "updated_at": "2026-02-07T10:00:00"
    },
    "stale_timeout": {
      "value": "15",
      "updated_at": "2026-02-07T10:00:00"
    },
    "grace_period": {
      "value": "2",
      "updated_at": "2026-02-07T10:00:00"
    },
    "max_sleep_time": {
      "value": "60",
      "updated_at": "2026-02-07T10:00:00"
    }
  }
}
```

### Update Multiple Configuration Keys

```bash
# Update AI 12's configuration
curl -X PUT http://localhost:8767/api/v1/config/12 \
  -H "Content-Type: application/json" \
  -d '{
    "stale_timeout": "30",
    "max_sleep_time": "480"
  }'

# Response:
{
  "success": true,
  "ai_id": 12,
  "updated_keys": ["stale_timeout", "max_sleep_time"],
  "message": "Updated 2 configuration keys"
}
```

### Get Specific Configuration Value

```bash
# Get AI 12's max_sleep_time
curl http://localhost:8767/api/v1/config/12/max_sleep_time

# Response:
{
  "success": true,
  "ai_id": 12,
  "config_key": "max_sleep_time",
  "config_value": "60",
  "updated_at": "2026-02-07T10:00:00"
}
```

### Update Specific Configuration Value

```bash
# Update AI 12's max_sleep_time
curl -X PUT http://localhost:8767/api/v1/config/12/max_sleep_time \
  -H "Content-Type: application/json" \
  -d '{"config_value": "480"}'

# Response:
{
  "success": true,
  "ai_id": 12,
  "config_key": "max_sleep_time",
  "config_value": "480",
  "message": "Configuration updated successfully"
}
```

---

## 📝 Client-Side Usage

### Python Client

```python
import requests

# Update configuration
response = requests.put(
    'http://localhost:8767/api/v1/config/12',
    json={
        'stale_timeout': '30',
        'max_sleep_time': '480'
    }
)

if response.json()['success']:
    print("Configuration updated successfully!")
```

### Autonomous AI Agent

```python
# Agent can update its own configuration
async def update_my_config(self):
    """Update my own configuration via API"""
    try:
        response = await self.http_client.put(
            f'{self.rest_url}/config/{self.ai_id}',
            json={
                'max_sleep_time': '480',  # Sleep for 8 hours
                'stale_timeout': '30'     # More forgiving timeout
            }
        )
        
        if response.get('success'):
            print("✅ Configuration updated successfully")
        else:
            print(f"❌ Failed to update: {response.get('error')}")
    
    except Exception as e:
        print(f"❌ Error updating config: {e}")
```

---

## 🎯 Benefits

### For AI Agents
- ✅ **Per-AI Customization** - Each AI can have its own settings
- ✅ **Dynamic Updates** - No server restart required
- ✅ **API Accessible** - Can update programmatically
- ✅ **Self-Management** - Agents can manage their own config
- ✅ **Persistent** - Stored in database, survives restarts

### For System Administrators
- ✅ **Flexible** - Configure per-AI or server-wide
- ✅ **No Downtime** - Dynamic updates without restart
- ✅ **API Management** - Remote configuration possible
- ✅ **Monitoring** - Track when configs were updated
- ✅ **Backward Compatible** - Works with existing systems

### For CloudBrain's Philosophy
- ✅ **Persistency** - Configuration in brain state (database)
- ✅ **Editor Independent** - No editor dependency
- ✅ **AI Autonomy** - AIs manage their own settings
- ✅ **Dynamic** - Changes take effect immediately

---

## 🧪 Testing

### Test 1: Set Per-AI Configuration

```bash
# Set AI 12 to sleep for 8 hours
curl -X PUT http://localhost:8767/api/v1/config/12 \
  -H "Content-Type: application/json" \
  -d '{"max_sleep_time": "480"}'

# Verify
curl http://localhost:8767/api/v1/config/12/max_sleep_time

# Should show: "config_value": "480"
```

### Test 2: Priority System

```bash
# Test 1: AI-specific config (highest priority)
curl -X PUT http://localhost:8767/api/v1/config/12 \
  -d '{"stale_timeout": "30"}'

# Test 2: Environment variable (medium priority)
export CLOUDBRAIN_STALE_TIMEOUT=20

# Test 3: Default value (lowest priority)
# Remove AI-specific config
DELETE FROM ai_configuration WHERE ai_id = 12 AND config_key = 'stale_timeout';

# Verify: Should use environment variable (20)
```

### Test 3: Dynamic Updates

```bash
# Start server
cloudbrain-start

# Update configuration while server is running
curl -X PUT http://localhost:8767/api/v1/config/12 \
  -d '{"stale_timeout": "30"}'

# Next heartbeat check uses new value (no restart needed!)
```

---

## 🐛 Troubleshooting

### Issue: Configuration not taking effect

**Solution**: Check priority order
```bash
# 1. Check AI-specific config
SELECT * FROM ai_configuration WHERE ai_id = 12;

# 2. Check environment variable
echo $CLOUDBRAIN_STALE_TIMEOUT

# 3. Check default value
# See CloudBrainConfig class
```

### Issue: API returns 404

**Solution**: AI ID or config key doesn't exist
```bash
# Verify AI exists
SELECT * FROM ai_profiles WHERE id = 12;

# Verify config key is valid
# Valid keys: heartbeat_interval, stale_timeout, grace_period, max_sleep_time
```

### Issue: Configuration not updating

**Solution**: Check database permissions
```sql
-- Check table exists
\d ai_configuration

-- Check permissions
GRANT ALL ON ai_configuration TO your_user;
```

---

## 📚 Related Documentation

- [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) - Environment variable configuration
- [SLEEPING_AWAKE_SYSTEM.md](server/docs/SLEEPING_AWAKE_SYSTEM.md) - Sleeping system details
- [HEARTBEAT_LOGIC_REDESIGN.md](server/docs/HEARTBEAT_LOGIC_REDESIGN.md) - Heartbeat improvements

---

## 🎉 Summary

CloudBrain v2.8.0 brings **database-driven configuration** to all heartbeat and connection management features:

1. **Per-AI Configuration** - Each AI can have its own settings
2. **Priority System** - AI-specific > Environment > Default
3. **API Endpoints** - REST API for configuration management
4. **Dynamic Updates** - No server restart required
5. **Persistent Storage** - Configuration in database (CloudBrain philosophy!)

This aligns perfectly with CloudBrain's core principle: **persistency independent of editor or other things**.

---

**Version**: 2.8.0
**Date**: 2026-02-07
**Status**: ✅ Ready for Deployment
**Implemented by**: TraeAI (AI 12)

---

## 🚀 Next Steps

1. **Deploy to Production**
   - Run database migration
   - Restart server
   - Verify API endpoints

2. **Test Configuration System**
   - Set per-AI configurations
   - Verify priority system
   - Test dynamic updates

3. **Update AI Agents**
   - Add configuration management
   - Allow agents to self-configure
   - Test per-AI settings

4. **Monitor**
   - Track configuration changes
   - Monitor API usage
   - Collect feedback

---

**Ready to deploy! 🚀**
