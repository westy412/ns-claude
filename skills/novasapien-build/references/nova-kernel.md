# Build on nova-kernel

`nova-kernel` is the private **Python backend kernel** for Nova-style agents: the
agent factory, the channel adapters (web/whatsapp/…), pluggable persistence, the
AG-UI event stream, MCP wiring, and the **render contract** that
`@novosapien/nova-ui` consumes. It is the **symmetric backend half** of nova-ui —
the agent emits render payloads, nova-ui's 5 renderers draw them. Most new Nova
agent services are **minted from it** (copier), not hand-wired.

- **Package:** `nova-kernel` (import `nova_kernel`) · **version `0.2.0`** (tag `v0.2.0`) · `RENDER_SCHEMA_VERSION = "1.1.0"`.
- **Repo:** `github.com/Novosapien/nova-kernel` (private, proprietary — never PyPI). Lives at parent level `/Users/.../novosapien/nova-kernel/`.
- **Python:** `>=3.12`. Built with hatchling + UV.

> ⚠️ **Auth is DIFFERENT from the npm packages.** `@novosapien/ui` and
> `@novosapien/nova-ui` use GitHub Packages (`read:packages` / `NODE_AUTH_TOKEN`).
> nova-kernel uses a **private git dep over SSH** (deploy keys / BuildKit `--ssh`).
> Don't carry the npm auth story over — see Install below.

---

## 1. Install & auth (private git dep over SSH)

Pin a **tag** — never `main`, never `:latest`. Extras select provider + channels.

```bash
uv add "nova-kernel[google,web] @ git+ssh://git@github.com/Novosapien/nova-kernel@v0.2.0"
```

Importing the package root pulls **no** channel/web deps (fastapi, ag-ui, deepgram) —
those live behind extras (enforced by an import-isolation test).

**CI auth (default = per-agent read-only Deploy Key, least privilege):** generate an
`ed25519` keypair → add the `.pub` as a read-only Deploy Key on `nova-kernel` → add
the private key as the agent repo secret `NOVA_KERNEL_DEPLOY_KEY` → load via
`webfactory/ssh-agent@v0.9.0` before `uv sync --frozen`. (Alternatives: GitHub App
token, fine-grained read-only `contents` PAT.)

**Docker (BuildKit SSH forwarding):**
```dockerfile
RUN apt-get install -y git openssh-client && mkdir -p ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
RUN --mount=type=ssh uv sync --frozen --no-install-project --no-dev
```
CI runs `docker build --ssh default`; locally the dev's ssh-agent is forwarded.

> **Commit `uv.lock` before the first deploy.** The Docker build is `uv sync --frozen`
> and fails without a lock. A lock pinning the kernel as an editable `../../nova-kernel`
> path is **not CI-installable** — `[tool.uv.sources]` must point at the git tag.

---

## 2. Mint a new agent (the recommended path)

Don't hand-build — scaffold. Two layers, both versioned **inside** the kernel repo
so the guides track the real API:

- **`mint-nova-agent` skill** (`nova-kernel/skills/authoring/mint-nova-agent/SKILL.md`) — the human entry point: asks ~12 questions in plain language, confirms, runs copier non-interactively. Routes to 5 guides (`configure-channels`, `wire-mcp`, `write-persona`, `add-domain-component`, `deploy`), each citing real `nova_kernel` symbols.
- **Copier template** directly: `uvx copier copy git+ssh://git@github.com/Novosapien/nova-kernel <dest>` (and `uvx copier update` to re-apply kernel changes).

**Inputs:** `agent_name`, `base_service_name`, `package_name`, `kernel_git_url`,
`kernel_version` (semver `v…`, **pin a real published tag** — the default `v0.1.0`
is stale vs `v0.2.0`), `llm_provider` (google|openai), `channels` (web/whatsapp),
`include_onboarding`, `persistence_backend` (`supabase-postgres`), `tenant_key`
(default `tenant_id`), `id_type` (`str` default / `uuid`), `mcp_server_name`, GCP
deploy vars, resources.

**Generates:** `src/<pkg>/` skeleton (`main.py`, `config.py` extending
`KernelSettings`, `agents/factory.py`, `channels/wiring.py`), `pyproject.toml`
(kernel pinned), `Dockerfile` (BuildKit SSH), CI/deploy workflows, Terraform tfvars
triplet, `prompts/` personas, `skills/`, `.env.example`, `CLAUDE.md`.

**Ownership (copier `update`):** user-owned files (`prompts/*`, `skills/README.md`,
`.env.example`) are `_skip_if_exists` (never overwritten); template-owned files
(infra, Dockerfile, skeleton, wiring) re-apply, and a locally-edited one that also
changed upstream gets **3-way-merge conflict markers**, never a silent overwrite.

---

## 3. Public API (`nova_kernel.__all__`) — for wiring / understanding

**Agent factory** — `create_agent(*, system_prompt, tools, model=None, checkpointer, channels=None, persistence=None, skills_dir=None, prompts_dir=None, settings=None, name=None) -> CompiledStateGraph` (wraps `deepagents.create_deep_agent`). Construction shape is driven by `channels` + `skills_dir`, not separate functions:
- **web** — `channels=["web"]` → app tools **+ `RENDER_TOOLS`** + skills backend.
- **whatsapp** — `channels=["whatsapp"]` → app tools, **no** render tools.
- **onboarding** — no channels/skills_dir → bare agent.
- `model=None` requires `settings` (resolves via `build_model`). Always installs `ToolErrorHandlerMiddleware`.

**Render tools** (`render/`) — `render_card`, `render_table`, `render_chart`
(`chart_type: bar|pie|line`), `render_list`, `render_todo` (live checklist; re-emit
same `id` to replace in place); `RENDER_TOOLS` bundles them. Each validates a
Pydantic payload then returns the legacy wire dict. Schema: `export_render_schema()`,
`RENDER_SCHEMA_VERSION`, the `Render*Payload` models + `RenderPayload` union. See §4.

**Channel adapters** (`channels/`) — `ChannelAdapter(ABC)` (ctor `*, agent, persistence, tenant_key`; class attr `channel`). Six methods: `resolve_identity`, `derive_thread_id`, `build_context` (concrete), `handle_turn`, persistence hooks (`ensure_conversation`/`persist_user_turn`/`persist_assistant_turn`, concrete), `push` (the `/notify` shape). Ships `WebAdapter` (SSE async-gen, no fastapi dep) + `WhatsAppAdapter` (app supplies `send_text`/`transcribe`/media hooks — deepgram is NOT a kernel dep). Generic dataclasses keep signatures stable: `Identity`, `InboundContext`, `PushRequest`.
**Implement a new channel (e.g. Slack):** subclass `ChannelAdapter`, supply app hooks, set `channel="slack"`, reuse `invoke_agent_with_retry`/`extract_final_text`/`split_response`, maintain an app-side `(channel, thread_ts) → kernel-UUID` map for `derive_thread_id`. **Zero edits to any base signature** (paper design: `docs/slack-adapter-paper-design.md`, gate PASS).

**AG-UI streaming** (`channels/agui.py`) — `stream_agui_events(agent, *, messages, thread_id, run_id, result) -> AsyncIterator[str]`: emits `RUN_STARTED → (TEXT_MESSAGE_* | TOOL_CALL_*)* → RUN_FINISHED|RUN_ERROR`, closing orphaned opens on both paths so the frontend never hangs. `TurnResult` accumulates for post-stream persistence. Non-streaming reuse: `invoke_agent_with_retry` (empty-response retry via `RemoveMessage`), `split_response`, `extract_final_text`.

**Persistence** (`persistence/`) — `PersistenceBackend(ABC)` (async; `create_conversation`/`get_conversation`/`list_conversations`/`update`/`delete`, `create_message`/`get_messages`/`get_message_count`/`get_messages_before`; abstract `tenant_key`). `user_id` + `tenant_value` are generic `IdValue = str | UUID` (verbatim `org_7`, Slack `Uxxxx`, or UUID); conversation/message ids are **kernel-minted UUIDs**; a `None` tenant_value → null column. **Register a 2nd backend** = add a key to `PERSISTENCE_BACKENDS` (the only kernel touchpoint), zero interface edits; construct via `get_persistence_backend(name, *, async_database_url, tenant_key="tenant_id", id_type="str")`. Ships `SupabasePostgresBackend`; `id_type="str"` (default, any id verbatim) or `"uuid"` (only to match a pre-existing UUID schema).

**Tenancy / auth / config** — `build_context_line(*, tenant_key, tenant_value, user_id=None)` (emits `USER_ID=…` first, then `TENANT_KEY=…`, uppercased; absent values omitted); `validate_supabase_jwt(...)` + `AuthError` (`[web]`, fixed alg allow-list); `build_model(settings)`; `build_mcp_config(*, server_name, base_url, sse_path="/mcp/sse", api_key=None, …)` (one server → merge N); `KernelSettings(BaseSettings)` — generic infra only, **apps subclass and add channel/domain fields**.

---

## 4. Render contract ↔ nova-ui (keep in lockstep)

Canonical doc: `nova-kernel/docs/render-contract.md`.

- **`RENDER_SCHEMA_VERSION = "1.1.0"`** — bump on any field add/remove/rename or discriminator change so the frontend can pin. `1.1.0` added the `todo` variant additively (now **5** payloads).
- **`kind` discriminator** (`card|table|chart|list|todo`) exists only to make the union discriminable in the schema. **`_wire()` strips `kind` before sending** — it's never on the wire; the frontend keys off the **tool name**. (Exception: `render_todo`'s `id` IS kept, so the frontend dedups in place.)
- **nova-ui pins the same version** and mirrors `export_render_schema()` as a generated TS discriminated union — it does **not** hand-redefine shapes. See `references/consume-nova-ui.md` → "Custom renderer" + the `Render*Payload` types.
- **Backend-author rules:** (1) any payload/discriminator change ⇒ bump `RENDER_SCHEMA_VERSION` + regenerate the TS union; (2) keep value fields opaque free strings (`type`, list/todo `status`) — no enums, no domain vocab (only `chart_type` is constrained); (3) the JSON Schema is the source of truth, the markdown is the companion.

---

## 5. Gotchas

1. **Auth ≠ the npm packages** — SSH git dep + deploy key + `docker build --ssh`, not `read:packages`/`NODE_AUTH_TOKEN` (§1).
2. **Commit `uv.lock` before deploy**; never an editable `../../nova-kernel` path in the lock (Docker `--frozen` fails / not CI-installable).
3. **`id_type`: default `str`.** Pick `uuid` only to match a pre-existing UUID schema — the wrong choice forces a destructive migration. (content-workforce used `id_type="uuid"`, `tenant_key="entity_id"`.)
4. **Domain-freeness (EC8):** no app vocabulary in `src/` field names/defaults/docstrings — CI greps it (`scripts/check_no_domain_vocab.sh src`). Only the RFC-7519 JWT claim literals are allow-listed, in `auth.py` only.
5. **Pin a real `kernel_version` tag** when minting — the copier default `v0.1.0` lags the real `v0.2.0`.
6. **`render_todo` is not vestigial** — it's the contract's portable primitive (stable `id`, re-emit collapses in place). Production content-workforce keys off deepagents-native `write_todos` (full-replace, synthetic id); both are intentional. Don't "clean up" `render_todo`.
7. **Extract from real source, not docs** — `ns-content-workforce-nova-agent/CLAUDE.md` was stale (described non-existent modules); the kernel's own authoring guides are versioned with the code to stay accurate.

---

## 6. Mount the web conversations + HITL-restore routers (`[web]`)

The `[web]` extra ships two mountable routers + an auth dependency, so a web agent
gets the whole chat-surface backend — list / paginated history / delete / rename
**and** the R14 reopen-restore read — with **zero hand-authored endpoint code**.
A minted web agent has the conversations router mounted by `main.py.jinja` by
default; mount both explicitly like this (`get_*` are lazy lambdas resolved at
request time off `app.state`, so module-load mounting is safe):

```python
from nova_kernel.web import (
    create_conversations_router, create_supabase_auth_dependency,
    create_pending_interrupt_router,
)
auth = create_supabase_auth_dependency(supabase_url=..., jwt_secret=...)  # audience="authenticated"

app.include_router(create_conversations_router(
    get_backend=lambda: app.state.persistence,   # REQUIRED, zero-arg
    auth_dependency=auth, channel="web", status="active",   # channel/status defaults shown
))
# GET /conversations · GET /conversations/{id}/messages?cursor=&limit= (cursor pagination)
# · DELETE /conversations/{id} (204) · PATCH /conversations/{id} ({status,title})
# IDOR → 404; messages on a nonexistent id → 200-empty.

app.include_router(create_pending_interrupt_router(
    get_agent=lambda: app.state.agents["web"],   # the graph (needs aget_state)
    derive_thread_id=_derive_thread_id,          # (conversation_id, user_id) -> thread_id — USER-SCOPED
    auth_dependency=auth, get_backend=lambda: app.state.persistence,   # get_backend REQUIRED (IDOR)
))
# GET /conversations/{id}/pending-interrupt -> {pending, pending_actions}
# both keys always present; pending_actions=[] when idle; a multi-action gate carries all N.
```

Conveniences with **one `[web]` import home** (canonical home is the FastAPI-free
core): `get_messages_paginated` (alias `paginate_messages`),
`generate_title_from_message`, `get_pending_interrupt`, `build_render_approval_payloads`.

### Gotchas
1. **`[web]` holds FastAPI — core stays FastAPI-free (EC7).** These factories live
   in `nova_kernel.web`, which `nova_kernel/__init__` deliberately does **not**
   import, so `import nova_kernel` with no `[web]` extra never pulls FastAPI in.
   **Never import `create_*_router` from a core path.** The helpers above also
   re-export from core (`from nova_kernel import paginate_messages, ...`) for
   FastAPI-free use in the agent stream.
2. **`get_backend` is REQUIRED on BOTH routers (IDOR).** The pending-interrupt
   route enforces the same ownership oracle as the conversations router
   (foreign-owned → 404) **before** consulting `derive_thread_id`, so the IDOR
   guard never depends on the app's derive being user-scoped. An optional backend
   invited apps to leak another user's pending gate by id.
3. **`derive_thread_id` maps conversation-id → checkpoint thread-id; user-scoped +
   idempotent.** Where the checkpoint thread id **is** the conversation row id
   (`conversation_id = UUID(thread_id)`), this map is the **identity**
   (`return str(conversation_id)`) — re-deriving via `uuid5` here would invent a
   thread with no checkpoint. The idempotence lives in the agent's *turn* derive
   (owned id → verbatim; else `uuid5`); see `consume-nova-ui-chat.md` §1 gotcha (b).
4. **Multi-action gates.** One interrupt can gate N tool calls; `pending_actions`
   carries all N in decision order, `pending` is the first. The app rebuilds the
   full N-decision resume from `pending_actions` (don't use `pending` alone).

---

## Status / pointers

Spec `ns-content-workforce/specs/2026-06-20-nova-kernel/` (built + reviewed PASS;
live typed-testing 23/23 PASS — `feedback/testing-001.md`; published `v0.2.0`; the
`nova-agent` service re-pointed onto it). Render-contract doc:
`nova-kernel/docs/render-contract.md`. Authoring: `nova-kernel/skills/authoring/`.
