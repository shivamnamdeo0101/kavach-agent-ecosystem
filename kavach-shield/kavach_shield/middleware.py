import asyncio
from fnmatch import fnmatch
from typing import Callable, Any, Dict, List, Optional, Set, Union

from fastmcp.server.middleware import Middleware, MiddlewareContext

from kavach_logger import get_logger, mask_sensitive_data
from kavach_events import event_manager, MCP_HOOKS
from .engine import DetectionEngine
from .rules import KAVACH_RULES
from .exceptions import SecurityException

logger = get_logger("kavach.shield.middleware")

class KavachMiddleware(Middleware):
    """
    Security middleware for MCP servers providing threat interception,
    data leakage prevention, and lifecycle event hooks with auto-emit.
    """
    
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
        
        logger.info(
            f"KavachMiddleware initialized | mode={'STRICT' if strict else 'MONITOR'} | rules_count={len(self.rules)}"
        )

    async def __call__(self, context: MiddlewareContext, call_next: Callable[..., Any]) -> Any:
        return await self.on_call_tool(context, call_next)

    def register_tool(self, tool_name: str) -> None:
        """Dynamically register tool identifier for sensitive tool scanning."""
        self.sensitive_tools.add(tool_name)
        logger.debug(f"Registered sensitive tool | tool_name={tool_name}")

    def _matches_pattern(self, tool_name: str) -> bool:
        """Check if tool matches registered sensitive tool patterns."""
        return any(fnmatch(tool_name, pattern) for pattern in self.sensitive_tools)

    async def on_call_tool(self, context: MiddlewareContext, call_next: Callable[..., Any]) -> Any:
        tool_name: str = getattr(context.message, "name", "unknown")
        args_dict: Dict[str, Any] = getattr(context.message, "arguments", {})
        is_sensitive: bool = self._matches_pattern(tool_name)

        # Baseline shared payload for event propagation
        event_payload = {
            "tool_name": tool_name,
            "arguments": args_dict,
            "context": context,
            "is_sensitive": is_sensitive
        }

        # ========== AUTO-EMIT: PRE-EXECUTION EVENT FOR ALL TOOLS ==========
        # Fire for ALL tools (not just sensitive), always emit standardized event
        pre_payload = {**event_payload, "phase": "pre"}
        
        # Emit standardized PRE_TOOL_CALL event
        await event_manager.emit(MCP_HOOKS.PRE_TOOL_CALL, tool_name, pre_payload)
        
        logger.info(f"🔹 PRE-CALL event | tool={tool_name} | sensitive={is_sensitive}")

        # --- PHASE 1: INBOUND THREAT INSPECTION ---
        if is_sensitive:
            logger.info(f"Scanning inbound request parameters | tool={tool_name}")
            violations: List[Any] = self.engine.scan(str(args_dict))
            
            if violations:
                sec_payload = {**event_payload, "violations": violations, "stage": "inbound"}
                
                # Emit standardized SECURITY_CHECK event
                await event_manager.emit(MCP_HOOKS.SECURITY_CHECK, tool_name, sec_payload)

                if self.strict:
                    logger.warning(f"Inbound security violation triggered | tool={tool_name} | violations={len(violations)}")
                    raise SecurityException(
                        f"Security Policy Violation: Inbound data injection blocked for tool '{tool_name}'."
                    )
                else:
                    logger.warning(f"Inbound violation observed in auditing mode | tool={tool_name} | violations={len(violations)}")
        else:
            logger.debug(f"Bypassing pre-scan routine for non-registered tool entity | tool={tool_name}")

        # --- PHASE 2: CORE RUNTIME EXECUTION LAYER ---
        try:
            response: Any = await call_next(context)
        except Exception as exc:
            # --- PHASE 3: ERROR HANDLING ---
            logger.error(f"Intercepted unhandled exception during tool processing | tool={tool_name} | error={str(exc)}")
            
            # Emit TOOL_ERROR event
            error_payload = {**event_payload, "error": str(exc), "phase": "execution"}
            await event_manager.emit(MCP_HOOKS.TOOL_ERROR, tool_name, error_payload)
            
            if self.strict:
                raise SecurityException("Internal Security Error: Execution terminated by system protection policy.")
            raise exc

        # --- PHASE 4: OUTBOUND DATA LEAK PREVENTION ---
        try:
            output_violations: List[Any] = self.engine.scan(str(response))
            
            if output_violations:
                sec_payload = {**event_payload, "violations": output_violations, "stage": "outbound", "response": response}
                
                # Emit standardized SECURITY_CHECK event
                await event_manager.emit(MCP_HOOKS.SECURITY_CHECK, tool_name, sec_payload)

                if self.strict:
                    logger.error(f"Outbound information data leak intercepted | tool={tool_name} | violations={len(output_violations)}")
                    raise SecurityException("Security Policy Violation: Sensitive response signatures blocked.")

            # Scrub lingering downstream entities like PII strings or credentials
            response = self._mask_response(response)
            
        except SecurityException:
            raise
        except Exception as scan_err:
            logger.error(f"Post-execution safety scanner encountered failure | error={str(scan_err)}")
            
        # ========== AUTO-EMIT: POST-EXECUTION EVENT FOR ALL TOOLS ==========
        # Fire for ALL tools (not just sensitive), always emit standardized event
        post_payload = {**event_payload, "response": response, "phase": "post"}
        
        # Emit standardized POST_TOOL_CALL event
        await event_manager.emit(MCP_HOOKS.POST_TOOL_CALL, tool_name, post_payload)
        
        logger.info(f"🔹 POST-CALL event | tool={tool_name}")

        return response

    def _mask_response(self, response: Any) -> Any:
        """Recursively inspect and mask sensitive data in response."""
        if isinstance(response, str):
            return mask_sensitive_data(response)
            
        if hasattr(response, 'content') and isinstance(response.content, list):
            for item in response.content:
                if hasattr(item, 'text') and isinstance(item.text, str):
                    item.text = mask_sensitive_data(item.text)
        
        return response

    def process(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous utility for processing static payload dicts."""
        violations: List[Any] = self.engine.scan(str(tool_call))
        if violations and self.strict:
            logger.warning(f"Synchronous transaction blocked | violations={len(violations)}")
            raise SecurityException("Security validation failed during static processing.")
            
        return {"allowed": True, "data": tool_call}
