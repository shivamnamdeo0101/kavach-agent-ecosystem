"""Router for handling request routing based on path prefixes."""
from typing import Dict, List, Optional
from .config import RouteConfig


class Router:
    """Routes requests to target services based on configured prefixes."""

    def __init__(self, routes: List[RouteConfig]):
        """
        Initialize router with routes.

        Args:
            routes: List of RouteConfig objects
        """
        self.routes = sorted(routes, key=lambda r: len(r.prefix), reverse=True)
        self.tool_routes = self._build_tool_routes(self.routes)

    def _build_tool_routes(self, routes: List[RouteConfig]) -> Dict[str, RouteConfig]:
        """Build a lookup table for MCP tool names."""
        tool_routes = {}
        short_names = {}
        duplicate_short_names = set()

        for route in routes:
            for tool in route.tools:
                namespaced_tool = f"{route.name}.{tool}"
                tool_routes[namespaced_tool] = route

                if tool in short_names:
                    duplicate_short_names.add(tool)
                short_names[tool] = route

        for tool, route in short_names.items():
            if tool not in duplicate_short_names:
                tool_routes[tool] = route

        return tool_routes

    def match(self, path: str) -> Optional[RouteConfig]:
        """
        Match a path to a route.

        Args:
            path: Request path (e.g., '/auth/login')

        Returns:
            Matching RouteConfig or None if no match found
        """
        for route in self.routes:
            if path.startswith(route.prefix):
                return route
        return None

    def get_target(self, path: str) -> Optional[str]:
        """
        Get target URL for a given path.

        Args:
            path: Request path

        Returns:
            Target URL or None if no match found
        """
        route = self.match(path)
        return route.target if route else None

    def match_tool(self, tool_name: str) -> Optional[RouteConfig]:
        """
        Match an MCP tool name to a route.

        Args:
            tool_name: Tool name, preferably namespaced (e.g., 'weather.forecast')

        Returns:
            Matching RouteConfig or None if no match found
        """
        return self.tool_routes.get(tool_name)

    def get_tool_target(self, tool_name: str) -> Optional[str]:
        """
        Get target URL for a given MCP tool name.

        Args:
            tool_name: Tool name, preferably namespaced

        Returns:
            Target URL or None if no match found
        """
        route = self.match_tool(tool_name)
        return route.target if route else None

    def get_route_list(self) -> List[str]:
        """Get list of all configured routes."""
        return [route.prefix for route in self.routes]

    def get_tool_list(self) -> List[str]:
        """Get list of all configured tool names."""
        return sorted(self.tool_routes)
