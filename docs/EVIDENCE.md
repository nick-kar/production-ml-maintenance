# My execution evidence

- Date / Python version / OS:
  9 November 2026 / Python 3.12.10 / Windows 11.

- Five local tests passed:
  Ran 5 tests in 0.791s — OK.
  Verified connection cleanup, predictions and validation, persistent
  logging, drift detection, reproducible training, and version rollback.

- v1 held-out metrics and prevalence:
  Average precision: 0.447604.
  ROC AUC: 0.832750.
  Positive prevalence: 12.2%.
  At threshold 0.30: TN=1235, FP=82, FN=108, TP=75.
  Results use synthetic data; they do not establish real machinery performance.

- Example prediction and model version:
  Input: temperature_c=75, vibration_mm_s=3, rpm=1500,
  tool_wear_min=110.
  HTTP 200; model_version=v1.
  Failure probability: 0.048362244025203054.
  Maintenance alert: false.

- Invalid-input response:
  rpm=-1 returned HTTP 422.
  Message: Input should be greater than or equal to 100.

- Normal / shifted traffic monitoring results:
  After normal traffic: 151 successful predictions; drift_alert=false.
  After adding 150 shifted requests: 301 successful predictions.
  Vibration mean shift: 1.440978 reference standard deviations.
  drift_alert=true.
  This detects feature distribution changes, not measured accuracy loss.

- v2 versus v1 comparison and release decision:
  v1 used C=1.0; v2 used C=0.5.
  Both used seed 42, the same dataset, split, and threshold.
  v2 average precision: 0.447584; ROC AUC: 0.832746.
  v2 confusion matrix: TN=1236, FP=81, FN=108, TP=75.
  No meaningful improvement established.
  Switched to v2 for release practice, then restored v1.

- Rollback verification:
  Promoted v1 and restarted the API.
  A prediction returned HTTP 200 with model_version=v1 and reproduced
  the original failure probability without retraining.

- GitHub repository:
  https://github.com/nick-kar/production-ml-maintenance

- GitHub Actions successful run:
  ML service checks #2, commit a96016d.
  https://github.com/nick-kar/production-ml-maintenance/actions
  Integration tests, image build, and container smoke test passed.

- Docker build/run result:
  Docker image built and container ran successfully on GitHub Actions.
  Verified /health, a v1 prediction, and successful prediction logging.
  Docker was not run locally on Windows.

- Hosted URL / hosting date / persistence test:
  Not deployed as a continuously available hosted service.
  Persistence across container replacement has not yet been verified.

- One issue diagnosed and fixed:
  Initial Windows tests failed during temporary database cleanup because
  SQLite connections remained open.
  Applied an assisted fix using explicit connection closing in the API
  and monitoring code.
  Verified all five tests passed on Windows, including the added
  connection-cleanup regression test.

- One change I implemented and why:
  Updated the GitHub Actions workflow with assistance to start the Docker
  container and verify health, predictions, and logging.
  This checks that the built image runs successfully, beyond build success.

## CV wording after verification

Built and verified a containerized ML prediction service with FastAPI,
input validation, SQLite prediction logging, feature-drift monitoring,
model version promotion and rollback, and GitHub Actions integration
and container smoke tests.

Personal production-oriented portfolio project using synthetic data.
Hosted deployment is not yet completed.

## Final operations update

Implementation added: persistent HTTP request/error counters and server processing latency; regression tests for invalid requests, server errors and counter persistence; automated container replacement, named-volume persistence, v2 release and v1 rollback verification. These additions do not change training or the recorded model results above.

Local verification of the update: seven tests passed in the assistant's Linux environment. Windows execution and the updated GitHub Actions container-lifecycle run are pending until this patch is applied and pushed. The prior green CI run remains valid evidence for the earlier container smoke test only. The updated workflow writes container-check.json as a downloadable Actions artifact; passed=true is the completion criterion for the lifecycle checks. No hosted endpoint has been deployed.
