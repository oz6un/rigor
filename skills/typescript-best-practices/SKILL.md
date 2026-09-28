---
name: typescript-best-practices
description: Rules for writing TypeScript that the compiler can check. Use when reading or editing any .ts or .tsx file.
disable-model-invocation: true
---

# TypeScript best practices

Other skills named here don't appear in the model's skill list. To use one, read `<this skill's dir>/../<name>/SKILL.md` (with symlinks in this skill's path resolved) and follow it.

Read the `type-system-discipline` principle (in the `principles` skill) first. Examples for each rule are in `references/patterns.md`.

| Rule | Summary |
|------|---------|
| Discriminated unions | Model variants with a literal discriminant such as `kind`, so contradictory states can't be represented. Don't use a bag of optional fields. |
| Branded types | Brand primitives with `& { readonly __brand: "X" }` so they can't be mixed up. Validate once at the boundary. |
| Constructive modeling | Shape the type so the illegal value can't be built: `[T, ...T[]]` for non-empty, `[T, T][]` for even length, `start` plus `duration` for a range. This replaces a runtime guard. |
| Simplest total type | Keep `T[]` while every operation on it is total. Switch to `NonEmpty<T>` only where the loose type forces `!`, a cast, or a "should never happen" throw. |
| `unknown` over `any` | Type external data as `unknown` and narrow it. |
| Schemas before guards | Before hand-writing a property-by-property type guard, use the repository's runtime schema library and infer the type from the schema (for example `z.infer`). |
| No `as` casts | An unverified `as` can crash at runtime. Cast only after validation. |
| Narrowing order | Prefer a discriminant check, then `in`, then `typeof`/`instanceof`, then a user-defined type guard, and `as` last. |
| Type guards | A guard must actually check what it claims. A guard that lies is worse than `as`, because its name says the value is safe. Name guards `isX` or `hasX`. |
| Exhaustiveness | Put `const _exhaustive: never = x;` in `default` arms so adding a variant is a compile error until it's handled. |
| `satisfies` over `as` | `satisfies` checks the value without widening literal types. |
| Boundary validation | Parse data where it enters into a named domain type. `Record<string, unknown>` (however it's spelled) shouldn't travel past that parse. Trust types inside. See the `boundary-discipline` principle. |
| Derived types | Use `Pick`, `Omit`, `Parameters`, `ReturnType`, `Awaited`, and `typeof` on existing or generated types before declaring a new interface. |
| Object arguments | Pass an object instead of several positional arguments, so call sites name each value. Skip this on hot paths (per-frame rendering, tokenizers, parsers). |
| Real tests | Don't mock what you can run. Use the framework's real test utilities with leak or disposal checks, and verify UI in a running build. Mock only what you can't run locally. |
| Structured logging | Use the project's structured logger with enough context to debug from an id. Don't ship `console.log`. |
