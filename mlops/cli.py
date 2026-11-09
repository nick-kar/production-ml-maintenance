import argparse, json, sqlite3
from contextlib import closing
import numpy as np
from mlops import core

def monitor():
    path=core.ROOT/"runtime"/"requests.db"
    if not path.exists(): raise ValueError("Send predictions first")
    with closing(sqlite3.connect(path)) as db, db:
        rows=db.execute("SELECT features, version FROM predictions ORDER BY rowid DESC LIMIT 1000").fetchall()
    reports=[]
    for version in sorted({r[1] for r in rows}):
        x=np.array([json.loads(r[0]) for r in rows if r[1]==version])
        _,meta=core.load(version)
        shift=np.abs(x.mean(axis=0)-np.array(meta["reference_mean"]))/np.maximum(meta["reference_std"],1e-8)
        reports.append({"model_version":version,"samples":len(x),"sufficient_samples":len(x)>=100,
            "mean_shift_in_reference_std":dict(zip(core.FEATURES,shift.tolist())),
            "drift_alert":bool((shift>1).any()) if len(x)>=100 else None})
    output={"reports":reports,"method":"demo heuristic: absolute mean shift > 1 reference standard deviation; at least 100 requests per version","warning":"Feature drift is not measured model accuracy. Repeated demo requests are not representative traffic."}
    (core.ROOT/"runtime"/"drift_report.json").write_text(json.dumps(output,indent=2))
    return output

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    t=sub.add_parser("train");t.add_argument("--version",required=True);t.add_argument("--seed",type=int,default=42);t.add_argument("--c",type=float,default=1)
    t=sub.add_parser("promote");t.add_argument("version")
    sub.add_parser("monitor")
    a=p.parse_args()
    if a.command=="train": result=core.train(a.version,a.seed,a.c)
    elif a.command=="promote": core.promote(a.version);result={"active":a.version,"next":"Restart API to load this version"}
    else: result=monitor()
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
