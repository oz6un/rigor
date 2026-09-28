# Source control (git and in-repo)

## What's here

- Commit history: messages, dates, authors, diffs
- PR descriptions, review comments, and discussion (via `gh`)
- Inline comments, TODOs, FIXMEs, deprecation notes
- ADRs, if the repo keeps them
- Tests, whose names and assertions often encode the edge case that motivated a change
- Files changed in the same commits (co-change signal)
- CHANGELOG entries and release notes
- Ticket IDs mentioned in commits and PR bodies

This is the source most directly tied to the code and usually the most complete.

## How to search

Expand the seed commit list:

```bash
git log --follow --oneline -- <file>        # history through renames
git log -S '<exact string>' -- <file>       # commits that added or removed this text
git log -G '<regex>' -- <file>              # same, by pattern
git blame -L <start>,<end> <file>           # who last touched each line, and when
git show <hash>                             # full diff of one commit
git log <old>..<new> -p -- <file>           # changes between two points
```

For each substantive commit, pull the PR. The `reviews` and `comments` fields usually carry the most signal:

```bash
git log -1 --format=%B <hash>
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews,files
```

Look for in-repo docs and tests:

```bash
rg -l -i 'architecture.decision' --glob '*.md'        # ADRs, often under docs/adr/
rg -n -C2 '(TODO|FIXME|HACK|XXX|NOTE)' <file>
rg -l '<symbol>' --glob '*test*'
```

## Good evidence

- A PR description that explains the problem, not only the change
- A review thread where alternatives were debated
- A comment near the target line explaining a non-obvious constraint
- A test like `test_handles_edge_case_when_X`
- A commit message referencing a ticket or incident ID
- A CHANGELOG entry stating the user-visible reason

## Pitfalls

- **Squash merges** erase branch commits. Fall back to the PR body and comments.
- **Misleading messages.** "Small refactor" sometimes hides an intentional behavior change. Read the diff.
- **Copied patterns.** The author may have copied a pattern without knowing its reason. Find where it first appeared and investigate that commit.
- **Bot commits** (Dependabot, Renovate, automated backports) rarely carry motivation. Skip them.
- **Code as evidence of intent.** "The function is named X" isn't evidence of why it exists.

## What to return

Each commit, PR, or comment that bears on the question, with the exact quoted text, the hash / PR number / `file:line`, author and date, and whether it's direct or circumstantial.
