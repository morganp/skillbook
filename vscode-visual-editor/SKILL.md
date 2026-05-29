---
name: vscode-visual-editor
description: Build a VS Code visual/custom editor extension where a webview hosts a graphical editor that round-trips JSON (or other structured text) with a TextDocument. Use this skill whenever the user wants to wrap an existing web-based visual editor (React/Svelte/Vue/plain JS) as a VS Code custom editor, add a "visual edit" panel for a structured file format, embed a graphical editor inside a webview that syncs with a `.json`/`.yaml`/`.xml`/`.md` file, or add a CodeLens "Edit visually" affordance for fenced code blocks. Triggers on phrases like "VS Code plugin for editing X visually", "custom editor", "webview editor", "graphical editor for JSON files", or "edit fenced block visually".
---

# VS Code Visual Editor Skill

Build a VS Code extension that hosts a graphical editor in a webview and keeps it in sync with a TextDocument. Covers the eight non-obvious patterns that cause the typical multi-day debugging cycle when JSON fails to round-trip cleanly between webview and document.

## When to use

- User has existing web editor (React/Svelte/Vue/vanilla) and wants VS Code integration
- Custom editor for structured file format (`.foo.json`, `.bar.yaml`, etc.)
- "Edit visually" CodeLens above fenced code blocks in Markdown
- Bidirectional sync between webview UI state and document text

## Architecture

```
┌────────────────────┐  postMessage  ┌──────────────────────┐
│ Extension Host (TS)│ ◄──────────► │ Webview (HTML+JS)    │
│  - CustomEditor    │               │  - acquireVsCodeApi  │
│  - WorkspaceEdit   │               │  - mounts editor UI  │
│  - TextDocument    │               │  - IIFE bundle       │
└────────────────────┘               └──────────────────────┘
        ▲                                       
        │ onDidChangeTextDocument               
        ▼                                       
   <file on disk>                               
```

Webview cannot import npm modules at runtime. Bundle your editor as an IIFE (Vite `formats: ['iife']`) that attaches a global, then copy the bundle into the extension's `media/` folder before packaging.

## Message protocol (the canonical contract)

**Inbound** (extension → webview):
- `{ type: 'init', payload: { initial, readonly? } }` — sent in response to `hello`
- `{ type: 'setJson', payload: '<text>' }` — pushed on external edits

**Outbound** (webview → extension):
- `{ type: 'hello' }` — webview ready, requesting init
- `{ type: 'change', payload: { json, jsonText } }` — user edited something
- `{ type: 'command', payload: { type: 'save' | ... } }` — discrete actions

## The eight patterns that bite

### 1. Handshake — `hello` first, `init` in reply

DO NOT push `init` from `resolveCustomTextEditor`. Webview script load is async; you'll race and lose the message. Have webview send `hello` after `acquireVsCodeApi()`, reply with `init`.

```js
// webview
vscode.postMessage({ type: 'hello' });
window.addEventListener('message', (ev) => {
  if (ev.data.type === 'init') mountEditor(ev.data.payload.initial);
});
```

```ts
// extension
panel.webview.onDidReceiveMessage((m) => {
  if (m.type === 'hello') panel.webview.postMessage({ type: 'init', payload: { initial: document.getText() } });
});
```

### 2. Loopback flag — break the echo

`applyEdit` triggers `onDidChangeTextDocument`, which would post `setJson` back to the webview, which would re-render and post `change`, which would `applyEdit` again. Cursor jumps, focus lost, infinite loops on slow machines.

```ts
let ourEdit = false;
vscode.workspace.onDidChangeTextDocument((e) => {
  if (e.document.uri.toString() !== document.uri.toString()) return;
  if (ourEdit) { ourEdit = false; return; }   // ← skip our own edits
  panel.webview.postMessage({ type: 'setJson', payload: document.getText() });
});

// when applying webview change:
ourEdit = true;
await vscode.workspace.applyEdit(edit);
```

### 3. Idempotent change check

Editor frameworks emit `onChange` on mount and on programmatic `setValue`. Compare before writing or you'll dirty the document on every focus.

```ts
case 'change': {
  const text = m.payload?.jsonText ?? '';
  if (text === document.getText()) return;   // ← no-op guard
  ...
}
```

### 4. Whole-document replace range

```ts
edit.replace(document.uri, new vscode.Range(0, 0, document.lineCount, 0), text);
```

`document.lineCount` (not `lineCount - 1`) plus column `0` covers the document including a trailing newline. Using `document.getText().length` and `positionAt` works too but is slower.

### 5. Normalize relaxed input formats

Many "JSON" formats in the wild are JS object literals (unquoted keys, trailing commas, single quotes). Parsing with `JSON.parse` fails; the webview sees an empty diagram and the user thinks the plugin is broken.

```ts
function normalizeJson(source: string): string {
  try { JSON.parse(source); return source; }
  catch {
    try {
      const obj = new Function('return (' + source + ')')();   // ← JS literal eval
      return jsonStringify(obj, detectIndent(source));
    } catch { return source; }                                 // ← bail to original
  }
}
```

For non-JSON formats (YAML/TOML), substitute the appropriate parser. Always fall through to the original text so a parse failure doesn't blank the user's file.

### 6. Preserve indent + minimize diff churn

If you re-serialize with `JSON.stringify(obj, null, 2)`, every edit produces a giant diff because you collapsed/expanded everything. Detect existing indent, use hybrid compact/pretty serialization (compact for objects ≤80 chars, pretty otherwise):

```ts
function detectIndent(source: string): string | number {
  const m = source.match(/\n(\s+)/);
  if (!m) return 0;
  return m[1][0] === '\t' ? '\t' : m[1].length;
}
```

See `extension.ts` `jsonStringify` in the wavedrom-editor repo for a reference hybrid serializer.

### 7. Fenced block — capture start, rescan end

For `wavedrom.editFencedBlock`-style CodeLens edits inside Markdown, the closing fence moves as content changes. Save only the start `Position`, re-scan to find the current closing ```` ``` ```` on every change.

```ts
const contentStart = range.start;   // ← stable
panel.webview.onDidReceiveMessage(async (m) => {
  if (m.type !== 'change') return;
  const doc = await vscode.workspace.openTextDocument(uri);
  let endLine = contentStart.line;
  while (endLine < doc.lineCount && doc.lineAt(endLine).text.trimEnd() !== '```') endLine++;
  const currentRange = new vscode.Range(contentStart, new vscode.Position(endLine, 0));
  const edit = new vscode.WorkspaceEdit();
  edit.replace(uri, currentRange, m.payload.jsonText + '\n');
  await vscode.workspace.applyEdit(edit);
});
```

CodeLens provider:

```ts
const re = /^```wavedrom\s*$([\s\S]*?)^```\s*$/gm;
// inside loop:
const start = doc.positionAt(m.index + m[0].indexOf('\n') + 1);
const end   = doc.positionAt(m.index + m[0].lastIndexOf('```'));
lenses.push(new vscode.CodeLens(new vscode.Range(start, end), {
  title: '$(edit) Edit visually',
  command: 'your.editFencedBlock',
  arguments: [doc.uri, new vscode.Range(start, end), m[1]],
}));
```

### 8. CSP + nonce + `localResourceRoots`

Webview HTML needs Content-Security-Policy. Without nonce, your inline bootstrap script is blocked silently. Without `localResourceRoots`, your bundled JS/CSS won't load.

```ts
panel.webview.options = {
  enableScripts: true,
  localResourceRoots: [vscode.Uri.joinPath(ctx.extensionUri, 'media')],
};
```

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'none';
               img-src ${webview.cspSource} data:;
               style-src ${webview.cspSource} 'unsafe-inline';
               script-src 'nonce-${nonce}' ${webview.cspSource};" />
<link rel="stylesheet" href="${uri('embed.css')}" />
<script nonce="${nonce}" src="${uri('embed.js')}"></script>
<script nonce="${nonce}">
  const vscode = acquireVsCodeApi();
  // ... handshake
</script>
```

Always also set `retainContextWhenHidden: true` so the editor state survives tab-switching:

```ts
vscode.window.registerCustomEditorProvider(VIEW_TYPE, provider, {
  webviewOptions: { retainContextWhenHidden: true },
});
```

## Project layout

```
extension/
├── package.json              # contributes.customEditors, activationEvents
├── tsconfig.json
├── src/extension.ts          # CustomTextEditorProvider
├── media/                    # webview assets (copied from shared bundle)
│   ├── embed.js              # IIFE bundle of your editor
│   └── embed.css
└── out/extension.js          # tsc output
```

## `package.json` essentials

```json
{
  "engines": { "vscode": "^1.85.0" },
  "main": "./out/extension.js",
  "activationEvents": [
    "onCustomEditor:your.editor",
    "onLanguage:markdown"
  ],
  "contributes": {
    "customEditors": [{
      "viewType": "your.editor",
      "displayName": "Your Visual Editor",
      "selector": [{ "filenamePattern": "*.your.json" }],
      "priority": "default"
    }],
    "commands": [{ "command": "your.editFencedBlock", "title": "Edit visually" }]
  },
  "scripts": {
    "compile": "tsc -p ./",
    "build:webview": "mkdir -p media && cp ../../dist/editor.iife.js media/embed.js && cp ../../dist/editor.css media/embed.css",
    "vscode:prepublish": "npm run build:webview && npm run compile",
    "package": "vsce package"
  }
}
```

Use `vscode:prepublish` to chain bundle-copy + compile before `vsce package`. Don't ship `node_modules`; `vsce` will warn but proceed.

## Editor mount API (shared embed contract)

Your editor IIFE should expose a `mount(rootEl, options)` returning a control handle:

```ts
window.YourEditor = {
  mount(root, { initial, embedded, onChange, onCommand }) {
    // ... render into root ...
    return {
      setJson(text) { /* programmatic update from extension */ },
      destroy() {},
    };
  }
};
```

The webview script wires `onChange` → `postMessage('change')` and listens for `setJson` → `editorApi.setJson(text)`.

## Reference implementation

Working reference: `packages/vscode-extension/src/extension.ts` in `wavedrom-editor` repo. ~240 lines, single file, implements all eight patterns above.

## Build + install

```sh
npm run build:webview       # bundle editor → media/
npm run package             # produces <name>-<version>.vsix
# VS Code: Extensions → ... → Install from VSIX
```

Bump version on every build (semver). Increment version string in any debug banner inside the HTML so you can see the loaded build at a glance.

## Common failure modes & fixes

| Symptom | Cause | Fix |
|---|---|---|
| Webview shows blank, no errors | Init posted before webview script loaded | Use `hello`/`init` handshake (#1) |
| Cursor jumps, file flickers | Loopback echo | Add `ourEdit` flag (#2) |
| File marked dirty on open | Editor emits onChange on mount | Idempotent guard (#3) |
| Massive diff on every edit | Reserializing kills formatting | Detect indent, hybrid stringify (#6) |
| Empty diagram for valid input | Source is JS literal not strict JSON | `new Function` fallback (#5) |
| Inline script not running | Missing CSP nonce | Add nonce, list in CSP (#8) |
| Bundle 404 in webview | Missing `localResourceRoots` | Add `media/` path (#8) |
| Editor state lost on tab switch | Default disposes hidden webview | `retainContextWhenHidden: true` (#8) |
| Fenced-block edit corrupts trailing content | Saved end Position went stale | Rescan closing fence (#7) |
