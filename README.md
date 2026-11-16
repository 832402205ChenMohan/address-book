# Address Book

A small address book web application built for the Software Engineering (FZU–MU) Extreme Programming assignment: bookmark contacts, attach several contact methods to one contact, and import/export Excel in both directions.

Repository: <https://github.com/832402205ChenMohan/address-book>

## Features against the grading rubric

| Requirement | Points | What this project does | Where |
| --- | --- | --- | --- |
| Bookmark contacts | 25 | Star toggle on each card, favourites-only filter, favourites sorted first | `static/js/app.js`, `models.set_favorite` |
| Multiple contact methods | 10 | Any number of phone / email / wechat / address / other entries per contact, each with its own label | `models.normalise_payload`, `templates/index.html` |
| Import and export | 25 | Real xlsx export (one row per contact, one column per kind of information); import by header, merging by name | `excel_io.py` |
| Web deployment (optional) | +15 | Deployment procedure and systemd/nginx config | `docs/DEPLOY.md` |
| Page style | 10 | Designed interface: card grid, statistics strip, dialog form, toasts | `static/css/style.css` |

## Tech stack

- Backend: Python 3.13 + Flask 3.1
- Database: SQLite (`data/addressbook.db`, schema created on first start)
- Excel: openpyxl 3.1
- Front end: plain HTML / CSS / JavaScript, no framework and no build step
- Tests: pytest

## Project layout

```
address-book/
├── app.py                 # Flask app: page route + JSON API
├── database.py            # SQLite connection and schema
├── models.py              # validation, CRUD, bookmarks, statistics
├── excel_io.py            # Excel import and export
├── requirements.txt
├── scripts/seed_demo.py   # insert sample contacts
├── templates/index.html   # page skeleton
├── static/css/style.css   # styles
├── static/js/app.js       # front-end logic
├── tests/test_app.py      # 12 automated tests
├── docs/                  # blog drafts, PSP, deployment and setup notes
└── screenshots/           # run screenshots and demo video
```

## Quick start

```powershell
cd address-book
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # PowerShell
python -m pip install -r requirements.txt

python scripts\seed_demo.py         # optional: insert sample data
python -m pytest -q                 # expect 12 passed
python app.py                       # start the server
```

Then open <http://127.0.0.1:5000>.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Address book page |
| GET | `/api/contacts?q=&favorite=1` | List contacts, with keyword and favourite filters |
| POST | `/api/contacts` | Create a contact |
| PUT | `/api/contacts/<id>` | Update a contact (methods are replaced wholesale) |
| DELETE | `/api/contacts/<id>` | Delete a contact and its methods |
| POST | `/api/contacts/<id>/favorite` | Bookmark or unbookmark (`{"favorite": true/false}`) |
| GET | `/api/export` | Download `contacts.xlsx` |
| GET | `/api/template` | Download an empty import template |
| POST | `/api/import` | Upload an xlsx file (form field `file`) |
| GET | `/healthz` | Health check used by the deployment |

## Excel format

- Rows: one contact per row. Columns: `Name`, `Company`, `Title`, `Notes`, `Favorite`, then `Phone 1`, `Phone 2`, `Email 1`, `WeChat 1`, `Address 1`, `Other 1` and so on.
- The exporter decides how many columns each kind needs from the actual data (at least one), styles the header and freezes the first row.
- The importer matches columns by header text, case and spacing insensitive. Unrecognised columns are ignored; a sheet with no recognisable column at all is rejected.
- Importing a name that already exists merges: existing methods are kept, new ones are appended, and no duplicate contact is created.
- Several values of one kind can share a cell, separated by `;` or a line break. `13800000001 (mobile)` is parsed as value plus label.

## Tests

```powershell
python -m pytest -q
```

Coverage: page rendering, create/list/update/delete, favourite toggling, search by contact method, export column layout, export→import round trip, merge by name, skipping rows without a name, and rejecting headerless sheets.
