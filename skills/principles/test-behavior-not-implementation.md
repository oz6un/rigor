# Test behavior, not implementation

A test should call the code the way its users do and assert what they observe against a literal expected value. A test that checks which calls the code made, or restates a constant from the code, does neither.

Before keeping a test you wrote, ask: would it still pass if every function it imports returned `undefined`? If so, it observes no behavior and can't fail for a defect. Rewrite the assertion or delete the test.

**Why:** A test that can't catch a defect costs CI time and review attention and protects nothing. A test that restates a constant also breaks whenever someone legitimately edits that constant or prompt, so it blocks the change instead of checking it.

Five shapes that still pass when every import returns `undefined`:

- **Weak or missing assertion:** no `expect`, or only `toBeDefined`, `toBeTruthy`, `not.toThrow`, `toBeInstanceOf`, `toBeGreaterThan(0)`.
- **Mocks or absence only:** only `toHaveBeenCalled`, `not.toHaveBeenCalled`, `toBeUndefined`, `toEqual([])`, `toHaveLength(0)`, `not.toBe(wrongValue)`.
- **Self-referential:** the expected value comes from the code under test, as in `expect(f(a)).toBe(f(a))` or `expect(parsed.url).toBe(buildUrl(...))`.
- **Constant pin:** the assertion restates a hand-maintained constant, config default, table row, or prompt string, as in `expect(LIMITS.maxTools).toBe(8)` or `expect(PROMPT).toContain("You are")`.
- **Fixture checks fixture:** the assertion reads data the test built itself or computed in `beforeEach`, and the code under test never runs in the test body.

How to fix them: call the subject in the test body with one concrete input and assert the literal output or observable effect, as in `expect(slugify("Hello, World!")).toBe("hello-world")`.

- For an absence, also assert the presence for a different input in the same test.
- For a constant, test the code that reads it with one input instead of restating the value.
- For a mock, assert the payload it received or the state after the call, not just that it was called.
- If no such assertion is possible, delete the test you wrote. An existing test is deleted only when the code it tests is deleted (see [migrate-callers-then-delete-legacy-apis](migrate-callers-then-delete-legacy-apis.md)).

Keep tests that check a relation across a table's rows (a key present in two tables, a parent that exists) and compile-time checks in `*.test-d.ts` files.
