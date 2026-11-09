# Start here — Windows 11

This is a complete working starter, with a guided operations exercise. No Docker, paid account, dataset download or PostgreSQL is needed for the first run. Commands assume you are inside the extracted project folder, the one containing requirements.txt.

## 1. Prepare Python
Open the folder in VS Code. Choose Terminal > New Terminal. Use PowerShell.
Run `py -0p` to list installed Python versions. Use Python 3.12 for this project. If absent, install Python 3.12 from https://www.python.org/downloads/ and reopen VS Code. Your old Python 3.9 can remain installed.

A virtual environment keeps this project's packages separate. Run each line:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
No environment activation or PowerShell execution-policy change is necessary.

## 2. Train and select the model
Training creates a versioned model, its preprocessing and evaluation metadata. Promotion selects the version the API loads on its next start.
```powershell
.\.venv\Scripts\python.exe -m mlops.cli train --version v1
.\.venv\Scripts\python.exe -m mlops.cli promote v1
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
Expected: JSON metrics, active v1, and five passing tests. Tests use temporary directories and preserve your model. If v1 already exists, reuse it; do not repeat the train command.

## 3. Start the API
An API lets other software request predictions. Start it:
```powershell
.\.venv\Scripts\python.exe -m uvicorn mlops.api:app --host 127.0.0.1 --port 8000
```
Keep this terminal open. Browse to http://127.0.0.1:8000/docs
Open POST /predict > Try it out. Replace the body with:
```json
{"temperature_c":75,"vibration_mm_s":3,"rpm":1500,"tool_wear_min":110}
```
Click Execute. Expected: HTTP 200, probability between 0 and 1, model_version v1, request_id, and a maintenance_alert boolean.
Try rpm = -1: expected HTTP 422. Open GET /health and GET /metrics too.

## 4. Generate traffic and inspect drift
Open a second terminal in the same folder. Drift means incoming data differs from the training reference. This demo checks mean changes; it cannot tell whether predictions remain accurate without true outcomes.
```powershell
.\.venv\Scripts\python.exe -m scripts.traffic
.\.venv\Scripts\python.exe -m mlops.cli monitor
.\.venv\Scripts\python.exe -m scripts.traffic --shift
.\.venv\Scripts\python.exe -m mlops.cli monitor
```
Expected: 150 normal requests, then 150 with increased vibration. The second report should flag vibration drift. Reports use the latest 1,000 successful requests, grouped by model version; prior traffic affects results. Read runtime/drift_report.json. GET /metrics reports the successful prediction count and mean inference time, not end-to-end latency or HTTP error rate.

## 5. Update and roll back
A rollback restores a previous model after a bad release. This project deliberately requires a server restart; it does not hot-reload models.
```powershell
.\.venv\Scripts\python.exe -m mlops.cli train --version v2 --c 0.5
```
Compare artifacts/v1/metadata.json and artifacts/v2/metadata.json. Explain the precision-recall tradeoff at the fixed 0.3 threshold before selecting a version. Promotion verifies loadability; YOU make the quality decision.
```powershell
.\.venv\Scripts\python.exe -m mlops.cli promote v2
```
Stop the first terminal with Ctrl+C and run its uvicorn command again. GET /health should show v2. Send a prediction. Promote v1, restart again, and confirm v1. Record the reason and results in docs/EVIDENCE.md.

## 6. Publish your code and enable CI
Create an empty GitHub repository. Upload the extracted folder's contents, including .github/workflows/ci.yml (use Git/VS Code to preserve hidden folders). Do not upload .venv, runtime logs or generated artifacts. GitHub Actions installs dependencies, runs tests and builds the Docker image. Record its actual link and status in EVIDENCE.md. A supplied workflow is not evidence that CI has run.

## 7. Optional Docker and hosted deployment
Follow docs/DEPLOYMENT.md after the local exercise works. Docker is not required for steps 1–6. A public URL is a separate milestone; running localhost does not establish cloud deployment experience.

## Troubleshooting
- `py` missing: install Python 3.12 with the Windows launcher; reopen terminal.
- `No module named mlops`: terminal must be in the folder containing mlops and requirements.txt.
- active.json missing: run training and promotion first.
- Port occupied: use --port 8001 and change the browser and traffic --url accordingly.
- Version exists: use a new version name or keep the existing version; versions are immutable.
- Dependency mismatch: use the project virtual environment, retrain under a new version and promote it.
- API errors: inspect its terminal. SQLite disk errors fail requests rather than silently losing audit records.
