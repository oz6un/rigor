# Analytics warehouse

Written for any SQL warehouse reachable through an MCP server (Snowflake, BigQuery, Databricks, ClickHouse, Redshift, often modeled with dbt). Use the server's read-only query tool. If a query returns a statement or job ID, poll for the result instead of rerunning it.

## What's here

The product and data view, complementing infrastructure observability's runtime view: what users did, which experiments ran, how feature usage changed, where a threshold constant came from.

- **Product analytics events**: raw event tables and, often, cleaned per-event models (deduplicated, typed columns). Feature usage, clicks, accepts and rejects, client-reported errors.
- **Usage and billing events**, for cost- or volume-driven decisions.
- **Experiment and feature-flag data**: exposure and outcome tables. Names are company-specific.
- **Warehouse system tables** (query history, compute, billing, access audit), where the warehouse exposes them: "was this query expensive?", "how often did anyone run it?"
- **Model lineage** (dbt or similar): which pipelines depend on a table or field. Upstream changes often explain consumer code changes.
- **Notebooks** usually aren't reachable through a SQL tool. If the rationale likely lives in one, report it as a gap.

## How to search

**Confirm table names before querying.** Schemas are company-specific. List tables and describe the candidates first (`SHOW TABLES ... LIKE '%<keyword>%'`, `DESCRIBE TABLE`, or `information_schema`).

**Bound every query by time.** Event tables are large and unbounded scans time out. Filter on the event timestamp with a window around the ship date, typically about 30 days either side.

**Prefer the cleaned models over raw events.** Raw tables often have duplicates and untyped JSON properties. Use raw data only when no model exists yet or you need events newer than the model's refresh.

Patterns that tend to pay off:

1. **Usage over time.** Daily counts of the relevant event across a window around the PR merge. A jump from zero to steady volume within a day or two of the merge suggests the PR launched the feature; a decay to zero suggests a deprecation.
2. **Where a threshold came from.** The distribution (median, p99, max) of the relevant property in the two weeks before the PR. A p99 that matches the target's constant suggests the number was chosen from data.
3. **Experiments and flags.** Find the exposure table, then pull exposure counts by variant for the target's flag key around the PR date.
4. **Expensive queries behind migrations, backfills, or perf rewrites.** Search query history for the table or symbol in a tight window and sort by duration or bytes read.
5. **Lineage.** If the target reads or writes a modeled table, the model's own git history often explains it. Hand that lead to the source-control investigator.

## Good evidence

- An error-classifying event that drops to near zero after a defensive-code PR
- An experiment record naming the target's flag key with a shipped or concluded decision near the PR date
- A pre-PR distribution whose tail matches the target's threshold

## Pitfalls

- **Instrumented isn't caused.** An event exists because someone wanted to log it, not necessarily because of the target. Pair it with a PR or commit citation before claiming cause.
- **Instrumentation changes.** A step in volume may mean a new event started being logged, not that behavior changed. Check for instrumentation PRs in the same window.
- **Schema drift.** A column may not have existed when the target was written; older data may keep the value only in raw JSON.
- **Refresh lag.** Modeled tables rebuild on a schedule. For the last few hours, use raw events and deduplicate.
- **Unconfirmed tables.** Reporting results from a table whose existence you never checked is a common mistake. Probe first.
- **Retention.** If the window predates retention or the model's creation, that's a gap, not a null result. Say so explicitly.

## What to return

For each finding: type (product event, experiment exposure, usage or billing event, system-table row, model lineage), fully qualified table name and the exact query, the time window, a compact numeric summary (counts, percentiles, first/last seen; no raw row dumps), how it lines up with the ship date ("first row 2024-08-15; PR #4907 merged 2024-08-14"), and strength (direct, circumstantial, weak).
