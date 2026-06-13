from dataclasses import dataclass
from typing import List, Pattern

@dataclass
class Rule:
    id: str
    name: str
    severity: str
    description: str
    patterns: List[Pattern]
