# CITLog Backup and Recovery Policy

CITLog stores operational attendance data in Supabase Postgres. The application also supports CSV export from the administrator dashboard for local reporting copies.

## Data Covered

- Teacher records
- Attendance records
- QR token records
- Administrator account records
- Audit logs

## Operational Practice

1. Export attendance records before clearing records from the dashboard.
2. Keep exported CSV files in the department's approved storage location.
3. Review Supabase project backup availability before production deployment, since backup features depend on the selected Supabase plan.
4. Test restoration after schema changes by applying `sql/schema.sql` to a non-production Supabase project and importing sample records.

## Recovery Objective

The minimum recovery target is the latest Supabase-managed backup or the latest department-approved CSV export, whichever is newer and available.
