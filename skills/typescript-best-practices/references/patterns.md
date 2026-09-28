# TypeScript patterns

Code examples for each rule in `SKILL.md`. The ideas behind them aren't specific to TypeScript; see the `type-system-discipline` and `boundary-discipline` principles in the `principles` skill.

## Branded types

Brand primitives so they can't be mixed up. Validate once at the boundary, and downstream code trusts the type.

```ts
type AgentId = string & { readonly __brand: "AgentId" };

function parseAgentId(input: string): AgentId {
  if (!isUUID(input)) throw new Error(`Invalid agent id: ${input}`);
  return input as AgentId;
}

function focusAgent(id: AgentId): void {
  /* input is trusted */
}
```

Use the `readonly __brand: "X"` shape, or whatever brand shape the codebase already uses. Don't introduce a second convention.

## Discriminated unions

Every variant has the same discriminant field with a unique literal value, so contradictory combinations can't exist.

```ts
// Don't: a boolean plus optional fields allows contradictory states.
type DiffState = { loading: boolean; diff?: GitDiff; error?: string };

// Do: only valid states exist.
type DiffState =
  | { kind: "loading" }
  | { kind: "ready"; diff: GitDiff }
  | { kind: "error"; error: string };
```

Pick one discriminant name (`kind`, `type`, or `tag`) and use it throughout.

## Constructive modeling

Build the type from parts that are all legal, instead of restricting a loose type with runtime checks.

Non-empty, with a variadic tuple:

```ts
type NonEmpty<T> = [T, ...T[]];

// Don't: T[] plus a length check that every caller must repeat
function pickWinner(entries: string[]): string {
  if (entries.length === 0) throw new Error("no entries");
  return entries[Math.floor(Math.random() * entries.length)];
}

// Do: an empty value of this type can't exist
function pickWinner(entries: NonEmpty<string>): string {
  return entries[Math.floor(Math.random() * entries.length)];
}
```

Where a plain `T[]` arrives, narrow it once with a guard, and the fact then travels with the type:

```ts
const isNonEmpty = <T>(arr: T[]): arr is NonEmpty<T> => arr.length > 0;
```

Even length, as pairs:

```ts
type Pairs<T> = [T, T][];
```

A time range, as start plus duration:

```ts
// Don't: only a comment enforces the invariant
type TimeRange = { start: Date; end: Date }; // start <= end

// Do: a negative range can't be written; derive the end when needed
type TimeRange = { start: Date; durationMs: number };
```

Keep `durationMs` a plain number. Brand it only if a raw number could realistically be passed where a duration is expected. Choose the representation that makes the bad state impossible to build, then add the accessors you need on top (`pairs.flat()`, a `rangeEnd()` helper).

## Simplest total type

Don't strengthen every type. Keep `T[]` when every operation on it is total:

```ts
const sum = (xs: number[]) => xs.reduce((a, b) => a + b, 0); // [] sums to 0
```

Strengthen it when the loose type forces an unchecked assumption at a use site. The signs are `!`, `arr[0] as T`, and a "should never happen" throw:

```ts
// Don't: the non-null assertion hides a possible undefined
function newestSession(sessions: Session[]): Session {
  return sessions.at(0)!;
}

// Do: require a non-empty input, and the assertion goes away
function newestSession(sessions: NonEmpty<Session>): Session {
  return sessions[0];
}
```

Returning `Session | undefined` is the other honest signature.

## `unknown` over `any`

External data is `unknown`. Narrow it before use.

```ts
// Don't
function handle(input: any) {
  return input.foo.bar;
}

// Do
function handle(input: unknown) {
  if (typeof input === "object" && input !== null && "foo" in input) {
    // narrowed; the compiler checks the access
  }
}
```

External data includes RPC payloads, `JSON.parse` results, `postMessage` and IPC messages, file contents, environment variables, and database results.

## Schemas before hand-written guards

Before writing a property-by-property type guard for external data, look for the repository's runtime schema library and existing schemas. Let one schema own validation and derive the TypeScript type from it, so there's no separate interface and guard to drift out of sync.

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  role: z.enum(["admin", "member"]),
});

type User = z.infer<typeof UserSchema>;

function parseUser(input: unknown): User {
  return UserSchema.parse(input);
}
```

Use `safeParse` when failure is an expected branch. If the repository uses a different schema library, use its inference helper. Don't add a schema dependency for a single guard.

## No `as` casts

An `as` cast is a claim the compiler doesn't check. Cast only after your code has verified the claim.

```ts
// Don't
const user = data as User;

// Do: earn the cast at the boundary
function parseUser(data: unknown): User {
  if (typeof data !== "object" || data === null) {
    throw new Error("expected object");
  }
  if (!("id" in data) || typeof (data as Record<string, unknown>).id !== "string") {
    throw new Error("expected id");
  }
  // ... validate the remaining fields
  return data as User; // safe after full validation
}
```

When removing an `as` from existing code, find out why TypeScript can't infer the type:

- Missing discriminant: add one and use a discriminated union.
- Source type too wide (for example `Record<string, unknown>`): narrow it.
- Untyped boundary: add a parse function or a schema.
- Not expressible in the type system: use a branded type or `satisfies`.

## Narrowing order

From most to least preferred:

1. A discriminant check in a `switch` or `if`. The compiler narrows automatically.
2. The `in` operator. `"key" in obj` narrows to the variants that have that key.
3. `typeof` or `instanceof`, for primitives and class instances.
4. A user-defined type guard, when none of the above work.
5. An `as` cast, only after validation.

```ts
function area(s: Shape): number {
  if ("radius" in s) return Math.PI * s.radius ** 2; // narrowed to circle
  return s.width * s.height; // narrowed to rect
}
```

## Type guards

A guard must actually check what it claims.

```ts
function isCircle(s: Shape): s is Shape & { kind: "circle" } {
  return s.kind === "circle";
}
```

Prefer narrowing on the discriminant directly when you can.

## Exhaustiveness

In `default` arms, assign the value to a `never`-typed local.

```ts
// Switch that returns a value
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.radius ** 2;
    case "rect":
      return s.width * s.height;
    default: {
      const _exhaustive: never = s;
      return _exhaustive;
    }
  }
}

// Switch used as a statement
function handle(s: Shape): void {
  switch (s.kind) {
    case "circle":
      drawCircle(s);
      break;
    case "rect":
      drawRect(s);
      break;
    default: {
      const _exhaustive: never = s;
      void _exhaustive;
    }
  }
}
```

## `satisfies` over `as`

`satisfies` checks the value against the type without widening its literal types.

```ts
// Don't: widens and loses the literal types
const config = { theme: "dark", cols: 3 } as Config;

// Do: checks the value and keeps the literal types
const config = { theme: "dark", cols: 3 } satisfies Config;
// config.theme is "dark", not string
```

## Boundary validation

Validate once where data enters and trust the types inside. See the `boundary-discipline` principle.

- Wire formats (protobuf, JSON-RPC): parse with unknown fields ignored (for example `ignoreUnknownFields`) so a newer sender doesn't break an older reader.
- Persisted JSON: store a versioned blob and wrap the parse in `try`/`catch`.
- Don't validate the same data again deeper in the call chain.

## Derived types

When a `.proto` file, OpenAPI spec, GraphQL schema, or database migration already defines a shape, derive from the generated types instead of redeclaring it.

```ts
// Don't: a duplicate shape that drifts when the schema changes
type CheckSummary = {
  totalCount: number;
  checks: { name: string; status: string }[];
};
function renderChecks(s: CheckSummary) {
  /* ... */
}

// Do: derive from the generated type
import type { ChecksMessage } from "<generated module>";
function renderChecks(s: Pick<ChecksMessage, "totalCount" | "checks">) {
  /* ... */
}
```

## Object arguments

```ts
// Don't: swapping two arguments still compiles
openFile(uri, {
  startLineNumber: 10,
  startColumn: 1,
  endLineNumber: 10,
  endColumn: 1,
});

// Do: each value is named at the call site
openFile({
  uri,
  selection: {
    startLineNumber: 10,
    startColumn: 1,
    endLineNumber: 10,
    endColumn: 1,
  },
});
```

Skip this on hot paths (per-frame rendering, tokenizers, parsers, tight loops) where the extra allocation matters.
