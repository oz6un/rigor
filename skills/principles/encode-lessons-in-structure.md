# Encode lessons in structure

Turn recurring fixes into mechanisms (lint rules, metadata flags, runtime checks, scripts, types) instead of written instructions. Treat every error, human correction, and surprise as a signal: capture it, route it, and act on it.

**Why:** Written instructions only work if the reader notices, remembers, and complies. A mechanism enforces the rule without anyone's cooperation.

When you're about to write the same instruction a second time:

1. Ask whether it can be a lint rule, a metadata flag, a runtime check, or a script.
2. If yes, build that and delete the instruction.
3. If no (it needs judgment), make the instruction more prominent and add an example of the failure.

If the fix is structural, use only the structural fix; the instruction was a symptom.

**Pick the strongest mechanism that fits.** In order: a state the types can't represent, then a lint rule or banned API that fails CI, then a canonical helper, then a runtime check. Agents copy whatever the surrounding code does, so a weak guard becomes the template for the next change.

Feedback loop:

- **Capture every correction.** When the user intervenes or a test fails, decide whether it's a one-off or a pattern.
- **Route it to the right layer.** One-off: a note (memory, `CLAUDE.md`, or `AGENTS.md`). Recurring fix: a skill or lint rule. Systemic issue: a principle.
- **Act on it.** Apply the fix now or add a concrete todo; recording alone isn't enough.

Failure modes:

- Acknowledging without recording. "I'll keep that in mind" doesn't persist past the session.
- Recording without routing. A note saying a lint rule should exist does nothing until the rule exists.
- Fixing the instance without the pattern.
