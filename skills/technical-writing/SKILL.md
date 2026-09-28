---
name: technical-writing
description: A layered standard for technical writing, built on Diátaxis, the Google developer style guide, Simplified Technical English, and Global English. Use when writing or reviewing docs, RFCs, READMEs, PR descriptions, or commit messages.
disable-model-invocation: true
---

# Technical writing

Other skills named here don't appear in the model's skill list. To use one, read `<this skill's dir>/../<name>/SKILL.md` and follow it.

The goal is writing that a tired engineer understands on the first read. Four layers get there, each answering one question:

1. What kind of document is this? (Diátaxis)
2. How do sentences address the reader? (Google developer style)
3. How much does each sentence carry? (Simplified Technical English)
4. Can any sentence be read two ways? (Global English)

Apply all four, and apply `unslop` to everything this skill touches. `unslop` owns word-level and sentence-level style (AI vocabulary, filler, hedging, active voice, sentence length, specificity, articles, punctuation, sentence-case headings, one name per thing or action), so this skill doesn't repeat it.

The rules serve the reader. When a rule makes a sentence worse, fix the sentence another way or leave it alone.

If you find a jargon word that `unslop` doesn't list yet, propose it and its replacement as an addition to the abstract-metaphor-nouns rule in your reply, with the diff. Don't edit `unslop` yourself.

## Pick the mode first (Diátaxis)

A document has one mode. Two questions pick it: does the content support doing something or understanding something, and does it serve someone learning or someone working?

| | Learning | Working |
|---|---|---|
| Doing | Tutorial | How-to guide |
| Understanding | Explanation | Reference |

The same test works on a single sentence that seems out of place.

**Tutorial.** The reader is learning by doing, and their success is your responsibility. Open with what they will build. Every step produces a visible result, and you tell them what they should see: the output, the prompt, the log line. Keep explanation to a clause and a link, because long asides interrupt the lesson. Write as "we", in commands: "First, run x. Now, open y."

**How-to guide.** The reader is competent and has a specific goal. Solve a problem a person has, not an operation the software supports. Give only the steps; link background instead of including it. Allow for forks: "If you need x, do y." Title it by the task: "How to calibrate the sensor", not "Sensor calibration".

**Reference.** Describe the thing and nothing else: no instructions, persuasion, or opinion. Be complete and state facts, options, limits, and errors without hedging. Mirror the structure of the thing described so readers can move between code and docs. Generate it from code where you can so it stays accurate.

**Explanation.** One bounded topic, readable away from the product. The title should still make sense with "About..." in front of it. Start from a real "why" question and give context: design decisions, history, constraints, alternatives. This is the only mode where opinion belongs: weigh the trade-offs and say what you conclude, instead of listing pros and cons.

Don't mix modes. A reference table inside a tutorial, or an argument inside a how-to guide, should be split out and linked.

Source: diataxis.fr.

## Address the reader (Google developer style)

- Write to "you", in the present tense. Use "will" only for things that happen later.
- Write instructions as commands ("Click **Submit**."), not "should be done".
- Put the condition before the instruction: "To delete the document, click **Delete**." The reader can skip what doesn't apply.
- Put the common case first and exceptions after.
- Don't use "please" in instructions, and don't call a step "simple", "easy", or "quick". A reader who needed the doc didn't find it simple.
- Don't pre-announce features ("we will soon support...").
- Don't start consecutive sentences with the same phrase.
- Link text says where the link goes: the page title or a short description, never "click here". Prefer a sentence of context on the page to a link away from it.
- Headings state the point, not just the topic ("Pick the mode first", not "Modes"). Task headings are verb phrases ("Create an instance"); concept headings are noun phrases. One h1 per page, and don't skip levels.
- Use numbered lists for sequences and bullets for everything else. Introduce a list with a complete sentence, and keep items parallel.
- Put code in code font and UI labels in bold. Use the serial comma. Instead of "etc.", say up front that a list is partial.

Source: developers.google.com/style.

## Control how much each sentence carries (Simplified Technical English)

- Give each instruction its own sentence, and split a sentence that carries two unrelated points.
- Consider splitting instructions longer than about 20 words and other sentences longer than about 25.
- Put a warning or condition before the step it applies to.
- Give each word one meaning. If "check" means inspect, don't also use it to mean restrain.
- Prefer a plain verb to an "-ing" form where you can. "-ing" words can play several grammatical roles and are easy to misread.

Source: ASD-STE100, Issue 9.

## Remove double readings (Global English)

- Put "only" and "not" next to the word they modify. "Only fails on growth" and "fails only on growth" mean different things.
- Break up long noun stacks. "The proto import budget check script" becomes "the script that checks the proto-import budget".
- Make each "it", "they", and "this" refer to one obvious thing. Repeat the noun when in doubt, and don't use "this" or "which" to refer to a whole clause.
- Don't drop verbs. "Phase 1 moves the converters and Phase 2 the runtime" leaves Phase 2 without a verb.
- Keep small words that show structure. "Ensure that the switch is off" keeps "that" so the sentence parses one way.
- Repeat the article in a series when the items are distinct: "the client and the host".
- When "and" or "or" could group two ways, use "both...and", "either...or", or restructure.
- Text in parentheses should be a complete phrase or its own sentence. Don't write plurals as "(s)".
- Avoid slashes: write "a, b, or both" instead of "a/b" or "and/or".
- When editing, don't reword sentences whose meaning didn't change; the churn costs reviewers time.
- Avoid idioms, Latin abbreviations, and metaphors. Non-native readers, translators, and agents all parse plain constructions best.

Source: Kohl, *The Global English Style Guide* (SAS Press).

## PR descriptions, commit messages, and repo specifics

- PR descriptions and commit messages follow every layer except Diátaxis. A PR description is a briefing a reviewer can read in under a minute. Link logs, SHA lists, and metric tables instead of pasting them.
- Product UI strings aren't documentation. Follow the product's copy guidelines for those.
- Use real paths and symbols. Any count or file tree in a doc must be true at the commit that lands it; include the command that regenerates it.
- Match the repository's indentation in code snippets.

## Example

Before:

> Configuration of the proto import ratchet budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

After:

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.
