# GitHub Repository Analytics

A full-stack analytics application for GitHub-related repository data. The frontend uses HTML, CSS and JavaScript; a Flask API reads and updates data in Oracle Database 21c XE.

## Project structure

- `frontend/` — dashboard, data views, login/registration and repository management pages
- `backend/app.py` — Flask API routes
- `backend/db.py` — Oracle connection configuration
- `backend/requirements.txt` — Python packages

## Local setup

1. Start Oracle Database XE and ensure the project tables contain the schema and records used by the application.
2. Open PowerShell in the project folder and configure the database connection for that terminal session:

   ```powershell
   $env:ORACLE_USER = "SYSTEM"
   $env:ORACLE_PASSWORD = "<your local Oracle password>"
   $env:ORACLE_DSN = "localhost:1521/xe"
   ```

3. Start the Flask API:

   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python app.py
   ```

4. In VS Code, open `frontend/dashboard.html` with Live Server. The application redirects to the login page until you sign in.

The environment variables apply only to that PowerShell session. Set them in the terminal that starts Flask. Do not commit real credentials. If the earlier hard-coded database password was pushed to a remote repository, rotate it.

## Main features

- Dashboard counts and analytics for repositories and activity
- User, repository, issue, pull-request, commit and language views
- Registration and login with Werkzeug password hashing
- Repository create, fetch, search, update and delete operations

## Important security note

The current page gate uses browser `sessionStorage`; it is suitable only as a demo navigation check. The API does not yet enforce authenticated access. Do not expose the application publicly until server-side authentication and authorization are added.