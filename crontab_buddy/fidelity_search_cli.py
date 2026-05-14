"""CLI commands for fidelity search."""

from crontab_buddy.fidelity_search import (
    search_history_by_fidelity,
    search_favorites_by_fidelity,
    search_above_score,
)


def _print_results(results, label: str) -> None:
    if not results:
        print(f"No {label} results found.")
        return
    for item in results:
        source = item.get("source", "")
        name = f" ({item['name']})" if "name" in item else ""
        print(
            f"[{source}]{name} {item['expression']} "
            f"| grade={item['grade']} score={item['score']:.2f} "
            f"| {item['description']}"
        )


def cmd_fidelity_search_history(args) -> None:
    """Search cron history by minimum fidelity score."""
    min_score = getattr(args, "min_score", 0.0)
    results = search_history_by_fidelity(min_score)
    _print_results(results, "history")


def cmd_fidelity_search_favorites(args) -> None:
    """Search favorites by minimum fidelity score."""
    min_score = getattr(args, "min_score", 0.0)
    results = search_favorites_by_fidelity(min_score)
    _print_results(results, "favorites")


def cmd_fidelity_search_all(args) -> None:
    """Search history and favorites above a fidelity score threshold."""
    min_score = getattr(args, "min_score", 0.5)
    results = search_above_score(min_score)
    _print_results(results, "combined")
