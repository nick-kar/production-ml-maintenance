import tempfile, unittest
from pathlib import Path
from fastapi.testclient import TestClient
from mlops import core
from mlops.api import app
from mlops.cli import monitor

class SystemTests(unittest.TestCase):
    def setUp(self):
        self.old=core.ROOT;self.temp=tempfile.TemporaryDirectory();core.ROOT=Path(self.temp.name)
        core.train("v1");core.promote("v1")
    def tearDown(self): core.ROOT=self.old;self.temp.cleanup()
    def test_prediction_validation_and_persistence(self):
        payload=dict(zip(core.FEATURES,[75,3,1500,110]))
        with TestClient(app) as c:
            r=c.post("/predict",json=payload);self.assertEqual(r.status_code,200)
            expected=app.state.model.predict_proba([[75,3,1500,110]])[0,1]
            self.assertAlmostEqual(r.json()["failure_probability"],expected)
            self.assertEqual(c.post("/predict",json={**payload,"rpm":-1}).status_code,422)
            self.assertEqual(c.post("/predict",json={**payload,"unknown":1}).status_code,422)
            self.assertEqual(c.get("/metrics").json()["successful_predictions"],1)
        with TestClient(app) as c: self.assertEqual(c.get("/metrics").json()["successful_predictions"],1)
    def test_version_switch_rollback_and_missing_version(self):
        core.train("v2",c=.5);core.promote("v2")
        with TestClient(app) as c:self.assertEqual(c.get("/health").json()["model_version"],"v2")
        core.promote("v1")
        with TestClient(app) as c:self.assertEqual(c.get("/health").json()["model_version"],"v1")
        with self.assertRaises(FileNotFoundError):core.promote("missing")
        self.assertEqual(core.active(),"v1")
    def test_detects_shift_and_insufficient_samples(self):
        with TestClient(app) as c:
            c.post("/predict",json=dict(zip(core.FEATURES,[75,8,1500,110])))
            self.assertIsNone(monitor()["reports"][0]["drift_alert"])
            for _ in range(100):c.post("/predict",json=dict(zip(core.FEATURES,[75,8,1500,110])))
        self.assertTrue(monitor()["reports"][0]["drift_alert"])
    def test_database_connections_close_without_garbage_collection(self):
        import sqlite3
        from unittest.mock import patch
        from mlops import api
        original_connect = sqlite3.connect
        connections = []
        def tracked(*args, **kwargs):
            connection = original_connect(*args, **kwargs)
            connections.append(connection)
            return connection
        with patch.object(sqlite3, "connect", side_effect=tracked):
            with TestClient(app) as client:
                client.post("/predict", json=dict(zip(core.FEATURES,[75,3,1500,110])))
                client.get("/metrics")
                monitor()
        self.assertGreaterEqual(len(connections), 4)
        for connection in connections:
            with self.assertRaises(sqlite3.ProgrammingError):
                connection.execute("SELECT 1")

    def test_reproducible_training_and_immutable_versions(self):
        m=core.train("repeat")
        import json
        old=json.loads((core.version_path("v1")/"metadata.json").read_text())
        self.assertEqual(m["metrics"],old["metrics"])
        with self.assertRaises(ValueError):core.train("v1")
        with self.assertRaises(ValueError):core.promote("../escape")
if __name__=="__main__":unittest.main()
