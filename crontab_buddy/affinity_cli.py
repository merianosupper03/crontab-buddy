"""CLI commands for affinity assessment."""

import json

from crontab_buddy.affinity import assess_affinity


def cmd_affinity_check(args) -> None:
    """Print a human-readable affinity report for two expressions."""
    result = assess_affinity(args.expr_a, args.expr_b)
    print(result)


def cmd_affinity_score(args) -> None:
    """Print only the numeric affinity score."""
    result = assess_affinity(args.expr_a, args.expr_b)
    print(f"{result.score:.4f}")


def cmd_affinity_grade(args) -> None:
    """Print only the affinity grade label."""
    result = assess_affinity(args.expr_a, args.expr_b)
    print(result.grade)


def cmd_affinity_json(args) -> None:
    """Print affinity result as JSON."""
    result = assess_affinity(args.expr_a, args.expr_b)
    payload = {
        "expression_a": result.expression_a,
        "expression_b": result.expression_b,
        "score": result.score,
        "grade": result.grade,
        "overlap_count": result.overlap_count,
        "notes": result.notes,
    }
    print(json.dumps(payload, indent=2))


def cmd_affinity_batch(args) -> None:
    """Assess affinity for a list of expression pairs (newline-separated 'A|B')."""
    pairs = [line.strip() for line in args.pairs.splitlines() if "|" in line]
    if not pairs:
        print("No valid pairs found. Use 'expr_a|expr_b' format per line.")
        return
    for pair in pairs:
        a, b = pair.split("|", 1)
        result = assess_affinity(a.strip(), b.strip())
        print(f"{a.strip()} <-> {b.strip()} : {result.grade} ({result.score:.2f})")
