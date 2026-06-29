# Consume @novosapien/nova-ui

The generative chat UI (Nova): chat shell, the AG-UI/CopilotKit transport
(client + server), 5 generic renderers (card/table/chart/list/todo), a
tool→renderer registry, and one shared streaming/dedup engine. Extracted verbatim
from `ns-content-workforce-app`; the frontend half of nova-kernel's render
contract. **Optional per app** (a WhatsApp/Slack-only agent skips it).

- **Repo:** `Novosapien/nova-ui` → GitHub Packages `@novosapien/nova-ui`.
- **Versions:** `0.1.0` + `0.1.1` published; `0.1.2` is the CSS-leak + injectable-icons fix.
- **Peer deps you already own:** `@copilotkit/react-core`, `@copilotkit/runtime`,
  `next` (^16), `react`/`react-dom` (^19), `tailwindcss` (^4), `@ag-ui/client`.
  Everything else (Radix, recharts, lucide, markdown, date-fns) is a regular dep —
  installs transitively, nothing else to add.

> **Building the full chat surface** (conversation list + paginated history, slash
> commands, gen-UI replay / HITL-gate restore)? Those packaged recipes + their
> gotchas live in `consume-nova-ui-chat.md`; this file is the base consume surface.

---

## 1. Install

Set up `@novosapien` registry auth (see `cross-cutting-rules.md` Rule 4 — the
canonical `NODE_AUTH_TOKEN` + `always-auth=true` `.npmrc`), then:

```bash
npm i @novosapien/nova-ui
```

Dev fallback if CI auth isn't wired yet: a local tarball
(`"@novosapien/nova-ui": "file:../../nova-ui/novosapien-nova-ui-0.1.2.tgz"`) or
`"github:Novosapien/nova-ui#<tag>"`. Not CI/deploy-installable — swap to `"^0.1.2"`
before pushing.

---

## 2. Server route (App Router)

The transport is a **server** route. `app/api/copilotkit/route.ts`:

```ts
import { createNovaRuntimeHandler } from '@novosapien/nova-ui/server'

export const POST = createNovaRuntimeHandler({
  agentUrl: `${process.env.NOVA_AGENT_SERVICE_URL}/agent`,
})
```

`createNovaRuntimeHandler({ agentUrl, agentName?='nova', endpoint?='/api/copilotkit', forwardHeaders? })`
runs `CopilotRuntime` + `HttpAgent(agentUrl)` and **mirrors** the incoming
`authorization` header (+ onboarding `x-entity-id` when present, + any
`forwardHeaders`) into CopilotKit `properties`, forwarding to the agent.

> Import the handler **only** from `@novosapien/nova-ui/server` — it pulls in
> server-only deps; never into a client component.

Multiple surfaces = multiple routes (content-workforce onboarding uses a second:
`agentName:'onboarding'`, `endpoint:'/api/copilotkit/onboarding'`,
`agentUrl: …/onboarding-agent`).

---

## 3. Client shell

`<NovaChat/>` lives in a `'use client'` component:

```tsx
'use client'
import { NovaChat } from '@novosapien/nova-ui'

export function Chat({ token }: { token: string }) {
  return (
    <NovaChat
      runtimeUrl="/api/copilotkit"            // default
      agent="nova"                            // default; match the handler's agentName
      getAuthHeaders={async () => ({ authorization: `Bearer ${token}` })}
      config={novaConfig}                     // domain strategies — §6
      icons={novaIcons}                       // match the app's icon set — §5
      composer={renderMyComposer}             // app's own input — §7
      engine={{ history, gateOnFirstInteraction: true, dedupVisibleHistory: true,
                resetMessagesOnMount: true, initialMessage }}
    />
  )
}
```

**Props:** `runtimeUrl?`, `agent?`, `threadId?`, `getAuthHeaders?` (sync/async),
`tenantContext?` (opaque bag → `properties`), `config?` (`NovaConfig`),
`renderers?` (registry overrides; unknown tool → null), `engine?`
(`UseStreamingMessagesOptions`: history, onboarding callbacks, pagination,
first-interaction gating, `initialMessage`), `composer?` (render-prop input slot),
`icons?` (`NovaIcons`), `isLoadingHistory?`, `placeholder?`, `className?`.
The shell applies `NOVA_ROOT_CLASS` (`.nova-ui-root`) to its own root.

---

## 4. Auth / tenant flow (one path)

`getAuthHeaders()` → CopilotKit request headers → server handler mirrors
`authorization` (+ `x-entity-id`) into `properties` → the agent. If
`getAuthHeaders()` **rejects, the send is aborted** and surfaced as an error —
**never sent unauthenticated** (this is the "EC8" contract; it holds for the
custom composer too). `tenantContext` is optional (content-workforce keys tenancy
off `conversationId`).

---

## 5. CSS (Tailwind v4) — zero global leak

See `cross-cutting-rules.md` Rule 1. In the app's Tailwind entry (e.g.
`globals.css`), path **relative to that file**:

```css
@import "tailwindcss";
@source "../node_modules/@novosapien/nova-ui/dist";   /* consumer generates the classes */
@import "@novosapien/nova-ui/styles.css";             /* .nova-ui-root-scoped base ONLY */
```

`styles.css` ships only a `.nova-ui-root`-scoped base reset (in `@layer base`) →
importing it changes **zero** global utilities. Set the **RGB-channel** tokens on
`:root` to rebrand (nova-ui reuses your existing `--primary`/`--card`/… and adds
`--nova-*`):

```css
:root {
  --nova-completion: 16 185 129;             /* todo "done" color */
  --nova-badge-success-bg: 209 250 229;      /* + -text -border; and warning/info/error/neutral */
}
```

Every `--nova-*` read carries an inline `rgb(var(--token, <default>))` fallback,
so badges/completion render with **no** tokens set. (Optional explicit preset:
`@novosapien/nova-ui/preset.css` — but **don't** import it if your app already
defines the reused tokens; it would override them.)

### Icons (exact-match parity)

Chrome icons default to lucide. To match the app (e.g. hugeicons), pass `icons`:

```tsx
import type { NovaIcons } from '@novosapien/nova-ui'
const novaIcons: NovaIcons = {
  send: <MySend/>, spinner: <MySpinner className="animate-spin"/>,
  toolActive: <MyDot/>, toolComplete: <MyCheck/>, toolExpand: <MyChevron/>,
  toolSkillLoad: <MySparkles/>,
}
```
(Per-tool *pill* icons come from `config.toolDisplay`, §6 — not these chrome icons.)

---

## 6. Domain strategies (`config: NovaConfig`)

nova-ui renderers are **domain-free**; app behavior is injected via three
strategies, reaching every renderer through React context (no prop-drilling):

```ts
import type { NovaConfig, NovaBadgeVariant, NovaToolDisplay } from '@novosapien/nova-ui'
```

- **`statusColors: Record<string, NovaBadgeVariant>`** — opaque status (lowercase)
  → `'success'|'warning'|'info'|'error'|'neutral'`. Unmapped → neutral (no error).
  Drives the badge in `RenderCard` (`metadata.status`) + `RenderList` items.
- **`renderCardMetadata(type, metadata) => ReactNode`** — per-card-`type` layout.
  Return the metadata block; **return `null`** to defer to the generic key/value
  fallback. Use the exported `StatusBadge` (it reads `statusColors` from context).
- **`toolDisplay(toolName, state:'active'|'complete') => {label, icon?} | undefined`**
  — tool-call pill label + icon, per lifecycle state. Return `undefined` to fall
  back to the generic `snake_case → Title` default. (The `read_file` skill-load
  special case keeps built-in behavior — it has no tool args to intercept.)

```tsx
const config: NovaConfig = { renderCardMetadata, statusColors, toolDisplay }
<NovaChat config={config} /* …transport… */ />
```

Worked content-workforce example (the campaign/post layout + the 13-entry
TOOL_DISPLAY map removed from the package to keep it domain-free) lives in the
package's `skills/authoring/add-domain-component/SKILL.md`.

---

## 7. Custom input (composer slot)

Re-attach the app's own input (slash-commands, voice, expand-modal) **while
keeping the auth/abort send path**:

```tsx
<NovaChat
  getAuthHeaders={getAuthHeaders}
  composer={({ onSend, disabled, isSending, placeholder }) => (
    <MyComposer onSubmit={onSend} disabled={disabled} sending={isSending} placeholder={placeholder} />
  )}
/>
```

`onSend` is the **same** send the built-in uses → runs `getAuthHeaders` →
abort-on-reject (EC8 holds). Default (no `composer`) = built-in `ChatInput`.

---

## 8. Custom renderer (new tool)

A new agent tool (e.g. `render_invoice`) needs a renderer authored against the
`{ payload, loading, toolCallId }` contract, registered via `renderers` (merged
over defaults; unregistered tool renders nothing, no throw):

```tsx
import { NovaChat, type RendererProps } from '@novosapien/nova-ui'

function RenderInvoice({ payload, loading }: RendererProps<{ number: string; total: number }>) {
  if (loading) return <div className="rounded-lg border border-border bg-card p-4 animate-pulse h-16" />
  return <div className="rounded-lg border border-border bg-card p-4 text-sm">…{payload.number}…</div>
}
<NovaChat renderers={{ render_invoice: RenderInvoice }} config={config} />
```

Build on nova token classes (`bg-card`, `text-muted-foreground`, `border-border`,
`bg-nova-completion`, …) so it rebrands with the consumer's tokens. For the 5
built-in tools, import contract types (`RenderCardPayload`, …, `RenderPayload`,
pinned to `RENDER_SCHEMA_VERSION = '1.1.0'`).

---

## Public API quick map

- **Client:** `NovaChat`; the 5 renderers + `StatusBadge`;
  `registry`/`resolveRegistry`/`getRenderer`; `useStreamingMessages` + engine types.
- **Server (`/server`):** `createNovaRuntimeHandler`.
- **Types/contract:** `NovaConfig`, `NovaIcons`, `NovaToolDisplay`,
  `NovaBadgeVariant`, `RendererProps<T>`, the `Render*Payload` set + `RenderPayload`,
  `RENDER_SCHEMA_VERSION`, `NOVA_ROOT_CLASS`, the token contract.
- **CSS:** `@novosapien/nova-ui/styles.css` (scoped base), optional
  `@novosapien/nova-ui/preset.css`.

In-package depth (when the repo is available):
`nova-ui/skills/authoring/{consume-nova-ui,add-domain-component}/SKILL.md`.
