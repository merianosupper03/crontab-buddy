"""CLI commands for workflow management."""

from crontab_buddy.workflow import (
    create_workflow, add_step, remove_step,
    get_workflow, delete_workflow, list_workflows,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_workflow_create(args, path=None):
    kwargs = {} if path is None else {"path": path}
    ok = create_workflow(args.name, **kwargs)
    if ok:
        print(f"Workflow '{args.name}' created.")
    else:
        print(f"Workflow '{args.name}' already exists.")


def cmd_workflow_add(args, path=None):
    kwargs = {} if path is None else {"path": path}
    label = getattr(args, "label", None)
    ok = add_step(args.name, args.expression, label=label, **kwargs)
    if ok:
        print(f"Step '{args.expression}' added to workflow '{args.name}'.")
    else:
        print(f"Workflow '{args.name}' not found.")


def cmd_workflow_remove(args, path=None):
    kwargs = {} if path is None else {"path": path}
    ok = remove_step(args.name, args.index, **kwargs)
    if ok:
        print(f"Step {args.index} removed from workflow '{args.name}'.")
    else:
        print(f"Could not remove step {args.index} from workflow '{args.name}'.")


def cmd_workflow_get(args, path=None):
    kwargs = {} if path is None else {"path": path}
    wf = get_workflow(args.name, **kwargs)
    if wf is None:
        print(f"Workflow '{args.name}' not found.")
        return
    print(f"Workflow: {wf['name']}")
    for i, step in enumerate(wf["steps"]):
        desc = _describe(step["expression"])
        print(f"  [{i}] {step['label']} — {step['expression']} ({desc})")


def cmd_workflow_delete(args, path=None):
    kwargs = {} if path is None else {"path": path}
    ok = delete_workflow(args.name, **kwargs)
    if ok:
        print(f"Workflow '{args.name}' deleted.")
    else:
        print(f"Workflow '{args.name}' not found.")


def cmd_workflow_list(args, path=None):
    kwargs = {} if path is None else {"path": path}
    workflows = list_workflows(**kwargs)
    if not workflows:
        print("No workflows saved.")
        return
    for wf in workflows:
        print(f"  {wf['name']} ({len(wf['steps'])} steps)")
