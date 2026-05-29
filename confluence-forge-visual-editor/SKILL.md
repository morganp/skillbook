---
name: confluence-forge-visual-editor
description: Build a Confluence Cloud (Atlassian Forge) macro that wraps an existing web-based visual editor as a Custom UI app, with edit-on-click modal flow and per-macro persistence via Forge app storage. Use this skill whenever the user wants to wrap a React/Svelte/Vue/vanilla web editor as a Confluence Cloud macro, add a "visual edit" modal to a Confluence Custom UI macro, persist structured data (JSON/YAML/XML) per macro instance via Forge storage, or build a draw.io-style click-to-edit experience for a custom content type in Confluence. Triggers on phrases like "Confluence Forge plugin", "Atlassian Forge macro", "Confluence Cloud editor", "custom macro for Confluence", "visual editor in Confluence", or "@forge/bridge".
---

# Confluence Forge Visual Editor Skill

Build a Confluence Cloud (Forge) Custom UI macro that hosts a graphical editor in an iframe, persists JSON per macro instance, and opens a full-screen edit modal on click. Covers the ten non-obvious failure modes that ate a multi-hour debugging cycle the first time through.

## When to use

- User has an existing web editor (React/Svelte/Vue/vanilla) and wants Confluence Cloud integration
- "Edit visually" UX on a Confluence macro (draw.io-style)
- Per-macro instance persistence of structured data (JSON / YAML / XML)
- Bidirectional sync between a webview UI and Forge app storage

## When NOT to use

- Confluence Data Center / Server (different platform — Maven + Java + atlassian-plugin.xml, not Forge)
- Confluence-wide rendering (e.g. a sidebar app) — different module type (`globalPage` / `confluencePageContextMenu`), not a macro
- Connect apps (legacy cloud platform) — different SDK, different deploy path

## Architecture

```
┌────────────────────────┐  invoke()    ┌─────────────────────────┐
│ Macro inline iframe    │ ───────────► │ Forge resolver function │
│  - view.getContext()   │              │  - @forge/resolver      │
│  - WavedromView.render │              │  - storage.get/set      │
│  - "Edit" button       │              └─────────────────────────┘
└──────────┬─────────────┘                          ▲
           │ new Modal({...}).open()                │
           ▼                                        │
┌────────────────────────┐  invoke()    ─────────────┘
│ Editor modal iframe    │
│  - WavedromEditor.mount│
│  - Save → view.close() │
└────────────────────────┘
```

Two iframes (macro view + edit modal), both Custom UI HTML/JS. Both talk to a single Forge backend resolver via `invoke()`. State lives in Forge `storage.set()` keyed by the macro's stable `localId`.

## Package layout

```
packages/confluence-forge/
├── manifest.yml                  # module declarations
├── package.json                  # @forge/api + @forge/resolver + @forge/bridge + vite
├── src/index.js                  # resolver dispatcher
├── src-ui/
│   ├── macro/
│   │   ├── index.html            # inline view shell
│   │   ├── main.js               # imports @forge/bridge, ES module
│   │   └── style.css             # external (no inline <style>)
│   └── editor/
│       ├── index.html            # modal shell
│       ├── main.js
│       └── style.css
├── built/                        # vite output, what the manifest points at
│   ├── macro/{index.html, assets/, bundle/view.js}
│   └── editor/{index.html, assets/, bundle/embed.js, bundle/embed.css}
└── vite.config.js                # builds src-ui/<entry>/ → built/<entry>/
```

## The ten patterns that bite

### 1. Custom UI HTML MUST be bundled — do not deploy raw HTML

Forge Custom UI iframes enforce strict CSP:
- `style-src 'self'` — no `'unsafe-inline'` → inline `<style>` blocks blocked
- `script-src 'self' ...` — no bare module specifiers → `import { view } from '@forge/bridge'` fails with `Failed to resolve module specifier "@forge/bridge"`

Two errors that surface in the iframe's DevTools:
```
Applying inline style violates the following Content Security Policy directive 'style-src 'self' ...'
Uncaught TypeError: Failed to resolve module specifier "@forge/bridge". Relative references must start with either "/", "./", or "../".
```

Fix: write source in `src-ui/<entry>/{index.html,main.js,style.css}` with `<link rel="stylesheet">` (no inline `<style>`) and `<script type="module" src="./main.js">`. Run Vite to bundle:

```js
// vite.config.js
import { defineConfig } from 'vite';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const entry = process.env.FORGE_UI_ENTRY || 'macro';

export default defineConfig({
  root: resolve(__dirname, `src-ui/${entry}`),
  base: './',
  build: {
    target: 'es2022',                                   // ← top-level await needs this
    outDir: resolve(__dirname, `built/${entry}`),
    emptyOutDir: true,
    assetsDir: 'assets',
    rollupOptions: {
      input: resolve(__dirname, `src-ui/${entry}/index.html`),
    },
  },
});
```

Build each entry separately via env var:
```sh
FORGE_UI_ENTRY=macro  vite build
FORGE_UI_ENTRY=editor vite build
```

Vite extracts inline CSS into external files (CSP-clean) and resolves `@forge/bridge` against `node_modules` so the bare import gets bundled in.

### 2. Resolver — Custom UI invoke() requires it, not standalone functions

This was the longest debugging session. Custom UI macros invoke backend functions through a **resolver dispatcher**, not via standalone `function:` keys.

Wrong:
```yaml
function:
  - key: wavedrom-load
    handler: index.loadDiagram
  - key: wavedrom-save
    handler: index.saveDiagram
```
With this, `invoke('wavedrom-load', payload)` in the iframe fails with:
```
Entry point "resolver" for extension "wavedrom-macro" could not be invoked as it does not exist or does not reference a function or endpoint
```

Right — bind a single resolver function to the macro module and dispatch by key:

```yaml
macro:
  - key: wavedrom-macro
    resource: macro-view
    resolver:
      function: resolver           # ← bind a single resolver
function:
  - key: resolver
    handler: index.handler
```

```js
// src/index.js
import ResolverImport from '@forge/resolver';
import { storage } from '@forge/api';

// Webpack CJS-interop fallback (see pattern 3).
const Resolver = ResolverImport?.default || ResolverImport;

const resolver = new Resolver();

resolver.define('wavedrom-load', async ({ payload }) => {
  const { id } = payload || {};
  // ...
  return { body, engine };
});

resolver.define('wavedrom-save', async ({ payload }) => {
  // ...
  return { ok: true };
});

export const handler = resolver.getDefinitions();
```

The iframe calls `invoke('wavedrom-load', {...})`. The string matches `resolver.define('wavedrom-load', ...)`.

### 3. Webpack CJS-interop guard around `@forge/resolver`'s default import

Forge bundles your function with webpack. `@forge/resolver`'s default export sometimes lands at `.default` after the transform, so `new Resolver()` against the raw import object fails with:
```
There was an error invoking the function - _forge_resolver__WEBPACK_IMPORTED_MODULE_0__ is not a constructor
```

Always guard:
```js
import ResolverImport from '@forge/resolver';
const Resolver = ResolverImport?.default || ResolverImport;
```

### 4. Do NOT set `"type": "module"` in the Forge package.json

The Forge bundler + resolver combo expects CJS interop. Adding `"type": "module"` to `packages/confluence-forge/package.json` causes the resolver to fail to load. Use `.js` files with ESM syntax — webpack handles them — but don't flag the package as ESM.

### 5. Manifest pitfalls

- `render: native` is **UI Kit only**. Strip it from Custom UI macros (otherwise the macro silently fails to register a usable resource).
- `nodejs20.x` is **deprecated**. Use `nodejs22.x` or `nodejs24.x`. `forge deploy` rejects 20.x at manifest validation.
- `icon: resource:<key>/<file>` wants a single-file resource. Pointing at a directory key fails with "Hosted resource for icon or thumbnail missing". Easiest: drop the icon from the manifest entirely (or declare the resource as the literal `.svg` path).

### 6. Macro instance identity — use `ctx.extension.localId`, skip the config dance

The intuitive approach — mint a UUID in `defaultConfig()` and read it from `ctx.extension.config.uuid` — does **not** work unless the user submits a macro config form. We don't render a config form, so config stays empty, no UUID is written, and every save errors with "missing id".

Right approach: use Forge's stable per-instance ID, available with no config:

```js
const ctx = await view.getContext();
const id  = ctx.extension?.localId;             // ← stable per macro instance
await invoke('wavedrom-load', { id });
```

Storage keys: `diagram:<localId>`, `engine:<localId>`. Caveat: `localId` does not change on page copy, so both copies share the storage entry (edits leak between them). Acceptable trade-off vs the much heavier attachment-based approach draw.io uses.

### 7. Modal flow — `Modal.open()` from view, `view.close()` from modal

From the macro view:
```js
import { Modal } from '@forge/bridge';
const modal = new Modal({
  resource: 'editor-modal',                   // resource key from manifest
  size: 'max',
  context: { id, initial, engine },           // arbitrary payload
  onClose: async () => { await refresh(); },  // re-render after edit
});
await modal.open();
```

Inside the modal, the passed `context` is at `ctx.extension.modal.context` in current Forge (older docs say other paths — defensively try multiple). Close with `view.close()`. Do **not** use `view.submit()` — that's the config submission flow, not the modal flow.

```js
const ctx = await view.getContext();
const { id, initial } = ctx.extension?.modal?.context || {};
// ... edit ...
await invoke('wavedrom-save', { id, body: latest });
view.close();
```

### 8. Bind click handlers BEFORE async work, or buttons never fire

Top-level `await view.getContext()` runs before any subsequent `addEventListener`. If `getContext` rejects (rare but happens), the listener is never attached and the Edit button does nothing. Bind first, resolve later:

```js
const editBtn = document.getElementById('edit');
let macroId = null;
async function resolveId() {
  if (macroId) return macroId;
  const ctx = await view.getContext();
  macroId = ctx.extension?.localId || null;
  return macroId;
}
editBtn.addEventListener('click', async () => {
  const id = await resolveId();
  // ... open modal ...
});
```

### 9. Call `view.resize()` after each render

Custom UI iframes don't auto-grow to fit content. Without `view.resize()` the macro looks clipped — and corner-positioned UI (Edit button, dropdowns) sits off-screen and looks broken.

```js
function render(jsonText) {
  previewEl.innerHTML = renderDiagram(jsonText);
  try { view.resize(); } catch { /* older bridges no-op */ }
}
```

Same call after the modal `onClose` re-render.

### 10. Edit button must be always-visible (not hover-revealed)

Hover-reveal works on a wide draw.io canvas but the WaveDrom macro can be 40-60 px tall — users miss the hover target entirely. Always-visible chip-style button works better:

```css
.edit-btn {
  position: absolute; top: 6px; right: 6px;
  background: #fff; border: 1px solid #d3d3d8;
  font-size: 12px; padding: 4px 10px; border-radius: 4px;
  z-index: 10;
}
.edit-btn:hover { background: #f4f5f7; }
```

## Backend resolver template

```js
// src/index.js
import ResolverImport from '@forge/resolver';
import { storage } from '@forge/api';

const Resolver = ResolverImport?.default || ResolverImport;

const DEFAULT_SPEC = { /* ...your default content... */ };
const DEFAULT_ENGINE = 'native';

const bodyKey   = (id) => `body:${id}`;
const engineKey = (id) => `engine:${id}`;

const resolver = new Resolver();

resolver.define('load', async ({ payload }) => {
  const { id } = payload || {};
  if (!id) throw new Error('load: missing id');
  let body = await storage.get(bodyKey(id));
  if (!body) {
    body = JSON.stringify(DEFAULT_SPEC, null, 2);
    await storage.set(bodyKey(id), body);
  }
  const engine = (await storage.get(engineKey(id))) || DEFAULT_ENGINE;
  return { body, engine };
});

resolver.define('save', async ({ payload }) => {
  const { id, body, engine } = payload || {};
  if (!id) throw new Error('save: missing id');
  if (typeof body !== 'string') throw new Error('save: body must be string');
  await storage.set(bodyKey(id), body);
  if (engine) await storage.set(engineKey(id), engine);
  return { ok: true };
});

export const handler = resolver.getDefinitions();
```

## Manifest template

```yaml
modules:
  macro:
    - key: my-macro
      resource: macro-view
      resolver:
        function: resolver
      title: My Visual Macro
      description: ...
      properties:
        layout: full-width

  function:
    - key: resolver
      handler: index.handler

resources:
  - key: macro-view
    path: built/macro/
  - key: editor-modal
    path: built/editor/

app:
  runtime:
    name: nodejs22.x
  id: ari:cloud:ecosystem::app/REPLACE_WITH_REAL_APP_ID

permissions:
  scopes:
    - storage:app
```

## package.json template

```json
{
  "name": "confluence-forge-myapp",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "build:ui": "FORGE_UI_ENTRY=macro vite build && FORGE_UI_ENTRY=editor vite build",
    "build": "npm run build:ui && cd ../.. && npm run build:forge:bundles",
    "deploy": "forge deploy",
    "install:dev": "forge install"
  },
  "dependencies": {
    "@forge/api": "^4.0.0",
    "@forge/bridge": "^4.0.0",
    "@forge/resolver": "^1.6.0"
  },
  "devDependencies": {
    "vite": "^6.3.5"
  }
}
```

Do **not** add `"type": "module"`.

## CLI / install / debug

Forge CLI is interactive — `forge login`, `forge register`, `forge create` cannot run in non-TTY shells (e.g. the Claude Code bash sandbox). Run those in a real terminal (Terminal.app / iTerm).

Once registered:
```sh
forge deploy --no-verify                                 # uploads code + resources
forge install -s <site>.atlassian.net -p Confluence \
              -e development --confirm-scopes --non-interactive
```

After changing module shape (adding/removing resolvers, changing resource paths) re-run `forge install --upgrade ...` — `forge deploy` alone won't refresh the macro module wiring.

Debug:
```sh
forge logs -s 30m -n 50          # function logs from past 30 minutes
```

Empty logs after a failed invoke ⇒ the resolver was **never called** (manifest binding problem, not function code). Logs with stack traces ⇒ resolver was called, your code threw.

Browser DevTools inside the iframe shows CSP / bundle errors. Forge iframes are sandboxed but DevTools attaches normally — F12 on the page works.

## Marketplace publishing

1. `forge deploy --environment production`
2. Developer console → Distribution → switch from Sharing to Marketplace: `https://developer.atlassian.com/console/myapps/<app-id>/manage/distribution`
3. Atlassian auto-creates a draft listing at `https://marketplace.atlassian.com/manage/vendors`
4. Fill: icon (512×512), tagline, description, screenshots (1280×720+, ≥1), categories, support URL, **privacy policy URL** (Atlassian requires one — a GitHub-hosted PRIVACY.md is fine)
5. Submit for review (5–10 business days first time, 1–3 days for updates)

Pre-marketplace, distribute via the Sharing-mode install link from the developer console:
```
https://developer.atlassian.com/console/install/<app-id>?signature=...&product=confluence
```
This link dies when you flip to Marketplace.

## Reference implementation

Working reference: `packages/confluence-forge/` in `wavedrom-editor` repo. Implements every pattern above.

## Common failure modes & fixes

| Symptom | Cause | Fix |
|---|---|---|
| Macro inserts but renders blank | Inline `<style>` blocked by CSP; bare ESM imports unresolved | Bundle with Vite (#1) |
| `Failed to resolve module specifier "@forge/bridge"` | Raw `import` deployed without bundling | #1 |
| `Applying inline style violates the following CSP directive` | Inline `<style>` in deployed HTML | #1 — extract to external CSS |
| `Entry point "resolver" for extension "<key>" could not be invoked` | No `resolver:` binding on macro module | #2 — bind resolver + dispatch via `resolver.define()` |
| `_forge_resolver__WEBPACK_IMPORTED_MODULE_0__ is not a constructor` | CJS interop ate the default export | #3 — guard `ResolverImport?.default || ResolverImport` |
| Resolver code never runs (forge logs empty) | `"type":"module"` set OR manifest binding broken | #4 or #2 |
| `nodejs20.x runtime is deprecated` | Old runtime in manifest | #5 — bump to `nodejs22.x` |
| `Hosted resource for icon or thumbnail missing` | Icon path points at a directory key | #5 — drop icon or use file path |
| "Cannot save: missing id" every time | Trying to use `config.uuid` without a config form | #6 — use `ctx.extension.localId` |
| Macro looks clipped, button off-screen | iframe sized to wrong height | #9 — call `view.resize()` after render |
| Edit button does nothing | Click listener attached after a failed `await` | #8 — bind listener first, resolve async inside |
| Save reaches function but data doesn't appear on reload | Modal context not flowing through | #7 — pass `context: {...}` to `new Modal`, read at `ctx.extension.modal.context` |
| `forge login`/`register` fails with "Prompts can not be meaningfully rendered in non-TTY environments" | Running in sandboxed shell | Use a real terminal (Terminal.app) |
