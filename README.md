# GitHub Repository Analytics

A database-focused analytics application for GitHub profile, repository, issue, pull-request, commit, and contribution data. The frontend uses HTML, CSS, and JavaScript; a Flask API reads and updates Oracle Database 21c XE.

## Project structure

- `frontend/` — dashboard, GitHub user activity, data views, login, and repository management
- `backend/app.py` — Flask API with session login and authenticated repository management
- `backend/db.py` — Oracle connection configuration
- `backend/schema_project.sql` — project tables for a fresh local schema
- `backend/migration_separate_app_accounts.sql` — one-time migration for an existing schema
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

   Log out and back in to load the administrator role. All signed-in accounts can currently add, update, and delete repositories; the ADMIN role is reserved for future administrator-only features.

Email password recovery requires SMTP settings in the backend environment: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM`. In production, also set `PASSWORD_RESET_URL` to the HTTPS reset page URL. Keep mail credentials private. For local recovery, run `python reset_password.py USERNAME` from `backend/`; it prompts for a replacement password. For public repository imports, no GitHub token is needed. If you configure an optional `GITHUB_TOKEN` for higher API limits, keep it secret and set it only in the backend terminal. The importer currently fetches up to 500 records per activity list. The Oracle variables apply only to the PowerShell terminal that starts Flask. Do not commit real credentials. The development Flask secret is generated for the local process; production requires FLASK_SECRET_KEY and APP_ENV=production.

## Main features

- Repository and activity dashboards
- Per-GitHub-user counts for contributions, repositories, commits, issues, and pull requests
- Separate application login accounts and GitHub profile records
- Server-side session authentication for API routes
- Authenticated repository create, update, and delete operations
- GitHub repository import/sync for repository details, contributors, recent commits, issues, pull requests, and languages
- Repository fetch and search, plus user, issue, pull-request, commit, and language views

## Deployment status

The application is prepared for authenticated local use. A public deployment still needs a cloud-accessible Oracle database, production secrets and allowed CORS origins, and a deployment-specific API routing configuration. The local Oracle XE database cannot be reached by a hosted Vercel function.

Before a public deployment, also configure HTTPS and review CSRF protection, login rate limiting, database least-privilege access, and account recovery.
