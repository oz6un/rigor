# Source playbooks

`why` runs one investigator per available evidence category, and each gets the one playbook below that matches its category. Each playbook is a worked example for one common tool; adapt it to whichever server in that category is actually available.

| Category | Playbook | Documents | Adapt for |
|---|---|---|---|
| Source control | [`code-archaeology.md`](./sources/code-archaeology.md) | git, `gh` | — |
| Issue tracker | [`linear.md`](./sources/linear.md) | Linear | Jira, GitHub Issues, Shortcut |
| Long-form docs | [`notion.md`](./sources/notion.md) | Notion | Confluence, Google Docs, Coda |
| Team chat | [`slack.md`](./sources/slack.md) | Slack | Discord, Teams, Mattermost |
| Infrastructure observability | [`datadog.md`](./sources/datadog.md) | Datadog | New Relic, Honeycomb, Grafana, Splunk |
| Error tracking | [`sentry.md`](./sources/sentry.md) | Sentry | Rollbar, Bugsnag, Airbrake |
| Analytics warehouse | [`analytics-warehouse.md`](./sources/analytics-warehouse.md) | Any SQL warehouse | Snowflake, BigQuery, Databricks, ClickHouse, Redshift, dbt |

Cross-cutting: [`incident-postmortem.md`](./sources/incident-postmortem.md). Add it to every investigator's prompt when the target looks defensive (null checks, retries, timeouts, rate limits, feature flags, egress guards, OOM handlers).
