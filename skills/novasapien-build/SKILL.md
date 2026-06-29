---
name: novasapien-build
description: Router and consume guide for building frontends, apps, or features on the private @novosapien package ecosystem — @novosapien/nova-ui (generative chat UI), @novosapien/ui (design system: theme, primitives, app-shell), and nova-kernel (backend render contract). Use when a task involves installing, theming, wiring, or extending any of these packages so you reference their real APIs, consume patterns, and hard-won gotchas instead of rediscovering them. Loaded by discovery / general-spec-builder / general-implementation-builder for any work that touches these packages.
---

# novasapien-build

Building anything on the NovaSapien package ecosystem? Load this first. It routes
you to the right package and carries the cross-cutting rules that, when missed,
broke the whole consuming app twice during extraction (a global-CSS leak and a
Turbopack `theme.css` parse bug). Treat the **Non-negotiables** below as gates.

These are **private GitHub Packages** under the `@novosapien` org (`Novosapien` on
GitHub). One auth story covers all of them — see `cross-cutting-rules.md`.

## Which package for what

| You're building… | Use | Subpath / entry |
|------------------|-----|-----------------|
| Generative **chat UI** (Nova) — streaming messages, tool-call pills, card/table/chart/list/todo renderers; **conversation list + paginated history, slash commands, HITL-gate restore** | `@novosapien/nova-ui` | `.` (client) + `/server` (Next route handler) + `/styles.css` |
| **App chrome / brand** — theme tokens, the 34 shadcn-style primitives, 9 shared components, sidebar/page-header shell | `@novosapien/ui` | `.` (primitives) + `/theme.css` + `/app-shell` + `/tokens` |
| A **Nova agent backend** (Python) — agent factory, channel adapters (web/whatsapp/…), pluggable persistence, AG-UI stream, MCP, the render contract nova-ui consumes, + **mountable `[web]` conversations + HITL-restore routers** | `nova-kernel` | minted via copier / `git+ssh` dep — **NOT** GitHub Packages |

The two frontend packages **coexist cleanly** (disjoint CSS namespaces: `--nova-*`
+ `.nova-ui-root` vs `@novosapien/ui`'s token contract). A new internal tool
typically starts from `@novosapien/ui` for chrome and adds `@novosapien/nova-ui`
only if it needs a Nova chat surface (the chat layer is **optional per app**).

## Non-negotiables (the gates that were learned the hard way)

Apply these to **every** `@novosapien` frontend integration. Full reasoning +
failure stories in `references/cross-cutting-rules.md`.

1. **Never import a global utility stylesheet from these libraries.** The
   consumer's own Tailwind generates the package classes via
   `@source "…/node_modules/@novosapien/<pkg>/dist…"`; the package ships only
   CSS-var **tokens** + a **scoped** base. Verify by compiling the consumer CSS
   *with vs without* the package → **zero existing rules change, additions only.**
2. **Every domain-free component needs an injection point** (prop / slot /
   context / strategy). If you strip an app-specific behavior to make a component
   generic, add the surface to put it back — or the consumer regresses or forks.
3. **Parity is verifiable only by running the real consumer app under its real
   bundler (`next dev` → Turbopack).** Code review, snapshot tests, and
   `next build --webpack` all passed builds that broke the app. Gate visual /
   integration parity on `next dev`, not on a green build.
4. **Auth is per-ecosystem — don't mix them up.** The two **npm** packages
   (`@novosapien/ui`, `@novosapien/nova-ui`) share one GitHub Packages story:
   `read:packages` in `NODE_AUTH_TOKEN`, a committed `.npmrc` with
   `always-auth=true`. **`nova-kernel` is different** — a private **git dep over
   SSH** (`git+ssh://…@v<tag>`), installed with a read-only **Deploy Key** /
   BuildKit `docker build --ssh`. Settle whichever applies early; a local tarball
   / editable path works for dev but is **not** CI/deploy-installable.
5. **RGB-channel tokens can't carry alpha.** `rgb(var(--token))` can't reproduce
   `rgba(…, 0.3)`. Anything translucent (badges, active-sidebar) must ship as
   `rgba()` / slash-alpha, not a bare channel triplet.
6. **Pin one icon set and make it injectable.** `@novosapien/ui` is **hugeicons**;
   `@novosapien/nova-ui` defaults to **lucide** → inject your icons to match.
7. **Defaults must match the reference app.** For a drop-in replacement,
   "reasonable but different" defaults (e.g. a solid-fill Button when the house
   style is a card surface) are **regressions**.

## Reference files

| Topic | File | Load when |
|-------|------|-----------|
| The 7 rules with full reasoning + the CSS-leak / Turbopack failure stories, the byte-identical verify recipe, and the canonical registry-auth setup | `references/cross-cutting-rules.md` | Any integration — read before wiring CSS or CI |
| `@novosapien/nova-ui` — install, server route, client shell, CSS, auth/tenant, icons, composer slot, domain strategies, custom renderers, public API | `references/consume-nova-ui.md` | Adding / extending the Nova chat UI |
| **Chat surface (as-built)** — conversation list + `useNovaHistory` pagination + the `/api/nova` proxy, slash commands, and the render-tool→`renderers` registry incl. R15 replay + R14 HITL-gate restore (+ the injected-fetcher / thread-id-continuity / app-callback-bridge gotchas) | `references/consume-nova-ui-chat.md` | Wiring conversations / history / slash / gen-UI on a Nova app |
| `@novosapien/ui` — install, CSS order, primitives + `/app-shell` slots, the 60-token contract, house-style Button / hugeicons, the Turbopack `theme.css` bug | `references/consume-novasapien-ui.md` | Using the design system / brand chrome |
| `nova-kernel` — Python agent kernel: SSH-git install, mint-via-copier, the factory + channel adapters + persistence + AG-UI stream + render contract (symmetric with nova-ui), **+ §6 mounting the `[web]` conversations + HITL-restore routers** | `references/nova-kernel.md` | Building or minting a Nova agent backend, or mounting its web chat-surface routers |

## Source of truth

The living cross-session record (versions, APIs, lessons) is
`ns-content-workforce/specs/novasapien-build-skill/coordination.md`, fed by each
package's spec and in-package `skills/authoring/` guides. If this skill and that
doc disagree, the coordination doc is newer — reconcile here.
