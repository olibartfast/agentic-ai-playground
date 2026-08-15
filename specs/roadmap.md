# Roadmap

Last replanned: 2026-08-15.

This roadmap starts from the repository's current brownfield state. Phases are
ordered to prove a small, comparable path before expanding the catalog. A phase
is complete only when its listed evidence exists; document count alone is not
completion.

## Status Legend

- **Complete**: declared evidence exists in the repository.
- **In progress**: the active branch is producing the evidence.
- **Next**: the next feature to specify and implement.
- **Planned**: ordered but not yet active.
- **Discovery**: important, but blocked on evidence or an earlier phase.

## Phase 0 — Separate the experiment layers

Status: **Complete**

Outcome: model profiles, serving sources, integrations, deployment targets,
benchmarks, and runnable experiments have distinct homes, with routing scenarios
describing how they compose.

Evidence:

- The root repository map and `docs/architecture.md` agree on the separation.
- Index pages exist for models, serving, integrations, deployments, benchmarks,
  and experiments.

## Phase 1 — Establish the spec-driven project baseline

Status: **In progress**

Outcome: durable intent, technical boundaries, an evidence-based delivery
order, and one active feature contract are available to humans and agents.

Exit evidence:

- `specs/mission.md`, `specs/tech-stack.md`, and this roadmap are reviewed.
- The next phase has requirements, plan, and validation documents.
- The root README points contributors to the roadmap.

## Phase 2 — Version a reproducible coding-agent benchmark

Status: **Next**

Outcome: the benchmark sequence becomes an executable, versioned contract with
clean fixtures, fixed prompts, explicit permissions, mechanical validators, and
a human rubric only where automation cannot decide the result.

Why now: the repository already lists candidate models, runtimes, providers,
and agents, but it cannot yet demonstrate a comparable end-to-end result. More
catalog growth before a stable task contract would multiply unverified paths.

Feature packet:
[`2026-08-15-reproducible-benchmark-baseline/`](2026-08-15-reproducible-benchmark-baseline/)

Exit evidence:

- A contributor can prepare every task from immutable versioned inputs.
- Pack self-tests detect fixture or validator drift without calling a model API.
- Each scenario declares machine-checkable and human-reviewed pass criteria.
- The result template identifies the benchmark pack and scenario outcomes.
- One documented dry run proves the instructions and reset path.

## Phase 3 — Record one managed end-to-end baseline

Status: **Planned**

Outcome: one coding agent completes the versioned benchmark through a managed
vendor API or hosted gateway, producing the first complete result record.

Exit evidence:

- Endpoint and model identity are verified.
- All scenario artifacts and validator outcomes are retained or linked.
- Tool reliability, latency, token use, estimated cost, and failures are
  recorded using the fixed benchmark version.
- No secret is present in committed files or logs.

## Phase 4 — Record one single-GPU self-hosted baseline

Status: **Planned**

Outcome: a verified quantized model served with a user-operated runtime runs the
same benchmark on one affordable GPU, without changing the task contract.

Exit evidence:

- The canonical checkpoint, license, quantization, chat template, context limit,
  and tool-call behavior are verified from current sources.
- Runtime version, flags, GPU, VRAM, RAM, observed memory, cold start, and
  throughput are recorded.
- The endpoint is private, and any remote path uses the documented tunnel.
- Results are compared with Phase 3 only on the fixed benchmark dimensions.

## Phase 5 — Compare agent integrations against a fixed source

Status: **Planned**

Outcome: at least two agents run the same benchmark against the same model
source so client/tooling behavior can be separated from model behavior.

Exit evidence:

- Both integrations document protocol, authentication variables, model mapping,
  and known tool limitations.
- The comparison fixes source, model, benchmark, fixture, prompt, permissions,
  and scoring while recording agent/version differences.

## Phase 6 — Evaluate hybrid and scale-out routing

Status: **Discovery**

Outcome: multi-GPU or hybrid main-agent/subagent paths are evaluated only where
the earlier baselines show a concrete capability or cost reason to do so.

Entry conditions:

- Candidate model cards and runtime recipes are verified.
- Required GPU topology and expected cost are explicit.
- The fixed benchmark exposes a limitation that the larger or hybrid path is
  intended to address.

## Phase 7 — Modernize selected framework prototypes

Status: **Discovery**

Outcome: an existing LangGraph or A2A example is promoted into `experiments/`
only if it supports a measured benchmark or routing question.

Entry conditions:

- The use case is tied to a prior result rather than catalog completeness.
- Unsafe tutorial shortcuts, stale dependencies, and secret handling are
  addressed in a dedicated feature contract.

## Replanning Triggers

Revisit phase order when validation reveals that:

- a selected API cannot express the required tool contract;
- the benchmark cannot distinguish model behavior from client behavior;
- a candidate checkpoint, runtime, or hardware path is unavailable or unsafe;
- measured cost makes the next phase disproportionate;
- a smaller slice can answer the same experiment question; or
- constitution assumptions are corrected by the maintainer.
