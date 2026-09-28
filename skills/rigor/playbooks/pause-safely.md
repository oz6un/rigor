# Pause safely

You own a clean stop: leave a checkpoint that an agent starting cold can resume from. Pause only when asked to, or when context is about to be compacted. "Keep going", "don't stop", and "I'm going to bed, keep going" are not pause requests.

1. Stop at a safe boundary. Finish the current atomic step or back out of it, start nothing new, cancel any running subagents, and stop any armed `/goal` (`/goal clear`) or `/loop` so it doesn't wake the session and continue.
2. Don't take an irreversible action in order to pause. No new PR and no push unless one was already out.
3. Make the work durable. Commit uncommitted edits as one `wip:` commit on the current branch. If the tree doesn't build or tests fail, say so in one line of the commit body.
4. Write a resume note outside the conversation: the intent, what you were doing, progress and what's verified, current state, next steps, key files, and gotchas. Before a compaction, write it to a file such as `/tmp/<slug>-resume.md`. If a `show-me-your-work` log exists, point to it instead of duplicating it.

**Reply:** where you are in the loop, what's on disk versus only in your context (paths, no diff dumps), the commits you made and whether the tree is clean, and the first action on resume. This is a pause, not a final report.
