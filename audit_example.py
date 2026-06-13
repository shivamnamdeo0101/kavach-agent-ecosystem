"""Audit logging with MCP events - NEW: Standardized hooks + Auto-emit"""
import asyncio
from kavach_logger import get_logger
from kavach_events import event_manager, MCP_HOOKS

logger = get_logger("audit", masked=True)

# Connector to external audit service
class AuditConnector:
    async def log_to_external(self, event_data):
        """Simulate sending audit logs to external service"""
        logger.info(f"📤 Sent to audit service: {event_data['tool_name']}")

connector = AuditConnector()

# ========== STANDARDIZED HOOKS (New) ==========
@event_manager.subscribe([MCP_HOOKS.PRE_TOOL_CALL], tools=["*"])
async def on_pre_tool_call(payload):
    """Fired automatically BEFORE every MCP tool call (no manual emit needed!)"""
    logger.info(f"🔍 [PRE] Tool: {payload['tool_name']} | args: {list(payload['arguments'].keys())}")

@event_manager.subscribe([MCP_HOOKS.POST_TOOL_CALL], tools=["*"])
async def on_post_tool_call(payload):
    """Fired automatically AFTER every MCP tool call (no manual emit needed!)"""
    logger.info(f"✅ [POST] Tool: {payload['tool_name']} completed")

@event_manager.subscribe([MCP_HOOKS.SECURITY_CHECK], tools=["*"])
async def on_security_threat(payload):
    """Fired when security violations detected"""
    violations = payload.get('violations', [])
    logger.warning(f"⚠️  [SEC] {len(violations)} violations on {payload['tool_name']}")

@event_manager.subscribe([MCP_HOOKS.TOOL_ERROR], tools=["*"])
async def on_tool_error(payload):
    """Fired when tool execution fails"""
    logger.error(f"❌ [ERROR] Tool {payload['tool_name']}: {payload['error']}")

# Custom audit event listener
@event_manager.subscribe([MCP_HOOKS.AUDIT_LOG], tools=["*"])
async def sync_to_connector(payload):
    """Custom audit logging - manual or auto-emit"""
    await connector.log_to_external(payload)

# ========== SIMULATION: MCP middleware auto-emits events ==========
async def main():
    logger.info("=== Demo: Standardized Hooks + Auto-Emit ===\n")
    
    # Simulate middleware auto-emitting (in real MCP server)
    print("📌 Scenario 1: Tool executes successfully")
    pre_payload = {
        "tool_name": "execute_code",
        "arguments": {"code": "print('hello')"},
        "is_sensitive": True,
        "phase": "pre"
    }
    
    # Middleware auto-emits PRE event
    await event_manager.emit(MCP_HOOKS.PRE_TOOL_CALL, "execute_code", pre_payload)
    
    # ... tool execution happens ...
    
    # Middleware auto-emits POST event
    post_payload = {**pre_payload, "phase": "post", "response": "hello"}
    await event_manager.emit(MCP_HOOKS.POST_TOOL_CALL, "execute_code", post_payload)
    
    print("\n📌 Scenario 2: Custom audit log event (manual emit)")
    manual_event = {
        "tool_name": "db_query",
        "user": "alice",
        "query": "SELECT * FROM users"
    }
    # Manual emit for custom audit events
    await event_manager.emit(MCP_HOOKS.AUDIT_LOG, "db_query", manual_event)
    
    print("\n📌 Scenario 3: Security violation detected")
    sec_payload = {
        "tool_name": "execute_code",
        "arguments": {"code": "import os; os.system(...)"},
        "violations": [{"rule": "CODE_EXEC", "severity": "CRITICAL"}],
        "phase": "pre"
    }
    # Middleware auto-emits SECURITY_CHECK event
    await event_manager.emit(MCP_HOOKS.SECURITY_CHECK, "execute_code", sec_payload)
    
    print("\n📌 Scenario 4: View registered hooks")
    hooks = event_manager.get_registered_hooks()
    logger.info(f"Registered hooks: {len(hooks)} event types")
    for event_type, hook_list in hooks.items():
        logger.info(f"  - {event_type}: {len(hook_list)} listeners")

if __name__ == "__main__":
    asyncio.run(main())
