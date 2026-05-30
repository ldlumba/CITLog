# CITLog

CITLog is a secure web-based faculty attendance system for the College of Information Technology. It supports manual and QR-assisted attendance logging, account-based administration, centralized Supabase storage, signed attendance records, QR payload validation, and tamper detection.

## Live Deployment

The current deployment is available at:

[https://citlog.onrender.com](https://citlog.onrender.com)

The application is deployed as a Flask web service on Render and uses Supabase Postgres for persistent storage.

## Features

- Manual faculty time-in and time-out logging
- QR-assisted attendance logging through the browser camera
- Signed QR payloads linked to registered faculty records
- Account-based administrator login
- Role-aware administrative permissions
- Faculty profile management
- QR code generation and download
- Attendance dashboard with verification status
- CSV export from the dashboard
- Clear-record workflow with confirmation safeguards
- Ed25519-signed attendance records
- Tamper detection for modified attendance fields
- Audit logging for security-relevant administrator actions

## Architecture

CITLog uses a server-controlled architecture:

- **Frontend:** HTML, CSS, and browser JavaScript templates served by Flask
- **Backend:** Flask routes and service modules
- **Database:** Supabase Postgres
- **Deployment:** Render web service
- **Cryptography:** Ed25519 signatures through the Python `cryptography` package

The browser communicates with Flask routes only. Supabase access is performed server-side using a service role key stored as a deployment secret.

## Security Model

- Supabase service credentials are never exposed to browser code.
- All public Supabase tables have Row Level Security enabled.
- Direct `anon` and `authenticated` table access is revoked.
- Attendance records are signed over a canonical payload.
- QR codes contain signed CITLog payloads rather than plain teacher IDs.
- Administrator accounts use password hashes, login throttling, sessions, and role checks.
- Security-relevant actions are written to `audit_logs`.

## Local Development

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a local `.env` file using `.env.example` as a reference.

Generate an Ed25519 signing key:

```powershell
python scripts/generate_keys.py
```

Run the Flask app:

```powershell
python app.py
```

For local HTTP development, set:

```text
SESSION_COOKIE_SECURE=false
```

Use secure cookies in production.

## Database Setup

Apply the database schema in Supabase:

```text
sql/schema.sql
```

The schema creates the following tables:

- `admin_users`
- `teachers`
- `qr_tokens`
- `attendance`
- `audit_logs`

The schema also enables Row Level Security and revokes direct `anon` and `authenticated` access to application tables.

## Administrator Setup

Generate a password hash for the first administrator account:

```powershell
python scripts/create_admin_hash.py
```

Insert the generated values into `public.admin_users`. Supported roles are:

- `viewer`
- `admin`
- `super_admin`

## Testing

Run the test suite:

```powershell
python -m pytest -q
```

The tests cover:

- attendance signing and tamper detection
- signed QR payload generation and validation
- administrator permission logic
- protected route behavior
- basic Flask route contracts

## Deployment

The repository includes a Render Blueprint:

```text
render.yaml
```

Required deployment secrets:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SECRET_KEY`
- `CITLOG_SIGNING_PRIVATE_KEY_B64`
- `CITLOG_SIGNING_KEY_ID`
- `APP_TIMEZONE`
- `SESSION_HOURS`
- `MAX_LOGIN_ATTEMPTS`
- `LOGIN_COOLDOWN_SECONDS`
- `SESSION_COOKIE_SECURE`

See [docs/deployment.md](docs/deployment.md) for deployment and verification details.

## Documentation

- [Deployment Guide](docs/deployment.md)
- [Backup and Recovery Policy](docs/backup-policy.md)
- [Paper Requirements Map](docs/paper-requirements-map.md)

## License

No license has been declared for this repository.
