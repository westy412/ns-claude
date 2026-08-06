# Phase 5 — Client Handoff

> **When to read:** Last phase, after the loop is proven. Output: the connector
> URL, the companion skill ZIP, and the message to stakeholders.

---

## 1. Assemble the connector URL

Two halves, joined by hand:

```bash
# base URL
gcloud run services describe <service_name> --project=coral-smoke-430718-p1 \
  --region=us-east1 --format='value(status.url)'
# secret
gcloud secrets versions access latest --secret=<service_name>-access-secrets \
  --project=coral-smoke-430718-p1
```

Connector URL = `<base-url>/v/<secret>/mcp`.

**The URL is the entire access control.** No IAM, no per-person revocation.
Treat it as a credential: send it person-to-person, never post it in a shared
channel, never commit it. Rotating the secret invalidates EVERY installed
connector at once — there is no partial rotation with a shared secret. Say this
at handoff, once, plainly.

## 2. Package the companion skill

The server repo ships a client-facing skill at `skill/` (`SKILL.md` +
`references/vault-conventions.md`, `references/worked-example.md`). It was
substituted in Phase 1 — verify the client name is theirs (an unsubstituted
skill tells one client about another client's vault), then zip it:

```bash
cd <server-repo> && zip -r <client_slug>-vault-skill.zip skill/
```

## 3. Distribution is per person — Projects cannot carry it

A claude.ai Project can hold neither a connector nor a skill; both are
account-level. Each stakeholder does two things themselves:

1. **Connector:** claude.ai → Settings → Connectors → Add custom connector →
   paste the URL. Authless custom connectors are accepted (proven live
   2026-08-05).
2. **Skill:** Settings → Capabilities/Skills → upload the ZIP.

Send `templates/client-handoff-message.md` (filled in) with the URL and ZIP.

## 4. Expectations to set in the message

- **What it serves:** the vault's served scope with one-line descriptions on
  every document; five tools (`glob`, `grep`, `read`, `links`, `shell`). The
  served set is deliberately less than the whole vault — the skill instructs
  the agent not to present the difference as concealment.
- **Freshness:** a vault push is serving in ~5 minutes; the server flags itself
  stale after 48h without a rebuild.
- **First response may be slow:** min-instances is 0; a cold start takes a few
  seconds after ~15 idle minutes.
- **Try first:** "Using the vault tools, give me an overview of <a component>"
  — the agent should triage on descriptions and read only a handful of files.

## 5. Record

Log the setup in the client's ops notes: repo names, service name, secret id
(NOT the value), who received the URL, the PAT's name and where it lives.
