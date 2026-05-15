# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`nldate` is a Python library that parses natural-language date strings (e.g. "5 days before December 1st, 2025", "next Tuesday") into `datetime.date` objects. It is managed with `uv` and uses a `src/` layout.

## Commands

```bash
uv run pytest               # run all tests
uv run pytest tests/test_foo.py::test_bar  # run a single test
uv run mypy                 # type-check src/
uv run ruff check .         # lint
uv run ruff format .        # format
```

## Architecture

- `src/nldate/__init__.py` — the entire public API lives here. The single entry point is:
  ```python
  def parse(s: str, today: date | None = None) -> date: ...
  ```
  `today` is the reference point for relative expressions; defaults to `datetime.date.today()`.
- `tests/` — pytest test suite. All autograder tests are public; the suite must have ≥ 10 passing tests.

## Tooling config

- `[tool.mypy]` runs in `strict` mode over `src/`.
- `[tool.ruff.lint]` selects `E`, `F`, `I` (errors, pyflakes, isort).
- `[tool.pytest.ini_options]` points pytest at `tests/`.
