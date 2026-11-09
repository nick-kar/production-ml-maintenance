import json, os, re, hashlib
from pathlib import Path
import numpy as np
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score, roc_auc_score, confusion_matrix
ROOT = Path(os.environ.get("ML_ROOT", Path(__file__).resolve().parents[1]))
FEATURES = ["temperature_c", "vibration_mm_s", "rpm", "tool_wear_min"]
def data(seed=42, n=6000):
    rng = np.random.default_rng(seed)
    x = rng.normal([75, 3, 1500, 110], [10, 1, 220, 55], (n, 4))
    x = np.clip(x, [20, 0, 100, 0], [150, 15, 5000, 500])
    z = -3 + .09*(x[:,0]-75) + 1.3*(x[:,1]-3) + .015*(x[:,3]-110)
    y = rng.binomial(1, 1/(1+np.exp(-z)))
    return x, y

def version_path(version):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", version):
        raise ValueError("Version must contain 1-40 letters, digits, underscores or hyphens")
    return ROOT / "artifacts" / version

def train(version, seed=42, c=1.0):
    dest = version_path(version)
    if dest.exists(): raise ValueError("Version already exists; choose a new version")
    x,y = data(seed)
    a,b,ya,yb = train_test_split(x,y,test_size=.25,random_state=42,stratify=y)
    model = make_pipeline(StandardScaler(), LogisticRegression(C=c,max_iter=1000))
    model.fit(a,ya)
    prob = model.predict_proba(b)[:,1]
    # Fixed threshold is a documented demo policy, never tuned on this test set.
    metrics = {"average_precision":float(average_precision_score(yb,prob)),
               "roc_auc":float(roc_auc_score(yb,prob)),"positive_prevalence":float(yb.mean()),
               "confusion_matrix_at_0_3":confusion_matrix(yb,prob>=.3).tolist()}
    import sklearn
    metadata = {"version":version,"seed":seed,"C":c,"threshold":.3,
                "features":FEATURES,"sklearn_version":sklearn.__version__,"metrics":metrics,
                "reference_mean":a.mean(axis=0).tolist(),"reference_std":a.std(axis=0).tolist(),
                "data_sha256":hashlib.sha256(x.tobytes()+y.tobytes()).hexdigest(),
                "data_kind":"synthetic; not validated for real machinery"}
    dest.mkdir(parents=True)
    joblib.dump(model,dest/"model.joblib")
    (dest/"metadata.json").write_text(json.dumps(metadata,indent=2))
    return metadata

def load(version):
    path = version_path(version)
    meta = json.loads((path/"metadata.json").read_text())
    import sklearn
    if meta["sklearn_version"] != sklearn.__version__:
        raise ValueError("scikit-learn version mismatch; retrain in this environment")
    # Only load locally generated, trusted artifacts.
    return joblib.load(path/"model.joblib"),meta

def promote(version):
    load(version)
    pointer = ROOT/"artifacts"/"active.json"
    temp = pointer.with_suffix(".tmp")
    temp.write_text(json.dumps({"version":version}))
    temp.replace(pointer)

def active():
    return json.loads((ROOT/"artifacts"/"active.json").read_text())["version"]
