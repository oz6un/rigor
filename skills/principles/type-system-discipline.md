# Type system discipline

Use the type checker to rule out impossible states, mixed-up primitives, and unhandled variants at compile time. Any case the types let you ignore becomes a runtime failure the compiler could have prevented. Prefer designing errors and special cases out of existence over adding handlers for them.

This applies to any statically typed language; skills like `typescript-best-practices` give the syntax for a specific one.

- **Make illegal states unrepresentable.** Model variants as sum types: discriminated unions in TypeScript, enums with payloads in Rust/Swift/Kotlin, sealed classes in Scala, ADTs in Haskell/OCaml. Don't model state as a bag of optional fields where contradictory combinations compile. For example, `{ completed: boolean; completedAt?: Date }` allows `completed: true` with no `completedAt`. Derive the boolean from one source (`completedAt !== null`) or model the variants: `{ kind: 'open' } | { kind: 'done'; at: Date }`. If a bug makes you ask "can this combination actually happen?", the type is too loose.
- **Build types from the values you want.** Construct the type rather than carving it out of a looser type with runtime checks. An invariant that seems to need a refinement type is usually one construction away: a non-empty list is a head plus a rest, not a list with a length check; a valid time range is a start plus a duration, not two timestamps you must keep ordered. Choose the representation that can't express the illegal value, then expose the interface callers need on top.
- **Brand semantic primitives.** `UserId` and `OrderId` may both be strings but shouldn't be interchangeable. Use newtypes in Rust, opaque types in Swift, value classes in Kotlin, phantom types in Haskell, branded intersections in TypeScript. Validate once at creation and trust the type afterwards.
- **External data is untyped until parsed.** RPC payloads, JSON, IPC messages, CLI args, config files, environment variables, and database rows each need a parse function at the boundary that produces the typed model. See [boundary-discipline](boundary-discipline.md) for where validation goes.
- **Don't lie to the compiler.** Casts, unsafe coercions, and assertion functions that bypass the checker are latent runtime crashes. If the compiler can't prove a fact, prove it (validate, narrow, refine the model) or treat the cast as a known hazard.
- **Make matches exhaustive.** When you match on a sum type, adding a variant without handling it should fail compilation. Use your language's idiom: a `never`-typed binding in TypeScript, a `match` without a wildcard arm in Rust, `-Wincomplete-patterns` in Haskell, sealed-class `when` in Kotlin.
- **Derive types from authoritative schemas.** When a protobuf, OpenAPI spec, GraphQL schema, database migration, or design-token file defines a shape, generate or derive the type from it instead of maintaining a parallel one (see [encode-lessons-in-structure](encode-lessons-in-structure.md)).
- **Strengthen a type only where partiality shows up.** A runtime assertion, null check, or "should never happen" throw marks where a type is too weak; move that check into the type, then stop. The goal is to track which cases each call site must handle, not to describe the data as precisely as possible. Prefer total functions: `sum` of an empty list is 0, so it takes a plain list; `head` of an empty list has no answer, so it takes a non-empty one.

Questions to ask:

- Could I write a comment explaining when this combination of fields is valid? Then the type is too loose; split it into a sum type.
- Do two arguments share a primitive type but mean different things? Brand them.
- Where did this `any`, `as`, or `assertNotNull` come from? Trace it to the boundary and validate there.
- If someone adds a variant next month, will the compiler show them where to handle it? If not, the match isn't exhaustive.
- Does this type duplicate a shape another file owns? Derive it instead.
- Am I strengthening this type to keep an operation total, or just for precision? If nothing would otherwise fail at runtime, keep the plain type.
