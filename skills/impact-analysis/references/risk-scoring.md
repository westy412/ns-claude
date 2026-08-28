# Risk Scoring and Rollback

> **When to read:** Step 7 of every run. Score the findings, then judge the rollback.

Risk is the product of two judgements: how likely the break is, and how bad it is. Score both, then read the level off the matrix.

---

## Likelihood

| Level | Meaning |
|-------|---------|
| **Certain** | The break happens on the next request or the next deploy. You read the consumer and it cannot work. |
| **Likely** | The break happens under normal traffic. It needs a common input or a common state. |
| **Possible** | The break needs an uncommon input, a race, or a specific environment. |
| **Unlikely** | The break needs a rare combination that you cannot show. |

## Severity

| Level | Meaning |
|-------|---------|
| **Severe** | Data loss, data corruption, a security or tenancy breach, or a full outage. |
| **Major** | A feature fails for every user, or the failure is silent and corrupts state over time. |
| **Moderate** | A feature fails for some users, or the failure is loud and recoverable. |
| **Minor** | Cosmetic, a log-only effect, or a developer-facing break. |

## The matrix

| | Severe | Major | Moderate | Minor |
|---|---|---|---|---|
| **Certain** | Critical | Critical | High | Medium |
| **Likely** | Critical | High | Medium | Low |
| **Possible** | High | Medium | Medium | Low |
| **Unlikely** | Medium | Medium | Low | Low |

Three cases score Critical whatever the matrix says:
1. The change can destroy or corrupt data with no backup.
2. The change can expose one user's data or one tenant's data to another.
3. The change cannot be rolled back.

---

## Confidence

Every finding carries one label. The label is not the risk level. A `suspected` Critical still goes at the top of the report.

| Label | Rule |
|-------|------|
| `confirmed` | You read the consumer code and you can name the file and the line where it breaks. |
| `suspected` | You found the reference but you did not read the consumer, or the consumer sits outside your reach. |

Never state a finding as fact when you did not read the consumer. Downgrade to `suspected` and say what a person must check.

---

## The verdict

| Verdict | Rule |
|---------|------|
| **STOP** | One or more Critical findings stand open. |
| **GO WITH CONDITIONS** | High findings exist and each one has a verification step or a mitigation. |
| **GO** | No finding scores above Medium, and every ring was checked. |

A run that could not check a ring never returns GO. Return GO WITH CONDITIONS and name the gap.

In described mode the verdict answers "should I make this change in this way". In diff mode it answers "should this change ship".

---

## Rollback assessment

Answer four questions. Put the answers in the Rollback section.

1. **Is the change reversible?** A code change is reversible. A dropped column, a rewritten row, a sent message, and a rotated secret are not.
2. **What must deploy first?** Give the order for the schema, the producer, the consumer, and the client. Say which pairs must not run together.
3. **How does a person undo it?** Give the concrete steps: the revert, the down migration, the flag to turn off, and the value to restore.
4. **What survives the rollback?** Rows that the new code wrote, messages already in the queue, and cache entries with new keys all stay behind. Name them.

When the answer to question 1 is "no", say so in the verdict line. An irreversible change needs a backup step before the push, not after it.

---

## Verification steps

Each Critical and High finding gets one verification step. A step is a command a person can run, or an observation a person can make. Write it as an instruction.

Good: `Run SELECT COUNT(*) FROM orders WHERE status IS NULL; expect 0 before you apply the migration.`
Weak: `Check the orders table.`

Order the steps the way a person must do them. Put the steps that must run before the change ships at the top.
