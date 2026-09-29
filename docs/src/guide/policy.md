# Policy

`Policy` owns thresholds and the TypeSafe question batteries used for input vs output checks. Invalid combinations (reversed cutoffs, non-finite numbers, Noul/confidence values outside 0–1) raise `PolicyConfigError` at construction.

Construction also fails when a check could never affect the verdict:

- a `block_checks` / `blockChecks` name that is not a Noul question on either side (a typo, a Score check, or a check you renamed), and
- a Score question without a `score_thresholds` / `scoreThresholds` entry.

To keep a Score check informational, give it cutoffs above its rubric maximum. To never block on Noul checks, pass an empty set.

## Defaults

| Knob | Default | Effect |
| --- | --- | --- |
| `review_threshold` / `reviewThreshold` | `0.35` | Noul ≥ this → at least `review` |
| `block_threshold` / `blockThreshold` | `0.70` | Noul ≥ this → `block` **if** the check is in `block_checks` |
| `harm_review_score` / `harmReviewScore` | `1.0` | Default Score review cutoff for the **`harm`** check |
| `harm_block_score` / `harmBlockScore` | `2.0` | Default Score block cutoff for the **`harm`** check |
| `min_confidence` / `minConfidence` | `0.5` | Score/Choice confidence below this (or missing) → `review`. Present Noul confidence below this → `review`. |
| `block_checks` / `blockChecks` | `{jailbreak}` | Which Noul checks may escalate to `block` |
| `score_thresholds` / `scoreThresholds` | `{harm: (1.0, 2.0)}` | Per-check Score review/block cutoffs |

Low or missing Score/Choice confidence defaults to **`review`**, never silent `allow`. Custom Score checks need their own `score_thresholds` entry; they do not inherit the harm 0–3 scale.

## Custom thresholds

::: code-group

```python [Python]
from blackrose import Guard, Policy, ScoreThresholds

policy = Policy(
    review_threshold=0.25,
    block_threshold=0.6,
    harm_block_score=1.5,
    block_checks=frozenset({"jailbreak", "needs_human"}),
    score_thresholds={
        "toxicity": ScoreThresholds(review=0.5, block=0.9),
    },
)
guard = Guard(policy=policy)
```

```ts [JavaScript]
import { Guard, Policy } from "blackrose";

const policy = new Policy({
  reviewThreshold: 0.25,
  blockThreshold: 0.6,
  harmBlockScore: 1.5,
  blockChecks: ["jailbreak", "needs_human"],
  scoreThresholds: {
    toxicity: { review: 0.5, block: 0.9 },
  },
});
const guard = new Guard({ policy });
```

:::

## Custom questions

Pass your own TypeSafe `Question` map for input and/or output. Names become keys in `scores` and `reasons`. `Guard` treats those names as expected checks: if TypeSafe omits one, or returns it unreadable, the verdict is at least `review`.

The default `block_checks` is `{jailbreak}`, so when you replace both batteries, say which of your Noul checks may block.

::: code-group

```python [Python]
from typesafe_sdk import Noul, NoulCriteria
from blackrose import Guard, Policy

spam = Noul(
    instructions="Is this spam?",
    criteria=NoulCriteria(true="It is spam.", false="It is not spam."),
)
policy = Policy(
    input_questions={"spam": spam},
    output_questions={"spam": spam},
    block_checks=frozenset({"spam"}),
)
guard = Guard(policy=policy)
```

```ts [JavaScript]
import { noul } from "@typesafe-ai/sdk";
import { Guard, Policy } from "blackrose";

const spam = noul("Is this spam?", {
  true: "It is spam.",
  false: "It is not spam.",
});
const policy = new Policy({
  inputQuestions: { spam },
  outputQuestions: { spam },
  blockChecks: ["spam"],
});
const guard = new Guard({ policy });
```

:::

## Side-specific batteries

`questions_for("input")` / `questionsFor("input")` returns `input_questions` or the built-in input defaults. Same for `"output"`. Invalid sides raise.
