# ADR 0002 — PostgreSQL as primary persistence

- Status: Accepted
- Date: 2026-10-01

## Context

Talent ID needs attendance history, schedules, multi-site reporting, immutable points transactions, reward redemptions and auditable corrections.

## Decision

Use PostgreSQL as the primary transactional store behind module-owned repositories.

## Rules

- UUID primary identifiers.
- UTC timestamps in persistence.
- No cross-module ORM relationships.
- Table ownership is explicit by module prefix.
- Ledger/fact tables are append-oriented.
- Alembic owns schema migrations.

## Why not DynamoDB first

DynamoDB can support the workload, but the expected volume is small and the reporting/transaction model is naturally relational. PostgreSQL minimizes modeling complexity for the first production version.
