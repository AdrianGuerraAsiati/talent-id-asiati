# Backend modules

Each module owns its business rules and persistence.

| Module | Owns |
|---|---|
| workforce | Employee projection, sites, schedules |
| devices | Android kiosk registration and lifecycle |
| biometrics | Enrollment, recognition and provider abstraction |
| attendance | Check-in/out facts, exceptions and corrections |
| rewards | Talent Points ledger, catalog and redemptions |
| integrations | Talent Intelligence/Odoo contracts |
| audit | Append-only administrative audit trail |

Rules:

1. Never import another module's infrastructure package.
2. Never access another module's tables directly.
3. Use public application contracts for queries/commands.
4. Use events for side effects.
5. Shared code is technical only.
