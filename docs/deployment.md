# CITLog Deployment Guide

This guide deploys the production-aligned CITLog implementation described in the manuscript.

## 1. Supabase Setup

1. Create a Supabase project.
2. Open the SQL editor.
3. Run `sql/schema.sql`.
4. Confirm Row Level Security is enabled for:
   - `admin_users`
   - `teachers`
   - `qr_tokens`
   - `attendance`
   - `audit_logs`
5. Confirm no direct `anon` or `authenticated` table policies grant browser access.

The Flask backend uses the Supabase service role key server-side. Do not expose this key in browser JavaScript or public repositories.

Supabase security advisors may report `RLS Enabled No Policy` at INFO level for CITLog tables. This is intentional for the current architecture: direct browser access is denied, and all table operations go through the Flask backend. Performance advisors may report unused indexes on a new database until the live service has query history.

## 2. Signing Key Setup

Generate an Ed25519 keypair:

```powershell
python scripts/generate_keys.py
```

Set `CITLOG_SIGNING_PRIVATE_KEY_B64` in Render or your local `.env`. Keep the private key secret.

## 3. First Admin Account

Generate an admin password hash:

```powershell
python scripts/create_admin_hash.py
```

Insert the generated values into `public.admin_users` with one of these roles:

- `viewer`: can view dashboard data.
- `admin`: can manage teachers, generate QR codes, verify records, export data, and clear attendance.
- `super_admin`: reserved for future admin-user management.

## 4. Local Run

```powershell
pip install -r requirements.txt
python app.py
```

For local HTTP testing, set:

```text
SESSION_COOKIE_SECURE=false
```

Use `SESSION_COOKIE_SECURE=true` in production.

## 5. Render Deployment

The repository includes `render.yaml`.

Required Render environment variables:

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

After deployment, verify:

1. The root page loads.
2. Admin login works with the seeded admin account.
3. Teacher creation works.
4. QR generation creates a downloadable QR code.
5. QR scanning records attendance.
6. Tamper verification marks altered signed records as invalid.
7. Audit logs are created for admin actions.

## 6. Verification Commands

```powershell
python -m compileall app.py attendance_service.py audit.py auth_service.py config.py crypto.py qr_service.py repository.py routes scripts tests
$env:PYTEST_ADDOPTS='-p no:cacheprovider'; python -m pytest -q
```
