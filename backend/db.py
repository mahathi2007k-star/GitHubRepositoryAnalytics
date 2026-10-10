import os

import oracledb


def get_connection():
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN", "localhost:1521/xe")
    wallet_dir = os.getenv("ORACLE_WALLET_DIR")
    wallet_password = os.getenv("ORACLE_WALLET_PASSWORD")

    if not user or not password:
        raise RuntimeError(
            "Set ORACLE_USER and ORACLE_PASSWORD before starting the backend."
        )

    connect_options = {"user": user, "password": password, "dsn": dsn}
    if wallet_dir:
        if not wallet_password:
            raise RuntimeError(
                "Set ORACLE_WALLET_PASSWORD when using an Oracle wallet."
            )
        if not os.path.isdir(wallet_dir):
            raise RuntimeError("ORACLE_WALLET_DIR must point to the extracted Oracle wallet files.")
        connect_options.update({
            "config_dir": wallet_dir,
            "wallet_location": wallet_dir,
            "wallet_password": wallet_password,
        })

    return oracledb.connect(**connect_options)
