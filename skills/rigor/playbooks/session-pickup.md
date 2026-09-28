# Session pickup

You own the resume point. Read what the previous agent did and continue from there; don't redo it.

1. Find the prior trail. It can be a transcript file, a pushed branch, or a PR.
   - Claude Code transcripts are `~/.claude/projects/<project-slug>/*.jsonl`, where the slug is the project's absolute path with `/` replaced by `-`. Look only in the current project's directory. Globbing across `~/.claude/projects/*/` reads private sessions from unrelated projects.
   - Codex transcripts are `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`. Keep only sessions whose recorded working directory is this project. To continue a Codex session in place, `codex resume` lists and reopens them.
   - For a branch or PR, read `gh pr view <pr> --comments`, the PR body, and `git log` on the branch.

   Read the session's opening request and its last messages first, then scan back for the decision points. Transcripts are large, so parse a long one in a subagent (`jq` over the JSONL works well) and keep only the reduced timeline in the main thread, per the `guard-the-context-window` principle.
2. Reconstruct the operational state: the branch and worktree, what already landed (`git log` and `git diff` against the base), open todos, and decisions made. Treat the prior trail as authoritative input instead of re-deriving it.
3. Compare what shipped against what was planned and name the resume point. Don't re-run the prior repro or redo finished work. Wanting to "verify everything from scratch" means you're treating the trail as untrustworthy when it isn't.
4. Route the remaining work to the matching playbook and choose the outcome: continue the execution, ship a finished recommendation, confirm or overturn a prior conclusion, or write a postmortem of a failed run. This playbook ends here; the routed playbook owns the rest.
5. Check the inherited claims against the original goal on the real artifact, per the `prove-it-works` principle. The previous agent's "tests pass" is not that proof.

**Reply:** where the previous agent stopped, what you inherited versus redid (ideally nothing redone), the resume point, and the outcome.
