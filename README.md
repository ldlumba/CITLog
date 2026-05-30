# CITLog

CITLog is a Flask and Supabase faculty attendance system with QR-assisted logging, account-based administration, signed attendance records, QR payload validation, and tamper detection.

## Security Model

- The browser communicates only with Flask routes.
- Supabase access is server-side only through `SUPABASE_SERVICE_ROLE_KEY`.
- All public Supabase tables have RLS enabled and grant no direct browser access to `anon` or `authenticated`.
- Attendance records are signed with Ed25519 using `cryptography`.
- QR codes contain signed CITLog payloads, not plain teacher IDs.
- Admin users are account-based and role-aware.
- Security-relevant actions are written to `audit_logs`.

## Setup

1. Create a Supabase project.
2. Run `sql/schema.sql` in the Supabase SQL editor.
3. Generate signing keys:

```powershell
python scripts/generate_keys.py
```

4. Create an admin password hash:

```powershell
python scripts/create_admin_hash.py
```

5. Insert the admin row into `public.admin_users`.
6. Set the environment variables shown in `.env.example`.
7. Run locally:

```powershell
pip install -r requirements.txt
python app.py
```

## Tests

```powershell
pytest
```

## Documentation

- `docs/deployment.md` explains Supabase, signing-key, admin-account, and Render setup.
- `docs/backup-policy.md` defines the operational backup and recovery policy.
- `docs/paper-requirements-map.md` maps the implementation to the manuscript claims.
