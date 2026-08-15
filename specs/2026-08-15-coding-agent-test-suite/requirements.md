# Coding Agent Test Suite — Requirements

Status: planned. This is Roadmap Phase 2.

## What We Are Building

Create a self-contained test suite under `benchmarks/coding-agent-v1/`. It will
let a contributor give the same small coding tasks to different agents and
compare the results fairly.

The finished directory should be easy to navigate:

```text
benchmarks/coding-agent-v1/
├── README.md
├── benchmark.json
├── prompts/
├── fixtures/
├── rubrics/
├── scripts/
├── tests/
└── examples/dry-run.md
```

`benchmark.json` is the machine-readable index. It records the suite version and
connects each task to its prompt, starting fixture, checker, time limit, and
allowed tools.

## The Six Tasks

| ID | Agent receives | Passing evidence |
| --- | --- | --- |
| `endpoint-check` | Endpoint URL and authentication instructions | Status, protocol, and returned model name are recorded |
| `repository-summary` | A small Python project | A reviewer scores the summary with a published rubric |
| `create-file` | A clean project and an exact file request | The required file exists with the requested content |
| `edit-function` | A function-change request | Focused tests and the full fixture tests pass |
| `fix-failing-test` | A project with one seeded failure | Production code is fixed and unchanged tests pass |
| `multi-file-refactor` | A bounded refactor request | Behavior stays green and the requested file split exists |

The five coding tasks each receive a separate, complete fixture directory. The
fixture should be a small standard-library Python project that can run without
installing packages.

## Required Behavior

- `scripts/prepare.py TASK DESTINATION` copies a task's fixture into an empty
  destination. It must refuse unknown tasks, non-empty destinations, and paths
  inside the canonical fixture directory.
- `scripts/check_result.py TASK WORKSPACE` checks the submitted workspace and
  exits non-zero with a useful message when a requirement is unmet.
- `scripts/check_pack.py` verifies that every entry in `benchmark.json` points
  to existing files and that all six task IDs are present exactly once.
- Preparation and pack tests work offline and never read API credentials.
- Every task states its exact prompt, allowed tools, time limit, expected files,
  automatic checks, and any manual scoring steps.
- Each result records `pass`, `fail`, `skipped`, or `invalid`, plus retries,
  prompt changes, permission changes, and human intervention.
- A task-changing edit to a prompt, fixture, checker, time limit, or permissions
  requires a new suite version.

## Out of Scope

- Running a real agent or choosing a winning model; that starts in Phase 3.
- Provisioning endpoints, cloud machines, or GPUs.
- A web dashboard, database, plugin system, or general benchmark framework.
- Modernizing the legacy LangGraph and A2A examples.

## Done When

- All six tasks have prompts and scoring instructions.
- The five coding fixtures can be prepared safely from clean state.
- Pack tests demonstrate expected failure and success cases for every checker.
- `benchmarks/README.md` and `benchmarks/result-template.md` use the new suite.
- A model-free dry run shows the exact contributor workflow.
