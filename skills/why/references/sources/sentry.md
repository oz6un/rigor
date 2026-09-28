# Error tracking (example: Sentry)

Written against the Sentry MCP server; adapt for Rollbar, Bugsnag, or Airbrake.

## What's here

The record of what went wrong. For defensive, corrective, or error-handling code, it often holds the direct motivation: the exceptions, stack traces, and frequencies that led someone to add a check, catch, retry, or fallback.

- **Issues**: grouped errors with counts, first/last seen, affected releases, comments
- **Events**: individual occurrences with stack traces, tags, and user context
- **Releases**: deploy records with their issues ("which version fixed this?")
- **Replays**: session recordings of user-facing errors, if enabled
- **Comments and assignments**: sometimes carry an engineer's root-cause notes

Its most valuable signal is timing: "issue X first appeared 2024-01-02, peaked at 500 events/day, and stopped after v2.14.0 on 2024-01-15, the release with the defensive check."

## How to search

1. **Orient**: `find_organizations`, `find_projects` if you don't know the org and project.
2. **Find related issues**: `search_issues` in natural language ("timeouts in PaymentService", "unhandled exceptions in uploadFile"), using the exception classes the target handles, its function or class names, the error messages it checks for, and its file path.
3. **Narrow by release and time**: `search_issue_events` (release, time, environment, tags) and `get_issue_tag_values`. For each candidate, check first seen, last seen, affected releases, and the frequency trend against the target's ship date.
4. **Read full events**: `get_sentry_resource` with a URL or type and ID. Does the stack trace pass through the target? Do the tags and breadcrumbs match what the target guards against?
5. **Check nearby releases**: `find_releases` around the commit date, and match release versions to the PR merge date.
6. **Treat AI root-cause analysis (Seer, `analyze_issue_with_seer`) as a hypothesis generator.** The events, traces, and timestamps are the evidence.

## Good evidence

- An issue first seen shortly before the target's PR and last seen shortly after
- Stack traces that pass through or end in the target function
- A comment on the issue from the PR author describing the fix
- A PR or commit message referencing a Sentry issue
- A high-volume issue that stops after the release containing the target

## Pitfalls

- **Regrouping.** Refactors can move the same error to a new issue ID. If an issue ends abruptly, look for a new one starting right after.
- **Releases contain many commits.** An issue stopping at a release doesn't prove the target fixed it. Match against the exact commit.
- **Upstream fixes.** The error may have stopped because something upstream changed.
- **"Resolved" is a manual marker**, not proof that code fixed anything.
- **AI analyses can be confidently wrong.** Base claims on events and timestamps.
- **Sampling.** A low count may reflect aggressive sampling. Note it when unsure.

## What to return

For each relevant issue: ID and title, project and org, first/last seen, event count (and sampling rate if known), affected releases, a verbatim stack-trace excerpt showing the connection to the target, how its timing lines up with the ship date, a link, and any author comments or resolution notes.
