# Roadmap

Last replanned: 2026-08-21.

This roadmap starts from the repository's current brownfield state. Phases are
ordered to prove a small, comparable path before expanding the catalog. A phase
is complete only when its listed evidence exists; document count alone is not
completion.

## Replan note, 2026-08-21

Two CPU-only experiments on a Ryzen 7 5700U laptop
([Qwen2.5-Coder-7B](../benchmarks/2026-08-21-qwen2.5-coder-7b-cpu/result.md),
[Gemma 4 E4B](../benchmarks/2026-08-21-gemma-4-e4b-cpu/result.md)) fired the
replanning trigger *"the benchmark cannot distinguish model behavior from
client behavior."* Phase order is unchanged; Phases 4 and 5 gain constraints.

What the evidence established:

- **Tool-call capability is model-specific and must be screened first.**
  Qwen2.5-Coder-7B Q4_K_M cannot emit the protocol wrapper under any client,
  `tool_choice`, or prompt. Gemma 4 E4B QAT does, and closed a full agent loop.
  An isolated request — one function, ~80 prompt tokens, no agent — settles
  this in seconds and does not need the target hardware. Run it before
  allocating any GPU.
- **Agent prompt size is a hardware-dependent cost that confounds agent
  comparison.** At ~54 tok/s of prefill, time to first token is set by the
  client's system prompt: Pi ships 1,370 tokens and completed the task in 40 s;
  OpenCode ships 7,876 and was cancelled mid-prefill; Hermes ships roughly
  16-19k. Same weights, same server, same task. Agents designed for hosted
  endpoints spend prompt budget on tool breadth because prefill is nearly free
  there; constrained self-hosting reverses that tradeoff.
- **A capability probe is not a suite run.** Neither record executed
  `benchmarks/README.md` steps 2-6, because
  [`benchmarks/coding-agent-v1/`](../benchmarks/) does not exist yet. Phase 2
  remains the blocking work.

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

## Phase 2 — Build the first coding-agent test suite

Status: **Next**

Outcome: add `benchmarks/coding-agent-v1/` with six named tasks, a small Python
sample project, fixed prompts, setup scripts, result checkers, and clear scoring
instructions.

Why now: `benchmarks/README.md` lists six activities, but the repository does
not yet provide the prompts, sample project, setup commands, or pass/fail checks
needed to run them consistently. Adding more model instructions first would
produce results that cannot be compared fairly.

Feature packet:
[`2026-08-15-coding-agent-test-suite/`](2026-08-15-coding-agent-test-suite/)

Exit evidence:

- Six exact prompts and five clean starting projects are checked in.
- The setup script creates a disposable task copy without overwriting inputs.
- Every coding-task checker is tested against wrong and correct results.
- The result template records the suite version and each task's outcome.
- One documented offline dry run proves the setup and checking commands.

## Phase 3 — Run the suite once with a hosted model

Status: **Planned**

Outcome: connect one named coding agent to a vendor API or hosted gateway, run
all six tasks, and commit the first complete result record.

Exit evidence:

- Endpoint and model identity are verified.
- All scenario artifacts and validator outcomes are retained or linked.
- Tool reliability, latency, token use, estimated cost, and failures are
  recorded using the fixed benchmark version.
- No secret is present in committed files or logs.

## Phase 4 — Run the suite once on a self-hosted GPU

Status: **Planned**

Outcome: serve one verified quantized model on a single affordable GPU and run
the same six tasks without changing their prompts or checks.

First target: an owned laptop RTX 3060 with 6 GB VRAM, before any rented
compute — the smaller slice that answers the same question. It holds Gemma 4
E4B QAT (4.22 GB) with room for a modest KV cache; it does not hold Gemma 4 12B
(6.72 GB) without partial offload, and 26B A4B (14.25 GB) is out of reach.
Budget context upward from a low `--ctx-size` rather than assuming the CPU
host's value, and account for VRAM the desktop session already holds.

That host also serves as the controlled intervention for the prompt-size
finding above: same model, same agents, same task, prefill faster by orders of
magnitude. If the prompt-heavy agents become usable there, the finding is
confirmed by intervention rather than by correlation across one host. Rented
compute stays reserved for checkpoints that do not fit locally.

Exit evidence:

- The canonical checkpoint, license, quantization, chat template, context limit,
  and tool-call behavior are verified from current sources.
- Runtime version, flags, GPU, VRAM, RAM, observed memory, cold start, and
  throughput are recorded.
- The endpoint is private, and any remote path uses the documented tunnel.
- Results are compared with Phase 3 only on the fixed benchmark dimensions.

## Phase 5 — Compare two coding agents on the same model

Status: **Planned**

Outcome: run the suite with two coding agents while keeping the model, endpoint,
prompts, permissions, and scoring unchanged.

Exit evidence:

- Both integrations document protocol, authentication variables, model mapping,
  and known tool limitations.
- The comparison fixes source, model, benchmark, fixture, prompt, permissions,
  and scoring while recording agent/version differences.
- **Each agent's system prompt size is measured and reported beside its
  results.** `hermes prompt-size` is one such instrument; server-side prompt
  token counts are another. Without this the comparison may measure prompt
  design rather than agent capability.
- The comparison runs on hardware where prefill is not the dominant cost, or
  states prompt-size-adjusted results explicitly. On the CPU host, agent
  ranking was fully determined by prompt size, and a richer prompt also gave a
  weak model more to imitate — degrading output as well as latency.

## Phase 6 — Test multi-GPU or main/subagent routing

Status: **Discovery**

Outcome: test a larger multi-GPU model or separate main-agent/subagent models
only when an earlier result shows why the extra complexity may help.

Entry conditions:

- Candidate model cards and runtime recipes are verified.
- Required GPU topology and expected cost are explicit.
- The fixed benchmark exposes a limitation that the larger or hybrid path is
  intended to address.

## Phase 7 — Update one legacy Python agent example

Status: **Discovery**

Outcome: move either the LangGraph or A2A example into `experiments/`, update its
dependencies and safety, and connect it to a specific measured question.

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
