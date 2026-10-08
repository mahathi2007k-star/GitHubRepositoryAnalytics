from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection

app = Flask(__name__)
CORS(app)


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
                USER_ID,
                USERNAME,
                EMAIL,
                NAME,
                USER_TYPE,
                PROFILE_URL,
                LOCATION,
                CREATED_AT
            FROM GITHUB_USER
            ORDER BY USER_ID
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
                "created_at": str(row[7])
                    if row[7] else None
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

        # Generate the next user ID
        cursor.execute("""
            SELECT NVL(MAX(USER_ID), 0) + 1
            FROM GITHUB_USER
        """)
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO GITHUB_USER (
                USER_ID,
                USERNAME,
                EMAIL,
                USER_TYPE,
                CREATED_AT,
                PASSWORD_HASH
            )
            VALUES (
                :1,
                :2,
                :3,
                :4,
                SYSTIMESTAMP,
                :5
            )
        """, (
            user_id,
            username,
            email,
            "User",
            password_hash
        ))

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

        cursor.execute("""
            SELECT
                USER_ID,
                USERNAME,
                PASSWORD_HASH,
                USER_TYPE
            FROM GITHUB_USER
            WHERE USERNAME = :1
        """, (username,))

        row = cursor.fetchone()

        if row is None:
            return jsonify({
                "error": "Invalid username or password"
            }), 401

        user_id = row[0]
        db_username = row[1]
        password_hash = row[2]
        user_type = row[3]

        if not password_hash or not check_password_hash(
            password_hash,
            password
        ):
            return jsonify({
                "error": "Invalid username or password"
            }), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user_id,
            "username": db_username,
            "user_type": user_type
        }), 200

    except Exception:
        app.logger.exception("Database/API request failed")
        return jsonify({"error": "The request could not be completed."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
if __name__ == "__main__":
    app.run(debug=True)