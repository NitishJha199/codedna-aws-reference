import os
from pathlib import Path

import psycopg


SQL_FILE = Path("/app/database/init.sql")


def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_host = os.getenv("DB_HOST")
    if not db_host:
        raise RuntimeError("DATABASE_URL or DB_HOST must be configured")

    return (
        f"postgresql://{os.getenv('DB_USER', 'codedna')}:"
        f"{os.environ['DB_PASSWORD']}@"
        f"{db_host}:{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'referenceapp')}"
    )


def main():
    sql = SQL_FILE.read_text(encoding="utf-8")

    with psycopg.connect(get_database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        connection.commit()

    print("Database schema initialized successfully")


if __name__ == "__main__":
    main()
