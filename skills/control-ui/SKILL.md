---
name: control-ui
description: Drive and inspect a web, desktop, or Electron UI with browser automation or CDP to gather evidence. Use for local UI verification, screenshots, accessibility snapshots, performance profiles, visual diffs, or reproducing UI bugs.
disable-model-invocation: true
---

# Control UI

Verify UI behavior with evidence from a real browser. Reuse the repo's own Playwright, browser, or Electron harness if it has one; otherwise drive the app's dev server or Chromium debug port with whatever browser automation the host provides.

Use it for:

- Reproducing bugs that depend on real focus, keyboard input, scrolling, resizing, or rendering.
- Verifying visual or accessibility changes with screenshots and snapshots.
- Checking local web, desktop, or Electron behavior before shipping.
- Capturing console logs, network logs, CPU profiles, traces, or heap snapshots.
- Producing before and after evidence for a PR.

## Pick a driver

Use the first one available:

1. **The repo's harness**: Playwright or Cypress tests, Storybook, browser scripts, Electron launch scripts, snapshot tools. It already knows the app's setup.
2. **The host's browser tools**: a browser-automation MCP server or built-in browser tool, if the session has one (for example Chrome DevTools MCP, Playwright MCP, a Chrome extension integration in Claude Code, or Codex's browser or computer-use tools). These give you navigation, clicks, accessibility snapshots, screenshots, console, and network without writing a script. Check the session's tool list rather than assuming.
3. **A one-off Playwright script**: if Playwright is already installed in the repo or globally. Don't add it as a project dependency just for a probe unless the user asks.
4. **Raw CDP**: for Electron or any Chromium app started with `--remote-debugging-port`, or when you need a capability the higher-level tools don't expose.

## Setup

1. Start the app with the repo's documented dev command. Note the URL or debug port.
2. For Electron or another Chromium shell, launch with `--remote-debugging-port=<port>` when the app allows it.
3. Select the page by a stable app marker (a root element, landmark, or `data-*` attribute), not by tab order.
4. Target elements by accessibility role and name, or stable `data-*` selectors, before coordinates.

## One-off web probe

```javascript
import { chromium } from "playwright";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
await page.goto("http://127.0.0.1:<port>");
await page.getByRole("button", { name: /submit/i }).click();
await page.screenshot({ path: "/tmp/ui-harness-after.png", fullPage: true });
await browser.close();
```

## CDP probe for Electron

```javascript
import { chromium } from "playwright";

const browser = await chromium.connectOverCDP("http://127.0.0.1:<debug-port>");
const pages = browser.contexts().flatMap((context) => context.pages());
let page;
for (const candidate of pages) {
  if (await candidate.locator("<app-root-selector>").count()) {
    page = candidate;
    break;
  }
}

if (!page) {
  console.log(await Promise.all(pages.map(async (p) => ({
    title: await p.title(),
    url: p.url(),
  }))));
  throw new Error("No matching app page found");
}

await page.screenshot({ path: "/tmp/ui-harness-cdp.png", fullPage: true });
await browser.close();
```

Replace `<app-root-selector>` with a stable marker from this repo. Many browser MCP servers can also attach to an existing debug port instead of launching their own browser; check the server's options.

## Interaction loop

1. Take a snapshot (accessibility tree preferred) or screenshot before acting.
2. Pick the target from that latest snapshot.
3. Perform one action: click, type, keypress, drag, scroll, navigate, or resize.
4. Take a fresh snapshot or screenshot.
5. Check that the expected state change happened.
6. Save before and after artifacts when the user asked for proof.

## Raw CDP capabilities

Drop to raw CDP only when the higher-level tools can't do the job:

- **Performance**: CPU profiles, traces, paint flashing, FPS meter, layout shifts.
- **Memory**: heap snapshots and forced GC for leak investigations.
- **Network**: request blocking, throttling, cache disabling, request and response logs.
- **Rendering**: viewport changes, color scheme and reduced-motion emulation, accessibility checks.
- **Debugging**: console streaming, exception capture, DOM snapshots.

## Page selection

When several windows or tabs share a debug port:

- Match a positive marker for the surface under test, such as the app root selector.
- Add a negative marker to exclude a similar surface when needed.
- If nothing matches, list the available page titles and URLs instead of guessing.

## Guardrails

- Re-query elements after navigation or structural changes; old references go stale.
- Click by coordinates only right after a fresh screenshot.
- Keep test data local and disposable.
- Don't save screenshots or heap snapshots from privacy-sensitive workspaces unless the user agrees.
- Discover this repo's selectors, ports, and scripts; don't copy them from another project.
- Shut down dev servers, debug sessions, and temp browser profiles you started when done.
