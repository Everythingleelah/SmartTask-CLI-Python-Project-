# SmartTask CLI 📋

A powerful, colorful command-line task manager built in pure Python with **zero dependencies**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python) ![License](https://img.shields.io/badge/License-MIT-green) ![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

---

## Features

- **Zero dependencies** — uses only Python standard library
- 🎨 **Color-coded priorities** — critical, high, medium, low
- 🏷️ **Tag support** — categorize and filter tasks by tags
- 📅 **Flexible dates** — `today`, `tomorrow`, or `YYYY-MM-DD`
- 🔴 **Overdue detection** — past-due tasks highlighted in red
- 📊 **Stats dashboard** — completion rate and breakdown by priority
- 💾 **Persistent storage** — saved as JSON in `~/.smarttask/tasks.json`

---

## Installation

```bash
git clone https://github.com/yourusername/smart-task-cli.git
cd smart-task-cli
chmod +x task_cli.py
```

Optionally alias it for fast access:

```bash
alias task="python3 /path/to/task_cli.py"
```

---

## Usage

```bash
# Add tasks
python3 task_cli.py add "Refactor auth module" --priority high --due tomorrow --tags "backend,security"
python3 task_cli.py add "Write integration tests" --priority medium --due 2024-12-31

# List tasks
python3 task_cli.py list                    # pending only
python3 task_cli.py list --all              # all tasks
python3 task_cli.py list --sort priority    # sorted by priority
python3 task_cli.py list --tag backend      # filter by tag

# Manage tasks
python3 task_cli.py show 1                  # view task details
python3 task_cli.py done 1                  # mark as complete
python3 task_cli.py delete 2                # remove a task

# Stats
python3 task_cli.py stats
```

---

## Demo Output

```
  ID    PRIORITY   DUE          TITLE
  ────────────────────────────────────────────────────────────
    1   critical   2024-12-20   Fix production auth bug  #backend #security
    2   high       2024-12-22   Write unit tests          #dev #testing
    3   medium     —            Update README
    4   low        2024-12-31   Refactor CSS              #frontend

  0/4 completed
```

---

## Data Format

Tasks are stored in `~/.smarttask/tasks.json`:

```json
{
  "id": 1,
  "title": "Fix production auth bug",
  "description": "JWT tokens expiring too early",
  "priority": "critical",
  "tags": ["backend", "security"],
  "due": "2024-12-20",
  "done": false,
  "created": "2024-12-15T10:30:00",
  "completed_at": null
}
```

---

## Project Structure

```
smart-task-cli/
├── task_cli.py       # Main CLI application
├── tests/
│   └── test_tasks.py # Unit tests
└── README.md
```

---

## Running Tests

```bash
python3 -m pytest tests/ -v
```

---

## License

MIT: free to use, modify, and distribute.
