# UK Tax Implications for JV Co Structure

> **When to read:** When discussing corporation tax, transfer pricing, profit distribution, VAT, or HMRC compliance.

---

## Corporation Tax (2025/26)

### Rates and Thresholds

| Augmented Profits | Rate |
|---|---|
| Up to £50,000 | 19% (Small Profits Rate) |
| £50,001 – £250,000 | Marginal Relief (effective 19%–25%) |
| Over £250,000 | 25% (Main Rate) |

Marginal relief formula: `CT = Profits × 25% − [3/200 × (£250,000 − Augmented Profits)]`

**Legislation:** CTA 2010 Part 3A (ss.18D–18J)

### Associated Company Rules — Critical

**This is the most significant CT issue for the structure.**

Two companies are associated if one controls the other, or both are under control of the same person(s) (CTA 2010 s.18E, ss.450–451).

**Applying the test:**
- Founder A controls Operating Co A (100%) and is part of the controlling group of JV Co (50%)
- JV Co and Operating Co A are **associated** (HMRC CTM03941)
- JV Co and Operating Co B are **associated** (same logic)
- Operating Co A and B are NOT associated with each other

**Result: JV Co has 2 associated companies. Thresholds divided by 3:**

| Threshold | Standard | JV Co (÷3) |
|---|---|---|
| Small profits lower limit | £50,000 | **£16,667** |
| Marginal relief upper limit | £250,000 | **£83,333** |

Profit above £16,667 enters marginal relief. Main rate (25%) applies at just £83,333. Must enter "2" in CT600 box 326.

**HMRC manuals:** CTM03940, CTM03941, CTM03935, CTM03950

### Close Investment Holding Company (CIHC)

JV Co must be genuinely trading to access small profits rate. A pure holding/distribution company cannot (CTA 2010 s.34). If JV Co's primary function is receiving revenue and distributing, HMRC could challenge. **Specialist opinion recommended before first CT return.**

---

## Transfer Pricing

### Framework

UK transfer pricing (TIOPA 2010 Part 4, s.147) requires arm's length pricing for related party transactions. Applies to UK-to-UK transactions (since Finance Act 2004).

The founders control all three companies → participation condition (s.148) is satisfied.

### At-Cost Reimbursement — Problem

**Pure at-cost reimbursement (zero markup) will not satisfy arm's length.** An independent provider would not work at zero margin.

Under the Cost Plus Method:
```
Arm's Length Price = Cost Base + (Cost Base × Appropriate Markup)
```

- **Routine services, limited risk:** 5%–10% markup typical
- **Specialist expertise, higher risk:** 10%–15%+ markup
- Must be documented with reference to comparable providers

**HMRC guidance:** INTM412000 onwards; INTM485120 (arm's length ranges)

### SME Exemption — Key Relief

TIOPA 2010 s.166 provides a **wholesale exemption** from transfer pricing for SMEs:

| Category | Employees | Turnover |
|---|---|---|
| Small | < 50 | < €10m |
| Medium | < 250 | < €50m |

If JV Co and related companies collectively qualify as SME, **transfer pricing rules do not apply**. Document SME status at each year-end.

Caveats:
- HMRC can issue a notice requiring TP treatment for medium enterprises
- Exemption falls away if companies grow beyond thresholds
- Does not apply if counterparty is in a non-treaty territory (not relevant — all UK)

**HMRC:** INTM412080 (SME exemption)

### Recommendation

Even with the SME exemption, include a **5%–10% markup** on cost reimbursement. This protects if the exemption is lost and insulates against HMRC challenge. Document the basis with comparable service providers.

---

## Profit Distribution

### How JV Co Profit is Taxed

1. JV Co receives client revenue
2. Deducts: operating company reimbursements, director salaries, employee bonuses (all CT-deductible)
3. Pays corporation tax on remaining profit
4. Distributes from post-tax retained earnings: dividends to founders

**Employee profit share pool:** If structured as discretionary/contractual bonus, deductible from CT as staff cost. Dividends to founders are NOT CT-deductible.

### Dividend Tax Rates (2025/26)

| Band | Income Range | Dividend Rate |
|---|---|---|
| Basic rate | £12,571 – £50,270 | 8.75% |
| Higher rate | £50,271 – £125,140 | 33.75% |
| Additional rate | Over £125,140 | 39.35% |

**Dividend allowance:** £500 (2025/26). First £500 of dividend income above personal allowance is tax-free.

**Key:** Dividends are NOT subject to National Insurance. This is central to salary/dividend optimisation.

**Legislation:** ITTOIA 2005 Part 4 Chapter 3; ITA 2007 ss.13–13A

### Salary vs Dividend Optimisation

**Step 1 — Minimum salary to preserve state pension:**
Take salary at £12,570 (personal allowance). Result:
- No income tax (within personal allowance)
- No employee NIC (below primary threshold)
- Employer NIC: (£12,570 − £9,100) × 15% = ~£521 per founder (offset by Employment Allowance)

**Step 2 — Dividends up to basic rate limit:**
Fill remaining basic rate band (up to £50,270 total) at 8.75% dividend tax.

**Step 3 — Higher rate assessment:**
Above £50,270, dividend tax is 33.75%. At this point salary may become marginally competitive when employer NIC is offset by CT deduction.

### Employee Profit Share — Tax Options

| Option | Tax Treatment | Best For |
|---|---|---|
| **Cash bonus** | PAYE + NIC (employee 8% + employer 15%). CT-deductible. | Simple, immediate |
| **EMI options** | No tax on grant/exercise. CGT on sale (20% or 10% with BADR). | Long-term retention, tax-efficient |
| **Growth shares** | CGT on value above hurdle. Requires HMRC valuation. | Avoiding strike price mechanics |
| **CSOP** | No income tax on exercise. CGT on gains. £60,000 limit. | If EMI criteria not met |

**EMI is strongly preferred** for growing businesses. From April 2026: gross assets limit rises to £120m, employee limit to 500. Must notify HMRC within 92 days of grant.

**Legislation:** ITEPA 2003 Schedule 5; HMRC ETASSUM50000+

---

## VAT Considerations

### VAT Group Registration

VATA 1994 s.43 requires one entity or person to control all group members. In this 50/50 structure:
- JV Co doesn't control the operating companies (doesn't own them)
- Neither founder solely controls all three

**VAT grouping is unlikely to be available** under the standard test. Specialist VAT advice needed to test whether joint control satisfies s.43.

### VAT on Intercompany Recharges (Non-Grouped)

Operating companies providing services to JV Co = **taxable supply at 20% standard rate**. This is NOT a disbursement (operating companies provide their own services, not acting as agent).

**Net effect:** VAT-neutral if JV Co is fully taxable. JV Co reclaims input VAT. Proper VAT invoicing is mandatory.

**Threshold:** All companies should VAT-register if turnover exceeds £90,000.

**HMRC guidance:** VAT Notice 700 (general); VAT Notice 700/14 (management services)

---

## Employer Obligations

### PAYE and NIC (2025/26)

| | Rate | Threshold |
|---|---|---|
| Employee NIC | 8% | £12,570 – £50,270 |
| Employee NIC | 2% | Above £50,270 |
| Employer NIC | 15% | Above £9,100 (secondary threshold) |

Employer NIC increased from 13.8% to 15% from April 2025. JV Co must register as employer, operate RTI payroll.

### Employment Allowance

**£10,500 per year** from April 2025. Offsets employer NIC pound-for-pound.

**Eligible if:** Prior year employer NIC < £100,000 AND company has at least one employee who is not the sole director. With two founder-directors, JV Co qualifies.

### Auto-Enrolment Pensions

Directors with employment contracts earning above £10,000/year must be auto-enrolled.

- **Minimum:** 8% total (3% employer + 5% employee)
- **Qualifying earnings band:** £6,240 – £50,270
- At £12,570 salary: employer contribution = 3% × £6,330 = ~£190/year per founder

**Legislation:** Pensions Act 2008 ss.2–9
