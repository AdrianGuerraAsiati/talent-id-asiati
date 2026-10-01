# ADR 0003 — Isolate biometric provider behind a port

- Status: Accepted
- Date: 2026-10-01

## Decision

The biometrics module defines provider-neutral application/domain contracts. AWS Rekognition is implemented as an infrastructure adapter.

## Rationale

Recognition thresholds, enrollment lifecycle and attendance decisions are Talent ID concerns. AWS request/response models are infrastructure concerns.

This prevents vendor SDK objects from propagating through the domain and gives us a controlled path to test with a fake provider or change providers later.

## Privacy rule

Raw recognition images are transient by default and are not stored as attendance history.
