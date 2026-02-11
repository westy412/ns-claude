# Text Agent (DSPy)

> **This is an alias for [Basic Agent](./basic-agent.md).**

## Why There's No Separate Text Agent in DSPy

In LangGraph, there's a distinction between:
- **Text Agent** — Returns raw string output
- **Structured Output Agent** — Returns Pydantic-validated schema

**DSPy doesn't make this distinction** because:

1. **Everything uses Signatures** — All DSPy agents define input/output via Signatures, which are inherently typed schemas.

2. **"Text" output is just a string field** — If you want text output, define a `str` output field in your Signature.

3. **No special handling needed** — DSPy's Predict works the same whether your output is a string, a list, or a complex Pydantic model.

## If You Want "Text-Like" Output

> **Structured Output Rule:** Use typed DSPy output fields (`bool`, `int`, `list[str]`, `dict[str, Any]`) or Pydantic `BaseModel`/`RootModel` as OutputField types. NEVER use `str` fields with JSON parsing instructions. See `frameworks/dspy/CHEATSHEET.md` Critical Rules.

Use a **Basic Agent (dspy.Predict)** with a string output field:

```python
import dspy

class TextOutputSignature(dspy.Signature):
    """
    Generate text content based on input.

    Write clear, well-structured content that addresses the prompt.
    """
    prompt: str = dspy.InputField(description="What to write about")

    # This is your "text output"
    content: str = dspy.OutputField(description="Generated text content")


# Use Basic Agent pattern
class TextGenerator(dspy.Module):
    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.generator = dspy.Predict(TextOutputSignature)
        self.generator.set_lm(shared_lm)

    def forward(self, prompt: str) -> str:
        result = self.generator(prompt=prompt)
        return result.content  # Just return the string


# Usage
lm = get_shared_lm()
gen = TextGenerator(shared_lm=lm)
text = gen("Write a brief introduction to Python")
print(text)  # Plain string output
```

## When to Use ChainOfThought for Text Generation

For **creative** text generation where quality matters, use **Reasoning Agent (ChainOfThought)**:

```python
class CreativeWritingSignature(dspy.Signature):
    """
    Generate creative content with careful consideration.

    Think through the tone, structure, and key points before writing.
    """
    topic: str = dspy.InputField()
    audience: str = dspy.InputField()

    content: str = dspy.OutputField(description="The generated content")


# ChainOfThought adds reasoning before generating content
generator = dspy.ChainOfThought(CreativeWritingSignature)
result = generator(topic="Benefits of remote work", audience="HR managers")

print(result.reasoning)  # See the thinking process
print(result.content)    # The final text
```

## Summary

| LangGraph | DSPy Equivalent |
|-----------|-----------------|
| Text Agent | Basic Agent with `str` output field |
| Structured Output Agent | Basic Agent with typed output fields |

**See [Basic Agent](./basic-agent.md) for the full implementation pattern.**
