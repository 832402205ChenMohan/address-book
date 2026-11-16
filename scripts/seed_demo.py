"""Insert a few sample contacts so the demo has something to show."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import models
from database import connect, init_db

SAMPLE_CONTACTS = [
    {
        "name": "Alice Chen",
        "company": "Fuzhou University",
        "title": "Course Coordinator",
        "notes": "Main contact for the Software Engineering module.",
        "is_favorite": True,
        "methods": [
            {"kind": "phone", "label": "mobile", "value": "13800000001"},
            {"kind": "email", "label": "work", "value": "alice.chen@example.edu"},
            {"kind": "wechat", "label": "", "value": "alice_chen_fzu"},
        ],
    },
    {
        "name": "Bob Liu",
        "company": "Maynooth University",
        "title": "Teaching Assistant",
        "notes": "Guides the Friday lab session.",
        "is_favorite": True,
        "methods": [
            {"kind": "phone", "label": "mobile", "value": "13800000002"},
            {"kind": "phone", "label": "office", "value": "0592-0000002"},
            {"kind": "email", "label": "work", "value": "bob.liu@example.edu"},
        ],
    },
    {
        "name": "Grace Wang",
        "company": "Logistics Lab",
        "title": "Project Partner",
        "notes": "Handles the Excel export review.",
        "is_favorite": False,
        "methods": [
            {"kind": "email", "label": "", "value": "grace.wang@example.com"},
            {"kind": "address", "label": "campus", "value": "Building 3, Room 502"},
        ],
    },
    {
        "name": "Daniel Xu",
        "company": "Cloud Services Ltd",
        "title": "Deployment Support",
        "notes": "Helped with the cloud server setup.",
        "is_favorite": False,
        "methods": [
            {"kind": "phone", "label": "work", "value": "13800000003"},
            {"kind": "wechat", "label": "", "value": "daniel_xu_cloud"},
            {"kind": "other", "label": "website", "value": "https://example.com/daniel"},
        ],
    },
    {
        "name": "Eva Lin",
        "company": "Student Union",
        "title": "Volunteer",
        "notes": "",
        "is_favorite": True,
        "methods": [
            {"kind": "phone", "label": "mobile", "value": "13800000004"},
            {"kind": "email", "label": "", "value": "eva.lin@example.com"},
        ],
    },
]


def main(database_path=None):
    init_db(database_path)
    connection = connect(database_path)
    try:
        created = 0
        for payload in SAMPLE_CONTACTS:
            if models.find_contact_by_name(connection, payload["name"]) is not None:
                continue
            models.create_contact(connection, payload)
            created += 1
    finally:
        connection.close()
    print("Sample contacts inserted: %d" % created)


if __name__ == "__main__":
    main()
