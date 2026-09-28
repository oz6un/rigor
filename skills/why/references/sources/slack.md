# Team chat (example: Slack)

Written against a Slack MCP server; adapt for Discord, Teams, or Mattermost. Chat tools vary between servers, so read the tool list and schemas first. If the server needs authentication and it fails, stop and report the gap. Don't produce findings from a source you couldn't search.

## What's here

- Real-time problem-solving and decisions
- Incident channels where decisions were made under pressure
- Design threads where tradeoffs were debated
- Answers from senior engineers that never reached a doc
- Post-merge discussions explaining why something was revisited
- DMs (usually not searchable)

For smaller changes that didn't get a doc, chat is often where the decision was actually made. It's also the least durable source: threads get deleted, channels archived, and old messages expire.

## How to search

1. **Author and date.** Messages from the PR author around the merge date. This narrows the search a lot and often finds the discussion.
2. **Keywords**: the feature name and key symbols, including casual phrasings and misspellings.
3. **PR links**: the PR URL or `/pull/<number>`, since PRs are often linked when discussed.
4. **Error strings** the code handles; incident threads tend to surface.
5. **Likely channels**: engineering (`#eng-*`), project (`#proj-*`), incident (`#incident-*`, `#sev-*`), the owning team's channels, design review channels.
6. **Whole threads.** When a message looks relevant, fetch its thread; the decision is often in the replies.

## Good evidence

- A thread that debates tradeoffs ("I was going to use A, but B is better because...")
- An incident message describing the bug the code prevents
- A reviewer's question with an answer from the author or lead
- A reference to a meeting where the decision was made
- A PM or customer-facing engineer explaining a customer request

## Pitfalls

- **Retention limits.** If nothing exists before a certain date, report the cutoff.
- **DMs** usually aren't searchable. Note it as a known limitation.
- **Jokes aren't decisions.** "lol just do the thing" isn't a rationale, even if it preceded the commit.
- **Messages out of context** read differently than in their thread. Always fetch the thread.

## What to return

For each relevant thread: channel, permalink or thread ID, participants, date range, the key quotes verbatim with attribution, and what larger discussion or incident it belonged to.
