from kavach_logger import get_logger, mask_sensitive_data

logger = get_logger("kavach.shield.engine")

class DetectionEngine:
    def __init__(self, rules):
        self.rules = rules
        logger.info(f"DetectionEngine initialized | rules={len(rules)}")

    def scan(self, text: str):
        violations = []
        masked_text = mask_sensitive_data(text)
        for rule in self.rules:
            for pattern in rule.patterns:
                if pattern.search(text):
                    violations.append({
                        "rule": rule.id,
                        "name": rule.name,
                        "severity": rule.severity
                    })
                    logger.debug(f"Rule matched | {rule.id} | severity={rule.severity} | data={masked_text}")
                    break
        return violations
