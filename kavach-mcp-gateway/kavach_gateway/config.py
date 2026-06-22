"""Configuration loader for MCP Gateway routes."""
import yaml
from typing import Any, Dict, List, Optional


class RouteConfig:
    """Represents a single route configuration."""

    def __init__(
        self,
        prefix: str,
        target: str,
        name: Optional[str] = None,
        tools: Optional[List[str]] = None,
    ):
        self.prefix = prefix
        self.target = target
        self.name = name or prefix.strip("/").replace("/", ".") or "root"
        self.tools = tools or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "prefix": self.prefix,
            "target": self.target,
            "name": self.name,
            "tools": self.tools,
        }

    def __repr__(self) -> str:
        return (
            "RouteConfig("
            f"prefix={self.prefix}, target={self.target}, "
            f"name={self.name}, tools={self.tools}"
            ")"
        )


def load_routes(config_path: str) -> List[RouteConfig]:
    """
    Load routes from YAML configuration file.

    Args:
        config_path: Path to routes.yaml file

    Returns:
        List of RouteConfig objects

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config format is invalid
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format: {e}")

    if not config or "routes" not in config:
        raise ValueError("Config must contain 'routes' list")

    routes = []
    for route in config["routes"]:
        if "prefix" not in route or "target" not in route:
            raise ValueError("Each route must have 'prefix' and 'target'")
        tools = route.get("tools", [])
        if tools is None:
            tools = []
        if not isinstance(tools, list) or not all(isinstance(tool, str) for tool in tools):
            raise ValueError("'tools' must be a list of strings")
        routes.append(
            RouteConfig(
                prefix=route["prefix"],
                target=route["target"],
                name=route.get("name"),
                tools=tools,
            )
        )

    return routes
