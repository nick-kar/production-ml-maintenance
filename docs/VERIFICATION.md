# Package verification

Verified on 9 November 2026 using Python 3.12.14 on Linux in a clean virtual environment installed from requirements.txt.

- Five unittest integration tests passed: reproducible training/version protection; API predictions/validation/persistent records; promotion/rollback; drift/insufficient-sample handling.
- Started an actual Uvicorn HTTP server with a newly trained v1.
- Sent 150 baseline requests: monitor samples=150, drift_alert=false.
- Sent 150 additional shifted requests: monitor samples=300, drift_alert=true.
- Verified /health returned status=ok and model_version=v1.

Windows commands were written for PowerShell but not executed on a Windows computer. Docker was unavailable in this verification environment. Docker image builds, GitHub Actions and cloud hosting have not been executed here. Run these stages and record your own evidence.

Generated model binaries and runtime logs are excluded from the ZIP; train locally so the model matches your installed environment. The package uses synthetic data and requires no external dataset download.

Windows cleanup fix: all API and monitoring connections now explicitly close after transaction completion. Added a regression test retaining connection references and asserting every connection is closed without garbage collection. Windows execution remains to be confirmed by the user.
