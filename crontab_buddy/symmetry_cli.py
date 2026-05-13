from crontab_buddy.symmetry import assess_symmetry
import json


def cmd_symmetry_check(args):
    result = assess_symmetry(args.expr_a, args.expr_b)
    print(f"Expression A : {args.expr_a}")
    print(f"Expression B : {args.expr_b}")
    print(f"Symmetric    : {result.symmetric}")
    print(f"Score        : {result.score:.3f}")
    print(f"Label        : {result.label}")
    if result.differences:
        print("Differences:")
        for field, (a, b) in result.differences.items():
            print(f"  {field}: '{a}' vs '{b}'")
    if result.error:
        print(f"Error        : {result.error}")


def cmd_symmetry_score(args):
    result = assess_symmetry(args.expr_a, args.expr_b)
    print(f"{result.score:.4f}")


def cmd_symmetry_label(args):
    result = assess_symmetry(args.expr_a, args.expr_b)
    print(result.label)


def cmd_symmetry_json(args):
    result = assess_symmetry(args.expr_a, args.expr_b)
    print(json.dumps({
        "expr_a": args.expr_a,
        "expr_b": args.expr_b,
        "symmetric": result.symmetric,
        "score": round(result.score, 4),
        "label": result.label,
        "differences": {
            k: list(v) for k, v in result.differences.items()
        },
        "error": result.error,
    }, indent=2))


def cmd_symmetry_batch(args):
    pairs = [(e.strip() for e in line.split(",", 1)) for line in args.pairs]
    for pair in pairs:
        a, b = pair
        result = assess_symmetry(a, b)
        status = "symmetric" if result.symmetric else "asymmetric"
        print(f"{a} | {b} => {status} ({result.score:.3f})")
