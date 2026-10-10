"""Import public GitHub repository data into the project's Oracle tables."""

import json
import os
import re
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from db import get_connection

API_ROOT = "https://api.github.com"
MAX_PAGES = 5
PAGE_SIZE = 100


class GitHubSyncError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def parse_github_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except (AttributeError, ValueError):
        return None


def github_request(url, token):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "GitHubRepositoryAnalytics/1.0",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        try:
            details = json.loads(error.read().decode("utf-8")).get("message", "")
        except (ValueError, AttributeError):
            details = ""
        if error.code == 404:
            raise GitHubSyncError("Repository not found or not accessible. Check owner/repository spelling.", 404)
        if error.code == 401:
            raise GitHubSyncError("GitHub rejected the configured token. Check GITHUB_TOKEN.", 502)
        if error.code in {403, 429}:
            if "rate limit" in details.lower():
                raise GitHubSyncError("GitHub API rate limit reached. Wait or configure a GitHub token.", 429)
            raise GitHubSyncError("GitHub denied this request. The repository may be private or inaccessible.", 502)
        raise GitHubSyncError("GitHub API request failed (HTTP {}).".format(error.code), 502)
    except (URLError, TimeoutError, OSError):
        raise GitHubSyncError("Could not connect to GitHub. Check your internet connection and try again.", 502)
    except (ValueError, UnicodeDecodeError):
        raise GitHubSyncError("GitHub returned an unreadable response.", 502)


def fetch_pages(path, token, params=None):
    records = []
    truncated = False
    for page in range(1, MAX_PAGES + 1):
        query = dict(params or {})
        query.update({"per_page": PAGE_SIZE, "page": page})
        url = API_ROOT + path + "?" + urlencode(query)
        batch = github_request(url, token)
        if not isinstance(batch, list):
            raise GitHubSyncError("GitHub returned an unexpected list response.")
        records.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        if page == MAX_PAGES:
            truncated = True
    return records, truncated


def user_record(user):
    if not isinstance(user, dict) or not user.get("id") or not user.get("login"):
        return None
    try:
        user_id = int(user["id"])
    except (ValueError, TypeError):
        return None
    return {
        "user_id": user_id,
        "username": str(user["login"])[:100],
        "user_type": str(user.get("type") or "User")[:30],
        "profile_url": str(user.get("html_url") or "")[:500] or None,
    }


def upsert_users(cursor, users):
    statement = """
        MERGE INTO GITHUB_USER target
        USING (SELECT :user_id USER_ID, :username USERNAME,
                      :user_type USER_TYPE, :profile_url PROFILE_URL FROM DUAL) source
        ON (target.USER_ID = source.USER_ID)
        WHEN MATCHED THEN UPDATE SET
            target.USERNAME = source.USERNAME,
            target.USER_TYPE = NVL(source.USER_TYPE, target.USER_TYPE),
            target.PROFILE_URL = NVL(source.PROFILE_URL, target.PROFILE_URL)
        WHEN NOT MATCHED THEN INSERT
            (USER_ID, USERNAME, USER_TYPE, PROFILE_URL)
            VALUES (source.USER_ID, source.USERNAME, source.USER_TYPE, source.PROFILE_URL)
    """
    if users:
        cursor.executemany(statement, list(users.values()))


def merge_repository(cursor, repository, owner_id):
    cursor.execute("""
        MERGE INTO REPOSITORY target
        USING (SELECT :repository_id REPOSITORY_ID FROM DUAL) source
        ON (target.REPOSITORY_ID = source.REPOSITORY_ID)
        WHEN MATCHED THEN UPDATE SET
            target.NAME = :name,
            target.FULL_NAME = :full_name,
            target.DESCRIPTION = :description,
            target.STARS = :stars,
            target.FORKS = :forks,
            target.OPEN_ISSUES = :open_issues,
            target.CREATED_AT = :created_at,
            target.UPDATED_AT = :updated_at,
            target.OWNER_ID = :owner_id
        WHEN NOT MATCHED THEN INSERT
            (REPOSITORY_ID, NAME, FULL_NAME, DESCRIPTION, STARS, FORKS,
             OPEN_ISSUES, CREATED_AT, UPDATED_AT, OWNER_ID)
            VALUES (:repository_id, :name, :full_name, :description, :stars, :forks,
                    :open_issues, :created_at, :updated_at, :owner_id)
    """, {
        "repository_id": int(repository["id"]),
        "name": str(repository.get("name") or "")[:255],
        "full_name": str(repository.get("full_name") or "")[:500],
        "description": (repository.get("description") or "")[:4000] or None,
        "stars": int(repository.get("stargazers_count") or 0),
        "forks": int(repository.get("forks_count") or 0),
        "open_issues": int(repository.get("open_issues_count") or 0),
        "created_at": parse_github_datetime(repository.get("created_at")),
        "updated_at": parse_github_datetime(repository.get("updated_at")),
        "owner_id": owner_id,
    })


def upsert_contributions(cursor, rows):
    if not rows:
        return
    cursor.executemany("""
        MERGE INTO CONTRIBUTES_TO target
        USING (SELECT :user_id USER_ID, :repository_id REPOSITORY_ID,
                      :contributions CONTRIBUTIONS FROM DUAL) source
        ON (target.USER_ID = source.USER_ID AND target.REPOSITORY_ID = source.REPOSITORY_ID)
        WHEN MATCHED THEN UPDATE SET target.CONTRIBUTIONS = source.CONTRIBUTIONS
        WHEN NOT MATCHED THEN INSERT (USER_ID, REPOSITORY_ID, CONTRIBUTIONS)
            VALUES (source.USER_ID, source.REPOSITORY_ID, source.CONTRIBUTIONS)
    """, rows)


def upsert_commits(cursor, rows):
    if not rows:
        return
    cursor.executemany("""
        MERGE INTO GIT_COMMIT target
        USING (SELECT :commit_id COMMIT_ID FROM DUAL) source
        ON (target.COMMIT_ID = source.COMMIT_ID)
        WHEN MATCHED THEN UPDATE SET
            target.COMMIT_MESSAGE = :message,
            target.COMMIT_DATE = :commit_date,
            target.AUTHOR_ID = :author_id,
            target.REPOSITORY_ID = :repository_id
        WHEN NOT MATCHED THEN INSERT
            (COMMIT_ID, COMMIT_MESSAGE, COMMIT_DATE, AUTHOR_ID, REPOSITORY_ID)
            VALUES (:commit_id, :message, :commit_date, :author_id, :repository_id)
    """, rows)


def upsert_issues(cursor, rows):
    if not rows:
        return
    cursor.executemany("""
        MERGE INTO ISSUE target
        USING (SELECT :issue_id ISSUE_ID FROM DUAL) source
        ON (target.ISSUE_ID = source.ISSUE_ID)
        WHEN MATCHED THEN UPDATE SET
            target.TITLE = :title,
            target.STATE = :state,
            target.CREATED_AT = :created_at,
            target.CLOSED_AT = :closed_at,
            target.CREATOR_ID = :creator_id,
            target.REPOSITORY_ID = :repository_id
        WHEN NOT MATCHED THEN INSERT
            (ISSUE_ID, TITLE, STATE, CREATED_AT, CLOSED_AT, CREATOR_ID, REPOSITORY_ID)
            VALUES (:issue_id, :title, :state, :created_at, :closed_at, :creator_id, :repository_id)
    """, rows)


def upsert_pull_requests(cursor, rows):
    if not rows:
        return
    cursor.executemany("""
        MERGE INTO PULL_REQUEST target
        USING (SELECT :pr_id PR_ID FROM DUAL) source
        ON (target.PR_ID = source.PR_ID)
        WHEN MATCHED THEN UPDATE SET
            target.TITLE = :title,
            target.STATE = :state,
            target.CREATED_AT = :created_at,
            target.MERGED_AT = :merged_at,
            target.CREATOR_ID = :creator_id,
            target.REPOSITORY_ID = :repository_id
        WHEN NOT MATCHED THEN INSERT
            (PR_ID, TITLE, STATE, CREATED_AT, MERGED_AT, CREATOR_ID, REPOSITORY_ID)
            VALUES (:pr_id, :title, :state, :created_at, :merged_at, :creator_id, :repository_id)
    """, rows)


def sync_github_repository(full_name):
    if not isinstance(full_name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", full_name.strip()):
        raise GitHubSyncError("Enter a repository as owner/repository.", 400)

    owner, repo_name = full_name.strip().split("/", 1)
    repo_path = "/repos/{}/{}".format(quote(owner, safe=""), quote(repo_name, safe=""))
    token = os.getenv("GITHUB_TOKEN")
    repo = github_request(API_ROOT + repo_path, token)
    owner_row = user_record(repo.get("owner"))
    if not owner_row:
        raise GitHubSyncError("GitHub did not provide a valid repository owner.")
    repository_id = int(repo["id"])
    owner_id = owner_row["user_id"]

    languages = github_request(API_ROOT + repo_path + "/languages", token)
    if not isinstance(languages, dict):
        raise GitHubSyncError("GitHub returned an unexpected languages response.")
    contributors, contributors_truncated = fetch_pages(repo_path + "/contributors", token, {"anon": "false"})
    commits, commits_truncated = fetch_pages(repo_path + "/commits", token)
    issue_items, issues_truncated = fetch_pages(
        repo_path + "/issues", token,
        {"state": "all", "sort": "created", "direction": "desc"},
    )
    pull_requests, prs_truncated = fetch_pages(
        repo_path + "/pulls", token,
        {"state": "all", "sort": "created", "direction": "desc"},
    )

    users = {owner_id: owner_row}
    contribution_rows = []
    for contributor in contributors:
        user = user_record(contributor)
        if user:
            users[user["user_id"]] = user
            contribution_rows.append({
                "user_id": user["user_id"],
                "repository_id": repository_id,
                "contributions": int(contributor.get("contributions") or 0),
            })

    commit_rows = []
    for item in commits:
        author = user_record(item.get("author"))
        commit = item.get("commit") or {}
        if not author or not item.get("sha"):
            continue
        users[author["user_id"]] = author
        commit_rows.append({
            "commit_id": str(item["sha"])[:40],
            "message": str(commit.get("message") or "")[:4000],
            "commit_date": parse_github_datetime((commit.get("author") or {}).get("date")),
            "author_id": author["user_id"],
            "repository_id": repository_id,
        })

    issue_rows = []
    for item in issue_items:
        if item.get("pull_request"):
            continue
        creator = user_record(item.get("user"))
        if not creator or not item.get("id") or not item.get("created_at"):
            continue
        users[creator["user_id"]] = creator
        issue_rows.append({
            "issue_id": int(item["id"]),
            "title": str(item.get("title") or "")[:500],
            "state": str(item.get("state") or "open")[:20],
            "created_at": parse_github_datetime(item.get("created_at")),
            "closed_at": parse_github_datetime(item.get("closed_at")),
            "creator_id": creator["user_id"],
            "repository_id": repository_id,
        })

    pull_request_rows = []
    for item in pull_requests:
        creator = user_record(item.get("user"))
        if not creator or not item.get("id") or not item.get("created_at"):
            continue
        users[creator["user_id"]] = creator
        pull_request_rows.append({
            "pr_id": int(item["id"]),
            "title": str(item.get("title") or "")[:500],
            "state": str(item.get("state") or "open")[:20],
            "created_at": parse_github_datetime(item.get("created_at")),
            "merged_at": parse_github_datetime(item.get("merged_at")),
            "creator_id": creator["user_id"],
            "repository_id": repository_id,
        })

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT FULL_NAME FROM REPOSITORY WHERE REPOSITORY_ID = :1", (repository_id,))
        existing_repository = cursor.fetchone()
        incoming_full_name = str(repo.get("full_name") or full_name.strip())
        if existing_repository and existing_repository[0] and existing_repository[0].casefold() != incoming_full_name.casefold():
            raise GitHubSyncError(
                "This GitHub repository ID is already attached to a different repository record. Resolve that ID conflict first.",
                409,
            )

        cursor.execute("LOCK TABLE LANGUAGE IN EXCLUSIVE MODE")
        cursor.execute("SELECT LANGUAGE_ID, LANGUAGE_NAME FROM LANGUAGE")
        existing_languages = {str(name).casefold() for _, name in cursor.fetchall() if name}
        cursor.execute("SELECT NVL(MAX(LANGUAGE_ID), 0) FROM LANGUAGE")
        next_language_id = int(cursor.fetchone()[0]) + 1
        inserted_languages = 0
        for language in sorted(languages):
            if language.casefold() in existing_languages:
                continue
            cursor.execute(
                "INSERT INTO LANGUAGE (LANGUAGE_ID, LANGUAGE_NAME) VALUES (:1, :2)",
                (next_language_id, language[:100]),
            )
            existing_languages.add(language.casefold())
            next_language_id += 1
            inserted_languages += 1

        upsert_users(cursor, users)
        merge_repository(cursor, repo, owner_id)
        upsert_contributions(cursor, contribution_rows)
        upsert_commits(cursor, commit_rows)
        upsert_issues(cursor, issue_rows)
        upsert_pull_requests(cursor, pull_request_rows)
        connection.commit()
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return {
        "repository": repo.get("full_name") or full_name.strip(),
        "contributors": len(contribution_rows),
        "commits": len(commit_rows),
        "issues": len(issue_rows),
        "pull_requests": len(pull_request_rows),
        "languages_added": inserted_languages,
        "truncated": {
            "contributors": contributors_truncated,
            "commits": commits_truncated,
            "issues": issues_truncated,
            "pull_requests": prs_truncated,
        },
    }
