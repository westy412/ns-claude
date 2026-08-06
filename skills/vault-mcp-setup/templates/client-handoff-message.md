# Template: stakeholder handoff message

> Fill the placeholders, attach the skill ZIP, and send PER PERSON — the URL is
> a credential and the setup is account-level, so a shared channel is the wrong
> place for it.

---

Subject: Your <Display Name> vault assistant — 2-minute setup

Hi <name>,

You now have direct access to the <Display Name> knowledge vault from Claude.
Two one-time steps, about two minutes:

**1. Add the connector**
In claude.ai go to Settings → Connectors → Add custom connector, and paste:

    <connector-url>

Please treat that link like a password — it is your access. Don't forward it
or post it in shared channels; if it leaks, tell us and we'll rotate it.

**2. Add the skill**
Upload the attached `<client_slug>-vault-skill.zip` under Settings → Skills.
It teaches Claude how the vault is organised so answers come back faster and
better-sourced.

**Then try it** — start a new chat and ask something like:

    Using the <client_slug> vault tools, give me an overview of <example topic>.

Good to know:
- The vault updates flow through within ~5 minutes of our team publishing.
- The first question after a quiet period can take a few extra seconds while
  the service wakes up.
- Claude sees the client-shared portion of the vault, with a one-line
  description on every document so it can find things without reading
  everything.

Any issues, reply here and we'll sort it.

<sender>
