# Issue tracker (example: Linear)

Written against the Linear MCP server; the same approach works for Jira, GitHub Issues, or Shortcut with their equivalent tools.

## What's here

- Issues describing features and bugs and why they were needed
- Project docs attached to issues (often PRDs or specs)
- Parent and sub-issue trees (initiative to task)
- Comments with clarifications, scope changes, and rationale
- Labels (`compliance`, `customer-request`, `perf`) that signal the kind of motivation
- Status updates and linked PRs

The tracker is where product and business context usually lives: "customer X asked for this", "this is for the Q3 compliance work".

## How to search

1. **Start with linked tickets.** If the seed commits or PRs reference IDs (`ENG-1234`, `[BUG-567]`), fetch those first (`get_issue`) and read them in full, including comments.
2. **Search by keyword** (`list_issues` with a text query) for the feature name, key symbols, and business terms. Try several phrasings.
3. **Walk up the tree.** Sub-issues are tactical; the parent often holds the reason.
4. **Read project docs** (`get_project`). Specs and rationale are often attached at the project level.
5. **Check labels and milestones.** Labels hint at the motivation; milestones tie work to deadlines.

## Good evidence

- A description stating the business problem: "Acme needs X for their SOC2 audit"
- A comment recording a decision: "going with B because A would require touching the billing service"
- A parent issue named like an initiative: "Reduce payment failures"
- An attached PRD or spec
- Labels like `customer:acme`, `incident-followup`, `compliance`, `perf-regression`

## Pitfalls

- **Scope drift.** A ticket may have been closed and reopened with a different scope. Read the history.
- **Template filler.** A required "Why" section filled with "improve user experience" isn't an answer.
- **Stale tickets.** Plans change. Compare the ticket's dates with the code's ship date.
- **Duplicate chains.** Follow duplicate-of links to the canonical ticket.
- **No access.** Record an inaccessible issue as a gap rather than guessing.

## What to return

For each relevant ticket: ID and title, the motivation quoted verbatim from the description or comments, labels, parent, and project, author with created and closed dates, and a link.
