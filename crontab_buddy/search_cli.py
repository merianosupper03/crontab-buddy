"""CLI commands for searching expressions."""

from crontab_buddy.search import search_history, search_favorites, search_by_tag, search_all


def _print_results(results):
    if not results:
        print("No results found.")
        return
    for item in results:
        source = item.get("source", "?")
        expr = item.get("expression", "")
        desc = item.get("description", "")
        name = item.get("name")
        tags = item.get("tags")
        label = f"[{source}]"
        if name:
            label += f" {name}:"
        print(f"{label} {expr}")
        print(f"  -> {desc}")
        if tags:
            print(f"  tags: {', '.join(tags)}")


def cmd_search_history(query: str):
    """Search command history for a query."""
    results = search_history(query)
    print(f"History results for '{query}':")
    _print_results(results)


def cmd_search_favorites(query: str):
    """Search favorites for a query."""
    results = search_favorites(query)
    print(f"Favorites results for '{query}':")
    _print_results(results)


def cmd_search_tag(tag: str):
    """Find all expressions tagged with a given tag."""
    results = search_by_tag(tag)
    print(f"Expressions tagged '{tag}':")
    _print_results(results)


def cmd_search_all(query: str):
    """Search across all sources."""
    results = search_all(query)
    print(f"All results for '{query}':")
    _print_results(results)
