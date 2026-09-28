# Exhaust the design space

When a new interaction or architecture decision has no precedent in the codebase, explore several concrete alternatives before implementing. Building the wrong thing costs more than exploring three options.

When the right answer isn't obvious, build two or three competing prototypes or sketches, compare them side by side, and only then commit. This is "design it twice". A variation on the first design doesn't count as a second option; the alternatives should differ in shape.

Applies to:

- New UI interactions with no prior art in the codebase.
- Architecture choices with several viable approaches.
- Product decisions where the experience depends on how it feels, not on logic.

Doesn't apply to:

- Mechanical implementation of an established pattern.
- Bug fixes or refactors with a clear target state.
- Changes where the constraints allow only one approach.

The `arena` skill runs this with parallel attempts; the rigor skill's Prototype playbook covers throwaway sketches.
