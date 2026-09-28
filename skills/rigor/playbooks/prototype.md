# Prototype

You own the design decision, not the code. The prototype is a throwaway instrument; the real build follows the Feature playbook.

This is the one playbook where the usual bar is reversed: speed over polish, code quality doesn't matter, and no planning step. The rigor is in choosing the right design cheaply. Propose variations the user didn't ask for, and discard an approach freely to try another.

1. Name the decision the prototype exists to make: which layout, interaction, or density, or, for an empirical question, which behavior, timing, or approach. If there's no decision to make, don't prototype; use the Feature playbook.
2. When the design space is open, gather references first: search for prior art, summarize a moodboard of themes, palettes, and layouts, and let the user pick directions before you build. Skip this when the direction is already set.
3. Build the throwaway in an isolated scratch directory, separate from production source. For a visual decision, use vanilla HTML/CSS/JS or the lightest stack that renders the idea, with CDN dependencies and a hot-reloading dev server. For a behavioral or timing decision, write the smallest script that exercises the question. No production framework, tests, or abstractions.
4. When comparing alternatives, put them behind one switcher (buttons or a keypress) with each variant labeled. This is the cheap form of the `exhaust-the-design-space` principle.
5. Verify on the relevant surface. For a visual decision, screenshot each variant and drive the interaction with `control-ui`. For a behavioral or timing decision, observe the thing you're deciding: log the timing, print the output, or watch the render. The observation is the test here, not an assertion.
6. Present the alternatives, tradeoffs, and a recommendation. The output is a decision plus the throwaway artifact, not shippable code. Hand the chosen direction to the Feature playbook (or `architect` for the shape) for the real build.

**Reply:** the variants explored; the evidence (screenshots for a visual decision, observed output or timing for a behavioral one); tradeoffs; your recommendation; and the scratch path. State plainly that the prototype is throwaway.
