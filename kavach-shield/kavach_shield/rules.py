import re
from .types import Rule

KAVACH_RULES = [
    Rule(
        id="prompt-injection",
        name="Prompt Injection",
        severity="critical",
        description="System override and jailbreak attempts",
        patterns=[
            re.compile(r"ignore\s+(all|previous)\s+instructions", re.I),
            re.compile(r"override\s+(system\s+)?(instructions|rules|policy)", re.I),
            re.compile(r"bypass\s+(rules|policy|security)", re.I),
            re.compile(r"you\s+are\s+now\s+(system|developer|admin|root)", re.I),
            re.compile(r"act\s+as\s+(system|developer|admin|root|unrestricted)", re.I),
            re.compile(r"(jailbreak|dan|developer\s*mode|god\s*mode)", re.I),
        ],
    ),
    Rule(
        id="data-exfiltration",
        name="Data Exfiltration",
        severity="critical",
        description="Attempts to leak system data or prompts",
        patterns=[
            re.compile(r"(send|upload|export|exfiltrate|dump).*(password|secret|token|env|file|system)", re.I),
            re.compile(r"(print|show|reveal).*(system\s*prompt|hidden\s*instructions|internal\s*rules)", re.I),
            re.compile(r"return\s+(system\s*prompt|config|secrets)", re.I),
        ],
    ),
    Rule(
        id="pii",
        name="PII Detection",
        severity="high",
        description="Sensitive personal data",
        patterns=[
            re.compile(r"\b\d{10}\b"),
            re.compile(r"\b\d{12}\b"),
            re.compile(r"\b\d{16}\b"),
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        ],
    ),
    Rule(
        id="secret-leak",
        name="Secret Leakage",
        severity="critical",
        description="API keys and credentials",
        patterns=[
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
            re.compile(r"AIza[0-9A-Za-z0-9_-]{35}"),
            re.compile(r"-----BEGIN (RSA|PRIVATE) KEY-----"),
            re.compile(r"(api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[:=]", re.I),
        ],
    ),
    Rule(
        id="dangerous-eval",
        name="Dangerous Execution",
        severity="critical",
        description="Code execution attempts",
        patterns=[
            re.compile(r"\b(eval|exec|compile)\s*\(", re.I),
            re.compile(r"os\.system|subprocess", re.I),
        ],
    ),
    Rule(
        id="sql-injection",
        name="SQL Injection Patterns",
        severity="high",
        description="SQL injection attempts",
        patterns=[
            re.compile(r"(DROP\s+TABLE|DELETE\s+FROM|UNION\s+SELECT|INSERT\s+INTO|UPDATE\s+.*SET)", re.I),
            re.compile(r"(' OR '1'='1|--|#|/\*)", re.I),
        ],
    ),
]
