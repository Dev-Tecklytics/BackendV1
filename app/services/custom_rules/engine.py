import re


def run_custom_rules(rules, workflow_metrics):
    findings = []

    for rule in rules:
        if rule.rule_type == "activity_count":
            if workflow_metrics["activity_count"] > rule.config["threshold"]:
                findings.append({
                    "rule": rule.name,
                    "severity": rule.severity,
                    "message": "Activity count exceeded"
                })

        if rule.rule_type == "nesting_depth":
            if workflow_metrics["nesting_depth"] > rule.config["threshold"]:
                findings.append({
                    "rule": rule.name,
                    "severity": rule.severity,
                    "message": "Nesting depth exceeded"
                })

    return findings
