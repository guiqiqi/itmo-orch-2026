import os

import psycopg2


CREATE_NOTES_TABLE = """
CREATE TABLE IF NOT EXISTS notes (
    id UUID PRIMARY KEY,
    message TEXT NOT NULL CHECK (btrim(message) <> ''),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def main():
    connection = psycopg2.connect(
        host=os.environ["DATABASE_HOST"],
        port=int(os.environ["DATABASE_PORT"]),
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        connect_timeout=5,
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_NOTES_TABLE)
    finally:
        connection.close()

    print("Database initialization completed.")


if __name__ == "__main__":
    main()
