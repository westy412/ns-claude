# UK Company Structures for Joint Ventures

> **When to read:** When discussing entity types, Companies House formation, or JV Co structural setup.

---

## Entity Selection: Ltd vs LLP

### Private Limited Company (Ltd) — Recommended

The dominant structure for UK joint ventures (95%+ of registered corporate bodies). For a 50/50 JV:

**Pros:**
- Separate legal personality and limited liability (Companies Act 2006, s.1)
- Profit retention at corporation tax rates (19–25%) rather than immediate personal tax exposure
- Clear governance via Articles of Association and shareholders' agreement
- Inter-company dividends typically exempt from further CT (substantial shareholding exemption)
- Flexible share classes (A/B ordinary) for voting rights and economic entitlement
- Widely understood by banks, investors, and counterparties

**Cons:**
- Statutory accounts filed publicly at Companies House (small company exemptions apply)
- More formal governance requirements than contractual JV
- At 50/50, deadlock risk without express contractual resolution

### Limited Liability Partnership (LLP) — Alternative

Tax-transparent entity governed by Limited Liability Partnerships Act 2000. Profits flow through to members.

**Pros:** Tax transparency, flexible profit-sharing, fewer governance formalities
**Cons:** No ability to retain earnings at low CT rate, less familiar to banks/investors, capital structure makes drag/tag-along complex

**Verdict:** For a JV Co that recharges costs to operating companies and accumulates surplus, **Ltd is strongly preferred**. LLP suits professional service partnerships with immediate profit distribution.

---

## JV Co Structure Diagram

```
     [Founder A Ltd]    [Founder B Ltd]
          50%                50%
            \              /
             [JV Co Ltd]
            /              \
   [Product Co Ltd]    [Services Co Ltd]
```

JV Co is the intermediate holding company. Each founder holds their 50% through their own existing Ltd (additional liability protection and personal tax planning flexibility).

**Group relief note:** For CT group relief (loss surrendering), JV Co must own at least 75% of each subsidiary (CTA 2010 s.97, s.151). The JV Co can form a group with 100%-owned subsidiaries regardless of the 50/50 split above.

---

## Companies House Formation

### Registration Process

Form IN01 submitted digitally or via formation agent. Required documents:

| Document | Notes |
|---|---|
| Form IN01 | Company name, registered office, director details, shareholder details, share capital, SIC codes |
| Memorandum of Association | Subscribers' statement of intent (CA2006 s.8) |
| Articles of Association | Bespoke for JV — Model Articles are inadequate |

Both corporate shareholders subscribe to the Memorandum.

### Current Fees (from 1 February 2026)

| Method | Fee |
|---|---|
| Digital incorporation (standard) | £100 |
| Same-day digital incorporation | £156 |
| Paper incorporation | £124 |
| Annual confirmation statement (digital) | £50 |
| Annual confirmation statement (paper) | £110 |

**Source:** gov.uk/government/publications/companies-house-fees

### SIC Codes

| SIC Code | Description | Applicability |
|---|---|---|
| **64202** | Activities of holding companies (non-financial) | Primary — correct for JV Co |
| **70100** | Activities of head offices | Secondary — if JV Co provides management services |

Up to four codes may be registered. Changed any time via confirmation statement.

---

## PSC (Persons with Significant Control) Register

Under CA2006 Part 21A, both 50% corporate shareholders must register as PSCs:

- Both exceed the 25% threshold for shares and voting rights
- Registered as **Relevant Legal Entities (RLEs)** (not individual PSCs) since they are UK companies
- Nature of control: "Owns more than 25% of shares" and "Holds more than 25% of voting rights"

### Identity Verification (ECCTA 2023)

From 18 November 2025, Companies House requires mandatory identity verification for all directors and PSCs under the Economic Crime and Corporate Transparency Act 2023. Must be completed before or at incorporation. 12-month transition for existing companies (to November 2026).

---

## Bespoke Articles of Association

Model Articles (CA2006 Schedule 1) are inadequate for a JV. Bespoke Articles must include:

- **Share classes** — one per JV party (A Ordinary, B Ordinary)
- **Reserved matters** — unanimous consent for major decisions
- **Deadlock resolution** — escalation, Russian roulette, Texas shoot-out
- **Director appointment rights** — each party appoints equal numbers
- **Quorum** — requires at least one director from each party
- **No casting vote** for chair (prevents de facto control)
- **Pre-emption rights** on share transfers
- **Drag-along / tag-along** provisions
- **Conflict of interest authorisation** under s.175(5)(b) for nominee directors

Articles are public. Sensitive provisions go in the private Shareholders' Agreement.

---

## Director Appointment Rules

- Minimum one natural person director (CA2006 s.155)
- Directors must be aged 16+ (CA2006 s.157)
- Corporate directors restricted under ECCTA 2023 (s.156A–156E) — direction of travel requires natural persons
- Each JV party has the **right** (not merely ability) to appoint and remove its director
- Removal by ordinary resolution (s.168) — in 50/50 JV, neither party can unilaterally remove the other's director

---

## Intercompany Agreements Required

| Agreement | Purpose |
|---|---|
| **Shareholders' Agreement** | Governs JV relationship, deadlock, reserved matters, exit |
| **Services Agreement (each OpCo → JV Co)** | Cost reimbursement for resources provided |
| **IP Licence Agreement** | If IP is used across entities |
| **Management Services Agreement** | If JV Co provides oversight to OpCos |
| **Cost Sharing Agreement** | Formal cost allocation methodology |

All should be written contracts (not board minutes), reviewed annually, and supported by transfer pricing documentation if non-SME.

---

## Key Companies Act 2006 Provisions

### Governance

| Section | Subject | JV Relevance |
|---|---|---|
| s.17 | Constitution includes Articles | Defines governance framework |
| s.21 | Amendment requires 75% special resolution | Entrench key provisions under s.22 |
| s.22 | Entrenchment of Articles | Protects deadlock and appointment provisions |
| s.33 | Articles bind as contract | Members contractually bound |
| s.171–177 | Directors' duties (including conflicts) | Nominee directors must manage conflicts |

### Shareholder Protections

| Mechanism | Description |
|---|---|
| **s.994 Unfair Prejudice** | Petition if affairs conducted unfairly. Key: *O'Neill v Phillips* [1999] |
| **s.122(1)(g) IA 1986** | Just and equitable winding up. Key: *Ebrahimi v Westbourne Galleries* [1973] |
| **s.561–577 Pre-emption** | New shares offered to existing holders pro rata |

### Dividends and Capital

| Provision | Detail |
|---|---|
| s.830 | Dividends only from distributable profits |
| s.836–840 | Relevant accounts for determining distributable profits |
| s.641–644 | Capital reduction by solvency statement |
| s.690–708 | Share buyback — must be from distributable profits |
