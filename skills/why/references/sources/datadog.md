# Infrastructure observability (example: Datadog)

Written against the Datadog MCP server; adapt for New Relic, Honeycomb, Grafana, or Splunk.

## What's here

The record of what actually happened in production, as opposed to what was planned.

- **Metrics.** A metric's existence is evidence that someone thought the number worth watching.
- **Monitors and alerts.** Conditions the team decided should page someone. A monitor on `rate_limit_hit > 10/min` shows the team cared about that threshold.
- **Dashboards.** What the team considers important for a subsystem.
- **APM traces and spans.** Request-level data, useful for "why is this timeout here".
- **Logs.** Often contain the error conditions that motivated defensive code.
- **Incidents.** Formal records with timelines and linked postmortems.
- **Notebooks.** Exploratory analyses and hypotheses.

## How to search

Start broad, then narrow.

1. **Find the owning services**: `search_datadog_services`, `search_datadog_service_dependencies` for upstream and downstream.
2. **Dashboards and monitors first**, since they show what the team watches: `search_datadog_dashboards`, `search_datadog_monitors`, queried by feature, service, and symbol names. Note the queries and thresholds. A monitor's threshold often answers "why is this clamped at N?"
3. **Metrics around the target**: `search_datadog_metrics` by name pattern, `get_datadog_metric_context` for description and units, `get_datadog_metric` for the time series. A metric trajectory that lines up with the change date is strong support: "`payment_timeout` spiked on 2023-11-03; the retry logic merged on 2023-11-06."
4. **Logs, narrowly**: `search_datadog_logs` with `use_log_patterns=true`, searching symbols, error strings, or feature names; `analyze_datadog_logs` when you need counts. Always bound the time window (for example 30 days either side of the change). Unbounded log searches are slow and may time out.
5. **Spans and traces**: `aggregate_spans` for failure rates, `search_datadog_spans` for individual spans, `get_datadog_trace` for one trace. Useful for timeouts, retries, slow paths, and cross-service behavior.
6. **Incidents**: `search_datadog_incidents` by title, team, or date, then `get_datadog_incident`. For defensive code, look for incidents around when it was added. A timeline entry like "added defensive check for X" is close to direct evidence.

## Good evidence

- A monitor whose query and threshold match what the code enforces (code clamps at 100; the monitor alerts above 100/min)
- A dashboard created by the target's author, with widgets matching what the code measures or guards
- A production spike just before the merge and stable values after
- An incident record that references the target code, its symbols, or its error strings
- Logs showing the error the code prevents, timestamped before the change

## Pitfalls

- **Correlation isn't causation.** A spike before and calm after is suggestive only. Check other PRs that landed in the same window.
- **A chart reflects its author's framing.** A "retry success rate" chart shows the team cared about retries, not that it explains a specific line.
- **Missing telemetry.** Metrics get renamed or deleted, and retention is limited. Missing data for the window is a gap, not a null result.
- **Volume.** Common strings match thousands of logs. Narrow by service, tag, and time, and aggregate rather than dumping.
- **Instrumented isn't caused.** A metric's existence doesn't mean the code was added because of it. Cross-check against commit and PR dates.

## What to return

For each relevant item: type (dashboard, monitor, metric, log pattern, trace, incident, notebook), name, ID or link, owner and created/modified dates, the condition, query, or quote that bears on the question (verbatim where possible), and what it suggests about the target and how strongly.
