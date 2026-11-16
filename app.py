"""Flask application exposing the address book UI and its JSON API."""

from __future__ import annotations

import io

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import HTTPException

import excel_io
import models
from database import DEFAULT_DB_PATH, connect, init_db


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = str(DEFAULT_DB_PATH)
    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
    if test_config:
        app.config.update(test_config)

    init_db(app.config["DATABASE"])

    def get_db():
        return connect(app.config["DATABASE"])

    @app.errorhandler(models.ValidationError)
    def handle_validation_error(error):
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": error.description}), error.code

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    @app.get("/api/contacts")
    def list_contacts():
        keyword = request.args.get("q", "")
        favorite_only = request.args.get("favorite", "") in ("1", "true", "yes")
        connection = get_db()
        try:
            contacts = models.list_contacts(connection, keyword, favorite_only)
            stats = models.count_contacts(connection)
        finally:
            connection.close()
        return jsonify({"contacts": contacts, "stats": stats})

    @app.post("/api/contacts")
    def create_contact():
        connection = get_db()
        try:
            contact = models.create_contact(connection, request.get_json(silent=True) or {})
        finally:
            connection.close()
        return jsonify(contact), 201

    @app.put("/api/contacts/<int:contact_id>")
    def update_contact(contact_id: int):
        connection = get_db()
        try:
            if models.get_contact(connection, contact_id) is None:
                return jsonify({"error": "Contact not found."}), 404
            contact = models.update_contact(
                connection, contact_id, request.get_json(silent=True) or {}
            )
        finally:
            connection.close()
        return jsonify(contact)

    @app.delete("/api/contacts/<int:contact_id>")
    def delete_contact(contact_id: int):
        connection = get_db()
        try:
            deleted = models.delete_contact(connection, contact_id)
        finally:
            connection.close()
        if not deleted:
            return jsonify({"error": "Contact not found."}), 404
        return jsonify({"deleted": contact_id})

    @app.post("/api/contacts/<int:contact_id>/favorite")
    def toggle_favorite(contact_id: int):
        payload = request.get_json(silent=True) or {}
        favorite = payload.get("favorite")
        connection = get_db()
        try:
            contact = models.set_favorite(
                connection, contact_id, None if favorite is None else bool(favorite)
            )
        finally:
            connection.close()
        if contact is None:
            return jsonify({"error": "Contact not found."}), 404
        return jsonify(contact)

    @app.get("/api/export")
    def export_xlsx():
        connection = get_db()
        try:
            contacts = models.list_contacts(connection)
        finally:
            connection.close()
        content = excel_io.export_bytes(contacts)
        return send_file(
            io.BytesIO(content),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="contacts.xlsx",
        )

    @app.get("/api/template")
    def download_template():
        content = excel_io.export_bytes([])
        return send_file(
            io.BytesIO(content),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="contacts-template.xlsx",
        )

    @app.post("/api/import")
    def import_xlsx():
        upload = request.files.get("file")
        if upload is None or not upload.filename:
            return jsonify({"error": "Please choose an xlsx file to import."}), 400
        if not upload.filename.lower().endswith(".xlsx"):
            return jsonify({"error": "Only .xlsx workbooks are supported."}), 400
        connection = get_db()
        try:
            result = excel_io.import_bytes(connection, upload.read())
        finally:
            connection.close()
        return jsonify(result)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
