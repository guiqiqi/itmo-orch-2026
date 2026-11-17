import json
import os
import tempfile
import threading
import uuid
from pathlib import Path

from flask import Flask, jsonify, request


DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
NOTES_FILE = DATA_DIR / "notes.json"
NOTES_LOCK = threading.Lock()

app = Flask(__name__)


def load_notes():
    if not NOTES_FILE.exists():
        return []

    with NOTES_FILE.open("r", encoding="utf-8") as notes_file:
        return json.load(notes_file)


def save_notes(notes):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_path = tempfile.mkstemp(
        dir=DATA_DIR,
        prefix=".notes-",
        suffix=".json",
    )

    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as notes_file:
            json.dump(notes, notes_file, ensure_ascii=False, indent=2)
            notes_file.flush()
            os.fsync(notes_file.fileno())
        os.replace(temporary_path, NOTES_FILE)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/notes")
def get_notes():
    with NOTES_LOCK:
        return jsonify(notes=load_notes()), 200


@app.post("/notes")
def create_note():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="The request body must be a JSON object."), 400

    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify(error="'message' must be a non-empty string."), 400

    note = {
        "id": uuid.uuid4().hex,
        "message": message.strip(),
    }

    with NOTES_LOCK:
        notes = load_notes()
        notes.append(note)
        save_notes(notes)

    return jsonify(note=note), 201


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
    )
