import os
from contextlib import contextmanager
from uuid import uuid4

import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor


app = Flask(__name__)


@contextmanager
def database_connection():
    connection = psycopg2.connect(
        host=os.environ["DATABASE_HOST"],
        port=int(os.environ["DATABASE_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    )

    try:
        yield connection
    finally:
        connection.close()


def serialize_note(note):
    return {
        "id": str(note["id"]),
        "message": note["message"],
        "created_at": note["created_at"].isoformat(),
    }


@app.get("/health")
def health():
    try:
        with database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
    except psycopg2.Error:
        app.logger.exception("Database health check failed.")
        return jsonify(status="unavailable", database="unavailable"), 503

    return jsonify(status="ok", database="ok"), 200


@app.get("/notes")
def get_notes():
    try:
        with database_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, message, created_at
                    FROM notes
                    ORDER BY created_at, id
                    """
                )
                notes = [serialize_note(note) for note in cursor.fetchall()]
    except psycopg2.Error:
        app.logger.exception("Could not read notes.")
        return jsonify(error="The database is unavailable."), 503

    return jsonify(notes=notes), 200


@app.post("/notes")
def create_note():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="The request body must be a JSON object."), 400

    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify(error="'message' must be a non-empty string."), 400

    try:
        with database_connection() as connection:
            with connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO notes (id, message)
                        VALUES (%s, %s)
                        RETURNING id, message, created_at
                        """,
                        (str(uuid4()), message.strip()),
                    )
                    note = serialize_note(cursor.fetchone())
    except psycopg2.Error:
        app.logger.exception("Could not create a note.")
        return jsonify(error="The database is unavailable."), 503

    return jsonify(note=note), 201


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
    )
