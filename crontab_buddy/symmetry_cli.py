from crontab_buddy.symmetry import check_symmetry
import json


def cmd_symmetry_check(args):
    result = check_symmetry(args.expr_a, args.expr_b)
    print(f"Expression A : {result.expr_a}")
    print(f"Expression B : {result.expr_b}")
    print(f"Symmetric    : {result.symmetric}")
    if result.differences:
        print("Differences:")
        for field, (a, b) in result.differences.items():
            print(f"  {field}: '{a}' vs '{b}'")
    else:
        print("No field differences found.")


def cmd_symmetry_score(args):
    result = check_symmetry(args.expr_a, args.expr_b)
    print(f"{result.score:.4f}")


def cmd_symmetry_label(args):
    result = check_symmetry(args.expr_a, args.expr_b)
    print(result.label)


def cmd_symmetry_json(args):
    result = check_symmetry(args.expr_a, args.expr_b)
    print(json.dumps({
        "expr_a": result.expr_a,
        "expr_b": result.expr_b,
        "symmetric": result.symmetric,
        "score": result.score,
        "label": result.label,
        "differences": {
            k: list(v) for k, v in result.differences.items()
        },
    }, indent=2))


def cmd_symmetry_batch(args):
    pairs = [
        (a.strip(), b.strip())
        for line in args.pairs
        for a, _, b in [line.partition(",")]
        if a and b
    ]
    for expr_a, expr_b in pairs:
        result = check_symmetry(expr_a, expr_b)
        sym = "YES" if result.symmetric else "NO "
        print(f"[{sym}] {expr_a!r:30s} <-> {expr_b!r:30s}  score={result.score:.2f}")
