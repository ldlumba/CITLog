# CITLog

CITLog is a secure web-based faculty attendance system developed for the College of Information Technology. The project modernizes faculty attendance recording by combining manual attendance entry, QR-assisted logging, centralized cloud storage, administrator-managed records, and cryptographic tamper detection.

The system demonstrates how web technologies, QR workflows, and digital signatures can improve the integrity and manageability of institutional attendance records.

## Live Deployment

The deployed system is available at:

[https://citlog.onrender.com](https://citlog.onrender.com)

The live version is hosted as a Flask web service on Render and uses Supabase Postgres for persistent data storage.

## Core Capabilities

- Faculty time-in and time-out logging
- Manual teacher ID entry
- QR-assisted attendance logging through the browser camera
- Administrator dashboard for reviewing attendance records
- Faculty profile management
- QR code generation and download for registered faculty
- Attendance verification status for each record
- CSV export from the administrative dashboard
- Clear-record workflow with confirmation safeguards
- Audit logging for security-relevant administrator actions

## Technical Overview

CITLog follows a server-controlled architecture. Browser clients interact with Flask routes, while database access is handled by the backend. This keeps database credentials and privileged operations out of client-side code.

The application is organized around several backend responsibilities:

- **Flask web service:** serves the attendance terminal, administrator dashboard, and API routes.
- **Attendance service:** records manual and QR-assisted attendance events.
- **Cryptographic service:** signs and verifies canonical attendance payloads.
- **QR service:** generates and validates signed QR payloads for registered faculty.
- **Authentication service:** manages administrator login, sessions, roles, and access checks.
- **Repository layer:** centralizes Supabase database operations.
- **Audit logging:** records important administrator and verification actions.

## System Architecture

- **Frontend:** HTML, CSS, and browser JavaScript templates served by Flask
- **Backend:** Python Flask routes and service modules
- **Database:** Supabase Postgres
- **Deployment:** Render web service
- **Cryptography:** Ed25519 signatures using the Python `cryptography` package
- **QR processing:** Browser camera capture with backend QR decoding and validation

The frontend is intentionally lightweight. Security-sensitive operations such as signature generation, QR payload validation, attendance verification, and database access occur on the server.

## Security Model

CITLog is designed to reduce common risks in attendance-record management while remaining practical for a web-based institutional system.

- Supabase service credentials are used only by the server-side application.
- Public browser code does not communicate directly with Supabase tables.
- Supabase Row Level Security is enabled on application tables.
- Direct `anon` and `authenticated` table access is revoked.
- Attendance records are signed over a canonical payload containing teacher ID, date, time, and action.
- Verification fails when signed attendance fields are modified after storage.
- QR codes contain signed CITLog payloads instead of plain teacher IDs.
- Administrator accounts use password hashes, login throttling, sessions, and role-aware access checks.
- Security-relevant administrator actions are written to audit logs.

## Data Storage Overview

Supabase Postgres stores the system's operational records. The main data areas are:

- **Administrator accounts:** account credentials, roles, login state, and access status
- **Teacher records:** registered faculty identifiers and profile details
- **QR tokens:** signed QR payload records generated from the administrator dashboard
- **Attendance records:** signed time-in and time-out entries with verification data
- **Audit logs:** security-relevant administrator and verification events

Attendance entries include both the recorded attendance fields and the cryptographic evidence needed to verify whether those fields remain unchanged.

## Attendance Integrity and Tamper Detection

Each attendance record is transformed into a canonical payload before storage. The payload is signed using Ed25519, and the resulting signature is stored with the attendance row. During dashboard verification, CITLog reconstructs the payload and validates the stored signature.

If a protected field such as teacher ID, date, time, or action is modified directly in the database after signing, verification fails and the dashboard marks the record as tampered. This behavior was tested on the live deployment.

## QR Validation

Generated QR codes contain signed CITLog payloads linked to registered teacher records. During QR attendance logging, the backend validates the QR envelope, checks that the token is registered, confirms that the linked teacher is active, and then records the attendance action.

This design avoids relying on plain teacher IDs alone as QR contents.

## Verification Summary

The project includes automated tests and live workflow verification. The implemented test coverage includes:

- attendance signing and tamper detection
- signed QR payload generation and validation
- administrator permission logic
- protected route behavior
- basic Flask route contracts

The live deployment has also been verified for:

- administrator login
- teacher creation
- QR generation and preview
- manual attendance logging
- QR attendance logging
- audit-log creation
- tamper detection on modified attendance data

## Supporting Documentation

- [Deployment Guide](docs/deployment.md)
- [Backup and Recovery Policy](docs/backup-policy.md)

These documents support review, verification, and maintainability of the completed project.

## License

No license has been declared for this repository.
