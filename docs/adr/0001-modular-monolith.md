# ADR 0001 — Use a modular monolith

- Status: Accepted
- Date: 2026-10-01

## Context

Talent ID will initially support approximately 50 employees distributed across several sites. The system includes Android kiosks, biometric recognition, attendance, points and rewards.

## Decision

Build one FastAPI backend deployable organized as explicit business modules.

Modules own their data and rules and interact only through public application contracts or events.

## Consequences

Positive:

- one deployment unit;
- lower AWS operating cost;
- simple local development;
- straightforward transactions;
- easier debugging;
- future module extraction remains possible.

Trade-offs:

- architectural boundaries require discipline because the runtime does not enforce network isolation;
- shared database migrations must be coordinated;
- module ownership must be enforced in code review.

## Rejected alternative

Microservices were rejected because current load and team size do not justify distributed-system complexity.
