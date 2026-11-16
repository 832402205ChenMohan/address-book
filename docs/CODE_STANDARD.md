# Code Standard

Coding rules used in this repository; they are what the "code standard link" in the assignment blog points to.

## Python

- Follow [PEP 8](https://peps.python.org/pep-0008/); keep lines under 100 characters.
- Naming: `snake_case` for modules, functions and variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Every module and every public function gets a docstring stating its job and return value. Non-obvious branches get a comment explaining *why*, not *what*.
- Type hints: annotate parameters and return types; dictionaries handed across layers are typed as `dict[str, Any]`.
- Validation failures raise `models.ValidationError` only; `app.py`'s error handler turns that into a 400 JSON response, so the domain layer never builds HTTP responses.
- SQL lives in `models.py` and `database.py` only (`excel_io.py` reaches data exclusively through models functions). The view layer writes no SQL.
- Table and column names are lower-case with underscores; every foreign key is declared and `PRAGMA foreign_keys = ON` is set on each connection.

## Front end

- Plain ES6, no framework and no build step; one concern per file (`app.js` only renders and calls the API).
- `camelCase` for variables; DOM nodes are collected once in the `el` object instead of scattered `document.getElementById` calls.
- All requests go through the single `api()` helper, and any non-2xx or domain error surfaces through `toast()` — nothing fails silently.
- CSS keeps colours and radii in custom properties, uses `block-element` class names, and avoids deeply nested selectors.

## Data and files

- The database file, exported xlsx files and virtual environments are git-ignored; only code, docs, tests and screenshots are tracked.
- Sample data comes from `scripts/seed_demo.py`, so the demo is reproducible on any machine with one command.

## Git

- Commit messages follow `type(scope): summary`, e.g. `feat(excel): support tagged method import`; type is one of `feat`, `fix`, `test`, `docs`, `refactor`, `chore`.
- One commit does one thing. `python -m pytest -q` must be green before each commit.
