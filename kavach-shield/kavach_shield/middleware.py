import asyncio
from fnmatch import fnmatch
from typing import Callable, Any, Dict, List, Optional, Set, Union

from kavach_logger import get_logger
from kavach_events import event_manager
from .engine import DetectionEngine
from .rules import KAVACH_RULES
from .exceptions import SecurityException

logger = get_logger("kavach.shield.middleware")

class KavachMiddleware:
    def __init__(
        self, 
        rules: Optional[List[Any]] = None, 
        strict: bool = True, 
        sensitive_tools: Optional[Union[List[str], Set[str]]] = None, 
        extend_rules: bool = True
    ) -> None:
        if rules and extend_rules:
            self.rules = KAVACH_RULES + rules
        else:
            self.rules = rules or KAVACH_RULES
        self.engine: DetectionEngine = DetectionEngine(self.rules)
        self.strict: bool = strict
        self.sensitive_tools: Set[str] = set(sensitive_tools or [])
        logger.info(f"KavachMiddleware initialized | mode={'STRICT' if strict else 'MONITOR'} | rules={len(self.rules)}")

    async def __call__(self, context: Any, call_next: Callable[..., Any]) -> Any:
        return await self.on_call_tool(context, call_next)

    def register_tool(self, tool_name: str) -> None:
        self.sensitive_tools.add(tool_name)
        logger.debug(f"Registered sensitive tool | tool_name={tool_name}")

    def _matches_pattern(self, tool_name: str) -> bool:
        return any(fnmatch(tool_name, pattern) for pattern in self.sensitive_tools)

    async def on_call_tool(self, context: Any, call_next: Callable[..., Any]) -> Any:
        tool_name: str = getattr(context.message, "name", "unknown")
        args_dict: Dict[str, Any] = getattr(context.message, "arguments", {})
        is_sensitive: bool = self._matches_pattern(tool_name)

        event_payload = {"tool_name": tool_name, "arguments": args_dict, "context": context, "is_sensitive": is_sensitive}

        if event_manager.has_listeners("pre", tool_name):
            asyncio.create_task(event_manager.emit("pre", tool_name, event_payload))

        if is_sensitive:
            logger.info(f"Scanning inbound request | tool={tool_name}")
            violations: List[Any] = self.engine.scan(str(args_dict))
            
            if violations:
                sec_payload = {**event_payload, "violations": violations, "stage": "inbound"}
                if event_manager.has_listeners("sec", tool_name):
                    asyncio.create_task(event_manager.emit("sec", tool_name, sec_payload))
                
                if self.strict:
                    raise SecurityException(f"Security violations detected: {violations}")

        try:
            result = await call_next(context)
        except Exception as e:
            logger.error(f"Tool execution failed | tool={tool_name} | error={str(e)}")
            raise

        if is_sensitive:
            logger.info(f"Scanning outbound response | tool={tool_name}")
            violations: List[Any] = self.engine.scan(str(result))
            
            if violations:
                sec_payload = {**event_payload, "violations": violations, "result": result, "stage": "outbound"}
                if event_manager.has_listeners("sec", tool_name):
                    asyncio.create_task(event_manager.emit("sec", tool_name, sec_payload))
                
                if self.strict:
                    raise SecurityException(f"Security violations in response: {violations}")

        if event_manager.has_listeners("post", tool_name):
            asyncio.create_task(event_manager.emit("post", tool_name, {**event_payload, "result": result}))

        return result
