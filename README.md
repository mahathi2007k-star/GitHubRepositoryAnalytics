# GitHub Repository Analytics

A database-focused analytics application for GitHub profile, repository, issue, pull-request, commit, and contribution data. The frontend uses HTML, CSS, and JavaScript; a Flask API reads and updates the database. The original local Oracle XE setup remains documented below; this deployment branch uses PostgreSQL for a free hosted demo.

## Project structure

- `frontend/` — dashboard, GitHub user activity, data views, login, and repository management
- `backend/app.py` — Flask API with session login and authenticated repository management
- `backend/db.py` — PostgreSQL connection configuration for this hosted-demo branch
- `backend/schema_postgres.sql` — schema for the hosted PostgreSQL database
- `backend/schema_project.sql` — project tables for a fresh local schema
- `backend/schema_cloud.sql` — portable tables for a dedicated Oracle Autonomous Database schema
- `render.yaml` — one-service Render deployment blueprint
- `backend/migration_separate_app_accounts.sql` — one-time migration for an existing schema
- `backend/migration_repository_audit.sql` — repair the repository audit trigger in an existing schema
- `backend/promote_admin.py` — promote an existing app account to administrator
- `backend/reset_password.py` — local operator password reset
- `backend/migration_add_password_resets.sql` — create the one-time email reset token table
- `backend/requirements.txt` — Python packages

## Existing database: separate app accounts

Back up the Oracle schema before migrating. At the SQL*Plus prompt, run the one-time migration as the owner of the project tables:

```sql
@C:\Users\mahat\OneDrive\Documents\GitHubRepositoryAnalytics\backend\migration_separate_app_accounts.sql
```

The migration checks for duplicate legacy usernames/emails, copies password-hash accounts from GITHUB_USER into APP_ACCOUNT, keeps all GitHub profile rows and their activity links, then drops the legacy PASSWORD_HASH column. Do not run it twice. To enable email password recovery on this existing database, also run `@C:\Users\mahat\OneDrive\Documents\GitHubRepositoryAnalytics\backend\migration_add_password_resets.sql` once.

If repository import fails with Oracle `ORA-04098` for `TRG_REPOSITORY_AUDIT`, run `@C:\Users\mahat\OneDrive\Documents\GitHubRepositoryAnalytics\backend\migration_repository_audit.sql` once as SYSTEM. It creates the missing audit table and sequence, then recompiles the trigger.

For a fresh database, run backend/schema_project.sql as the schema owner instead. This export currently names the SYSTEM schema and tablespace because that is where the local project tables were created; change those qualifiers before using a different schema.

## Local setup

1. Start Oracle XE and run the migration above if this is your existing project database.
2. In PowerShell at the project root, set the Oracle connection for that terminal session:

   ```powershell
   $env:ORACLE_USER = "SYSTEM"
   $env:ORACLE_PASSWORD = "your local Oracle password"
   $env:ORACLE_DSN = "localhost:1521/xe"
   ```

3. Start the backend:

   ```powershell
   cd backend
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   .\venv\Scripts\python.exe app.py
   ```

4. Open frontend/login.html with VS Code Live Server. Use the same hostname consistently (localhost or 127.0.0.1) so the browser can send the session cookie to Flask.
5. If the migration moved your existing login, keep using that username and password. If this is a fresh database, register an account first. Promote your account from the backend folder:

   ```powershell
   .\venv\Scripts\python.exe promote_admin.py YOUR_USERNAME
   ```

   Log out and back in to load the administrator role. The analytics pages show the signed-in username and role. All signed-in accounts can add, update, and delete repositories; the ADMIN role identifies the project administrator without restricting teammate repository management.

Email password recovery requires SMTP settings in the backend environment: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM`. In production, also set `PASSWORD_RESET_URL` to the HTTPS reset page URL. Keep mail credentials private. For local recovery, run `python reset_password.py USERNAME` from `backend/`; it prompts for a replacement password. For public repository imports, no GitHub token is needed. If you configure an optional `GITHUB_TOKEN` for higher API limits, keep it secret and set it only in the backend terminal. The importer currently fetches up to 500 records per activity list. The Oracle variables apply only to the PowerShell terminal that starts Flask. Do not commit real credentials. The development Flask secret is generated for the local process; production requires FLASK_SECRET_KEY and APP_ENV=production.

## Main features

- Repository and activity dashboards
- Per-GitHub-user counts for contributions, repositories, commits, issues, and pull requests
- Separate application login accounts and GitHub profile records
- Server-side session authentication for API routes
- Authenticated repository create, update, and delete operations
- GitHub repository import/sync for repository details, contributors, recent commits, issues, pull requests, and languages
- Repository fetch and search, plus user, issue, pull-request, commit, and language views

## Deploy for teammate access (free hosted demo)

This branch is the online-demo variant. It uses Render for the Flask app and Neon PostgreSQL for hosted data. Your local Oracle XE project remains a separate version; Oracle data is not copied to Neon automatically. Render's free web service can sleep when idle, so the first visit after inactivity may take around a minute. Neon and Render free-plan limits can change; check their current dashboards before relying on the demo for long-term storage.

### 1. Create the PostgreSQL database

1. Create a free PostgreSQL project in Neon.
2. Copy its pooled PostgreSQL connection string from the Connect panel. Keep it private.
3. Open Neon SQL Editor, paste and run `backend/schema_postgres.sql` from this repository. This creates the app-account, repository, GitHub activity, reset-token, and audit tables.

### 2. Publish this branch to GitHub

This deployment uses the `codex/postgres-online-demo` branch. Push this branch to your GitHub repository after reviewing the changed files. Do not push `.env` files, passwords, database URLs, API keys, or wallet files.

### 3. Create the Render service

1. In Render, create a new Blueprint and select your GitHub repository and the `codex/postgres-online-demo` branch.
2. Render reads `render.yaml`. Set `DATABASE_URL` to the Neon connection string. Keep the value in Render's Environment settings only.
3. After Render assigns a URL, set `PASSWORD_RESET_URL` to `https://YOUR-SERVICE.onrender.com/reset_password.html`.
4. Deploy and open the Render URL. Register your own account, then use the Neon SQL Editor to promote it:

   ```sql
   UPDATE APP_ACCOUNT SET ROLE = 'ADMIN' WHERE USERNAME = LOWER('your_username');
   ```

5. Log out and back in so the browser session loads the ADMIN role. Teammates can register through the same app URL; all authenticated users can manage repository records.

### 4. GitHub sync and password-reset email

Public repositories can be synced without a GitHub token. To raise GitHub API rate limits, set `GITHUB_TOKEN` as a private Render environment variable.

Password-reset emails use Resend's HTTPS API, since Render's free web services block outbound SMTP. Create a Resend account, verify a sending domain you control, then set `RESEND_API_KEY` and `RESEND_FROM_EMAIL` in Render. The sender address must belong to that verified domain. Until this is configured, app registration and login can work, but email password recovery will not send reset links. A custom domain is therefore needed for password-reset emails to all users through this setup.

Never paste secret values into chat, source files, screenshots, or GitHub. The deployed app has its own empty hosted database; importing data from your Oracle XE instance is a separate migration task.
