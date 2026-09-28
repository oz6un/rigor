# Review bot triage

Use this when the Babysit playbook (`../playbooks/babysit.md`) handles comments from an automated PR reviewer: Codex review, Claude review, Copilot, CodeRabbit, Bugbot, an automated security review, or similar. These tools find real bugs and also file noise. The goal is to judge each comment on its merits, not to ignore bots by default and not to treat every comment as a required change.

## Decision rubric

Classify each thread before acting:

- `fix`: the comment identifies a plausible correctness, security, privacy, data-loss, auth, billing, migration, idempotency, race, or shipped-behavior problem. Fix it in the lowest PR that owns the code, reply with the commit SHA, and resolve the thread.
- `dismiss`: the comment matches a documented low-risk noise pattern below, and the current code proves no change is needed. Reply with a short, concrete reason and resolve the thread.
- `ask`: the comment is novel, high-severity, touches security, privacy, or data, or is ambiguous. Ask the user instead of guessing.

When unsure, ask. Skipping a noisy style comment costs little; skipping a real data or security bug costs a lot.

Some claims are cheap to check directly. If a comment says a test no longer matches the code or docs, run the test on the PR tip before classifying it: a failure confirms the claim, and a pass is the disproof for your reply.

## Always ask

Don't dismiss these on your own, even if a similar comment was dismissed on an earlier PR:

- Security, privacy, auth, billing, data retention, training-data, and permission-boundary findings.
- High-severity findings.
- Migration, schema, idempotency, concurrency, and cross-system behavior findings.
- Comments whose suggested fix is small and clearly reduces risk without changing product intent.

A human dismissing a security or data-flow comment on one PR is that owner's judgment call, not a team-wide rule.

## Pattern format

Record new patterns in this shape:

```markdown
### <short pattern name>

- Confidence: candidate | recurring | strong
- Dismiss when: <conditions that must all be true>
- Don't dismiss when: <risk boundaries>
- Example signal: <phrases or code context that identify the pattern>
- Source: <PR or comment URL, or a short note>
```

Use `candidate` for one or two examples, `recurring` after several verified dismissals, and `strong` only for a narrow, low-risk pattern that has been verified many times. Add a new entry as `candidate` to the section it fits, and raise its confidence as more PRs confirm it.

## Known noise patterns

### Intentional UI or design-system visual change

- Confidence: candidate
- Dismiss when: the PR description, screenshots, design review, or nearby code makes the visual change explicit, and the comment only restates that a shared visual default changed.
- Don't dismiss when: the comment concerns accessibility, focus visibility, keyboard navigation, color contrast, or a component API contract the PR didn't mean to change.
- Example signal: comments about focus outlines, button sizes, spacing, or shared component defaults, where the owner has said the change is intended.

### Usage later in the stack that the bot can't see

- Confidence: candidate
- Dismiss when: the bot flags an export, component, helper, or file as unused, and the diffs of later PRs in the stack show it is used there.
- Don't dismiss when: the PR isn't part of a stack, the symbol is public API, or you can't verify the later use.
- Example signal: "Exported component is never used", with a human reply like "used upstack".

### Temporary duplication during a parallel implementation

- Confidence: candidate
- Dismiss when: the PR deliberately duplicates a small amount of code to keep a new path alongside an old one that is being deleted, replaced, or proven out.
- Don't dismiss when: the duplicated code affects security, billing, data access, or API behavior, or a shared abstraction would clearly reduce risk.
- Example signal: "Significant duplication" or "duplicated validation logic", where the owner explains that the old path will be deleted or the duplicate is intentionally local.

### An existing invariant already covers the concern

- Confidence: candidate
- Dismiss when: a shared component, framework contract, type invariant, or single source of truth visible in the diff or nearby code already guarantees what the comment asks for.
- Don't dismiss when: the invariant is assumed rather than enforced, depends on timing, or crosses async or state boundaries where values can diverge.
- Example signal: a missing max-height on an inner popover when the shared popover already bounds it to the viewport; a nullable value where the checked value and the passed value come from the same source.

### Follow-up the owner has already deferred

- Confidence: candidate
- Dismiss when: the PR owner has said the issue is a known follow-up, the PR doesn't make it worse, and it isn't in a high-risk area.
- Don't dismiss when: you're acting without owner input, the issue is medium- or high-severity product behavior, or deferring it would merge a new regression.
- Example signal: "I'll handle that later", "we'll delete this eventually".

### The bot withdrew the finding

- Confidence: recurring
- Dismiss when: the comment or a later reply from the bot says the finding is withdrawn, compliant, or a false positive, and you can verify the relevant rule locally.
- Don't dismiss when: the only evidence is a human calling a high-risk finding a false positive without explanation.
- Example signal: a file-naming comment whose body says the file already complies.

### Stale finding already fixed later in the same PR

- Confidence: candidate
- Dismiss when: an automated security review claims a missing authorization or validation call, and the PR tip already includes that exact check, with tests, typically added in a commit after the review ran.
- Don't dismiss when: the cited helper does nothing for the principal in question, the check runs after the side effect it should guard, or the claimed principal has no test coverage.
- Example signal: a high-severity "missing authorization check" while the tip already calls the guard before the side effect.

### Widening a deliberately narrow error condition

- Confidence: candidate
- Dismiss when: the comment asks to broaden a specific error condition (an `errno`, error code, or status class) into a catch-all, and the narrow condition encodes a real distinction. The usual case is a fallback gated on `ENOENT`: "the binary isn't installed" is different from "the command ran and failed". Retrying on any non-zero exit would rerun a legitimate failure (not found, expired auth, network) against the fallback and then report the fallback's error instead of the real one.
- Don't dismiss when: the narrow condition misses another case of the same kind (such as `EACCES` for an unusable binary), the unhandled path loses data or leaves partial state, or the retry is idempotent and still surfaces the original error.
- Example signal: "only retries when X fails with ENOENT; never tries the fallback even when a working Y exists", on code whose fallback exists for a missing dependency rather than a failed operation.

## Findings that are usually real

Patterns where bot findings have so far been real. Default to fixing these.

### Manual reimplementation of native browser behavior

- Confidence: candidate
- Dismiss when: almost never. When a diff replaces native browser behavior with a manual version (native sticky positioning replaced by JS-positioned clones, native scrolling by forwarded wheel or touch events, paint-order occlusion by masks or `clip-path`), bot findings about logic bugs in that code have consistently been real.
- Don't dismiss when: the finding concerns gaps in event forwarding (wheel `deltaMode`, touch pans, scroll chaining at edges, tap slop), hit-testing that differs under masks or clips, or timing races between an observer callback and framework state updates.
- Example signal: "masks do not affect hit-testing", "overlay blocks wheel scroll", "ignores deltaMode", "runs in the IntersectionObserver callback before React applies state".
- Source: one sticky-occlusion PR with six review passes and about eighteen findings, all fixed.

### Tests that pin prose drift as the prose is edited

- Confidence: candidate
- Dismiss when: never without running the test. When a PR has a test that pins documentation or protocol wording (regexes over a `SKILL.md`, a snapshot of doc text) and a bot says the test and the text no longer match, run the test on the PR tip first.
- Don't dismiss when: n/a. This is a verification step, not a dismissal pattern. The "lean toward dismissing from the third pass" rule in Babysit misfires here, because each earlier round of fixes edits the pinned text.
- Example signal: "Contract test omits the pre-fix wait" on a PR whose earlier fix commits reworded the pinned passage; the test failed on exactly the cited assertion.
- Source: one PR with eight review passes; the claim was real on pass seven after every earlier pass had been fixed.
