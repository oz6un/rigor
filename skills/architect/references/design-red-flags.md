# Design red flags

Screen every candidate before combining. A red flag is a reason to revise or reject the shape.

## Shallow module

A shallow module exposes a large interface and hides little. Judge depth by how much capability and policy sits behind the public surface relative to the size of that surface. Prefer a simple interface backed by substantial behavior.

A deep module is not a deep call chain. A deep call chain spreads understanding across layers; a deep module concentrates capability behind one interface.

Signs:

- Callers coordinate several methods to complete one operation.
- Public options expose internal stages or implementation choices.
- Learning the interface doesn't save the caller from learning the implementation.

## Information leakage

Several modules depend on the same internal decision: a representation, policy, or protocol detail appears in more than one place, so changing it requires coordinated edits.

Re-exporting transport or wire types publicly is leakage. Parse external data into domain types behind the interface, and keep storage schemas, framework objects, and protocol details private.

## Temporal decomposition

Modules are organized by execution order (load, validate, transform, save) instead of by the knowledge they own. Each stage then repeats the same representation and its invariants across a boundary.

Group code by domain knowledge and ownership. Methods that run at different times can belong to one module when they protect the same decisions.

## Pass-through method

A method forwards the same arguments to another method with the same shape. It adds a layer without hiding anything.

Remove it, or move the responsibility to the module that can complete the operation. Keep a forwarding boundary only when it adds policy, adaptation, or a distinct abstraction.
