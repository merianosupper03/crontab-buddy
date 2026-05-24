"""CLI commands for coverage_density."""
import json
from crontab_buddy.coverage_density import assess_coverage_density, format_coverage_density


def cmd_coverage_density_check(args) -> None:
    """Print a human-readable coverage+density summary."""
    expressions = args.expressions
    result = assess_coverage_density(expressions)
    print(f"Expressions : {', '.join(result.expressions) if result.expressions else 'none'}")
    if result.error:
        print(f"Error       : {result.error}")
        return
    print(f"Coverage    : {result.coverage_score:.2f}")
    print(f"Density     : {result.density_score:.2f}")
    print(f"Combined    : {result.combined_score:.2f}")
    print(f"Grade       : {result.grade}")


def cmd_coverage_density_score(args) -> None:
    """Print only the combined score."""
    result = assess_coverage_density(args.expressions)
    print(result.combined_score)


def cmd_coverage_density_grade(args) -> None:
    """Print only the grade."""
    result = assess_coverage_density(args.expressions)
    print(result.grade)


def cmd_coverage_density_json(args) -> None:
    """Print full result as JSON."""
    result = assess_coverage_density(args.expressions)
    print(json.dumps(format_coverage_density(result), indent=2))
