#!/usr/bin/env python3
"""
SmartTask CLI - An intelligent command-line task manager
Author: Your Name
License: MIT
"""

import json
import os
import sys
import argparse
from datetime import datetime, date
from pathlib import Path
from typing import Optional
import re

DATA_FILE = Path.home() / ".smarttask" / "tasks.json"

PRIORITIES = {"low": 1, "medium": 2, "high": 3, "critical": 4}
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "dim": "\033[2m",
}


def c(color: str, text: str) -> str:
    """Wrap text in ANSI color codes."""
    if not sys.stdout.isatty():
        return text
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def load_tasks() -> list[dict]:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE) as f:
        return json.load(f)


def save_tasks(tasks: list[dict]) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2, default=str)


def generate_id(tasks: list[dict]) -> int:
    return max((t["id"] for t in tasks), default=0) + 1


def parse_due_date(raw: Optional[str]) -> Optional[str]:
    """Parse flexible date inputs like 'today', 'tomorrow', 'YYYY-MM-DD'."""
    if not raw:
        return None
    raw = raw.strip().lower()
    today = date.today()
    if raw == "today":
        return today.isoformat()
    if raw in ("tomorrow", "tmr"):
        from datetime import timedelta
        return (today + timedelta(days=1)).isoformat()
    try:
        parsed = datetime.strptime(raw, "%Y-%m-%d").date()
        return parsed.isoformat()
    except ValueError:
        raise ValueError(f"Invalid date '{raw}'. Use 'today', 'tomorrow', or YYYY-MM-DD.")


def add_task(args) -> None:
    tasks = load_tasks()
    due = parse_due_date(args.due)
    task = {
        "id": generate_id(tasks),
        "title": args.title,
        "description": args.description or "",
        "priority": args.priority,
        "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()],
        "due": due,
        "done": False,
        "created": datetime.now().isoformat(),
        "completed_at": None,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(c("green", "✓") + f" Task #{task['id']} added: {c('bold', task['title'])}")


def list_tasks(args) -> None:
    tasks = load_tasks()

    if args.done:
        tasks = [t for t in tasks if t["done"]]
    elif not args.all:
        tasks = [t for t in tasks if not t["done"]]

    if args.priority:
        tasks = [t for t in tasks if t["priority"] == args.priority]

    if args.tag:
        tasks = [t for t in tasks if args.tag in t.get("tags", [])]

    if args.sort == "priority":
        tasks.sort(key=lambda t: PRIORITIES.get(t["priority"], 0), reverse=True)
    elif args.sort == "due":
        tasks.sort(key=lambda t: t.get("due") or "9999-99-99")
    elif args.sort == "created":
        tasks.sort(key=lambda t: t["created"])

    if not tasks:
        print(c("dim", "  No tasks found."))
        return

    today = date.today().isoformat()
    print()
    print(f"  {'ID':<5} {'PRIORITY':<10} {'DUE':<12} {'TITLE'}")
    print("  " + "─" * 60)

    for t in tasks:
        pid = t["id"]
        pri = t["priority"]
        pri_color = {"low": "cyan", "medium": "yellow", "high": "red", "critical": "magenta"}.get(pri, "reset")
        due = t.get("due") or "—"
        due_str = c("red", due) if due != "—" and due < today else due
        done_mark = c("dim", "✓ ") if t["done"] else "  "
        title = c("dim", t["title"]) if t["done"] else t["title"]
        tags = " " + c("cyan", " ".join(f"#{g}" for g in t.get("tags", []))) if t.get("tags") else ""
        print(f"  {done_mark}{str(pid):<4} {c(pri_color, pri):<10} {due_str:<12} {title}{tags}")

    print()
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    print(c("dim", f"  {done_count}/{total} completed"))
    print()


def complete_task(args) -> None:
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == args.id:
            if t["done"]:
                print(c("yellow", f"⚠ Task #{args.id} is already done."))
                return
            t["done"] = True
            t["completed_at"] = datetime.now().isoformat()
            save_tasks(tasks)
            print(c("green", "✓") + f" Task #{args.id} marked as complete: {c('bold', t['title'])}")
            return
    print(c("red", f"✗ Task #{args.id} not found."))


def delete_task(args) -> None:
    tasks = load_tasks()
    original_len = len(tasks)
    tasks = [t for t in tasks if t["id"] != args.id]
    if len(tasks) == original_len:
        print(c("red", f"✗ Task #{args.id} not found."))
        return
    save_tasks(tasks)
    print(c("green", "✓") + f" Task #{args.id} deleted.")


def show_task(args) -> None:
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == args.id:
            pri_color = {"low": "cyan", "medium": "yellow", "high": "red", "critical": "magenta"}.get(t["priority"], "reset")
            print()
            print(f"  {c('bold', t['title'])}")
            print("  " + "─" * 50)
            print(f"  {'ID:':<14} {t['id']}")
            print(f"  {'Status:':<14} " + (c("green", "Done ✓") if t["done"] else c("yellow", "Pending")))
            print(f"  {'Priority:':<14} {c(pri_color, t['priority'])}")
            print(f"  {'Due:':<14} {t.get('due') or '—'}")
            print(f"  {'Tags:':<14} {', '.join(t.get('tags', [])) or '—'}")
            print(f"  {'Created:':<14} {t['created'][:10]}")
            if t.get("description"):
                print(f"\n  {c('dim', t['description'])}")
            print()
            return
    print(c("red", f"✗ Task #{args.id} not found."))


def stats(args) -> None:
    tasks = load_tasks()
    if not tasks:
        print(c("dim", "  No tasks yet."))
        return

    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    overdue = sum(1 for t in tasks if not t["done"] and t.get("due") and t["due"] < date.today().isoformat())

    by_priority = {}
    for t in tasks:
        p = t["priority"]
        by_priority[p] = by_priority.get(p, 0) + 1

    print()
    print(f"  {c('bold', 'Task Statistics')}")
    print("  " + "─" * 40)
    print(f"  {'Total:':<20} {total}")
    print(f"  {'Completed:':<20} {c('green', str(done))}")
    print(f"  {'Pending:':<20} {total - done}")
    print(f"  {'Overdue:':<20} {c('red', str(overdue)) if overdue else '0'}")
    print(f"  {'Completion Rate:':<20} {round(done / total * 100)}%")
    print()
    print(f"  {c('bold', 'By Priority')}")
    for p in ["critical", "high", "medium", "low"]:
        count = by_priority.get(p, 0)
        bar = "█" * count
        pri_color = {"low": "cyan", "medium": "yellow", "high": "red", "critical": "magenta"}.get(p)
        print(f"  {p:<10} {c(pri_color, bar)} {count}")
    print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task",
        description="SmartTask CLI — A smart terminal task manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  task add "Write unit tests" --priority high --due tomorrow --tags "dev,testing"
  task list --sort priority
  task list --tag dev
  task done 3
  task show 3
  task delete 3
  task stats
        """,
    )
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task title")
    p_add.add_argument("-d", "--description", help="Optional description")
    p_add.add_argument("-p", "--priority", choices=PRIORITIES.keys(), default="medium")
    p_add.add_argument("--due", help="Due date: today, tomorrow, or YYYY-MM-DD")
    p_add.add_argument("-t", "--tags", help="Comma-separated tags")

    # list
    p_list = sub.add_parser("list", help="List tasks", aliases=["ls"])
    p_list.add_argument("--all", action="store_true", help="Show all tasks including done")
    p_list.add_argument("--done", action="store_true", help="Show only completed tasks")
    p_list.add_argument("--priority", choices=PRIORITIES.keys(), help="Filter by priority")
    p_list.add_argument("--tag", help="Filter by tag")
    p_list.add_argument("--sort", choices=["priority", "due", "created"], default="created")

    # done / complete
    p_done = sub.add_parser("done", help="Mark a task as complete", aliases=["complete"])
    p_done.add_argument("id", type=int, help="Task ID")

    # delete
    p_del = sub.add_parser("delete", help="Delete a task", aliases=["rm"])
    p_del.add_argument("id", type=int, help="Task ID")

    # show
    p_show = sub.add_parser("show", help="Show task details")
    p_show.add_argument("id", type=int, help="Task ID")

    # stats
    sub.add_parser("stats", help="Show task statistics")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "add": add_task,
        "list": list_tasks,
        "ls": list_tasks,
        "done": complete_task,
        "complete": complete_task,
        "delete": delete_task,
        "rm": delete_task,
        "show": show_task,
        "stats": stats,
    }

    if args.command in dispatch:
        try:
            dispatch[args.command](args)
        except ValueError as e:
            print(c("red", f"✗ Error: {e}"))
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
