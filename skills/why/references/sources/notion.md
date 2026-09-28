# Long-form docs (example: Notion)

Written against the Notion MCP server; adapt for Confluence, Google Docs, or Coda.

## What's here

- PRDs, technical specs, RFCs, and ADRs
- Design review meeting notes
- Team pages with domain context
- Incident postmortems and runbooks (which often explain defensive code)
- Strategy documents that set priorities

A significant feature usually has a doc, and the doc often states the reason before the code exists.

## How to search

1. **Keyword search** (`notion-search`) for the feature name, key symbols and class names, the PR author, error strings and user-facing terms. Bound by date if you know when the code shipped.
2. **Fetch candidate pages in full** (`notion-fetch`). The rationale is often in the middle of the document, not the preview.
3. **Follow child pages and backlinks.** Alternatives-considered and appendix sub-pages are common.
4. **Query related databases and meeting notes** (`notion-query-data-sources`, `notion-query-meeting-notes`) for discussions of the decision.
5. **Check the author's personal space** if the org uses them; exploratory notes sometimes precede the code.

## Good evidence

- A PRD with a problem statement or motivation matching the target's purpose
- An "Alternatives considered" or "Rejected approaches" section
- A postmortem naming the target as the fix for an incident
- Meeting notes recording "we decided X because Y", matching the PR's author and dates
- A filled-in ADR (status, context, decision, consequences)

## Pitfalls

- **Outdated specs.** Docs written before implementation often aren't updated. Compare with the PR.
- **Doc says X, code does Y.** Report the divergence; the synthesizer will surface it.
- **Template filler.** Look for specifics.
- **Unlinked docs.** The most relevant page may not be linked anywhere; broad keyword searches help.
- **Multiple drafts.** Find the finalized or most recently updated one.
- **No access.** Record inaccessible pages as gaps.

## What to return

For each relevant doc: title and URL, authors and last-updated date, the motivation quoted verbatim with its section, relevant linked pages, and whether it's final or a draft.
