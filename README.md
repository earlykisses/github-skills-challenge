# GitHub Challenge

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey there!

Your challenge is ready.
Follow the instructions provided for this challenge and complete the required tasks in this repository.

Make sure your work is committed and pushed to your repository before submission.

Good luck!


---

&copy; 2025 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)

# AIOps Service Monitoring Assessment

## Scenario
This project simulates an AIOps workflow for monitoring a payment service. The service emits operational records containing metrics and log entries. The goal is to detect unusual behaviour, raise anomaly events, pass those events through an in-memory event stream, and produce an AIOps output that highlights the operational issue.

The service being monitored is "payment-service".  

## Operational Data Description
The repository includes synthetic telemetry in "data/service_data.json". Each record contains:

- `timestamp`: when the observation was recorded
- `service`: application/service name
- `response_time_ms`: latency metric
- `cpu_percent`: CPU utilization metric
- `memory_percent`: memory utilization metric
- `log_level`: log severity
- `message`: textual log message

Metrics are:
- `response_time_ms`
- `cpu_percent`
- `memory_percent`

Log information is:
- `log_level`
- `message`

The timestamp is used as the event time for each observation. It allows the service behaviour to be correlated across time and helps identify abrupt changes in health.

Examples of normal behaviour include records with a response time below ~150 ms, CPU below 60%, memory below 60%, and `INFO` log entries such as:

- `"Payment request processed successfully"`

These data points represent normal processing under expected operating conditions.


The unusual records are clearly around the later timestamps in the dataset:

  {
    "timestamp": "2026-09-20T10:05:00",
    "service": "payment-service",
    "response_time_ms": 610,
    "cpu_percent": 75,
    "memory_percent": 70,
    "log_level": "ERROR",
    "message": "Payment service timeout"
  },
  {
    "timestamp": "2026-09-20T10:06:00",
    "service": "payment-service",
    "response_time_ms": 640,
    "cpu_percent": 94,
    "memory_percent": 91,
    "log_level": "ERROR",
    "message": "Database connection timeout"
  },

These indicate a service degradation event, including timeout-like errors and elevated resource pressure.


- `data/service_data.json`: operational records used for detection
- `src/anomaly_detector.py`: identifies abnormal observations using configured thresholds
- `src/event_topic.py`: in-memory event stream/topic abstraction
- `src/event_producer.py`: publishes events to the topic
- `src/event_consumer.py`: reads events from the topic
- `src/aiops_pipeline.py`: orchestrates end-to-end processing

## Anomaly Detection Findings
The provided detection logic uses thresholds for:

- response time over 500 ms
- CPU over 80%
- memory over 80%
- error-level logs (`ERROR`)

When run against the synthetic service data, the detector flags two anomalies:

1. `2026-09-20T10:05:00`
   - `High response time`
   - `Error log detected`

2. `2026-09-20T10:06:00`
   - `High response time`
   - `High CPU utilization`
   - `High memory utilization`
   - `Error log detected`

These anomalies are readable and explain why each record was flagged. The detection is effective for the provided dataset and does not incorrectly flag the normal `INFO` records.

One limitation is that this approach is a simple threshold-based detector. It does not model seasonality, service baselines, or multi-signal anomaly scoring, so it may miss subtle degradation patterns or overreact to one noisy metric.

## Workflow
The workflow is:

Operational Data → Anomaly Detection → Event → Producer → Topic → Consumer → AIOps Output

This is implemented in the lightweight event simulation:

- `AnomalyDetector.detect()` identifies an anomaly record
- `EventProducer.publish()` sends the event to the topic
- `EventTopic` stores the event in memory
- `EventConsumer.consume()` reads the event from the topic
- `run_pipeline()` collects the consumed events and returns the final AIOps result

## Final Workflow Result
The end-to-end pipeline was executed successfully with the project code. The final AIOps output reported:

- `Records processed: 10`
- `Anomalies detected: 2`
- `Events consumed: 2`

Observed issue summary:

- Payment service latency increased dramatically above normal thresholds
- CPU and memory usage rose sharply during the failure period
- Error-level logs indicate service degradation and timeout conditions

## Issues Identified and Corrected
The assessment environment included a few workflow issues that were corrected without changing the overall architecture:

1. The detector was checking for `WARNING` instead of `ERROR` log severity.
   - Affected component: `src/anomaly_detector.py`
   - Cause: log-level comparison did not match the actual dataset
   - Fix: updated the condition to flag `ERROR` logs

2. The event producer and consumer were using mismatched topics.
   - Affected component: `src/aiops_pipeline.py`
   - Cause: the producer sent events to one topic while the consumer read from another
   - Fix: both components now operate on the same `anomaly-events` topic

3. The project imports did not resolve correctly under pytest collection.
   - Affected components: `tests/test_aiops_pipeline.py`, `src/event_producer.py`, `src/event_consumer.py`, `src/aiops_pipeline.py`
   - Cause: package imports were not being resolved consistently in the test environment
   - Fix: project root was added to `sys.path` in the test and imports were updated to use package-qualified module names
4. to validate and test PYTHONPATH=. python -m src.aiops_pipeline and "pytest --cov=src --verbose"

5. Review the output to confirm that the service data is processed and the anomaly events are produced and consumed.

## Validation
The repository validation passes successfully. The test suite confirms:

- operational data can be processed
- anomaly detection behaves as expected
- anomaly events are generated
- the simulated event flow works end to end

The key verification command used was:

cd /workspaces/github-skills-challenge && pytest --cov=src --verbose

It completed successfully with `8 passed`.
