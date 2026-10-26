"""PostgreSQL connection for the hosted demo deployment."""

import os
import psycopg


def get_connection():
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError("Set DATABASE_URL to the PostgreSQL connection string before starting the backend.")
    return psycopg.connect(database_url, sslmode=os.getenv("PGSSLMODE", "require"))
