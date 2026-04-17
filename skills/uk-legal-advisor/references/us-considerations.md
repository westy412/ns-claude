# US Considerations for Future Expansion

> **When to read:** When cross-border or US expansion is mentioned. This is an overview for planning — specialist US legal and tax advice is required before action.

---

## US Entity Types for a JV

### Quick Comparison

| Feature | LLC | C-Corp | S-Corp |
|---|---|---|---|
| Foreign owners allowed | Yes | Yes | **No** — US persons only |
| Default tax treatment | Pass-through (partnership) | Double taxation (21% federal) | Pass-through |
| Flexibility | Very high | Moderate | Restricted |
| UK parent compatibility | **Complex** (see tax trap below) | Clean and unambiguous | Not applicable |
| Investor familiarity | Good for private deals | Preferred by VCs | Limited |

**S-Corp is immediately disqualified** for any structure with UK founders or entities. Non-resident aliens and foreign entities cannot hold S-Corp shares.

**Recommendation: Delaware C-Corp** is the cleanest structure for a UK parent holding a US subsidiary. Both jurisdictions understand it, tax treatment is unambiguous.

### Operating Agreement vs Shareholders' Agreement

- **Operating Agreement** governs an LLC — member-managed vs manager-managed, capital contributions, profit allocation, voting, transfer restrictions, exit
- **Shareholders' Agreement** governs a corporation — voting, dividends, share transfers, tag/drag-along, deadlock, buy-sell

Both should include reserved matters, deadlock resolution, and exit provisions. Without a written agreement, state default rules apply.

### Delaware vs Other States

**Delaware is the default** for most JV incorporations:
- Most developed corporate statute and case law
- No state income tax on out-of-state profits
- Strong director/officer protections and business judgment rule
- Annual LLC franchise tax: flat $300; Corp minimum: $175
- Director/officer names not in public filings

Wyoming is a credible alternative (no state income/franchise tax, strong privacy). Nevada offers anonymity but more administrative burden.

---

## The UK LLC Tax Trap — Critical

A Delaware LLC creates a **classification mismatch**:
- **US:** Multi-member LLC defaults to partnership (transparent — income taxed to members directly)
- **UK:** HMRC treats Delaware LLCs as **opaque** (taxed on distributions, not income as earned)

This mismatch can create **double taxation** that treaty relief doesn't fully resolve. *Anson v HMRC* (2015 Supreme Court) provided some relief but HMRC treats it as fact-specific, not a general rule.

**Practical impact:** A UK parent holding a US LLC faces complex, potentially unfavourable tax treatment. Using a **US C-Corp eliminates this entirely** — both jurisdictions treat it as opaque.

**Do not use an LLC without specialist UK-US tax advice.**

---

## UK-US Tax Treaty

The UK-US Income Tax Convention (2001, as amended) governs withholding rates:

| Payment Type | Standard Rate | Treaty Rate |
|---|---|---|
| Dividends (UK parent holds 10%+ voting) | 30% | **5%** |
| Dividends (UK parent holds 80%+ for 12 months) | 30% | **0%** (possible) |
| Interest | 30% | **0%** (most categories) |
| Royalties | 30% | **0%–15%** depending on type |

UK relief: foreign tax credit mechanism — UK parent credits US taxes against UK CT on same income. Capped at UK rate.

**Limitation on Benefits:** Treaty benefits require genuine UK tax residence and active UK trade. A pure holding company may fail this test.

---

## Cross-Border Structure Options

| Option | Liability | UK Parent Tax Exposure |
|---|---|---|
| **US Subsidiary** (recommended) | Limited to investment | US entity taxed in US; parent shielded until distribution |
| Branch | UK parent fully liable | UK parent taxed on US PE profits directly |
| New US JV entity | Depends on structure | Depends on ownership and control |

**Subsidiary is strongly preferred.** Limits liability, creates governance separation, allows US profit accumulation before UK taxation.

---

## Transfer Pricing (Cross-Border)

All UK-US intercompany transactions must be arm's length under both TIOPA 2010 and IRC Section 482:
- Products, services, management fees, IP licensing, loans
- Both jurisdictions require contemporaneous documentation
- Mispricing carries penalties in both and can cause double taxation
- US requires documentation available within 30 days of IRS audit

---

## Permanent Establishment Risk

A UK company triggers a US PE (and US taxation) when it has sufficient US presence:

**Creates PE:**
- Fixed place of business in the US (office, warehouse, construction site >12 months)
- Dependent agent habitually concluding contracts for the UK parent

**Does NOT create PE:**
- Storage, display, delivery activities alone
- Preparatory or auxiliary functions
- Independent agent acting in ordinary course

**Key risk:** UK founders making operational decisions for US entity, or US individuals with authority to bind the UK parent, can trigger PE. Use a US subsidiary with genuine local management.

---

## State-Level Obligations

### Sales Tax Nexus

Since *South Dakota v. Wayfair* (2018), states impose tax based on economic activity alone:
- Most threshold: **$100,000 annual sales** into that state (some add 200 transactions)
- Must register, collect, and remit sales tax once triggered
- **Applies even without a US entity** — UK companies selling to US customers can trigger nexus

### Foreign Qualification

Forming in Delaware doesn't authorise operations in other states. Must file for foreign qualification (Certificate of Authority) in each state where business is conducted:
- Requires certified Delaware formation documents, Certificate of Good Standing
- Filing fee: $100–$300 per state
- Registered agent needed in each state ($50–$150/year)

---

## Practical Setup

### Banking

| Option | Requirements | Best For |
|---|---|---|
| Traditional bank (Chase, BoA) | US entity, EIN, US address, often in-person | Physical US presence |
| Mercury / Relay | US LLC or Corp, EIN, US address | Non-residents |
| Wise / Airwallex | UK business docs + EIN | Interim USD transactions before US entity |

### EIN (Employer Identification Number)

US equivalent of UK UTR. Required for tax filings, bank accounts, employment.
- Apply via Form SS-4 by fax to IRS (+1 855 641 6935)
- Processing: ~4 weeks
- No fee
- UK director acceptable as responsible party

### Employment Options

| Option | Entity Required | Cost | Speed |
|---|---|---|---|
| **EOR** (Deel, Remote, Rippling) | No | 10–20% on salary | Days |
| **Direct employment** via US sub | Yes | Lower at scale | Weeks |

**Recommendation:** EOR for first 1–2 US hires. Switch to direct employment once headcount justifies entity costs. Note: EOR doesn't eliminate PE risk if the individual can bind the UK parent.

---

## UK vs US Feature Comparison

| Feature | UK Ltd | US C-Corp |
|---|---|---|
| Governing law | Companies Act 2006 (uniform) | State law (varies) |
| Formation | Articles of Association | Certificate of Incorporation + Bylaws |
| Public disclosure | High (Companies House) | Low (state filings only) |
| Tax rate | 25% (main) | 21% federal + state |
| Director duties | Statutory, stakeholder-oriented | Common law, shareholder-oriented |
| Business judgment rule | Implied | Explicit (strong protection) |

### Employee Incentives

| Approach | UK | US |
|---|---|---|
| Tax-advantaged options | EMI (CGT treatment) | ISOs (CGT if conditions met) |
| Profit sharing (cash) | Bonus, discretionary | Bonus, phantom equity |
| Cross-border grants | **Compliance trap** — do not grant UK EMI to US employees without specialist advice |
