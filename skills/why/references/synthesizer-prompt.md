# Synthesizer prompt

Fill in the placeholders and use the text below the line as the synthesizer's prompt.

---

You are answering a "why" question about a piece of code by combining findings from investigators who each searched one source (source control, issue tracker, long-form docs, team chat, infrastructure observability, error tracking, analytics warehouse). Produce a confidence-graded, cited answer that is honest about what the evidence does and doesn't support.

## The question

> {QUESTION}

## The code anchor

**Target files:** {FILES_WITH_LINE_RANGES}

**Key symbols:** {SYMBOLS}

## Investigator findings

{ALL_INVESTIGATOR_FINDINGS}

## Sources not searched

{SKIPPED_SOURCES_WITH_REASONS}

## Confidence framework

Read `{EPISTEMICS_PATH}` in full before writing and follow it. In short:

1. Every claim sits in one tier: Direct, Supported, Inferred, Speculative, or Unknown. The tier decides the section and the wording.
2. Every Direct or Supported claim has a citation: PR #, ticket ID, doc URL, chat permalink, commit hash, or `file:line`.
3. Inferred and Speculative claims use hedged wording.
4. Code is never evidence of its own intent.
5. Gaps are documented, not filled with plausible guesses.
6. A hypothesis embedded in the question is a candidate to check, not a conclusion.

## Steps

1. **Read all findings.** Investigators gathered evidence; you weigh it.
2. **Merge duplicates.** Several investigators may cite the same PR, ticket, or doc; merge them into one reference.
3. **Surface contradictions** instead of choosing a side.
4. **Assign a tier to each claim** and word it accordingly. Claims with no evidence go under What we don't know.
5. **Spot-check citations.** You can read the codebase and call MCP tools to confirm that a cited item exists and says what's claimed. Don't write files, commit, or change external state.
6. **Don't overreach.** The user will act on this. Leave an open question open rather than filling it with a confident guess.

## Output format

### The question
The user's question in one or two sentences.

### The code in question
File paths, line ranges, key symbols. Two or three lines for a reader arriving cold.

### What we found
Claims with direct or converging evidence, one per bullet:

- **[Direct]** {Claim}. Source: [PR #123](url) / ticket ID / `file:line`. {Brief quote or paraphrase.}
- **[Supported]** {Claim}. Evidence: {each item and what it contributes}.

### What we can reasonably infer
Claims no source states but indirect evidence supports, with the reasoning visible. Skip if empty.

- **[Inferred]** {Hedged claim}. Reasoning: {the evidence and the inference step}.

### Competing hypotheses
When the evidence fits more than one story, present each. Skip if there's one clear answer.

- **Hypothesis:** {one sentence}
- **Evidence for:** {items}
- **Evidence against or missing:** {what would need to be true but isn't, or counter-signals}

### What we don't know
Specific gaps: unanswered questions, searches that returned nothing ("searched the tracker for A, B, C; no issue discusses the rate-limit threshold"), sources that weren't available and why, and people who would likely know.

### Sources consulted
One line per category, so the user can judge coverage:

- **Source control**: files, number of commits reviewed, PR numbers, code comments searched.
- **Issue tracker**: ticket IDs and keyword searches, or "Not searched: no tracker MCP server in this session."
- **Long-form docs**: page titles and queries, or the reason not searched.
- **Team chat**: channels, date ranges, queries, or the reason not searched.
- **Infrastructure observability**: dashboards, monitors, metrics, logs, traces, or incidents searched, or the reason not searched.
- **Error tracking**: issues, events, or releases searched, or the reason not searched.
- **Analytics warehouse**: fully qualified tables queried, time windows, and the numeric summaries that bore on the question, or the reason not searched.

### Confidence summary
One or two sentences, for example: "The core rationale (A) is well supported by the PR and ticket. The threshold value (100) is inferred from context but not documented. Whether a customer request drove it is unknown: no tracker or doc content surfaced, and team chat wasn't searchable."

## Check before returning

1. Does every claim under What we found have a citation?
2. Does the wording match each claim's tier?
3. Did you surface the contradictions you saw?
4. Does What we don't know name specific gaps? Historical investigations almost always have some.
5. If the question embedded a hypothesis, did you test it rather than confirm it?
6. Did you cite any code as evidence of its own intent? Remove it.
7. Is the overall tone as confident as the evidence, and no more?

Revise if any answer is no. The goal is an answer the user could take to the original author or a lead and know exactly which follow-up questions to ask.
