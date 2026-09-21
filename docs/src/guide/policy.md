# Policy

`Policy` owns thresholds and the TypeSafe question batteries used for input vs output checks.

## Defaults

| Knob | Default | Effect |
| --- | --- | --- |
| `review_threshold` / `reviewThreshold` | `0.35` | Noul ≥ this → at least `review` |
| `block_threshold` / `blockThreshold` | `0.70` | Noul ≥ this → `block` **if** the check is in `block_checks` |
| `harm_review_score` / `harmReviewScore` | `1.0` | Harm Score ≥ this → at least `review` |
| `harm_block_score` / `harmBlockScore` | `2.0` | Harm Score ≥ this → `block` |
| `min_confidence` / `minConfidence` | `0.5` | Score/Choice confidence below this → `review` |
| `block_checks` / `blockChecks` | `{jailbreak}` | Which Noul checks may escalate to `block` |

Low confidence defaults to **`review`**, never silent `allow`.

## Custom thresholds

::: code-group

```python [Python]
from blackrose import Guard, Policy

policy = Policy(
    review_threshold=0.25,
    block_threshold=0.6,
    harm_block_score=1.5,
    block_checks=frozenset({"jailbreak", "needs_human"}),
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
});
const guard = new Guard({ policy });
```

:::

## Custom questions

Pass your own TypeSafe `Question` map for input and/or output. Names become keys in `scores` and `reasons`.

::: code-group

```python [Python]
from typesafe_sdk import Noul, NoulCriteria
from blackrose import Guard, Policy

spam = Noul(
    instructions="Is this spam?",
    criteria=NoulCriteria(true="It is spam.", false="It is not spam."),
)
policy = Policy(input_questions={"spam": spam}, output_questions={"spam": spam})
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
});
const guard = new Guard({ policy });
```

:::

## Side-specific batteries

`questions_for("input")` / `questionsFor("input")` returns `input_questions` or the built-in input defaults. Same for `"output"`. Invalid sides raise.
