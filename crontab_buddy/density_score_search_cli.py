"""CLI commands for density score search."""
from crontab_buddy.density_score_search import (
    search_history_by_density_score,
    search_favorites_by_density_score,
)


def _print_results(results, label):
    if not results:
        print(f"No {label} results found.")
        return
    for r in results:
        expr = r.get("expression", "?")
        desc = r.get("description", "")
        grade = r.get("grade", "?")
        score = r.get("score", 0.0)
        src = r.get("source", label)
        print(f"[{src}] {expr}  grade={grade}  score={score:.2f}  {desc}")


def cmd_density_score_search_history(args):
    """Search history for expressions matching a minimum density score."""
    try:
        min_score = float(args.min_score)
    except (ValueError, AttributeError):
        print("Error: --min-score must be a float between 0 and 1.")
        return
    results = search_history_by_density_score(min_score=min_score)
    _print_results(results, "history")


def cmd_density_score_search_favorites(args):
    """Search favorites for expressions matching a minimum density score."""
    try:
        min_score = float(args.min_score)
    except (ValueError, AttributeError):
        print("Error: --min-score must be a float between 0 and 1.")
        return
    results = search_favorites_by_density_score(min_score=min_score)
    _print_results(results, "favorites")


def cmd_density_score_search_all(args):
    """Search both history and favorites by minimum density score."""
    try:
        min_score = float(args.min_score)
    except (ValueError, AttributeError):
        print("Error: --min-score must be a float between 0 and 1.")
        return
    history_results = search_history_by_density_score(min_score=min_score)
    favorites_results = search_favorites_by_density_score(min_score=min_score)
    all_results = history_results + favorites_results
    _print_results(all_results, "all")
