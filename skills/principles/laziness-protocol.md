# Laziness protocol

Get the most result from the least code and complexity.

- **Prefer deletion.** When asked to refactor or improve something, look for what to remove before what to add.
- **Keep the call hierarchy flat.** Avoid deep call chains. (An interface that hides substantial work isn't a deep chain.) If answering a question means tracing through more than three files or layers, flatten it.
- **Make each decision once.** Don't repeat the same choice in several places. Put it behind one source of truth and pass the result down as a simple value.
- **Minimize the diff.** Make the smallest change that solves the problem. Fewer lines beat elegant boilerplate.
- **Question new threading.** If a task seems to require passing a new signal through types, schemas, pipelines, or other layers, stop and look for a more direct path.
- **Fix small leaks early.** Remove tiny pass-throughs, representation leaks, and duplicated choices before they spread; they compound into permanent coordination costs.

Test: if a human developer would find the code tiring to maintain, it's a bad solution.
