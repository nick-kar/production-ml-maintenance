# Interview demonstration

## Accurate description

Personal production-oriented ML engineering project using synthetic predictive-maintenance data. Implements reproducible training, model serving, validation, logging, drift monitoring, explicit model version selection and rollback, and automated container verification. It is not commercial production employment, a service used by a real customer, or evidence of real-machine predictive performance.

## Five-minute walkthrough

1. Show the repository and latest successful Actions run. Open the integration-test and container-lifecycle logs; download container-verification.
2. Explain the training-only fitted scaler inside the saved sklearn pipeline, seeded split, data fingerprint and version compatibility check.
3. Show a valid POST /predict and an invalid RPM request returning 422. /metrics separates successful predictions from HTTP 4xx/5xx responses and persists counters across restarts when storage is retained.
4. Explain the normal versus shifted traffic experiment: vibration drift is a change in inputs, not measured loss of accuracy.
5. Show immutable v1/v2 artifacts, promotion pointer and required restart. The lifecycle test replaces the worker to load v2 and then rolls back to v1. SQLite logs remain in a named volume independent of the worker container.

## Operational decisions

Single replica and one operator at a time. Local SQLite is an inspectable educational choice. Promotion checks loadability, not model quality: the recorded v2 comparison did not establish an improvement, so v2 was used for the release exercise only. Real deployment needs representative validation data, cost-based thresholds, true-label feedback, authentication, backup/restore, and release coordination appropriate to its users. Those are extensions, not completed features.

No cloud account is required for the completed local/CI demonstration. A public endpoint would add hosting practice but would not turn simulated traffic into commercial experience.

## How the project was developed

Built using an assisted starter and debugging support. Personally ran and inspected Windows tests, API requests, validation errors, drift simulation, version switching, Git commits and CI results. Be ready to explain each component and distinguish assisted implementation from independent design.

## CV wording after the latest checks pass

Developed and verified a containerized ML inference service with FastAPI, SQLite audit logging, input validation, HTTP error/latency monitoring, feature-drift checks, and model version rollback; automated integration and container persistence/release tests using GitHub Actions.
