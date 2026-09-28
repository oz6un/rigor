# Incidents and postmortems

Not a separate source but an extra angle for every investigator. Incidents often motivate defensive code ("we added this check after the X outage"), so when the target looks defensive (null checks, retries, timeouts, rate limits, feature flags), look for incident history inside your own source:

- **Long-form docs**: postmortems that mention the target file, feature, or error string.
- **Issue tracker**: tickets labeled `incident`, `sev-*`, `postmortem-action-item`, or `reliability`.
- **Team chat**: incident channels (`#incident-*`, `#sev-*`) around the date the code was added.
- **Source control**: messages like "fix for incident" or "add defensive check", and a revert followed by "re-apply with...".
- **Infrastructure observability**: formal incident records with timelines, and dashboards or monitors created as postmortem action items.
- **Error tracking**: issues whose first/last-seen window brackets the target's ship date, with stack traces through the target.
- **Analytics warehouse**: user-facing error events that spike during the incident and drop after the target ships. This supports the target fixing the visible symptom even when observability and error-tracking signals are noisy.

When you find an incident link, fetch the full postmortem. Its action items usually map directly to code changes. Evidence is strongest when sources corroborate each other: an incident ID in a ticket, the ticket in a postmortem, the postmortem linked from a chat thread that links the target PR, and the error-event count dropping after the fix.

Skip this angle for code that doesn't look defensive.
