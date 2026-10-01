# Talent ID Infrastructure

Infrastructure will be codified after the first backend vertical slice is stable.

Target AWS principles:

- core resources in `us-east-2`;
- one backend deployable;
- managed PostgreSQL;
- AWS Rekognition behind the biometrics adapter;
- Secrets Manager/SSM for secrets;
- CloudWatch observability;
- least-privilege IAM;
- no long-lived AWS credentials in Android.

Infrastructure as code will be added before the production pilot.
