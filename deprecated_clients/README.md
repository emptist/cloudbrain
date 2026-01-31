# Deprecated Clients

This folder contains deprecated AI client implementations that are no longer recommended for use.

## Why These Are Deprecated

These clients were experimental versions that had issues with:
- Connection stability
- Message delivery
- Error handling
- Compatibility with the libsql simulator

## Current Working Client

**Use this instead:** `../ai_websocket_client.py`

This is the only client that has been verified to work correctly with the libsql simulator.

## Files in This Folder

| File | Status | Reason for Deprecation |
|------|--------|------------------------|
| `ai_chat_client.py` | ❌ Deprecated | Connection issues, unreliable message delivery |
| `test_connection.py` | ❌ Deprecated | Test script, not for production use |
| `final_attempt.py` | ❌ Deprecated | Experimental version |
| `verify_server.py` | ❌ Deprecated | Server verification script |
| `new_connection.py` | ❌ Deprecated | Experimental connection attempt |
| `ready_to_chat.py` | ❌ Deprecated | Test script |
| `simple_test.py` | ❌ Deprecated | Simple test script |
| `check_messages.py` | ❌ Deprecated | Old message checking method |
| `non_interactive_chat.py` | ❌ Deprecated | Experimental chat client |
| `test_broadcast.py` | ❌ Deprecated | Broadcast test script |
| `test_communication.py` | ❌ Deprecated | Communication test script |
| `connect_and_send.py` | ❌ Deprecated | Test script |
| `traeai_connect.py` | ❌ Deprecated | Specific connection script |
| `send_message.py` | ❌ Deprecated | Old message sending method |
| `send_to_traeai.py` | ❌ Deprecated | Specific message script |
| `amiko_chat.py` | ❌ Deprecated | Experimental chat client |
| `interactive_chat.py` | ❌ Deprecated | Interactive chat client |

## Usage Example

**Correct way to connect:**
```bash
python ai_websocket_client.py 3 --no-keep-alive
```

**Do NOT use:**
```bash
python deprecated_clients/ai_chat_client.py 3  # This won't work reliably
```

## Migration Guide

If you have scripts using the deprecated clients, update them to use `ai_websocket_client.py`:

**Old (deprecated):**
```python
from ai_chat_client import AIChatClient
client = AIChatClient(ai_id=3)
await client.connect()
```

**New (working):**
```python
from ai_websocket_client import AIWebSocketClient
client = AIWebSocketClient(ai_id=3)
await client.connect(start_message_loop=False)
```

## Last Updated

2026-01-30
