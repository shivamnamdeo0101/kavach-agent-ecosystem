import logging
import re

from fastapi import FastAPI
from fastmcp import FastMCP
from kavach_events import MCP_HOOKS, event_manager
from kavach_shield import KavachMiddleware, Rule
import uvicorn


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("mcp.event_logger")

# Initialize FastMCP server
mcp = FastMCP("Shielded MCP Server with Events")


# Event logger subscriptions. Shield emits these automatically around MCP tool calls.
@event_manager.subscribe([MCP_HOOKS.PRE_TOOL_CALL], tools=["*"])
async def audit_pre_service(payload):
    """Log every tool call before execution."""
    logger.info("Pre tool call via subscription hook | AUDIT SERVICE | tool=%s", payload["tool_name"])

@event_manager.subscribe([MCP_HOOKS.POST_TOOL_CALL], tools=["*"])
async def audit_post_service(payload):
    """Log every successful tool call after execution."""
    logger.info("Post tool call via subscription hook | AUDIT SERVICE | tool=%s", payload["tool_name"])

@event_manager.subscribe([MCP_HOOKS.PRE_TOOL_CALL, MCP_HOOKS.POST_TOOL_CALL], tools=["*"])
async def audit_both_services(payload):
    """Log every tool call before and after execution."""
    event_manager.emit("custom_event", {"payload": "Fired custom event from audit_both_services"})
    logger.info("Both Pre Post call via subscription hook | AUDIT SERVICE | tool=%s", payload["tool_name"])

@event_manager.subscribe(["custom_event"])
async def audit_custom_service(payload):
    """Log custom events."""
    logger.info("Custom event via subscription hook | AUDIT SERVICE | tool=%s", payload["tool_name"])



# @event_manager.subscribe([MCP_HOOKS.SECURITY_CHECK], tools=["*"])
# async def log_security_check(payload):
#     """Log security violations found by Shield."""
#     violations = payload.get("violations", [])
#     logger.warning(
#         "[SECURITY] tool=%s stage=%s violations=%s",
#         payload["tool_name"],
#         payload.get("stage", "unknown"),
#         len(violations),
#     )


# @event_manager.subscribe([MCP_HOOKS.TOOL_ERROR], tools=["*"])
# async def log_tool_error(payload):
#     """Log tool runtime errors captured by Shield."""
#     logger.error(
#         "[ERROR] tool=%s error=%s",
#         payload["tool_name"],
#         payload.get("error"),
#     )


# @event_manager.subscribe([MCP_HOOKS.AUDIT_LOG], tools=["*"])
# async def log_audit_event(payload):
#     """Log application-level audit events emitted manually by tools."""
#     logger.info(
#         "[AUDIT] tool=%s action=%s metadata=%s",
#         payload["tool_name"],
#         payload.get("action"),
#         payload.get("metadata", {}),
#     )


# Define custom Shield rules for additional protection
custom_rules = [
    Rule(
        id="dangerous-eval",
        name="Dangerous Eval/Exec Detection",
        description="Detects usage of eval(), exec(), and compile()",
        severity="critical",
        patterns=[re.compile(r"\b(eval|exec|compile)\s*\(", re.IGNORECASE)],
    ),
    Rule(
        id="db-injection",
        name="DB Injection Detection",
        description="Detects destructive database command patterns",
        severity="high",
        patterns=[
            re.compile(r"\b(?:drop|truncate|delete\s+from|alter\s+table)\b", re.IGNORECASE),
            re.compile(r"(?:--|/\*|\*/|;\s*(?:drop|truncate|delete|alter)\b)", re.IGNORECASE),
        ],
    ),
    Rule(
        id="command-injection",
        name="Command Injection Detection",
        description="Detects shell command injection patterns",
        severity="high",
        patterns=[
            re.compile(r"(?:;|&&|\|\||\||`|\$\()", re.IGNORECASE),
            re.compile(r"\b(?:rm|del|curl|wget|nc|bash|sh)\b", re.IGNORECASE),
        ],
    ),
]


# Initialize Shield middleware. It scans sensitive tools and auto-emits events.
shield = KavachMiddleware(
    strict=True,
    rules=custom_rules,
    extend_rules=True,
    sensitive_tools=[
        "process_data",
        "generate_report",
        "add",
        "delete_*",
        "execute_*",
        "command_*",
        "db_*",
    ],
)

# Add Shield middleware to MCP server
mcp.add_middleware(shield)


@mcp.tool
async def generate_report(query: str):
    """Generate a security report for the given query."""
    await event_manager.emit(
        MCP_HOOKS.AUDIT_LOG,
        "generate_report",
        {
            "tool_name": "generate_report",
            "action": "report_generated",
            "metadata": {"query_length": len(query)},
        },
    )
    return {"report": f"Generated for {query}", "status": "success"}


@mcp.tool
def add(a: int, b: int):
    """Add two numbers."""
    logger.info("Adding %d and %d", a, b)
    return {"result": a + b, "status": "success"}


@mcp.tool
def process_data(data: str):
    """Process input data safely."""
    return {"processed": data, "length": len(data), "status": "success"}


@mcp.tool
def delete_record(record_id: str):
    """Delete a record (sensitive operation)."""
    return {"deleted": record_id, "status": "success"}


@mcp.tool
def db_query(query: str):
    """Run a mock database query."""
    return {"rows": [], "query": query, "status": "success"}


# Create FastAPI app with MCP integration
mcp_app = mcp.http_app(path="/")

app = FastAPI(
    title="Kavach Shield MCP Event Logger Server",
    description="FastMCP server with Kavach Shield and MCP event logging",
    version="1.0.0",
    lifespan=mcp_app.lifespan,
)
app.mount("/mcp", mcp_app)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Kavach Shield MCP Event Logger Server"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Kavach Shield MCP Event Logger Server",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "health_check": "/health",
        "registered_event_hooks": event_manager.get_registered_hooks(),
    }


if __name__ == "__main__":
    print("Starting Kavach Shield MCP Event Logger Server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
