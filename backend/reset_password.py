"""Reset an application account password from a trusted local backend terminal."""

import argparse
import getpass
import sys

from werkzeug.security import generate_password_hash

from db import get_connection


def main():
    parser = argparse.ArgumentParser(
        description="Set a new password for an existing application account."
    )
    parser.add_argument("username", help="The application account username to reset.")
    args = parser.parse_args()
    username = args.username.strip().lower()
    if not username:
        parser.error("username cannot be blank")

    password = getpass.getpass("New password (minimum 8 characters): ")
    if len(password) < 8:
        parser.error("password must be at least 8 characters")
    confirmation = getpass.getpass("Confirm new password: ")
    if password != confirmation:
        parser.error("passwords do not match")

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE APP_ACCOUNT SET PASSWORD_HASH = :1 WHERE USERNAME = :2",
            (generate_password_hash(password), username),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            print("No application account found for {!r}.".format(username))
            return 1
        connection.commit()
        print("Password reset successfully for {!r}.".format(username))
        return 0
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    sys.exit(main())
