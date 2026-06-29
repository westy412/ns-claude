# Chat surface: conversations, history, slash, gen-UI replay

The packaged chat-surface recipes: conversation list + paginated history,
slash commands, and the render-tool→renderer registry incl. R15 persistence
replay + R14 HITL-gate restore. Track B upstreamed these into the packages so a
new Nova app needs only nova-ui + nova-kernel (no per-app re-derivation). These
are **as-built** from the outbound Nova surface (`ns-cold-outreach-app` @ `8e3ee4f`,
nova-ui @ `81aeff3`); the backend half (mounting the routers) is `nova-kernel.md` §6.

> **The boundary that governs all of this:** nova-ui takes **injected fetchers +
> callbacks** — there is **no** React Query, auth, or routing *inside* the package.
> Transport, auth, the DB-row map, and routing all live **app-side**. Cross that
> line and you fork the package.

---

## 1. History + conversation list (`useNovaHistory` + `NovaConversationList`)

**The auth-forwarding proxy** (`app/api/nova/[[...path]]/route.ts`) — one catch-all
route fronts the agent's whole kernel conversations surface. The browser calls it
with the Supabase session cookie (`credentials:'include'`); the route resolves the
bearer **server-side** and forwards it (+ the active-org header) to the agent, and
**forwards the upstream status verbatim** (the agent owns IDOR→404 + nonexistent→200-empty).

```ts
const r = await fetch(`${NOVA_AGENT_URL}${path}${search}`, {
  method, headers: { Authorization: getAuthHeader(token), ... }, body,
  redirect: 'manual',   // pass 3xx through verbatim — no SSRF-adjacent off-host follow
})
```

**The fetcher (app-side).** `useNovaHistory` is headless; you inject a fetcher
`(conversationId, cursor?) => Promise<{ messages: NovaHistoryMessage[], has_more, next_cursor }>`.
The DB-row → `NovaHistoryMessage` map (`rowToNovaHistoryMessage`) lives **app-side**
and carries `tool_calls` + `content_blocks` for R15 replay (§3).

**The hook + shell wiring.** `useNovaHistory(fetcher, conversationId)` returns the
exact engine bundle; spread it into `<NovaChat>`:

```tsx
const fetcher = useMemo(() => createNovaHistoryFetcher({ onError: toast }), [])
const { history, isLoadingHistory, hasNextPage, isFetchingNextPage, fetchNextPage } =
  useNovaHistory(fetcher, conversationId)   // conversationId=null → empty, no fetch, no skeleton

<NovaChat
  key={conversationId ?? `new-${nonce}`}              // remount on switch
  {...(conversationId ? { threadId: conversationId } : {})}  // round-trip the id — gotcha (b)
  getAuthHeaders={getAuthHeaders}
  isLoadingHistory={isLoadingHistory}
  engine={{ history, hasNextPage, isFetchingNextPage, fetchNextPage,
            gateOnFirstInteraction: true, dedupVisibleHistory: true, resetMessagesOnMount: true,
            onConversationCreated: (id) => window.history.replaceState(null, '', `/nova/${id}`) }}
/>
```

`onConversationCreated` rewrites the URL on the FIRST send of a new chat with
`history.replaceState` — the URL becomes `/nova/{id}` **without remounting** (the
live stream survives; a `router.push` would remount and drop it).

**The list.** `NovaConversationList` is **presentational** (props + callbacks only;
it groups internally via `groupConversationsByDate`). The app owns the data
(`useNovaConversations`) and routing: `onSelect`→`router.push('/nova/{id}')`,
`onArchive`/`onDelete`→PATCH/DELETE + redirect to `/nova` if the open one was hit.

### Gotchas
- **(a) The injected-fetcher boundary.** nova-ui has no fetch/auth/router. The
  proxy, the row map, and any React Query all live app-side — keep them there.
- **(b) thread-id continuity.** The conversation row id **is** the checkpoint
  thread id. Round-trip `conversation.id` back as `threadId` on reopen
  (`<NovaChat threadId={conversationId}>`). The agent's turn-derive **must be
  idempotent on owned conversation ids** (owned id → verbatim; else `uuid5`) or
  reopen/resume **forks a fresh empty checkpoint** (you reload but the model has no
  memory of the thread). See `nova-kernel.md` §6 gotcha 3 + the agent derive.
- **(c) No error channel.** A fetcher rejection silently resets `useNovaHistory`
  to **empty** history → a transient failure reads as a blank conversation. Wrap
  the fetcher: toast on reject, then re-throw (the as-built `createNovaHistoryFetcher`
  takes an `onError`).

---

## 2. Slash commands (`commands` prop / `SlashCommandInput`)

`NovaSlashCommand = { command, description, icon?, run? }`. Leading-`/` trigger
only (a `/` typed mid-message never opens the menu).

- **Turnkey:** `<NovaChat commands={[...]} />` (built-in composer). Or drop
  `<SlashCommandInput {...composerApi} commands={...} />` into the `composer` slot
  for a custom input — same slash behavior, your own textarea.
- **No `run`** → the default action sends `command` via `api.onSend` (the **EC8
  auth/abort send path** — the agent drives it, e.g. `/source`, `/lists`).
- **`run(api)`** → runs **client-side**, never hits the agent (e.g. `/new` starts a
  fresh conversation, `/help` shows a local summary).

```tsx
const commands: NovaSlashCommand[] = [
  { command: '/source', description: 'Source new leads', icon: <Search/> },         // → onSend
  { command: '/new', description: 'New conversation', icon: <Plus/>, run: () => startNewChat() },
]
```

---

## 3. Generative UI: render-tool → `renderers` registry + R15 replay

**Generic flow.** The 5 kernel render tools (`render_card/table/chart/list/todo`)
draw through nova-ui's built-in registry end-to-end — **no app code**.

**Custom DOMAIN renderer.** The agent emits a `render_<kind>` payload (the tool
**name** is the registry key); register a matching renderer in `renderers`:

```tsx
const renderers: RendererRegistry = { render_lead_list: RenderLeadList, ... }
function RenderLeadList({ payload, loading }: RendererProps<RenderLeadListPayload>) { ... }
<NovaChat renderers={renderers} />   // merged over defaults; unknown tool name → ignored (no crash)
```

Build it on app primitives + nova tokens so it auto-brands. `RendererProps` is
`{ payload, loading, toolCallId }` — **nothing else** (see the bridge gotcha).

**The app-callback bridge gotcha.** Renderers receive only `{payload, loading,
toolCallId}` — the registry can't pass app callbacks as props. To cross an app
action (e.g. "open a panel") into a renderer, wrap `<NovaChat>` in an app **Context**
and read it inside the renderer — same shape as nova-ui's own `NovaRespond`:

```tsx
<LeadListPanelProvider value={{ openLeadList }}>
  <NovaChat renderers={renderers} ... />
</LeadListPanelProvider>
// inside RenderLeadList: const { openLeadList } = useLeadListPanel()  // no-op default outside provider
```

**R15 persistence/replay.** Assistant turns persist `tool_calls=[{name,arguments,result}]`
+ `content_blocks=[{type:'text',text} | {type:'tool_call',tool_call_index}]`. The
app maps both JSONB blocks verbatim into `NovaHistoryMessage`; nova-ui's engine does
the **positional join** `content_blocks[i].tool_call_index → tool_calls[index]` and
renders by `name`, so cards replay on reload (not just text).

**HITL-gate gotcha (R14 × R15).** A persisted `render_approval` gate is **transient
checkpoint state, not durable content**:
- **Strip the persisted gate from EVERY history page** — else a gate on a
  scrolled-up older page re-renders a **second clickable card** (and clicking it
  resumes a resolved interrupt).
- **Re-fetch the LIVE gate** from `GET /conversations/{id}/pending-interrupt` and
  append **exactly one** actionable card — **only on the newest page** (`cursor===undefined`).
  Resolved → `pending:null` → no stale buttons (the decision is still visible via the
  persisted user line). Multi-action gate → `pending_actions` carries all N in
  decision order; rebuild the full N-decision resume from it (not from `pending` alone).

---

## Pointers
- **Backend half** (mount the routers, the IDOR + FastAPI-free gotchas): `nova-kernel.md` §6.
- **Base nova-ui consume** (install, server route, CSS-no-leak, domain strategies, the
  composer slot, the generic custom-renderer contract, the public API): `consume-nova-ui.md`.
- **As-built source:** app `src/components/chat/*` + `src/lib/api/nova-conversations.ts`
  + `src/app/(authenticated)/nova/*` @ `8e3ee4f`; nova-ui `src/{engine,shell}` @ `81aeff3`.
