import json, sqlite3, time, uuid
from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field
from mlops import core

class Measurement(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    temperature_c: float = Field(ge=20,le=150)
    vibration_mm_s: float = Field(ge=0,le=15)
    rpm: float = Field(ge=100,le=5000)
    tool_wear_min: float = Field(ge=0,le=500)

def connect():
    (core.ROOT/"runtime").mkdir(parents=True,exist_ok=True)
    return sqlite3.connect(core.ROOT/"runtime"/"requests.db",timeout=10)

@asynccontextmanager
async def lifespan(app):
    app.state.model,app.state.meta = core.load(core.active())
    with closing(connect()) as db, db:
        db.execute("CREATE TABLE IF NOT EXISTS predictions (id TEXT PRIMARY KEY, ts TEXT, version TEXT, features TEXT, probability REAL, latency_ms REAL)")
    yield

app = FastAPI(title="Maintenance ML Service", version="1.0.0",lifespan=lifespan)
@app.get("/health")
def health(): return {"status":"ok","model_version":app.state.meta["version"]}
@app.get("/model")
def model(): return app.state.meta
@app.post("/predict")
def predict(item:Measurement):
    started=time.perf_counter()
    values=[getattr(item,f) for f in core.FEATURES]
    probability=float(app.state.model.predict_proba([values])[0,1])
    elapsed=(time.perf_counter()-started)*1000
    request_id=str(uuid.uuid4())
    with closing(connect()) as db, db:
        db.execute("INSERT INTO predictions VALUES (?,?,?,?,?,?)",(request_id,datetime.now(timezone.utc).isoformat(),app.state.meta["version"],json.dumps(values),probability,elapsed))
    return {"request_id":request_id,"model_version":app.state.meta["version"],"failure_probability":probability,
            "maintenance_alert":probability>=app.state.meta["threshold"]}
@app.get("/metrics")
def metrics():
    with closing(connect()) as db, db:
        row=db.execute("SELECT COUNT(*), AVG(latency_ms) FROM predictions").fetchone()
    return {"successful_predictions":row[0],"mean_inference_ms":row[1],"scope":"persistent local successful predictions; inference time excludes database and HTTP overhead"}
