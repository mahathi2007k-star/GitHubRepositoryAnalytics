import argparse
import sys

from db import get_connection


def main():
    parser = argparse.ArgumentParser(
        description="Promote an existing application account to administrator."
    )
    parser.add_argument("username", help="The application account username to promote.")
    args = parser.parse_args()
    username = args.username.strip().lower()
    if not username:
        parser.error("username cannot be blank")

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE APP_ACCOUNT SET ROLE = 'ADMIN' WHERE USERNAME = :1",
            (username,),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            print(f"No application account found for {username!r}. Register first.")
            return 1
        connection.commit()
        print(f"{username!r} is now an administrator.")
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
