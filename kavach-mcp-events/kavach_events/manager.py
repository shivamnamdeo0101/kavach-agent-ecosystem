import asyncio
import inspect
from collections import defaultdict
from typing import Callable, Any, Dict, List, Optional

class EventManager:
    def __init__(self) -> None:
        self._registry: Dict[str, Dict[str, List[Callable[..., Any]]]] = defaultdict(lambda: defaultdict(list))

    def subscribe(self, events: List[str], tools: Optional[List[str]] = None) -> Callable[..., Any]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            target_tools: List[str] = tools if tools else ["*"]
            for event in events:
                for tool in target_tools:
                    if func not in self._registry[event][tool]:
                        self._registry[event][tool].append(func)
            return func
        return decorator

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
