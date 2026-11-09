import argparse
import httpx
from mlops.core import data, FEATURES
p=argparse.ArgumentParser();p.add_argument("--shift",action="store_true");p.add_argument("--url",default="http://127.0.0.1:8000");a=p.parse_args()
x,_=data(seed=99,n=150)
if a.shift: x[:,1]=(x[:,1]+3).clip(0,15)
with httpx.Client(base_url=a.url,timeout=15,trust_env=False) as client:
    for row in x:
        r=client.post("/predict",json=dict(zip(FEATURES,row.tolist())));r.raise_for_status()
print("Sent 150 requests. Run: python -m mlops.cli monitor")
