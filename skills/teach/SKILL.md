---
name: teach
description: Explains a body of work (a subsystem, a change, a concept in the codebase) so a person actually understands it, combining what the `how` and `why` skills find into one plain account at the person's pace. Use for "teach me this", "help me really understand X", or "explain this change to me".
disable-model-invocation: true
---

# Teach

Other skills named here don't appear in the model's skill list. To use one, read `<this skill's dir>/../<name>/SKILL.md` and follow it.

Explain what a thing is, how it works, and why it's built that way, in one plain account at the person's pace. The goal is their understanding; you don't change anything.

Teach builds on `how` and `why`. Orient yourself on what the work is and what it touches, run `how` for the mechanics and `why` for the reasons, then blend their results into one explanation that leads with what matters to this person. Reword freely, except for `why`'s confidence language: its hedges are findings, so keep them intact.

## Steps

1. **Decide what they should come away understanding.** Pick a few things, based on why they're asking (about to change it, reviewing it, debugging it, new to it) and what they already know. Read both from the conversation rather than quizzing them. Skip what they clearly know, and put the depth where their question is.
2. **Let `how` and `why` do the research.** Read enough code yourself to get oriented, then run `how` and `why` in parallel and combine what they return. Size it to the question: a subsystem needs both; a small change may need only one. Keep `why` narrow by default, since its full sweep is slow. Put the narrowing in the request itself (a scoped question, git plus one or two sources) so `why` records the skipped categories in its own output. Widen it only when the reasons are the point.
3. **Start with a plain definition.** Name the thing and say what it is in general terms, the way a senior engineer would say it out loud, using its common name if it has one. Then tie it to the case at hand ("in X, we use this to...") and build from there: how it works, the deeper reasons, the edge cases. For each part, explain the problem it solves and how it actually works. When it helps, walk through what happens as the person does something (opens a long chat, scrolls up). Listing functions and constants is reference material, not teaching.

   Give the smallest complete answer first, a sentence or two, and stop. Add layers when they ask.
4. **Keep it a conversation.** Offer to go deeper or move on, and follow their lead. No quizzes, no asking them to repeat it back, no announcing that a part is important or tricky; just explain it. Where you'd naturally pause, stop and let them respond. If you're running one-shot with no live person, deliver the explanation cleanly and put the offer to go deeper at the end.
5. **Show as well as tell.** Open the diff, the code, or the debugger when that's the fastest way to make it land. Draw when a picture is faster than words.
   - For anything with three or more moving parts, build the picture in a sequence of diagrams, each redrawing the previous one and adding one part, so the reader watches the system assemble. To teach a flow from A to B to C: draw A to B, then redraw with C added, then redraw with the return path or the next piece. One all-at-once diagram, especially saved for the end, is reference material.
   - Use mermaid for flows and structures where labels carry the meaning.
   - For spatial ideas (layout, overlap, scroll position, before and after), use an image-generation tool if your host has one, in a whiteboard-sketch style with a few short labels (image models garble long text). The build-up rule applies to images too.
   - A single simple point needs no figure.

## How to write it

Write through `unslop`, which owns sentence-level style, in plain spoken English, as you'd explain it to a colleague. Be tight without being terse, and keep the part that makes it click. Prefer short sentences. State the concrete mechanism rather than a metaphor, a framing label, a mirror sentence (both in the mannered-prose rule), or a preview of what's coming. Don't echo the step names above as headings; they're instructions to you. Target density:

> Virtualization runs in two parts, one for rendering and one for loading from disk. When an item scrolls out past the buffer, both its DOM node and its in-memory data are evicted.

The reply is the explanation itself, not a report about what you did. Lead with the main point, give the plain account of what it is, how it works, and why, and end with the threads worth following up with `how` or `why`.
