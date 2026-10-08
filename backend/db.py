import os

import oracledb


def get_connection():
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN", "localhost:1521/xe")

    if not user or not password:
        raise RuntimeError(
            "Set ORACLE_USER and ORACLE_PASSWORD before starting the backend."
        )

    return oracledb.connect(user=user, password=password, dsn=dsn)