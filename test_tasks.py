"""Unit tests for SmartTask CLI"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import date, timedelta

# Patch DATA_FILE before import
TEMP_DIR = tempfile.mkdtemp()
TEMP_DATA = Path(TEMP_DIR) / "tasks.json"

import importlib
import task_cli

task_cli.DATA_FILE = TEMP_DATA


class TestTaskCLI(unittest.TestCase):

    def setUp(self):
        if TEMP_DATA.exists():
            TEMP_DATA.unlink()

    def _add_task(self, title="Test Task", priority="medium", due=None, tags=""):
        class Args:
            pass
        args = Args()
        args.title = title
        args.priority = priority
        args.due = due
        args.tags = tags
        args.description = None
        task_cli.add_task(args)

    def test_add_task_creates_file(self):
        self._add_task("My first task")
        self.assertTrue(TEMP_DATA.exists())

    def test_add_task_increments_id(self):
        self._add_task("Task A")
        self._add_task("Task B")
        tasks = task_cli.load_tasks()
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[1]["id"], 2)

    def test_task_defaults(self):
        self._add_task("Default task")
        tasks = task_cli.load_tasks()
        task = tasks[0]
        self.assertEqual(task["priority"], "medium")
        self.assertFalse(task["done"])
        self.assertIsNone(task["due"])
        self.assertEqual(task["tags"], [])

    def test_add_task_with_tags(self):
        self._add_task("Tagged task", tags="dev, testing, backend")
        tasks = task_cli.load_tasks()
        self.assertEqual(tasks[0]["tags"], ["dev", "testing", "backend"])

    def test_complete_task(self):
        self._add_task("To complete")
        class Args:
            id = 1
        task_cli.complete_task(Args())
        tasks = task_cli.load_tasks()
        self.assertTrue(tasks[0]["done"])
        self.assertIsNotNone(tasks[0]["completed_at"])

    def test_complete_already_done(self, capsys=None):
        self._add_task("Already done")
        class Args:
            id = 1
        task_cli.complete_task(Args())
        tasks = task_cli.load_tasks()
        self.assertTrue(tasks[0]["done"])

    def test_delete_task(self):
        self._add_task("To delete")
        class Args:
            id = 1
        task_cli.delete_task(Args())
        tasks = task_cli.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_nonexistent_task(self):
        class Args:
            id = 999
        # Should not raise
        task_cli.delete_task(Args())

    def test_parse_due_today(self):
        result = task_cli.parse_due_date("today")
        self.assertEqual(result, date.today().isoformat())

    def test_parse_due_tomorrow(self):
        result = task_cli.parse_due_date("tomorrow")
        expected = (date.today() + timedelta(days=1)).isoformat()
        self.assertEqual(result, expected)

    def test_parse_due_iso_date(self):
        result = task_cli.parse_due_date("2025-06-15")
        self.assertEqual(result, "2025-06-15")

    def test_parse_due_invalid(self):
        with self.assertRaises(ValueError):
            task_cli.parse_due_date("next-friday")

    def test_parse_due_none(self):
        result = task_cli.parse_due_date(None)
        self.assertIsNone(result)

    def test_generate_id_empty(self):
        self.assertEqual(task_cli.generate_id([]), 1)

    def test_generate_id_increment(self):
        tasks = [{"id": 1}, {"id": 3}, {"id": 2}]
        self.assertEqual(task_cli.generate_id(tasks), 4)

    def test_multiple_tasks_persist(self):
        for i in range(5):
            self._add_task(f"Task {i}", priority=["low", "medium", "high", "critical", "low"][i])
        tasks = task_cli.load_tasks()
        self.assertEqual(len(tasks), 5)


if __name__ == "__main__":
    unittest.main()
