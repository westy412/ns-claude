# DSPy Training Data

## dspy.Example Structure

Training data in DSPy uses `dspy.Example` objects:

```python
import dspy

# Create an example with all fields
example = dspy.Example(
    # Input fields
    company_name="Acme Corp",
    description="B2B SaaS for sales teams",
    website_content="[crawled content]",

    # Output fields (ground truth)
    industry="B2B SaaS",
    target_audience="Sales teams",
    ranking="A"
)

# Mark which fields are INPUTS (rest are assumed outputs)
example = example.with_inputs(
    "company_name",
    "description",
    "website_content"
)
```

### Input vs Output Fields

```python
# Method 1: with_inputs() marks input fields
example = dspy.Example(a=1, b=2, c=3).with_inputs("a", "b")
# → inputs: a, b
# → outputs: c

# Method 2: Access input/output subsets
example.inputs()   # Returns Example with only input fields
example.labels()   # Returns Example with only output fields
```

---

## Loading Data from JSON

```python
import json
import dspy

def load_trainset(filepath: str, input_fields: list[str]) -> list[dspy.Example]:
    """
    Load training data from JSON file.

    Args:
        filepath: Path to JSON file (list of dicts)
        input_fields: Which fields are inputs (rest are outputs)

    Returns:
        List of dspy.Example objects
    """
    with open(filepath) as f:
        data = json.load(f)

    examples = [
        dspy.Example(**item).with_inputs(*input_fields)
        for item in data
    ]

    return examples


# Usage
trainset = load_trainset(
    "trainset.json",
    input_fields=[
        "company_name",
        "description",
        "website_content",
        "lead_job_title"
    ]
)
```

---

## Stratified Splitting

Ensure training and validation sets have representative distribution.

### Why Stratify?

| Problem | Impact | Solution |
|---------|--------|----------|
| Val set missing category | Optimizer doesn't see failure mode | Ensure all categories in val |
| Uneven distribution | Metrics skewed toward common cases | Even distribution in val |
| Random splits vary | Non-reproducible optimization | Fixed indices |

### Stratified Split Pattern

```python
import json
from collections import defaultdict
import random

def create_stratified_split(
    data: list[dict],
    stratify_key: str,
    val_per_category: int = 3,
    seed: int = 42
) -> tuple[list[int], list[int]]:
    """
    Create stratified train/val split with fixed indices.

    Args:
        data: Full dataset
        stratify_key: Field to stratify by (e.g., "icp_rank")
        val_per_category: How many val examples per category
        seed: Random seed for reproducibility

    Returns:
        train_indices, val_indices (both lists of ints)
    """
    random.seed(seed)

    # Group by category
    by_category = defaultdict(list)
    for i, item in enumerate(data):
        category = item.get(stratify_key, "Unknown")
        by_category[category].append(i)

    # Sample val_per_category from each
    val_indices = []
    for category, indices in by_category.items():
        if len(indices) >= val_per_category:
            sampled = random.sample(indices, val_per_category)
            val_indices.extend(sampled)
        else:
            # Take all if not enough
            val_indices.extend(indices)

    # Rest goes to training
    val_set = set(val_indices)
    train_indices = [i for i in range(len(data)) if i not in val_set]

    return train_indices, val_indices


def save_split_info(train_indices, val_indices, filepath):
    """Save split for reproducibility."""
    split_info = {
        "seed": 42,
        "train_indices": train_indices,
        "val_indices": val_indices,
        "trainset_size": len(train_indices),
        "valset_size": len(val_indices),
    }
    with open(filepath, "w") as f:
        json.dump(split_info, f, indent=2)
```

### Loading Fixed Splits

```python
def load_stratified_trainset(
    data_path: str,
    split_path: str,
    input_fields: list[str]
) -> tuple[list[dspy.Example], list[dspy.Example]]:
    """
    Load data with pre-computed stratified split.

    Returns:
        trainset, valset (both lists of dspy.Example)
    """
    # Load data
    with open(data_path) as f:
        data = json.load(f)

    # Load fixed split indices
    with open(split_path) as f:
        split_info = json.load(f)

    train_indices = split_info["train_indices"]
    val_indices = split_info["val_indices"]

    # Create Examples
    trainset = [
        dspy.Example(**data[i]).with_inputs(*input_fields)
        for i in train_indices
    ]

    valset = [
        dspy.Example(**data[i]).with_inputs(*input_fields)
        for i in val_indices
    ]

    print(f"Loaded: {len(trainset)} train, {len(valset)} val")
    print(f"Val indices: {val_indices}")

    return trainset, valset
```

---

## Pseudo-Labeling

When you don't have ground truth labels, use model predictions:

```python
def add_pseudo_labels(
    data: list[dict],
    model: dspy.Module,
    label_fields: list[str]
) -> list[dict]:
    """
    Add pseudo-labels by running unoptimized model.

    Args:
        data: Raw data without labels
        model: Unoptimized DSPy module
        label_fields: Which output fields to pseudo-label

    Returns:
        Data with pseudo-labels added
    """
    enriched = []

    for item in data:
        # Run model to get predictions
        pred = model(**{k: v for k, v in item.items() if k in INPUT_FIELDS})

        # Add pseudo-labels
        item_with_labels = item.copy()
        for field in label_fields:
            item_with_labels[f"predicted_{field}"] = getattr(pred, field, None)

        enriched.append(item_with_labels)

    return enriched
```

### Why Pseudo-Labels?

1. **Enable stratification** - Can split by predicted category even without ground truth
2. **Bootstrap optimization** - Start with model's best guess, improve from there
3. **Identify error patterns** - Where does the unoptimized model struggle?

---

## Data Size Guidelines

| Trainset Size | Valset Size | Optimizer | Notes |
|---------------|-------------|-----------|-------|
| 20-50 | 5-10 | BootstrapFewShot | Minimum viable, high variance |
| 50-100 | 10-15 | MIPROv2 / GEPA | Good balance of coverage and cost |
| 100-200 | 15-25 | GEPA | Best for complex multi-agent |
| 200+ | 25-50 | GEPA + subset sampling | Diminishing returns, sample trainset |

### Val Set Design Principles

1. **Small but representative** - 10-15 examples with even category distribution
2. **Fixed indices** - Same val set every run for reproducible metrics
3. **Cover edge cases** - Include examples that historically fail
4. **Match production distribution** - If 80% are category A, val should reflect that

---

## Round-Robin Assignment Pattern

For multi-variant workflows (different templates, offers, etc.):

```python
def assign_variants_round_robin(
    examples: list[dict],
    variants: list[tuple]  # (variant_name, variant_value)
) -> list[dict]:
    """
    Assign variants evenly across examples using round-robin.

    Ensures every variant combination appears in both train and val sets.
    """
    # Shuffle examples first
    random.shuffle(examples)

    # Round-robin assignment
    for i, example in enumerate(examples):
        variant_idx = i % len(variants)
        variant_name, variant_value = variants[variant_idx]
        example[variant_name] = variant_value

    return examples
```

---

## Complete Data Preparation Example

```python
import json
import dspy
from pathlib import Path

# Configuration
DATA_DIR = Path("trainsets")
INPUT_FIELDS = [
    "company_name",
    "description",
    "website_content",
    "lead_job_title",
    "lead_location"
]

def prepare_optimization_data():
    """
    Full data preparation workflow.

    1. Load raw data
    2. Add pseudo-labels (if needed)
    3. Create stratified split
    4. Save split info for reproducibility
    5. Return train/val sets
    """
    # 1. Load raw data
    with open(DATA_DIR / "raw_data.json") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} raw examples")

    # 2. Check for existing split
    split_path = DATA_DIR / "stratified_split_info.json"

    if split_path.exists():
        # Load existing split
        with open(split_path) as f:
            split_info = json.load(f)
        train_indices = split_info["train_indices"]
        val_indices = split_info["val_indices"]
        print(f"Loaded existing split: {len(train_indices)} train, {len(val_indices)} val")
    else:
        # Create new stratified split
        train_indices, val_indices = create_stratified_split(
            data,
            stratify_key="predicted_rank",  # Pseudo-label field
            val_per_category=3,
            seed=42
        )
        save_split_info(train_indices, val_indices, split_path)
        print(f"Created new split: {len(train_indices)} train, {len(val_indices)} val")

    # 3. Create dspy.Example objects
    trainset = [
        dspy.Example(**data[i]).with_inputs(*INPUT_FIELDS)
        for i in train_indices
    ]

    valset = [
        dspy.Example(**data[i]).with_inputs(*INPUT_FIELDS)
        for i in val_indices
    ]

    # 4. Print distribution info
    print("\n" + "=" * 40)
    print("STRATIFIED SPLIT LOADED")
    print("=" * 40)
    print(f"Trainset: {len(trainset)} examples")
    print(f"Valset:   {len(valset)} examples")
    print(f"Val indices: {val_indices}")
    print("=" * 40 + "\n")

    return trainset, valset


# Usage
trainset, valset = prepare_optimization_data()
```

---

## Data Quality Checklist

Before running optimization:

- [ ] **Input fields marked** - `with_inputs()` called correctly
- [ ] **Output fields present** - Ground truth or pseudo-labels exist
- [ ] **No missing values** - Handle None/empty strings
- [ ] **Consistent types** - Strings are strings, lists are lists
- [ ] **Stratification verified** - Val set has all categories
- [ ] **Split is fixed** - Indices saved to JSON
- [ ] **Size is appropriate** - At least 50 train, 10 val

---

## Related Documentation

- [Overview](overview.md) - Optimization concepts
- [Metrics](metrics.md) - Defining success metrics
- [GEPA Workflow](gepa-workflow.md) - Running optimization
- [Custom Proposers](custom-proposers.md) - Domain-aware instruction generation
