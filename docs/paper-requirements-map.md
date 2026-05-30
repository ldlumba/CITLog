# Paper Requirements Map

## Covered Requirements

- Web-based faculty attendance system: Flask app with attendance terminal and admin dashboard.
- Manual attendance logging: `/time` route stores signed `IN` and `OUT` records.
- QR-assisted logging: browser scanner decodes signed CITLog QR payloads and submits them to `/scan-time`.
- Centralized cloud storage: Supabase-backed repository layer.
- Admin dashboard: protected `/admin` route and dashboard API routes.
- Account-based administrative access: `admin_users` table and username/password login.
- Role-aware administrative controls: route permissions for viewing, teacher management, QR generation, and clearing records.
- Session security: HttpOnly, SameSite, configurable Secure cookies, login cooldown, and password hashing.
- Teacher profile management: protected teacher creation and listing.
- QR generation: protected QR generation with registered QR tokens.
- Strong QR validation: signed QR envelopes plus token registration checks.
- Digital signature verification: Ed25519 signatures over canonical attendance payloads.
- Tamper detection: verification fails when protected attendance fields change.
- CSV export support: dashboard client-side CSV export from verified rows.
- Controlled clearing safeguards: dashboard export/proceed/final warning flow and protected backend clear route.
- Audit logging: admin login, verification, teacher creation, QR generation, and clearing actions are recorded.
- Supabase RLS: schema enables RLS and revokes direct `anon`/`authenticated` table access.
- Render deployment: `render.yaml` and deployment guide included.
- ISO/IEC 25010 technical evidence: unit and route integration tests cover functional and security behavior.

## Requirements Needing Live Environment Completion

- Apply `sql/schema.sql` to the selected Supabase project.
- Insert the first real admin account.
- Configure Render secrets.
- Deploy from GitHub to Render.
- Run post-deployment verification against the live service.

## Intentional Future Work

- Larger user acceptance and field evaluation with faculty, administrators, and IT professionals.
- Offline or low-connectivity fallback.
- Expanded analytics by academic term or department.
- Institution-managed identity-provider integration.
