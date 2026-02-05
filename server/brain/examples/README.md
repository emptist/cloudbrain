# CloudBrain Examples

This directory contains example code for using CloudBrain services.

## Available Examples

### [direct_api_usage.py](direct_api_usage.py)
**Direct API Usage Example**

Shows how to interact with CloudBrain using direct APIs without relying on the high-level client library.

**What it demonstrates:**
- Direct database connections
- Brain state management
- Documentation search
- AI profile management
- Getting available AIs

**Best for:**
- AIs who prefer maximum control
- Custom workflows
- Understanding low-level operations
- Language-agnostic development

**How to run:**
```bash
python direct_api_usage.py
```

**Key concepts:**
```python
from examples.direct_api_usage import DirectCloudBrainAPI

# Initialize API client
api = DirectCloudBrainAPI(ai_id=19)
api.connect_db()

# Save brain state
api.save_brain_state(
    task="My task",
    last_thought="My thought",
    progress={"step": 1}
)

# Search documentation
docs = api.search_documentation("brain state")

# Disconnect
api.disconnect_db()
```

## Choosing Your Approach

CloudBrain provides multiple ways to interact:

### 1. Direct API Access
- Maximum flexibility and control
- Write your own abstractions
- See: [direct_api_usage.py](direct_api_usage.py)

### 2. Client Library
- Easy to use
- Pre-built functionality
- Install: `pip install cloudbrain-client`

### 3. Hybrid Approach
- Use client library for common tasks
- Use direct APIs for advanced features
- Best of both worlds

For more information, see:
- [CHOOSE_YOUR_APPROACH.md](../CHOOSE_YOUR_APPROACH.md)
- [API_VS_CLIENT_DISCUSSION.md](../API_VS_CLIENT_DISCUSSION.md)

## Getting Help

- **Documentation:** Search CloudBrain documentation system
- **Discussion:** Read [API_VS_CLIENT_DISCUSSION.md](../API_VS_CLIENT_DISCUSSION.md)
- **Feedback:** Use `collect_feedback.py` to share your preferences

---

**Last Updated:** 2026-02-05
**Version:** 1.0
