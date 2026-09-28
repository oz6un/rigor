### Eval

You own the experiment design: plan it, blind it, run it, and synthesize the result.

**Blinding rules.** A candidate that knows it's being tested behaves differently, so the setup has to look like ordinary work.

- Nothing the candidate sees (directory names, file names, prompt) contains `eval`, `test`, `judge`, `experiment`, `rubric`, `score`, `compare`, `benchmark`, `candidate`, or `arena`. Use project-shaped names a user might pick.
- The candidate prompt reads like a real user request. State the goal, not what is being measured.
- Don't ask candidates to list the skills, principles, or files they used. Ask for design notes in general, and grade chain-following from what they actually did.
- Don't tell a candidate that other candidates exist.
- The judge knows it is judging, but sees outputs only under sanitized labels, never model names.
- When comparing two variants, one judge scores both sets in a single pass on one scale, without knowing which variant produced which set.

**Steps:**

1. **Frame.** State the variant under test and the behavior that counts as success. Write a rubric of 3-6 concrete criteria for the judge only.
2. **Set up sanitized environments.** Give each candidate its own working directory with the variant in place. Plant the context a real task would have: a project skeleton and the skills the candidate would naturally read.
3. **Write one organic prompt.** What a user would actually type, with no hint of what is being measured.
4. **Run N candidates in parallel** per the `arena` skill's candidate phase, each in its own directory with the same prompt. Vary the model where you can: host subagents on different models, plus the other CLI through the rigor skill's `<rigor skill dir>/scripts/second-opinion.sh --write --cd <candidate dir>`.
5. **Run one blinded judge** per the `arena` skill's judge phase, on a different model family from the candidates where possible (the other CLI through `<rigor skill dir>/scripts/second-opinion.sh`). The judge gets the rubric and the outputs under sanitized labels.
6. **Check what each candidate actually did from its transcript, not its self-report.** In Claude Code, read the session JSONL under `~/.claude/projects/<project-slug>/` for the candidate's working directory (subagent transcripts are stored with the parent session). In Codex, read the `~/.codex/sessions/**/rollout-*.jsonl` files whose recorded working directory is the candidate's directory. Stay within this run's transcripts; don't search other projects' sessions, which are private and unrelated. Grade chain-following from the files each candidate opened and the shape of its code.
7. **Read every candidate output yourself**, end to end, and compare with the judge's verdict. Disagreement means either a model is biased or the rubric is ambiguous; resolve which before you synthesize.

**Reply:** the variant under test, the rubric, notes per candidate, the judge's verdict (and whether the other CLI fell back to a host subagent), your synthesis, and a recommendation on whether to adopt the variant.
