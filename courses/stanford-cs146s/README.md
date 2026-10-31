# Stanford CS146S learning tracker

Use `agentic-ai-playground` as the central record of learning, experiments, and
evidence from studying [The Modern Software Developer](https://themodernsoftware.dev/).
This is a personal self-study tracker, not an official course submission or credential.

## Where work belongs

| Repository | Responsibility | Evidence to link here |
| --- | --- | --- |
| `agentic-ai-playground` | Course notes, isolated exercises, agent integrations, and comparative evaluations | Notes, experiment reports, configurations, and benchmark results |
| [skills](https://github.com/olibartfast/skills) | Reusable agent instructions and workflows extracted from successful exercises | Skill file and the commit or PR that adds it |
| [neuriplo-infer](https://github.com/olibartfast/neuriplo-infer) | Applying a learned technique to real C++ software engineering | Issue, PR, test results, and an account of what required human correction |

The external repository names come from the proposed learning plan; their current
contents and availability have not been checked. Inspect each repository's own
instructions before implementing work there.

## Working loop

1. Choose a topic or assignment from the course and record its source in
   [progress.md](progress.md). Preserve the course's actual title when recording it.
2. Write the learning objective and a small, observable success criterion.
3. Run an exercise here. Put course-specific work beside this tracker; use the
   existing shared areas below when an experiment has broader value.
4. Record the result, including failures, human intervention, and evidence.
5. If the workflow proves reusable, implement it in `skills` and link its commit or PR.
6. When useful, apply it in `neuriplo-infer` through that repository's normal workflow
   and link the outcome here.
7. Update progress only when the recorded completion criterion is met.

## Use existing repository areas

- [integrations/](../../integrations/): agent setup and tool connections.
- `experiments/`: create this area when adding runnable prototypes useful beyond
  one exercise.
- [benchmarks/](../../benchmarks/): repeatable evaluations and comparisons.
- [models/](../../models/), [serving/](../../serving/), and
  [deployments/](../../deployments/): configuration used by an experiment.

Link to implementation where it lives. Keep the learning objective, observations,
and conclusions here so course progress remains readable across repositories.

## Exercise record

Create a Markdown note beside this file when starting an exercise:

```markdown
# Exercise title

- Course source:
- Learning objective:
- Completion criterion:
- Status: planned / in progress / complete / blocked
- Implementation and revision:
- Agent, model, tools, and relevant configuration:
- Prompt or reproducible steps:
- Validation and results:
- Human corrections and limitations:
- Reusable skill PR or commit, if applicable:
- Practical application PR or commit, if applicable:
- What I learned:
```

Completing a local exercise, publishing a reusable skill, and applying it in another
project are separate outcomes. An exercise can be complete without either follow-up.
