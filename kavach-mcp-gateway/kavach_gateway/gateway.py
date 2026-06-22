"""MCP Gateway - Config-driven routing for microservices."""
import asyncio
from typing import Optional
from kavach_logger import get_logger
from kavach_events import event_manager
from .config import load_routes, RouteConfig
from .router import Router

logger = get_logger("mcp.gateway", masked=False)


def _emit_event(event_name: str, payload: dict) -> None:
    """Emit gateway events from sync code without leaking coroutines."""
    result = event_manager.emit(event_name, payload)
    if asyncio.iscoroutine(result):
        asyncio.run(result)


class MCPGateway:
    """
    MCP Gateway with config-driven routing.

    Example:
        gateway = MCPGateway()
        gateway.load_routes("routes.yaml")
        target = gateway.get_target("/auth/login")
    """

    def __init__(self):
        """Initialize gateway."""
        self.router: Optional[Router] = None
        self._config_path: Optional[str] = None

    def load_routes(self, config_path: str) -> None:
        """
        Load routes from YAML configuration file.

        Args:
            config_path: Path to routes.yaml file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config format is invalid
        """
        try:
            routes = load_routes(config_path)
            self.router = Router(routes)
            self._config_path = config_path
            logger.info(f"Loaded {len(routes)} routes from {config_path}")
            for route in routes:
                logger.debug(f"Route: {route.prefix} -> {route.target}")
            # Emit event
            _emit_event("gateway_routes_loaded", {
                "count": len(routes),
                "config_path": config_path,
                "routes": [r.to_dict() for r in routes]
            })
        except Exception as e:
            logger.error(f"Failed to load routes: {e}")
            _emit_event("gateway_load_error", {
                "error": str(e),
                "config_path": config_path
            })
            raise

    def get_target(self, path: str) -> Optional[str]:
        """
        Get target service URL for a given request path.

        Args:
            path: Request path (e.g., '/auth/login')

        Returns:
            Target URL or None if no match found
        """
        if not self.router:
            logger.warning("Router not initialized. Call load_routes() first.")
            return None
        target = self.router.get_target(path)
        if target:
            _emit_event("gateway_route_matched", {
                "path": path,
                "target": target
            })
        return target

    def get_tool_target(self, tool_name: str) -> Optional[str]:
        """
        Get target MCP server URL for a given tool name.

        Args:
            tool_name: Tool name, preferably namespaced (e.g., 'weather.forecast')

        Returns:
            Target URL or None if no match found
        """
        if not self.router:
            logger.warning("Router not initialized. Call load_routes() first.")
            return None
        target = self.router.get_tool_target(tool_name)
        if target:
            _emit_event("gateway_tool_matched", {
                "tool_name": tool_name,
                "target": target
            })
        return target

    def match(self, path: str) -> Optional[RouteConfig]:
        """
        Match a path to a route configuration.

        Args:
            path: Request path

        Returns:
            RouteConfig or None if no match found
        """
        if not self.router:
            return None
        return self.router.match(path)

    def match_tool(self, tool_name: str) -> Optional[RouteConfig]:
        """
        Match an MCP tool name to a route configuration.

        Args:
            tool_name: Tool name, preferably namespaced

        Returns:
            RouteConfig or None if no match found
        """
        if not self.router:
            return None
        return self.router.match_tool(tool_name)

    def get_routes(self) -> list:
        """Get list of all configured routes."""
        if not self.router:
            return []
        return self.router.get_route_list()

    def get_tools(self) -> list:
        """Get list of all configured tool names."""
        if not self.router:
            return []
        return self.router.get_tool_list()

    def reload(self) -> None:
        """Reload routes from the last loaded configuration file."""
        if not self._config_path:
            logger.warning("No config path to reload from")
            return
        logger.info(f"Reloading routes from {self._config_path}")
        _emit_event("gateway_reload_started", {
            "config_path": self._config_path
        })
        self.load_routes(self._config_path)
