# Steer with principle names

mstack ships 23 principles in the [`principles`](../../skills/principles/) skill. `/rigor` reads the index at the start of each multi-step task, applies the ones that fit, and names each applied principle in its reply along with the decision it changed.

You don't invoke principles; you use their names to redirect work. Each name points to a full rule the agent has already read, so one phrase is more precise than a paragraph of instructions.

## Examples

The agent is about to add a new adapter next to three existing ones:

```text
use subtract before you add. delete the obsolete adapters first, then design what's left.
```

It claims success because the build passed:

```text
apply prove it works. run the real import flow and show me the written records.
```

Two parallel attempts are about to write to the same branch:

```text
separate before serializing shared state. give each attempt its own worktree, no locks.
```

The reply still has to say which decision the principle changed. A citation with no changed decision means the agent named it without applying it.

## The list

**Core**: how much to build and when to rethink.

- `laziness-protocol`: prefer deletion and the smallest change that works.
- `foundational-thinking`: choose the core data structures before writing logic.
- `redesign-from-first-principles`: integrate a new requirement as if it had been there from the start.
- `attack-the-premise`: when two fixes with the same premise fail, question the premise.
- `subtract-before-you-add`: remove dead weight before building on top.
- `minimize-reader-load`: collapse layers and hidden state.
- `outcome-oriented-execution`: move rewrites to the target design without throwaway compatibility layers.
- `experience-first`: favor the user's result over implementation convenience.
- `exhaust-the-design-space`: build two or three prototypes when there's no precedent.
- `build-the-lever`: write the script that does or checks the work so a reviewer can rerun it.

**Architecture**: where state, validation, and compatibility live.

- `model-the-domain`: encode repeated rules in one structure, not scattered conditionals.
- `boundary-discipline`: validate at the boundary and trust internal types.
- `type-system-discipline`: make illegal states unrepresentable.
- `make-operations-idempotent`: retries reach the same end state.
- `migrate-callers-then-delete-legacy-apis`: migrate and delete in one change.
- `separate-before-serializing-shared-state`: remove sharing before adding locks.

**Verification**: what counts as proof.

- `prove-it-works`: check the real artifact, not a proxy.
- `fix-root-causes`: reproduce and trace to the cause before changing code.
- `sequence-verifiable-units`: end each small unit with a check before starting the next.
- `test-behavior-not-implementation`: call code the way users do and assert a literal expected value.

**Delegation**

- `guard-the-context-window`: send bulk reading to subagents; keep findings in the main session.
- `never-block-on-the-human`: do reversible work and show the result instead of asking.

**Meta**

- `encode-lessons-in-structure`: turn advice you've repeated twice into a lint, check, or script.

Don't memorize the list. Come back when the agent does something a principle would have prevented; that's when the names stick.

Next: [Make it yours](./09-make-it-yours.md).
