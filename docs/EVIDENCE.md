# My execution evidence

- Date / Python version / OS:
  9 November 2026 / Python 3.12.10 / Windows 11.

- Local integration tests:
  All seven tests passed on Windows:
  Ran 7 tests in 1.821s — OK.
  Covered database connection cleanup, prediction consistency,
  input validation, persistent logging, drift detection,
  HTTP request/error monitoring, reproducible training,
  model version switching and rollback.

- v1 held-out metrics and prevalence:
  Average precision: 0.447604.
  ROC AUC: 0.832750.
  Positive prevalence: 12.2%.
  At threshold 0.30: TN=1235, FP=82, FN=108, TP=75.
  Results use synthetic data and do not establish performance
  on real machinery.

- Example prediction and model version:
  Input: temperature_c=75, vibration_mm_s=3, rpm=1500,
  tool_wear_min=110.
  HTTP 200; model_version=v1.
  Failure probability: 0.048362244025203054.
  Maintenance alert: false.

- Invalid-input response:
  rpm=-1 returned HTTP 422.
  Message: Input should be greater than or equal to 100.

- Normal / shifted traffic monitoring:
  After normal traffic: 151 successful predictions; drift_alert=false.
  After 150 additional shifted requests: 301 successful predictions.
  Vibration mean shift: 1.440978 reference standard deviations.
  drift_alert=true.
  Feature drift does not establish a decrease in prediction accuracy.

- HTTP monitoring:
  Persistent request counts, HTTP 4xx/5xx counts, and mean server
  processing time.
  Metrics requests are excluded from HTTP counters.
  Server processing time excludes network transfer and is distinct
  from model inference time.

- v2 versus v1 comparison:
  v1 used C=1.0; v2 used C=0.5.
  Both used seed 42, the same dataset, split and threshold.
  v2 average precision: 0.447584.
  v2 ROC AUC: 0.832746.
  v2 confusion matrix: TN=1236, FP=81, FN=108, TP=75.
  No meaningful improvement established.
  v2 was used for release practice, then v1 was restored.

- Local rollback verification:
  Promoted v1 and restarted the API.
  A prediction returned HTTP 200 with model_version=v1 and
  reproduced the original probability without retraining.

- GitHub repository:
  https://github.com/nick-kar/production-ml-maintenance

- Final successful GitHub Actions run:
  ML service checks #5, commit fcc9504.
  https://github.com/nick-kar/production-ml-maintenance/actions
  Passed integration tests, Docker image build, and automated
  container persistence, release and rollback verification.

- Container lifecycle verification:
  Served a valid v1 prediction and rejected invalid input.
  Preserved prediction logs and HTTP counters in named Docker volumes
  across container replacement.
  Loaded v2 after container replacement.
  Rolled back to v1 and reproduced the original prediction.
  The workflow preserves a container-verification artifact.

- Docker execution environment:
  Docker built and ran containers on GitHub Actions.
  Docker was not run locally on Windows.

- Hosted deployment:
  No continuously available public endpoint was deployed.
  Persistence was verified using Docker volumes in CI,
  not through a hosted service.

- Issues diagnosed and fixed with assistance:
  Explicitly closed SQLite connections to resolve Windows temporary
  database cleanup failures.
  Corrected HTTP client lifecycle handling in the container-check
  script after a failed CI run.
  The final workflow passed after the fixes.

- Implementation and verification:
  Extended the workflow with assistance to verify running containers,
  persistent storage, model releases and rollback.
  Personally executed the Windows workflow, inspected API responses,
  tested drift and rollback, committed changes and reviewed CI results.

## CV wording

Built and verified a containerized ML inference service with FastAPI,
input validation, SQLite audit logging, HTTP error/latency monitoring,
feature-drift checks and model version rollback; automated integration
and container persistence/release tests using GitHub Actions.

Personal production-oriented portfolio project using synthetic data
and simulated traffic.