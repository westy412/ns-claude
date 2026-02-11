# Formatters

Convert DSPy Prediction objects to markdown between pipeline stages.

## The Problem

Raw DSPy Prediction objects don't transfer well between agents. LLMs process markdown with headers and bullets better than nested data structures.

## The Pattern

```python
def format_extraction_output(prediction) -> str:
    """
    Convert DSPy Prediction to markdown for downstream LLM consumption.
    """
    if not prediction:
        return "No data available."

    # Handle both Prediction objects and dicts
    if hasattr(prediction, '_store'):
        data = prediction._store
    elif hasattr(prediction, '__dict__'):
        data = prediction.__dict__
    else:
        data = prediction

    markdown = "# Company Analysis Report\n\n"

    if 'overview' in data:
        markdown += f"## Overview\n{data['overview']}\n\n"

    if 'industry' in data:
        markdown += f"## Industry\n{data['industry']}\n\n"

    if 'primary_offering' in data:
        markdown += f"## Primary Offering\n{data['primary_offering']}\n\n"

    return markdown
```

## Enum Enrichment

Inject semantic definitions for enum fields to give downstream agents context:

```python
def format_with_definitions(prediction) -> str:
    """Format with enum definitions for context."""
    if hasattr(prediction, '_store'):
        data = prediction._store
    else:
        data = prediction.__dict__

    markdown = "# Analysis Report\n\n"

    if 'pricing_model' in data and data['pricing_model']:
        model = data['pricing_model']
        markdown += f"## Pricing Model\n**{model}**\n"

        # Inject definition for context
        definitions = {
            "Subscription": "Recurring payments for ongoing access",
            "Usage-based": "Pay per unit consumed",
            "One-time": "Single purchase, perpetual license",
            "Freemium": "Free tier with paid upgrades",
            "Contact Sales": "Custom pricing requires sales conversation"
        }
        if model in definitions:
            markdown += f"*{definitions[model]}*\n\n"

    return markdown
```

## Usage in Pipeline

```python
class MyPipeline(dspy.Module):
    async def aforward(self, input_data: str):
        # Stage 1: Extract
        stage1_result = await self.extractor.acall(input=input_data)
        stage1_formatted = format_extraction_output(stage1_result)

        # Stage 2: Receives formatted markdown, not raw Prediction
        stage2_result = await self.analyzer.acall(
            previous_analysis=stage1_formatted,  # Markdown string
            input=input_data
        )

        return stage2_result
```

## Accessing Prediction Data

DSPy Predictions store data in different ways:

```python
# Method 1: Direct attribute access (most common)
value = result.field_name

# Method 2: _store dict (internal storage)
if hasattr(result, '_store'):
    data = result._store

# Method 3: __dict__ (fallback)
data = result.__dict__

# Method 4: For Pydantic models in OutputFields
if hasattr(result.field, 'model_dump'):
    data = result.field.model_dump()
```

## Complete Formatter Example

```python
def format_lead_analysis(prediction) -> str:
    """
    Format lead analysis for message creation agent.

    Converts structured extraction into readable context.
    """
    if not prediction:
        return "No analysis available."

    # Get data from prediction
    if hasattr(prediction, '_store'):
        data = prediction._store
    else:
        data = {k: v for k, v in prediction.__dict__.items()
                if not k.startswith('_')}

    sections = []

    # Company overview
    if data.get('company_overview'):
        sections.append(f"## Company Overview\n{data['company_overview']}")

    # Industry with definition
    if data.get('industry'):
        industry = data['industry']
        definitions = {
            "B2B SaaS": "Software-as-a-Service for businesses",
            "Enterprise Software": "Large-scale business software",
            # ... more definitions
        }
        industry_section = f"## Industry\n**{industry}**"
        if industry in definitions:
            industry_section += f"\n*{definitions[industry]}*"
        sections.append(industry_section)

    # Pain points (list)
    if data.get('pain_points'):
        points = data['pain_points']
        if isinstance(points, list):
            points_md = "\n".join(f"- {p}" for p in points)
        else:
            points_md = points
        sections.append(f"## Identified Pain Points\n{points_md}")

    # Target persona
    if data.get('target_persona'):
        sections.append(f"## Target Persona\n{data['target_persona']}")

    return "\n\n".join(sections)
```

## Anti-Patterns

```python
# WRONG: Passing raw Prediction object
stage2_result = await self.analyzer.acall(
    previous_analysis=stage1_result,  # Raw object, LLM struggles
    input=input_data
)

# WRONG: Passing dict with nested structures
stage2_result = await self.analyzer.acall(
    previous_analysis=stage1_result.__dict__,  # Nested dict, hard to parse
)

# WRONG: JSON string
stage2_result = await self.analyzer.acall(
    previous_analysis=json.dumps(stage1_result.__dict__),  # JSON is harder than markdown
)
```

## Why Markdown?

| Format | LLM Comprehension |
|--------|-------------------|
| Markdown | Best - headers, bullets, clear structure |
| Plain text | Good - but lacks structure |
| JSON | Moderate - parsing overhead |
| Nested dict | Poor - hard to interpret |
| Raw Prediction | Worst - may not serialize properly |

## Formatter Checklist

- [ ] Handle both Prediction objects and dicts
- [ ] Use markdown headers for sections
- [ ] Use bullets for lists
- [ ] Include enum definitions for context
- [ ] Handle missing fields gracefully
- [ ] Return "No data available" for empty input
