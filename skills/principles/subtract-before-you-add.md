# Subtract before you add

When changing a system, remove complexity first, then build.

**Why:** Adding to a complex system compounds the complexity. Removing first leaves less code, exposes the essential structure, and often makes the next design obvious.

Treat simplification as ongoing work: leave the design a little simpler, and more capable behind the same or a smaller surface, than you found it.

- Do removals before construction.
- Cut before you polish. Get to the minimum before investing in quality.
- Design for observed usage, not speculative edge cases.
- Don't add validators, parsers, or guards beyond what the spec requires.
- Simplify prompts: remove redundant instructions and oversized templates.
- When a reference file has nothing new in it, delete it instead of leaving a stub.

See also [laziness-protocol](laziness-protocol.md).
