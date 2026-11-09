# Model card

Task: predict a synthetic sampled failure event from temperature, vibration, RPM and wear. No real measurements, organizations, people or machine identifiers are used.

Generation: 6,000 seeded feature vectors; clipped normal distributions and a logistic failure probability with Bernoulli sampling. RPM is intentionally an uninformative feature. There is no simulated chronology, so the stratified random holdout is suitable for this toy process; real deployment would require asset/time-aware evaluation.

Model: standardized logistic regression. Evaluate on 25% held-out data using average precision, ROC AUC, prevalence and confusion matrix. No hyperparameter selection on the test set is automated. Repeatedly selecting versions using this test set would bias evaluation; use validation plus a final untouched holdout when extending the project.

Threshold 0.3 is illustrative. Establish actual false-positive/false-negative costs and choose a threshold on validation data before real use. Probabilities are not established as calibrated for real equipment.

Limitations: synthetic distribution, no temporal dependencies, no label-feedback pipeline, simple marginal mean-shift monitoring misses many distribution changes, no verified external validity. Do not use for actual maintenance or safety decisions.
