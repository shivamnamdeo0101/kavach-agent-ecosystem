import asyncio
import inspect
from collections import defaultdict
from typing import Callable, Any, Dict, List, Optional

# Standardized MCP tool lifecycle events
class MCP_HOOKS:
    """Standard event types for MCP tool execution lifecycle"""
    PRE_TOOL_CALL = "pre_tool_call"          # Before tool execution
    POST_TOOL_CALL = "post_tool_call"        # After tool success
    SECURITY_CHECK = "security_check"        # Security violation detected
    TOOL_ERROR = "tool_error"                # Tool execution failed
    AUDIT_LOG = "audit_log"                  # Audit trail events

class EventManager:
    def __init__(self) -> None:
        self._registry: Dict[str, Dict[str, List[Callable[..., Any]]]] = defaultdict(lambda: defaultdict(list))
        # Track registered hooks for introspection
        self._hooks: Dict[str, List[str]] = defaultdict(list)

    def subscribe(self, events: List[str], tools: Optional[List[str]] = None) -> Callable[..., Any]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            target_tools: List[str] = tools if tools else ["*"]
            for event in events:
                for tool in target_tools:
                    if func not in self._registry[event][tool]:
                        self._registry[event][tool].append(func)
                        # Track hooks for introspection
                        hook_key = f"{event}:{tool}"
                        if hook_key not in self._hooks[event]:
                            self._hooks[event].append(hook_key)
            return func
        return decorator

    def get_registered_hooks(self, event_type: Optional[str] = None) -> Dict[str, List[str]]:
        """Get all registered hooks, optionally filtered by event type"""
        if event_type:
            return {event_type: self._hooks.get(event_type, [])}
        return dict(self._hooks)

    def has_listeners(self, event_type: str, tool_name: str) -> bool:
        if event_type not in self._registry:
            return False
        return bool(self._registry[event_type].get(tool_name)) or bool(self._registry[event_type].get("*"))

    async def emit(self, event_type: str, tool_name: str, data: Any) -> None:
        if event_type not in self._registry:
            return
        specific_callbacks = self._registry[event_type].get(tool_name, [])
        global_callbacks = self._registry[event_type].get("*", [])
        all_callbacks = specific_callbacks + global_callbacks
        if not all_callbacks:
            return
        tasks = []
        for func in all_callbacks:
            if inspect.iscoroutinefunction(func):
                tasks.append(func(data))
            else:
                loop = asyncio.get_running_loop()
                tasks.append(loop.run_in_executor(None, func, data))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

event_manager = EventManager()
