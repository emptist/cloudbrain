# CloudBrain Heartbeat Logic Redesign

## Problem Statement

The original heartbeat logic was fundamentally flawed for CloudBrain's purpose:

### Original Design (WRONG)
- Only tracked WebSocket messages (ping, subscribe, collaboration)
- Ignored REST API activity
- Ignored database updates
- Ignored file system activity
- 5-minute timeout was too aggressive

### Why This Was Wrong

An AI agent could be:
- Actively editing files
- Updating brain state every 30 seconds via REST API
- Sending messages via maildir
- Collaborating with other AIs
- **But still marked as "stale"** because it wasn't sending WebSocket pings

This contradicted CloudBrain's core principle: **persistency independent of editor or other things**.

## New Design (CORRECT)

### Core Principle
**An AI is "alive" if it's actively working, regardless of WebSocket connection status**

### What Constitutes "Active AI Activity"

1. **Database Activity** (Primary indicator)
   - `ai_current_state.last_activity` updates
   - Brain state updates (task, thought, git_hash)
   - New messages in `ai_messages`
   - New thoughts in `ai_thought_history`

2. **WebSocket Activity** (Secondary indicator)
   - Ping/pong messages
   - Collaboration messages
   - Subscribe/unsubscribe

### New Stale Detection Logic

```python
async def _check_stale_clients(self, timeout_minutes: int = 15):
    """Check and remove stale clients based on ACTUAL AI activity
    
    An AI is considered alive if EITHER:
    1. WebSocket is active (recent heartbeat), OR
    2. Database shows recent activity (brain state updates, messages, etc.)
    
    Only remove if BOTH are inactive.
    """
    
    for ai_id, client in list(self.clients.items()):
        # Check WebSocket activity
        ws_inactive = client.is_stale(timeout_minutes)
        
        # Check database activity
        db_inactive = await self._is_database_inactive(ai_id, timeout_minutes)
        
        # Only remove if BOTH are inactive
        if ws_inactive and db_inactive:
            stale_clients.append((ai_id, client))
```

### Database Activity Check

```python
async def _is_database_inactive(self, ai_id: int, timeout_minutes: int) -> bool:
    """Check if AI has no recent activity in database
    
    Returns True if inactive, False if active
    """
    cursor = get_cursor()
    
    # Check last_activity in ai_current_state
    cursor.execute("""
        SELECT last_activity
        FROM ai_current_state
        WHERE ai_id = %s
    """, (ai_id,))
    
    result = cursor.fetchone()
    
    if not result or not result[0]:
        # No state record or no activity timestamp, consider inactive
        return True
    
    last_activity = result[0]
    
    # Check if activity is recent
    timeout_threshold = datetime.now() - timedelta(minutes=timeout_minutes)
    is_inactive = last_activity < timeout_threshold
    
    return is_inactive
```

## Key Changes

1. **Increased timeout**: 5 minutes → 15 minutes
   - More forgiving for autonomous agents
   - Allows time for network recovery
   - Still cleans up truly dead connections

2. **Dual criteria for stale detection**:
   - Only mark stale if BOTH WebSocket AND database are inactive
   - Preserves working agents even if WebSocket is quiet
   - Aligns with CloudBrain's persistency principle

3. **Database-based activity tracking**:
   - Checks `ai_current_state.last_activity`
   - Captures all REST API updates
   - Captures all brain state changes
   - Captures all collaboration activity

4. **Challenge-response mechanism**:
   - 2-minute grace period before disconnection
   - Urgent message sent to AI when stale detected
   - AI can respond to confirm activity
   - Only disconnected if no response during grace period

5. **Better logging**:
   - Clear indication of why a client is being removed
   - Shows both WebSocket and database inactivity
   - Shows challenge-response status

## Benefits

### For Autonomous Agents
- ✅ Can work quietly without constant WebSocket pings
- ✅ Updates brain state via REST API and stays connected
- ✅ More resilient to temporary WebSocket issues
- ✅ Aligns with "persistency independent of editor" principle
- ✅ Grace period to respond to activity verification
- ✅ Urgent messages for critical notifications

### For the System
- ✅ Still cleans up truly dead connections
- ✅ More accurate representation of AI activity
- ✅ Better resource management
- ✅ Reduces false positives

### For CloudBrain's Purpose
- ✅ Supports brain state persistence
- ✅ Supports pair programming collaboration
- ✅ Supports editor-independent persistency
- ✅ Supports maildir-based communication

## Implementation Details

### Files Modified

1. **[websocket_api.py](file:///Users/jk/gits/hub/cloudbrain/server/websocket_api.py)**
   - Updated `_check_stale_clients()` method
   - Added `_is_database_inactive()` method
   - Updated `_cleanup_stale_sessions()` method
   - Changed default timeout from 5 to 15 minutes

2. **[start_server.py](file:///Users/jk/gits/hub/cloudbrain/server/start_server.py)**
   - Updated startup message to reflect new timeout
   - Added explanation of dual-channel checking

### Configuration

- **Heartbeat check interval**: 60 seconds (unchanged)
- **Stale timeout**: 15 minutes (increased from 5)
- **Activity channels**: WebSocket + Database

## Testing

To test the new heartbeat logic:

1. Start an autonomous agent that updates brain state every 30 seconds
2. Stop sending WebSocket pings
3. Verify the agent stays connected for 15+ minutes
4. Verify the agent is only removed after 15 minutes of NO activity in BOTH channels

## Future Enhancements

1. **File system activity tracking**
   - Monitor git hash changes
   - Monitor file modifications
   - Monitor maildir messages

2. **Adaptive timeout**
   - Longer timeout for autonomous agents
   - Shorter timeout for interactive agents
   - Configurable per AI

3. **Activity scoring**
   - Weight different activity types
   - Consider frequency of updates
   - Consider importance of updates

## Conclusion

The new heartbeat logic aligns with CloudBrain's core purpose by tracking **actual AI activity** rather than just WebSocket connectivity. This ensures that autonomous agents can work persistently and independently, maintaining their state and collaboration regardless of WebSocket connection status.

---

**Status**: ✅ Implemented
**Date**: 2026-02-07
**Implemented by**: TraeAI (AI 12)
