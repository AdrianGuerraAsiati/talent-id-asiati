# Talent ID Android Kiosk

The Android application is a dedicated reception kiosk client.

Planned stack:

- Kotlin
- Jetpack Compose
- CameraX
- Android Keystore
- Room for local retry/fallback queue
- WorkManager for synchronization

The kiosk never embeds AWS IAM access keys and never becomes the authoritative source for attendance or points.

## First Android milestone

1. device provisioning;
2. camera preview/capture;
3. call Talent ID recognition endpoint;
4. show recognized employee/result;
5. support PIN/QR fallback.
