"""compliance_cli.py — CLI commands for compliance checking."""

import json
from typing import List, Optional

from crontab_buddy.compliance import check_compliance, list_policies


def cmd_compliance_check(args) -> None:
    """Check a single expression against policies."""
    policies: Optional[List[str]] = (
        [p.strip() for p in args.policies.split(",")] if getattr(args, "policies", None) else None
    )
    result = check_compliance(args.expression, policies=policies)
    print(str(result))


def cmd_compliance_batch(args) -> None:
    """Check multiple expressions (one per line via --expressions)."""
    expressions: List[str] = [e.strip() for e in args.expressions.split(",") if e.strip()]
    policies: Optional[List[str]] = (
        [p.strip() for p in args.policies.split(",")] if getattr(args, "policies", None) else None
    )
    passed = 0
    failed = 0
    for expr in expressions:
        result = check_compliance(expr, policies=policies)
        print(str(result))
        if result.passed:
            passed += 1
        else:
            failed += 1
    print(f"\nSummary: {passed} passed, {failed} failed out of {len(expressions)} expressions.")


def cmd_compliance_json(args) -> None:
    """Output compliance result as JSON."""
    policies: Optional[List[str]] = (
        [p.strip() for p in args.policies.split(",")] if getattr(args, "policies", None) else None
    )
    result = check_compliance(args.expression, policies=policies)
    data = {
        "expression": result.expression,
        "passed": result.passed,
        "violations": result.violations,
        "warnings": result.warnings,
    }
    print(json.dumps(data, indent=2))


def cmd_compliance_policies(args) -> None:  # noqa: ARG001
    """List all available policy names and descriptions."""
    policies = list_policies()
    print("Available compliance policies:")
    for name, description in policies.items():
        print(f"  {name}: {description}")
