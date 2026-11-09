# Practical learning route

Run the Windows guide first. Then make these changes yourself and record evidence.

1. Pipeline: explain why the scaler is fitted on training data only. Compare saved-pipeline inference with your own manual prediction.
2. Validation: send a missing field, out-of-range RPM and extra key. Explain the 422 responses.
3. Evaluation: read the confusion matrix as [[TN, FP], [FN, TP]]. Compute precision and recall at 0.3. Explain why accuracy alone is misleading with rare failures.
4. Monitoring: run normal and shifted traffic. Explain why 10 requests are insufficient and why drift does not prove worse accuracy.
5. Releases: train v2, compare metadata, promote and restart. Roll back and prove /health reports v1.
6. CI: intentionally break a test in a branch, observe a failed run, fix it and obtain a green run. Do not merge a deliberately broken branch.
7. Extend: add total HTTP request/error counts and end-to-end latency instrumentation, with a test that an invalid request is counted. Current /metrics does not do this.
8. Feedback: design a label table keyed by request_id and a join to compute delayed precision/recall by model version. Do not treat invented outcomes as real measurements.

Interview prompts: What did you deploy? Who uses it? How are features validated? What is persisted? How do you detect drift? What does monitoring fail to capture? How do releases and rollback work? What would change for multiple replicas? What did you implement yourself? Be explicit that users and traffic are simulated unless that changes.
