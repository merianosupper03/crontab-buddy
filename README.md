# crontab-buddy

> A CLI tool to interactively build, validate, and document cron expressions with human-readable previews.

---

## Installation

```bash
pip install crontab-buddy
```

Or install from source:

```bash
git clone https://github.com/yourusername/crontab-buddy.git
cd crontab-buddy
pip install .
```

---

## Usage

Launch the interactive builder:

```bash
crontab-buddy
```

Validate and explain an existing expression:

```bash
crontab-buddy explain "*/15 9-17 * * 1-5"
# Output: Every 15 minutes, between 09:00 and 17:00, Monday through Friday
```

Generate a cron expression from a plain-English description:

```bash
crontab-buddy build
# ? How often should this run? Every hour
# ? Any time restrictions? Weekdays only
# ✔ Generated: 0 * * * 1-5
```

---

## Features

- 🕐 Interactive step-by-step cron expression builder
- ✅ Validates existing cron expressions and highlights errors
- 📖 Translates cron syntax into plain-English descriptions
- 📋 Copies final expression to clipboard

---

## Requirements

- Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).