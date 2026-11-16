"""Excel import and export.

Layout rules required by the assignment:
    * one contact per row;
    * one column per kind of information, so several phone numbers become
      ``Phone 1``, ``Phone 2`` and so on.
"""

from __future__ import annotations

import io
import re
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

import models

FIXED_COLUMNS = [
    ("name", "Name"),
    ("company", "Company"),
    ("title", "Title"),
    ("notes", "Notes"),
    ("is_favorite", "Favorite"),
]

METHOD_HEADERS = {
    "phone": "Phone",
    "email": "Email",
    "wechat": "WeChat",
    "address": "Address",
    "other": "Other",
}

HEADER_ALIASES = {
    "name": "name",
    "company": "company",
    "organisation": "company",
    "organization": "company",
    "title": "title",
    "job": "title",
    "position": "title",
    "notes": "notes",
    "note": "notes",
    "remark": "notes",
    "remarks": "notes",
    "favorite": "is_favorite",
    "bookmark": "is_favorite",
    "bookmarked": "is_favorite",
    "starred": "is_favorite",
}

METHOD_PATTERN = re.compile(
    r"^(phone|email|wechat|address|other)(?:\s*(?:no\.?|#)?\s*(\d+))?$"
)

HEADER_FILL = PatternFill("solid", fgColor="0F766E")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
THIN = Side(style="thin", color="D9E2E0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

TRUTHY = {"1", "true", "yes", "y", "on", "favorite", "starred"}


def _method_widths(contacts: list[dict[str, Any]]) -> dict[str, int]:
    """Wide enough for the largest number of methods of each kind."""
    widths = {kind: 1 for kind in models.METHOD_KINDS}
    for contact in contacts:
        counters = {kind: 0 for kind in models.METHOD_KINDS}
        for method in contact["methods"]:
            counters[method["kind"]] += 1
            widths[method["kind"]] = max(widths[method["kind"]], counters[method["kind"]])
    return widths


def build_workbook(contacts: list[dict[str, Any]]) -> Workbook:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Contacts"

    headers = [label for _, label in FIXED_COLUMNS]
    widths = _method_widths(contacts)
    for kind in models.METHOD_KINDS:
        for index in range(1, widths[kind] + 1):
            headers.append("%s %d" % (METHOD_HEADERS[kind], index))

    sheet.append(headers)
    for cell in sheet[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER

    for contact in contacts:
        row: list[Any] = [
            contact["name"],
            contact["company"],
            contact["title"],
            contact["notes"],
            "Yes" if contact["is_favorite"] else "No",
        ]
        buckets: dict[str, list[str]] = {kind: [] for kind in models.METHOD_KINDS}
        for method in contact["methods"]:
            text = method["value"]
            if method["label"]:
                text = "%s (%s)" % (text, method["label"])
            buckets[method["kind"]].append(text)
        for kind in models.METHOD_KINDS:
            cells = buckets[kind] + [""] * (widths[kind] - len(buckets[kind]))
            row.extend(cells)
        sheet.append(row)

    for column_index, header in enumerate(headers, start=1):
        letter = get_column_letter(column_index)
        sheet.column_dimensions[letter].width = max(12, min(46, len(header) + 12))
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = "A1:%s%d" % (
        get_column_letter(len(headers)),
        max(1, sheet.max_row),
    )
    return workbook


def export_bytes(contacts: list[dict[str, Any]]) -> bytes:
    workbook = build_workbook(contacts)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _parse_header(raw: Any):
    text = str(raw or "").strip().lower().replace("_", " ")
    if not text:
        return None
    if text in HEADER_ALIASES:
        return ("field", HEADER_ALIASES[text])
    match = METHOD_PATTERN.match(text)
    if match:
        return ("method", match.group(1))
    return None


def _flatten(value: Any) -> list[str]:
    """Split a cell into the individual entries it holds."""
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    parts = re.split(r"[;\n]+", text)
    return [part.strip() for part in parts if part.strip()]


def _split_entry(entry: str) -> tuple[str, str]:
    """Turn ``13800000000 (mobile)`` into value and label."""
    match = re.match(r"^(.*?)[\(\[]([^\)\]]+)[\)\]]\s*$", entry)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return entry, ""


def import_bytes(connection, payload: bytes) -> dict[str, Any]:
    """Read an Excel file and merge its rows into the address book."""
    try:
        workbook = load_workbook(io.BytesIO(payload), data_only=True)
    except Exception as error:  # noqa: BLE001 - any parser error is a user error
        raise models.ValidationError("The uploaded file is not a readable xlsx workbook.") from error

    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise models.ValidationError("The uploaded worksheet is empty.")

    column_map = []
    unknown = 0
    for raw in rows[0]:
        parsed = _parse_header(raw)
        column_map.append(parsed)
        if parsed is None:
            unknown += 1

    if not any(column_map):
        raise models.ValidationError(
            "No recognizable columns found. Export a file first and use it as a template."
        )

    result = {"imported": 0, "merged": 0, "skipped": 0, "columns_ignored": unknown}

    for row in rows[1:]:
        if row is None:
            result["skipped"] += 1
            continue
        fields: dict[str, Any] = {"name": "", "company": "", "title": "", "notes": "", "is_favorite": 0}
        methods: list[dict[str, str]] = []

        for index, parsed in enumerate(column_map):
            if parsed is None or index >= len(row):
                continue
            kind, name = parsed
            cell = row[index]
            if cell is None or (isinstance(cell, str) and not cell.strip()):
                continue
            if kind == "field":
                if name == "is_favorite":
                    fields["is_favorite"] = 1 if str(cell).strip().lower() in TRUTHY else 0
                else:
                    fields[name] = str(cell).strip()
            else:
                for entry in _flatten(cell):
                    value, label = _split_entry(entry)
                    if value:
                        methods.append({"kind": name, "label": label, "value": value})

        name = fields["name"].strip()
        if not name:
            result["skipped"] += 1
            continue

        existing = models.find_contact_by_name(connection, name)
        if existing is None:
            models.create_contact(
                connection,
                {
                    "name": name,
                    "company": fields["company"],
                    "title": fields["title"],
                    "notes": fields["notes"],
                    "is_favorite": bool(fields["is_favorite"]),
                    "methods": methods,
                },
            )
            result["imported"] += 1
            continue

        merged_methods = [
            {"kind": item["kind"], "label": item["label"], "value": item["value"]}
            for item in existing["methods"]
        ]
        existing_keys = {(item["kind"], item["value"]) for item in merged_methods}
        for method in methods:
            if (method["kind"], method["value"]) not in existing_keys:
                merged_methods.append(method)

        models.update_contact(
            connection,
            existing["id"],
            {
                "name": existing["name"],
                "company": existing["company"] or fields["company"],
                "title": existing["title"] or fields["title"],
                "notes": existing["notes"] or fields["notes"],
                "is_favorite": existing["is_favorite"] or bool(fields["is_favorite"]),
                "methods": merged_methods,
            },
        )
        result["merged"] += 1

    return result
