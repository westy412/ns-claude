# Transformer/Formatter Agent

## Role Description
Converts data between formats, restructures data, and maps schemas. Transformers are the adapters and converters of agent systems—they take input in one structure and produce output in another with precision and consistency. They handle format conversion (JSON to XML), schema migration (v1 to v2), extraction (text to structured data), and normalization (standardizing dates, phones, etc.).

## When to Use
- The agent's sole job is converting data from format A to format B
- You need schema-to-schema mapping with explicit field correspondence
- Extracting structured data from unstructured input (parsing text into JSON)
- Normalizing inconsistent data into a standard format

## When NOT to Use
- The agent needs to make decisions about WHAT to do with the data → Use [Router] or [Orchestrator] instead
- The agent analyzes data and provides insights → Use [Analyzer] instead
- The agent generates new content rather than transforming existing content → Use [Generator] instead
- The agent needs to interact with users to clarify ambiguities → Use a Conversational framework instead

## Selection Criteria
- Is the agent's primary job converting data from one format to another? → Yes = this role
- Does every input have a corresponding deterministic output structure? → Yes = this role
- Does the agent need to exercise judgment about content (not just format)? → If yes, consider [Analyzer]
- Does the agent need to create new information beyond what's in the input? → If yes, consider [Generator]

## Framework Fit
**Primary:** Single-Turn
**Why:** Transformation is a pure function—defined inputs produce defined outputs. There's no dialogue, no clarification, no back-and-forth. The transformation rules are fixed at prompt time.
**When to use the other:** Never. If you find yourself wanting conversation, you don't have a pure transformer—you have an analyzer or assistant that happens to output structured data.

## Section-by-Section Guidance

### For Single-Turn Framework:

**`<who_you_are>`**
- Frame identity around transformation expertise: "data format specialist," "schema migration expert," "extraction specialist"
- Emphasize precision, consistency, and reliability over creativity
- Avoid personality traits—transformers are functional, not personable
- Keep it to 1-2 sentences; the work speaks for itself

**`<skill_map>`**
- List skills relevant to the transformation type: format conversion, schema mapping, pattern extraction, data normalization
- Include domain-specific skills if the data has domain context (e.g., "medical terminology normalization")
- Keep skills technical and concrete—avoid soft skills
- 3-5 skills is typical; don't pad the list

**`<context>`**
- Explain WHERE the output goes—this affects formatting decisions (database, UI display, API response, human reader)
- State the stakes: "accuracy is critical because..." helps the model understand error tolerance
- Mention upstream/downstream systems if relevant to the transformation
- Omit business context that doesn't affect transformation decisions

**`<inputs>`**
- Document the source data format explicitly—don't assume the model knows the schema
- For each input, specify: what it is, what's included, and how the transformer should use it
- Include both the data to transform AND any configuration (field mappings, format templates, normalization rules)
- If input can be malformed, say so and specify how to handle it

**`<task>`**
- Structure as numbered steps: parse → map → transform → validate → output
- Be explicit about field-by-field mapping when schemas differ
- Include normalization rules inline (dates to ISO 8601, phones to E.164)
- Specify handling for edge cases: missing fields, null values, type mismatches
- End with the output action, not analysis or recommendations

**`<output_format>`**
- Provide the EXACT target structure—this is non-negotiable for transformers
- Use placeholders that show where source data maps: `[field_name]`, `[source.nested.field]`
- Include format specifications inline: `[created_at as ISO 8601]`, `[phone as +1-XXX-XXX-XXXX]`
- Show handling of optional fields: `[due_date or "Not set"]`
- For complex structures, show the full shape including nested objects and arrays

**`<important_notes>`**
- Define ALL edge case handling: missing fields, null values, empty arrays, unknown enum values
- Specify normalization rules comprehensively: date formats, phone formats, casing rules
- Include type coercion rules: how to handle string "123" vs number 123
- State what happens to unmapped source fields (discard vs. preserve in legacy object)
- Add validation rules: what makes output invalid, what to do if validation fails

## Modifier Notes

**If adding Tools:**
- See `modifiers/tool-usage.md` for per-tool documentation patterns (if tools are added)
- Rarely needed—transformation should be self-contained
- Exception: lookup tables, validation APIs, or reference data
- If you need complex tool workflows, this is probably an Orchestrator

**If using Structured Output:**
- See `modifiers/structured-output.md` for schema design patterns
- Almost always required—transformers produce predictable schemas by definition
- Define the output schema to match your target format exactly
- Use strict mode to catch schema violations early
- For agent-to-agent: this IS structured output; the entire role is about format conversion

**If adding Memory:**
- See `modifiers/memory.md` for memory implementation patterns
- Transformers should NOT have memory—each transformation is independent
- If you need to track transformation history, that's the calling system's job
- Exception: batch transformations that need deduplication across items

## Common Pitfalls
1. **Ambiguous field mappings** — Every source field must map to exactly one target location. Explicit beats implicit.
2. **Undefined missing-data behavior** — Always specify: null, default value, or error? Don't leave it to inference.
3. **Implicit type coercion** — Be explicit: does string "true" become boolean `true`? Does "123" become number `123`?
4. **Lost data on schema migration** — Unmapped source fields should go somewhere (legacy object) not disappear.
5. **Inconsistent normalization** — Define canonical formats once and apply everywhere: "dates are always ISO 8601 UTC."
6. **No validation step** — The task should include validating output against the target schema before returning.
