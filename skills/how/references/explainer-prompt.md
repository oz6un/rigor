# Explainer prompt

Fill in the placeholders and use the text below the line as the explainer's prompt. For a simple question with no explorers, drop the "Explorer findings" section and the first paragraph of "Instructions"; the explainer explores on its own.

---

You are writing an architectural explanation for a senior engineer who is new to this area. After reading it, they should understand the subsystem well enough to start working in it.

## Question

> {QUESTION}

## Explorer findings

{EXPLORER_FINDINGS_ALL}

## Instructions

Several explorers each traced a different slice of the same subsystem. Their findings overlap and may contradict each other. Merge the overlaps, resolve contradictions by checking the code yourself, and combine the slices into one picture. You shouldn't need to re-explore from scratch.

You have read-only access to the codebase. Use it to check details and fill gaps.

## Output format

Use this structure, dropping sections that don't apply to the question.

### Overview
One or two paragraphs: what this is, what it does, and why it exists. A reader should be able to stop here and decide whether to keep going.

### Key concepts
The types, services, or abstractions needed to follow the rest, with brief definitions.

### How it works
The main and longest section. Walk through the flow: what triggers it, what happens step by step, where data goes, and where the decision points are. Write prose, not pseudocode. Name files and functions so the reader knows where to look; include a code snippet only when a point depends on it.

When several components interact or data passes through stages, add a diagram: mermaid for sequences, flowcharts, and component graphs, ASCII for simpler relationships. Skip it if the prose already makes the flow clear.

### Where things live
A short map of the files and directories someone needs to start working here.

### Gotchas
Surprising behavior, historical context, and pitfalls. Omit if there's nothing worth noting.

## Style

- Be concrete: "`UserService` calls `AuthClient.refresh()`", not "the service delegates to the client".
- When something is complex, explain why it's complex instead of only describing it. When it's simple, keep it short.
- Use an analogy only if a good one exists.
- If explorers flagged open questions or gaps, include them.
