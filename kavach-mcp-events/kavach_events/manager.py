import asyncio
import contextvars
import inspect
from collections import defaultdict
from typing import Awaitable, Callable, Any, Dict, List, Optional, Set

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
        self._registry: Dict[str, Dict[str, Dict[str, Callable[..., Any]]]] = defaultdict(lambda: defaultdict(dict))
        # Track registered hooks for introspection
        self._hooks: Dict[str, Set[str]] = defaultdict(set)
        self._current_tool_name: contextvars.ContextVar[str] = contextvars.ContextVar(
            "kavach_current_tool_name",
            default="*",
        )

    def _callback_key(self, func: Callable[..., Any]) -> str:
        """Stable callback identity across app reloads and double imports."""
        code = getattr(func, "__code__", None)
        filename = getattr(code, "co_filename", None) or inspect.getsourcefile(func) or getattr(func, "__module__", "")
        qualname = getattr(func, "__qualname__", getattr(func, "__name__", repr(func)))
        return f"{filename}:{qualname}"

    def subscribe(self, events: List[str], tools: Optional[List[str]] = None) -> Callable[..., Any]:
        """Register listeners without executing them."""
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            target_tools: List[str] = tools if tools else ["*"]
            callback_key = self._callback_key(func)
            for event in events:
                for tool in target_tools:
                    self._registry[event][tool][callback_key] = func
                    self._hooks[event].add(f"{event}:{tool}:{callback_key}")
            return func
        return decorator

    def get_registered_hooks(self, event_type: Optional[str] = None) -> Dict[str, List[str]]:
        """Get all registered hooks, optionally filtered by event type"""
        if event_type:
            return {event_type: sorted(self._hooks.get(event_type, set()))}
        return {event: sorted(hooks) for event, hooks in self._hooks.items()}

    def has_listeners(self, event_type: str, tool_name: str = "*") -> bool:
        if event_type not in self._registry:
            return False
        event_registry = self._registry[event_type]
        return bool(event_registry.get(tool_name)) or bool(event_registry.get("*"))

    def emit(self, event_type: str, tool_name: Any = "*", data: Any = None) -> Awaitable[None]:
        """
        Publish an event.

        Supports both:
        - await emit(event_type, tool_name, payload)
        - emit(event_type, payload) from inside a running event loop
        """
        target_tool, payload = self._normalize_emit_args(tool_name, data)
        coroutine = self._emit(event_type, target_tool, payload)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return coroutine
        return loop.create_task(coroutine)

    def _normalize_emit_args(self, tool_name: Any, data: Any) -> tuple[str, Any]:
        if data is None:
            payload = tool_name
            target_tool = self._current_tool_name.get()
        else:
            payload = data
            target_tool = str(tool_name)

        if isinstance(payload, dict):
            target_tool = str(payload.setdefault("tool_name", target_tool))

        return target_tool, payload

    async def _emit(self, event_type: str, tool_name: str, data: Any) -> None:
        if event_type not in self._registry:
            return
        all_callbacks = self._get_callbacks(event_type, tool_name)
        if not all_callbacks:
            return
        await asyncio.gather(
            *(self._run_callback(func, tool_name, data) for func in all_callbacks),
            return_exceptions=True,
        )

    def _get_callbacks(self, event_type: str, tool_name: str) -> List[Callable[..., Any]]:
        event_registry = self._registry[event_type]
        callbacks = {}
        callbacks.update(event_registry.get("*", {}))
        callbacks.update(event_registry.get(tool_name, {}))
        return list(callbacks.values())

    async def _run_callback(self, func: Callable[..., Any], tool_name: str, data: Any) -> None:
        token = self._current_tool_name.set(tool_name)
        try:
            if inspect.iscoroutinefunction(func):
                await func(data)
            else:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, func, data)
        finally:
            self._current_tool_name.reset(token)

event_manager = EventManager()
