"""Optional security extensions for gateway using kavach-shield."""
from typing import Optional
try:
    from kavach_shield import DetectionEngine, KAVACH_RULES
    SHIELD_AVAILABLE = True
except ImportError:
    SHIELD_AVAILABLE = False

from kavach_logger import get_logger

logger = get_logger("mcp.gateway.security", masked=False)


class SecurityScanner:
    """Optional security scanning for gateway requests/responses."""

    def __init__(self, enabled: bool = True):
        """
        Initialize security scanner.

        Args:
            enabled: Enable scanning (requires kavach-shield)
        """
        if enabled and not SHIELD_AVAILABLE:
            logger.warning(
                "Security scanning disabled: kavach-shield not installed. "
                "Install with: pip install kavach-mcp-gateway[security]"
            )
            self.enabled = False
            self.engine = None
        elif enabled:
            self.engine = DetectionEngine(KAVACH_RULES)
            self.enabled = True
            logger.info("Security scanner initialized")
        else:
            self.enabled = False
            self.engine = None

    def scan_path(self, path: str) -> list:
        """
        Scan request path for security violations.

        Args:
            path: Request path to scan

        Returns:
            List of violations found
        """
        if not self.enabled or not self.engine:
            return []
        violations = self.engine.scan(path)
        if violations:
            logger.warning(
                f"Security violations found in path: {path} violations={len(violations)}"
            )
        return violations

    def scan_body(self, body: str) -> list:
        """
        Scan request body for security violations.

        Args:
            body: Request body to scan

        Returns:
            List of violations found
        """
        if not self.enabled or not self.engine:
            return []
        violations = self.engine.scan(body)
        if violations:
            logger.warning(
                f"Security violations found in body: violations={len(violations)}"
            )
        return violations
