"""Disposable Docker lifecycle check; requires a running Docker engine (CI supported)."""
import json
from pathlib import Path
import subprocess
import time
import uuid
import httpx
from contextlib import closing

suffix = uuid.uuid4().hex[:10]
name = "maintenance-check-" + suffix
runtime_volume = name + "-runtime"
model_volume = name + "-models"
image = "maintenance-ml"
report = {"checks": [], "passed": False}
payload = {"temperature_c":75,"vibration_mm_s":3,"rpm":1500,"tool_wear_min":110}

def docker(*args, capture=False):
    result = subprocess.run(["docker", *args], check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None

def start():
    docker("run", "-d", "--name", name, "-p", "127.0.0.1::8000",
           "-v", runtime_volume+":/app/runtime", "-v", model_volume+":/app/artifacts", image)
    port = docker("port", name, "8000/tcp", capture=True).split(":")[-1]
    client = httpx.Client(base_url="http://127.0.0.1:"+port, timeout=10, trust_env=False)
    for attempt in range(60):
        try:
            response = client.get("/health")
            response.raise_for_status()
            return client
        except httpx.HTTPError:
            time.sleep(1)
    client.close()
    raise RuntimeError("Container did not become healthy")

def prediction(client, version):
    response = client.post("/predict", json=payload)
    response.raise_for_status()
    result = response.json()
    assert result["model_version"] == version, result
    assert 0 <= result["failure_probability"] <= 1, result
    assert isinstance(result["maintenance_alert"], bool), result
    return result["failure_probability"]

def remove():
    docker("rm", "-f", name)

try:
    with closing(start()) as client:
        original = prediction(client, "v1")
        response = client.post("/predict", json={**payload,"rpm":-1})
        assert response.status_code == 422
        metrics = client.get("/metrics").json()
        assert metrics["successful_predictions"] == 1, metrics
        assert metrics["http_4xx"] == 1, metrics
        docker("exec", name, "python", "-m", "mlops.cli", "train", "--version", "v2", "--c", "0.5")
        docker("exec", name, "python", "-m", "mlops.cli", "promote", "v2")
        # The already running worker stays on v1 until replacement.
        assert client.get("/health").json()["model_version"] == "v1"
    report["checks"].append("v1 prediction, validation, HTTP monitoring, explicit restart semantics")
    remove()
    with closing(start()) as client:
        metrics = client.get("/metrics").json()
        assert metrics["successful_predictions"] == 1, metrics
        assert metrics["http_4xx"] == 1, metrics
        prediction(client, "v2")
        docker("exec", name, "python", "-m", "mlops.cli", "promote", "v1")
    report["checks"].append("volume persistence after container replacement; v2 release")
    remove()
    with closing(start()) as client:
        assert client.get("/metrics").json()["successful_predictions"] == 2
        restored = prediction(client, "v1")
        assert abs(restored-original) < 1e-12
        assert client.get("/metrics").json()["successful_predictions"] == 3
    report["checks"].append("rollback restores v1 predictions and preserves audit records")
    report["passed"] = True
finally:
    logs = subprocess.run(["docker","logs",name], text=True, capture_output=True)
    Path("container-logs.txt").write_text(logs.stdout+logs.stderr)
    subprocess.run(["docker","rm","-f",name], check=False)
    subprocess.run(["docker","volume","rm",runtime_volume,model_volume], check=False)
    Path("container-check.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
