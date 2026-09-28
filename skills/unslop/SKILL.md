---
name: unslop
description: The writing standard for all prose you produce (replies, docs, PR descriptions, commit messages, comments). Use it while drafting and to edit existing text that reads as AI-generated, padded, or mannered.
disable-model-invocation: true
---

# Unslop

Write plain, specific prose that a tired engineer can read once and act on. Apply these rules while drafting, then scan the result for the patterns below and rewrite what you find. Keep the meaning and the intended tone.

Other skills cite rules by name, for example "the mannered-prose rule in `unslop`".

The rules serve the reader. If following one makes a sentence worse, fix the sentence another way or leave it alone. Text that obeys every rule and still sounds machine-written has failed.

## Content

**Superficial -ing phrases.** Trailing clauses like "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering..." add a claim without support. Delete them, or turn them into a real statement with its evidence.

**Vague attributions.** "Experts believe", "industry reports suggest", "some critics argue". Name the source or delete the claim.

**Generic conclusions.** "The future looks bright", "this sets us up for success". State the specific plan, result, or open question.

**Says nothing about this project.** If a sentence could appear unchanged in another project's docs, it tells the reader nothing. Replace it with the fact that is specific here, or cut it.

## Word choice

**AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, robust, seamless, showcase, tapestry (abstract), testament, underscore, vibrant. Use the plain word, or nothing.

**Plain words.** "Use", not "utilize" or "leverage". "Help", not "facilitate". "Many", not "numerous". "If", not "in the event that". "Do", not "perform". A longer word has to earn its place with precision.

**Fancy ways to say "is".** "Serves as", "stands as", "boasts", "features". Write "is" or "has".

**Abstract metaphor nouns.** Words that sound technical but stand in for a plainer concrete one: substrate, wedge, vector, locus, vantage, nexus, primitive (as a noun), harness (as a metaphor), surface (as in "API surface"), bedrock, scaffolding (as a metaphor), modality, paradigm, gold-plating, ratchet (as a metaphor), evacuate (for moving code), endgame, north star, flywheel. Replace with the concrete word: "substrate" is "base", "wedge in" is "add", "vector" is "way", "gold-plating" is "more than the job needs", "ratchet" is the mechanism's real name or "a limit that only tightens", "evacuate" is "move out", "endgame" is "the last phase".

**Invented jargon.** Don't coin a term where a plain phrase works ("several parallel attempts", not "a gauntlet"). If a coined term is worth keeping, define it the first time and use it the same way every time after.

**Synonym cycling.** Calling one thing "the gate", "the check", and "the budget script" in one doc makes the reader think there are three things. Pick one name and repeat it, and likewise one verb per action (not "start" in one place and "initiate" in another). Use the real symbol, file, flag, or command name when there is one.

**Adverbs propping up verbs.** "Runs quickly" becomes "is fast" or the measured number. "Significantly improves" becomes the measured delta. If a verb needs an adverb, look for a better verb.

## Sentences

**Say what it does, not how it feels.** "SQL you can read" and "types that follow your schema" describe a feeling. Name the mechanism or a number instead: "`.toSQL()` returns the exact string sent to the database", "a column rename fails the build". Ask what the sentence tells the reader to do or know, and write that. If you can't restate it as an instruction, a fact, or a number, cut it.

**Active voice.** Name the actor. "Queries are validated" becomes "the compiler validates queries". Passive is fine when the actor is unknown or doesn't matter.

**Dense sentences.** If the reader has to backtrack to parse a sentence, split it or drop clauses. Long sentences are fine when they read cleanly; vary the length so the text doesn't sound clipped.

**Filler.** "In order to" is "to". "Due to the fact that" is "because". "It is important to note that" gets deleted. If the sentence survives without a word, remove the word.

**Excessive hedging.** "It could potentially be argued that it might" becomes "it may". Hedge once, where the uncertainty is real, and say what it depends on.

**"Not just X, but Y."** State Y directly.

**Rule of three.** Don't force items into groups of three. Use the number the content has.

**False ranges.** "From X to Y" where X and Y aren't ends of a real scale. List the items instead.

**Over-compression.** Dropped articles, verbless fragments, arrows, and private abbreviations make the reader decode instead of read. "Parser rejects bad date → exit 2, no write" becomes "The parser rejects a bad date, exits with code 2, and writes nothing." Write whole sentences with their articles and verbs.

## Voice

**Mannered prose.** Figurative language where a literal phrase exists: aphorisms ("wire it or delete it"), slogans ("green is not safe"), rhetorical fragments for effect, personified code ("the plan holds it"), figurative verbs ("rides along", "stands on"), framing labels ("the key insight", "at its core", "TL;DR"), mirror sentences ("A without B, or B without A"), and dramatic emphasis. Say the literal thing: "A passing CI run doesn't prove the change is correct, so verify each PR before merging." The abstract-metaphor-nouns rule covers the single-word version.

**Persona and performance.** Don't write in character. No in-jokes, mock drama, catchphrases, villain or hype voices, self-mythology, or deliberate lowercase affect. The text is instructions and facts for an engineer, not a performance.

**Shouting.** No ALL CAPS for emphasis, no stacked "never" and "always", no "non-negotiable". State the rule once and give the reason when it isn't obvious.

**Sycophancy.** "Great question!", "You're absolutely right!" Answer directly. If you disagree, say so and why.

**Chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remove them.

## Formatting

**Punctuation habits.** Em dashes, colons, semicolons, and parentheses are all fine. Don't lean on any of them. Several em dashes in a paragraph, or a colon used as a dramatic pause ("The fix: delete it"), is a tell. Rewrite so the sentence carries its own structure.

**Inline-header lists.** A bold label and colon that restate the line ("**Performance:** Performance improved...") is a tell. Turn those into plain bullets or prose. A bold lead-in that names the item and is followed by new detail ("**Schema in TypeScript.** Tables live in one file.") is fine.

**Boldface overuse.** Bold only what a skimming reader must not miss. Don't bold every product name or acronym.

**Title case headings.** Use sentence case.

**Decorative emojis.** Remove them from headings and bullets.

**Curly quotes.** Use straight quotes.
