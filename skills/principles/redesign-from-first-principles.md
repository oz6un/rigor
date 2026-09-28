# Redesign from first principles

When adding a requirement to an existing design, don't bolt it on. Redesign as if the requirement had been there from the start.

- Read all affected files and understand the current design.
- Ask what you would build if you were writing this from scratch with the new requirement.
- Carry the change through every reference: types, docs, examples, and rationale sections.
- Design the whole change, then deliver it in increments (see [sequence-verifiable-units](sequence-verifiable-units.md)).

This is how you keep option value when integrating changes. To question an assumption the current design already makes, see [attack-the-premise](attack-the-premise.md).
