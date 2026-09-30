### Opening a PR

The last step of every other playbook. All PR operations use the GitHub CLI (`gh`); don't require Graphite (`gt`).

**Worktree.** Work in a git worktree branched from main; subagents inherit it. Parallel subagents on the same branch each get their own worktree, or run `git fetch && git reset --hard origin/<branch>` between them. If the branch has unrelated uncommitted work, save it as a patch, create a fresh worktree, and apply your change there. If a worktree gets tangled, reset it from main and redo the change minimally.

**Commits.** Commit often, then rebase into small, ordered commits before opening PRs. Each commit should be able to become its own PR: landable on its own, and ordered so the sequence explains the change. Amend when a fix belongs in the commit you just made; make a new commit when it's separable.

**Before opening.** Run `deslop` over the diff before committing and `no-comments` before requesting review. Write every PR title, PR description, and commit body with `technical-writing` (every layer except Diátaxis), then run `unslop` over it.

**Review before done.** After verifying the change, and before opening the PR or telling the user it's done, have someone other than you review it, scaled to what a mistake would cost:

- The full `interrogate` panel when a mistake would be costly or hard to undo, or when the code runs where your tests don't reach: other people's machines and settings, concurrent runs, state left by earlier runs or versions, installs and updates, security.
- One reviewer (`interrogate` with reviewer A alone) for other changes to behavior.
- None for a small change whose behavior your tests fully cover; say so in the report.

Fix what the verdict puts under Act on and verify the fix; review again only if the fix is substantial. A known blocker means the work isn't done. Bring findings that conflict with the user's request to the user.

**Titles.** Use Conventional Commits: `type(scope): subject`, where type is `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, or `perf`, and scope is the changed area (for example `rigor` or `watch-pr`). Keep the subject short and imperative, name a real symbol when one carries the change, and leave off the trailing period. Example: `fix(watch-pr): count review passes per run id`.

**Descriptions.** The PR body is a briefing for a reviewer who has the diff: why the change exists, what's out of scope, and how you proved it works. The squash commit body is the PR body, so if it would push the squash commit past about 40 lines, cut it. Use these sections in order, and drop any with nothing to say:

- `## Why`: the intent and approach in one or two short paragraphs. No SHAs, rebase history, or "based on main" preamble.
- `## Scope`: bullets naming real symbols and paths. Name both sides of a rename or retarget. State what's in and out only when the boundary matters.
- `## Tradeoffs`: only the rejected alternatives a reviewer would otherwise ask about. Skip it when there was no real choice.
- `## Blast Radius`: one to three sentences on who or what the change touches and why it's safe or risky. If main is broken without the fix, say what that keeps costing.
- `## Verification`: each real run path and its outcome. For a performance change, one primary number with its unit as `before → after`, with a link to the arena or swarm directory for the rest of the evidence.

After the sections, attach screenshots or videos when they prove a claim. Leave out full SHAs, per-lane arena or swarm results, file-by-file checklists, sample-size methodology, and metric tables; put those in a linked artifact. Don't use `## Summary` or `## Test plan` boilerplate. A commit body doesn't repeat its subject.

**Size and stacks.** Prefer several narrow PRs to one large one. A stack is a chain of base branches: the root PR targets trunk, each child branch is rebased onto its parent's exact tip, and each child PR targets its parent branch. Create a child with `gh pr create --base <parent-branch>` and retarget one with `gh pr edit <pr> --base <parent-branch>`. Branch from trunk only for independent work, and rebase on trunk before substantial work on a stack.

**Readiness.** Open every PR ready for review, not as a draft (omit `--draft`). If one opens as a draft anyway, run `gh pr ready <number>`. Run `gh pr view <number>` before you describe a PR's status.

**No automatic babysitting.** Opening a PR doesn't start a babysit. Post the URL and keep building until the phase or stack is done. Babysit only when the user asks, after the whole stack exists; babysitting each PR as it opens stalls the build and spends CI on commits that later pushes will restart. Push back when review feedback drifts from the intent of the change.

A subagent that opens a PR runs `interrogate`, `deslop`, and `no-comments`, posts the URL, and returns to its parent without babysitting. The exception is an Autopilot-full or Autopilot-stack owner: its brief assigns the babysit loop, which counts as the request `playbooks/babysit.md` waits for. That owner starts the loop after its code-ready report and reports merge-ready (or STACK-READY) as its playbook says, and the rule above about waiting for the whole stack doesn't apply to it.
