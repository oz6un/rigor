# Investigation

You own the answer. Investigations are read-only: they produce a cited explanation or a recommendation, not a code change.

1. Run the `how` skill over the subject. For questions about motivation ("why was this built this way?"), also run the `why` skill.
2. Write the throughput checkpoint as one line: `throughput checkpoint: n/a, read-only investigation`.
3. Produce the `how`-shaped output (Overview, Key concepts, How it works, Where things live, Gotchas). If the request is a choice between alternatives, produce a recommendation with a tradeoffs table instead.
4. Apply the `unslop` skill to the reply.

No PR, no Babysit, and no `architect` unless the investigation precedes a code change. If it does, finish the investigation, report back, and route the change to the Bug fix or Feature playbook.

**Reply:** the investigation output. For "are we sure?" questions, give your actual judgment with reasons, and say so if the premise is wrong (see Autonomy in `SKILL.md`).
