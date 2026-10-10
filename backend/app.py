import os
import secrets
import hashlib
from datetime import timedelta

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from github_sync import GitHubSyncError, sync_github_repository
from password_recovery import RecoveryConfigurationError, make_reset_url, send_reset_email, validate_smtp_configuration

app = Flask(__name__)
production = os.getenv("APP_ENV", "").lower() == "production"
secret_key = os.getenv("FLASK_SECRET_KEY")
if production and not secret_key:
    raise RuntimeError("Set FLASK_SECRET_KEY before deploying.")
app.config.update(
    SECRET_KEY=secret_key or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=production,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
)
configured_origins = os.getenv("CORS_ORIGINS")
cors_origins = (
    [origin.strip() for origin in configured_origins.split(",") if origin.strip()]
    if configured_origins
    else [r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"]
)
CORS(app, origins=cors_origins, supports_credentials=True)


def parse_integer(value, field, minimum=0):
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a whole number.")
    raw = str(value).strip() if value is not None else ""
    if not raw.isdigit():
        raise ValueError(f"{field} must be a whole number.")
    parsed = int(raw)
    if parsed < minimum:
        raise ValueError(f"{field} must be at least {minimum}.")
    return parsed


def json_object():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


@app.before_request
def enforce_api_access():
    if request.method == "OPTIONS" or not request.path.startswith("/api/"):
        return None

    public_endpoints = {"login_user", "register_user", "logout_user", "request_password_reset", "complete_password_reset"}
    if request.endpoint in public_endpoints:
        return None

    if not session.get("account_id"):
        return jsonify({"error": "Authentication required."}), 401


    return None

@app.route("/")
def home():

    return "GitHub Repository Analytics Backend is Running!"


@app.route("/api/users")
def get_users():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                U.USER_ID,
                U.USERNAME,
                U.EMAIL,
                U.NAME,
                U.USER_TYPE,
                U.PROFILE_URL,
                U.LOCATION,
                U.CREATED_AT,
                NVL((
                    SELECT SUM(C.CONTRIBUTIONS)
                    FROM CONTRIBUTES_TO C
                    WHERE C.USER_ID = U.USER_ID
                ), 0) AS CONTRIBUTIONS,
                (
                    SELECT COUNT(DISTINCT C.REPOSITORY_ID)
                    FROM CONTRIBUTES_TO C
                    WHERE C.USER_ID = U.USER_ID
                ) AS REPOSITORIES_CONTRIBUTED,
                (
                    SELECT COUNT(*)
                    FROM GIT_COMMIT C
                    WHERE C.AUTHOR_ID = U.USER_ID
                ) AS COMMITS_AUTHORED,
                (
                    SELECT COUNT(*)
                    FROM ISSUE I
                    WHERE I.CREATOR_ID = U.USER_ID
                ) AS ISSUES_OPENED,
                (
                    SELECT COUNT(*)
                    FROM PULL_REQUEST P
                    WHERE P.CREATOR_ID = U.USER_ID
                ) AS PULL_REQUESTS_OPENED
            FROM GITHUB_USER U
            ORDER BY U.USER_ID
        """)

        rows = cursor.fetchall()
        users = []
        for row in rows:
            users.append({
                "user_id": row[0],
                "username": row[1],
                "email": row[2],
                "name": row[3],
                "user_type": row[4],
                "profile_url": row[5],
                "location": row[6],
                "created_at": str(row[7]) if row[7] else None,
                "contributions": row[8],
                "repositories_contributed": row[9],
                "commits_authored": row[10],
                "issues_opened": row[11],
                "pull_requests_opened": row[12]
            })

        return jsonify(users)

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
@app.route("/api/repositories")
def get_repositories():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                REPOSITORY_ID,
                NAME,
                FULL_NAME,
                STARS,
                FORKS,
                OPEN_ISSUES,
                CREATED_AT
            FROM REPOSITORY
            ORDER BY REPOSITORY_ID
        """)

        rows = cursor.fetchall()

        repositories = []

        for row in rows:

            repositories.append({
                "repository_id": row[0],
                "name": row[1],
                "full_name": row[2],
                "stars": row[3],
                "forks": row[4],
                "open_issues": row[5],
                "created_at": str(row[6])
                    if row[6] else None
            })

        return jsonify(repositories)

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
@app.route("/api/issues")
def get_issues():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
    SELECT
        ISSUE_ID,
        TITLE,
        STATE,
        CREATED_AT,
        CLOSED_AT,
        CREATOR_ID,
        REPOSITORY_ID
    FROM ISSUE
    ORDER BY ISSUE_ID
""")

        rows = cursor.fetchall()

        issues = []

        for row in rows:

            issues.append({
    "issue_id": row[0],
    "title": row[1],
    "state": row[2],
    "created_at": str(row[3])
        if row[3] else None,
    "closed_at": str(row[4])
        if row[4] else None,
    "creator_id": row[5],
    "repository_id": row[6]
})

        return jsonify(issues)

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
@app.route("/api/pull-requests")
def get_pull_requests():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                PR_ID,
                TITLE,
                STATE,
                CREATED_AT,
                MERGED_AT,
                CREATOR_ID,
                REPOSITORY_ID
            FROM PULL_REQUEST
            ORDER BY PR_ID
        """)

        rows = cursor.fetchall()

        pull_requests = []

        for row in rows:

            pull_requests.append({
                "pr_id": row[0],
                "title": row[1],
                "state": row[2],
                "created_at": str(row[3])
                    if row[3] else None,
                "merged_at": str(row[4])
                    if row[4] else None,
                "creator_id": row[5],
                "repository_id": row[6]
            })

        return jsonify(pull_requests)

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
@app.route("/api/commits")
def get_commits():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COMMIT_ID,
                COMMIT_MESSAGE,
                COMMIT_DATE,
                AUTHOR_ID,
                REPOSITORY_ID
            FROM GIT_COMMIT
            ORDER BY COMMIT_DATE DESC
        """)

        rows = cursor.fetchall()

        commits = []

        for row in rows:

            commits.append({
                "commit_id": row[0],
                "commit_message": row[1],
                "commit_date": str(row[2])
                    if row[2] else None,
                "author_id": row[3],
                "repository_id": row[4]
            })

        return jsonify(commits)

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
@app.route("/api/languages")
def get_languages():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                LANGUAGE_ID,
                LANGUAGE_NAME
            FROM LANGUAGE
            ORDER BY LANGUAGE_ID
        """)

        rows = cursor.fetchall()

        languages = []

        for row in rows:
            languages.append({
                "language_id": row[0],
                "language_name": row[1]
            })

        return jsonify(languages)

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

@app.route("/api/dashboard-stats")
def get_dashboard_stats():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM GITHUB_USER),
                (SELECT COUNT(*) FROM REPOSITORY),
                (SELECT COUNT(*) FROM ISSUE),
                (SELECT COUNT(*) FROM PULL_REQUEST),
                (SELECT COUNT(*) FROM GIT_COMMIT),
                (SELECT COUNT(*) FROM LANGUAGE)
            FROM DUAL
        """)

        row = cursor.fetchone()

        stats = {
            "users": row[0],
            "repositories": row[1],
            "issues": row[2],
            "pull_requests": row[3],
            "commits": row[4],
            "languages": row[5]
        }

        return jsonify(stats)

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
@app.route("/api/analytics")
def get_analytics():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Total stars and forks
        cursor.execute("""
            SELECT
                NVL(SUM(STARS), 0),
                NVL(SUM(FORKS), 0)
            FROM REPOSITORY
        """)

        repository_stats = cursor.fetchone()

        total_stars = repository_stats[0]
        total_forks = repository_stats[1]


        # Open and closed issues
        cursor.execute("""
            SELECT
                NVL(SUM(
                    CASE
                        WHEN LOWER(STATE) = 'open' THEN 1
                        ELSE 0
                    END
                ), 0),
                NVL(SUM(
                    CASE
                        WHEN LOWER(STATE) = 'closed' THEN 1
                        ELSE 0
                    END
                ), 0)
            FROM ISSUE
        """)

        issue_stats = cursor.fetchone()

        open_issues = issue_stats[0]
        closed_issues = issue_stats[1]


        # Open and merged pull requests
        cursor.execute("""
            SELECT
                NVL(SUM(
                    CASE
                        WHEN LOWER(STATE) = 'open' THEN 1
                        ELSE 0
                    END
                ), 0),
                NVL(SUM(
                    CASE
                        WHEN MERGED_AT IS NOT NULL THEN 1
                        ELSE 0
                    END
                ), 0)
            FROM PULL_REQUEST
        """)

        pull_request_stats = cursor.fetchone()

        open_pull_requests = pull_request_stats[0]
        merged_pull_requests = pull_request_stats[1]


        # Total contributions
        cursor.execute("""
            SELECT NVL(SUM(CONTRIBUTIONS), 0)
            FROM CONTRIBUTES_TO
        """)

        total_contributions = cursor.fetchone()[0]


        analytics = {
            "total_stars": total_stars,
            "total_forks": total_forks,
            "open_issues": open_issues,
            "closed_issues": closed_issues,
            "open_pull_requests": open_pull_requests,
            "merged_pull_requests": merged_pull_requests,
            "total_contributions": total_contributions
        }

        return jsonify(analytics)


    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500


    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

@app.route("/api/github/sync", methods=["POST"])
def sync_github_data():
    data = json_object()
    if data is None:
        return jsonify({"error": "A JSON object is required."}), 400

    try:
        result = sync_github_repository(data.get("full_name"))
        return jsonify({
            "message": "GitHub repository data synchronized successfully.",
            **result,
        }), 200
    except GitHubSyncError as error:
        return jsonify({"error": str(error)}), error.status_code
    except Exception:
        app.logger.exception("GitHub repository synchronization failed")
        return jsonify({"error": "Synchronization failed while saving data to Oracle."}), 500


@app.route("/api/repositories", methods=["POST"])
def add_repository():
    connection = None
    cursor = None

    try:
        data = json_object()
        if data is None:
            return jsonify({"error": "A JSON object is required."}), 400

        try:
            repository_id = parse_integer(data.get("repository_id"), "Repository ID", 1)
            owner_id = parse_integer(data.get("owner_id"), "Owner ID", 1)
            stars = parse_integer(data.get("stars", 0), "Stars")
            forks = parse_integer(data.get("forks", 0), "Forks")
            open_issues = parse_integer(data.get("open_issues", 0), "Open issues")
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        name = data.get("name")
        full_name = data.get("full_name")
        description = data.get("description")
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Repository name is required."}), 400
        if not isinstance(full_name, str) or not full_name.strip():
            return jsonify({"error": "Full repository name is required."}), 400
        if description is not None and not isinstance(description, str):
            return jsonify({"error": "Description must be text."}), 400
        name = name.strip()
        full_name = full_name.strip()

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO REPOSITORY (
                REPOSITORY_ID,
                NAME,
                FULL_NAME,
                DESCRIPTION,
                STARS,
                FORKS,
                OPEN_ISSUES,
                OWNER_ID
            )
            VALUES (
                :1, :2, :3, :4, :5, :6, :7, :8
            )
        """, (
            repository_id,
            name,
            full_name,
            description,
            stars,
            forks,
            open_issues,
            owner_id
        ))

        connection.commit()

        return jsonify({
            "message": "Repository added successfully"
        }), 201

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
@app.route("/api/repositories/search", methods=["GET"])
def search_repositories():
    connection = None
    cursor = None

    try:
        name = request.args.get("name", "").strip()
        if not name:
            return jsonify({"error": "Enter a repository name to search."}), 400

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                REPOSITORY_ID,
                NAME,
                FULL_NAME,
                STARS,
                FORKS,
                OPEN_ISSUES,
                OWNER_ID
            FROM REPOSITORY
            WHERE LOWER(NAME) LIKE LOWER(:1)
            ORDER BY REPOSITORY_ID
        """, (f"%{name}%",))

        rows = cursor.fetchall()

        repositories = []

        for row in rows:
            repositories.append({
                "repository_id": row[0],
                "name": row[1],
                "full_name": row[2],
                "stars": row[3],
                "forks": row[4],
                "open_issues": row[5],
                "owner_id": row[6]
            })

        return jsonify(repositories), 200

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
@app.route("/api/repositories/<int:repository_id>", methods=["GET"])
def fetch_repository(repository_id):
    connection = None
    cursor = None

    try:
        if repository_id < 1:
            return jsonify({"error": "Repository ID must be a positive integer."}), 400

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                REPOSITORY_ID,
                NAME,
                FULL_NAME,
                DESCRIPTION,
                STARS,
                FORKS,
                OPEN_ISSUES,
                OWNER_ID
            FROM REPOSITORY
            WHERE REPOSITORY_ID = :1
        """, (repository_id,))

        row = cursor.fetchone()

        if row is None:
            return jsonify({
                "error": "Repository not found"
            }), 404

        repository = {
            "repository_id": row[0],
            "name": row[1],
            "full_name": row[2],
            "description": row[3],
            "stars": row[4],
            "forks": row[5],
            "open_issues": row[6],
            "owner_id": row[7]
        }

        return jsonify(repository), 200

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
# ================================
# PART C - UPDATE REPOSITORY
# ================================
@app.route("/api/repositories/<int:repository_id>", methods=["PUT"])
def update_repository(repository_id):
    connection = None
    cursor = None

    try:
        if repository_id < 1:
            return jsonify({"error": "Repository ID must be a positive integer."}), 400

        data = json_object()
        if data is None:
            return jsonify({"error": "A JSON object is required."}), 400

        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Repository name is required."}), 400
        try:
            stars = parse_integer(data.get("stars"), "Stars")
            forks = parse_integer(data.get("forks"), "Forks")
            open_issues = parse_integer(data.get("open_issues"), "Open issues")
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        name = name.strip()

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE REPOSITORY
            SET
                NAME = :1,
                STARS = :2,
                FORKS = :3,
                OPEN_ISSUES = :4
            WHERE REPOSITORY_ID = :5
        """, (
            name,
            stars,
            forks,
            open_issues,
            repository_id
        ))

        if cursor.rowcount == 0:
            return jsonify({"error": "Repository not found"}), 404

        connection.commit()

        return jsonify({
            "message": "Repository updated successfully"
        }), 200

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
# ================================
# PART C - DELETE REPOSITORY
# ================================
@app.route("/api/repositories/<int:repository_id>", methods=["DELETE"])
def delete_repository(repository_id):
    connection = None
    cursor = None

    try:
        if repository_id < 1:
            return jsonify({"error": "Repository ID must be a positive integer."}), 400

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM REPOSITORY
            WHERE REPOSITORY_ID = :1
        """, (repository_id,))

        if cursor.rowcount == 0:
            return jsonify({"error": "Repository not found"}), 404

        connection.commit()

        return jsonify({
            "message": "Repository deleted successfully"
        }), 200

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
# ================================
# USER REGISTRATION
# ================================
@app.route("/api/register", methods=["POST"])
def register_user():
    connection = None
    cursor = None

    try:
        data = json_object()
        if data is None:
            return jsonify({"error": "A JSON object is required."}), 400

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        if not isinstance(username, str) or not username.strip():
            return jsonify({"error": "Username is required."}), 400
        if len(username.strip()) > 50:
            return jsonify({"error": "Username must be 50 characters or fewer."}), 400
        if not isinstance(email, str) or "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            return jsonify({"error": "Enter a valid email address."}), 400
        if len(email.strip()) > 255:
            return jsonify({"error": "Email must be 255 characters or fewer."}), 400
        if not isinstance(password, str) or len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long."}), 400

        username = username.strip()
        email = email.strip()
        password_hash = generate_password_hash(password)

        connection = get_connection()
        cursor = connection.cursor()

        username = username.lower()
        email = email.lower()

        cursor.execute("""
            SELECT COUNT(*)
            FROM APP_ACCOUNT
            WHERE USERNAME = :1 OR EMAIL = :2
        """, (username, email))
        if cursor.fetchone()[0]:
            return jsonify({"error": "That username or email is already registered."}), 409

        cursor.execute("""
            INSERT INTO APP_ACCOUNT (
                USERNAME,
                EMAIL,
                PASSWORD_HASH,
                ROLE,
                CREATED_AT
            )
            VALUES (:1, :2, :3, 'USER', SYSTIMESTAMP)
        """, (username, email, password_hash))

        connection.commit()

        return jsonify({
            "message": "Registration successful"
        }), 201

    except Exception:
        if connection:
            connection.rollback()
        app.logger.exception("Registration request failed")
        return jsonify({"error": "Registration could not be completed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
# ================================
# USER LOGIN
# ================================
@app.route("/api/password/forgot", methods=["POST"])
def request_password_reset():
    data = json_object()
    email = data.get("email") if data else None
    if not isinstance(email, str) or not email.strip() or len(email.strip()) > 255:
        return jsonify({"error": "Enter the email address for your account."}), 400

    generic_response = {
        "message": "If an account matches that email and recovery email is configured, a reset link will be sent."
    }
    try:
        make_reset_url(request, "configuration-check", data.get("reset_page_url"))
        validate_smtp_configuration()
    except RecoveryConfigurationError as error:
        return jsonify({"error": str(error)}), 503

    connection = None
    cursor = None
    try:
        email = email.strip().lower()
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT ACCOUNT_ID, USERNAME, EMAIL FROM APP_ACCOUNT WHERE EMAIL = :1",
            (email,),
        )
        account = cursor.fetchone()
        if account:
            reset_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(reset_token.encode("utf-8")).hexdigest()
            reset_url = make_reset_url(request, reset_token, data.get("reset_page_url"))
            cursor.execute("""
                SELECT COUNT(*) FROM APP_PASSWORD_RESET
                WHERE ACCOUNT_ID = :1
                  AND CREATED_AT > SYSTIMESTAMP - INTERVAL '1' MINUTE
            """, (account[0],))
            if cursor.fetchone()[0] > 0:
                connection.rollback()
                return jsonify(generic_response), 202
            cursor.execute("DELETE FROM APP_PASSWORD_RESET WHERE ACCOUNT_ID = :1", (account[0],))
            cursor.execute("""
                INSERT INTO APP_PASSWORD_RESET (TOKEN_HASH, ACCOUNT_ID, EXPIRES_AT)
                VALUES (:1, :2, SYSTIMESTAMP + INTERVAL '30' MINUTE)
            """, (token_hash, account[0]))
            send_reset_email(account[2], account[1], reset_url)
            connection.commit()
        else:
            connection.rollback()
        return jsonify(generic_response), 202
    except Exception:
        if connection:
            connection.rollback()
        app.logger.exception("Password-reset email could not be sent")
        return jsonify(generic_response), 202
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route("/api/password/reset", methods=["POST"])
def complete_password_reset():
    data = json_object()
    if data is None:
        return jsonify({"error": "A JSON object is required."}), 400
    token = data.get("token")
    password = data.get("password")
    if not isinstance(token, str) or not token or len(token) > 256:
        return jsonify({"error": "This reset link is invalid or expired."}), 400
    if not isinstance(password, str) or len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long."}), 400

    connection = None
    cursor = None
    try:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ACCOUNT_ID
            FROM APP_PASSWORD_RESET
            WHERE TOKEN_HASH = :1 AND EXPIRES_AT > SYSTIMESTAMP
            FOR UPDATE
        """, (token_hash,))
        row = cursor.fetchone()
        if not row:
            connection.rollback()
            return jsonify({"error": "This reset link is invalid or expired."}), 400

        account_id = row[0]
        password_hash = generate_password_hash(password)
        cursor.execute(
            "UPDATE APP_ACCOUNT SET PASSWORD_HASH = :1 WHERE ACCOUNT_ID = :2",
            (password_hash, account_id),
        )
        cursor.execute("DELETE FROM APP_PASSWORD_RESET WHERE ACCOUNT_ID = :1", (account_id,))
        connection.commit()
        return jsonify({"message": "Password reset successfully. You can now log in."}), 200
    except Exception:
        if connection:
            connection.rollback()
        app.logger.exception("Password reset failed")
        return jsonify({"error": "Password reset could not be completed."}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/api/login", methods=["POST"])
def login_user():
    connection = None
    cursor = None

    try:
        data = json_object()
        if data is None:
            return jsonify({"error": "A JSON object is required."}), 400

        username = data.get("username")
        password = data.get("password")
        if not isinstance(username, str) or not username.strip():
            return jsonify({"error": "Username is required."}), 400
        if not isinstance(password, str) or not password:
            return jsonify({"error": "Password is required."}), 400
        username = username.strip()

        connection = get_connection()
        cursor = connection.cursor()

        username = username.lower()
        cursor.execute("""
            SELECT
                ACCOUNT_ID,
                USERNAME,
                PASSWORD_HASH,
                ROLE
            FROM APP_ACCOUNT
            WHERE USERNAME = :1
        """, (username,))

        row = cursor.fetchone()

        if row is None:
            return jsonify({
                "error": "Invalid username or password"
            }), 401

        account_id = row[0]
        db_username = row[1]
        password_hash = row[2]
        role = row[3]

        if not password_hash or not check_password_hash(
            password_hash,
            password
        ):
            return jsonify({
                "error": "Invalid username or password"
            }), 401

        session.clear()
        session.permanent = True
        session["account_id"] = account_id
        session["username"] = db_username
        session["role"] = role

        return jsonify({
            "message": "Login successful",
            "account_id": account_id,
            "username": db_username,
            "role": role
        }), 200

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/api/logout", methods=["POST"])
def logout_user():
    session.clear()
    return jsonify({"message": "Logged out."}), 200


@app.route("/api/me")
def current_account():
    return jsonify({
        "account_id": session.get("account_id"),
        "username": session.get("username"),
        "role": session.get("role")
    }), 200

if __name__ == "__main__":
    app.run(debug=not production)
