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

## Host note, 2026-08-23

The Phase 4 target host was profiled directly. No model was served and nothing
below is measured throughput; this is a hardware and fit record that narrows
Phase 4 before any run.

| Property | Value |
| --- | --- |
| CPU | Intel i5-11400H, 6 cores / 12 threads, Tiger Lake-H |
| Vector ISA | AVX-512 with VNNI; no AMX, no `avx512_bf16` |
| GPU | RTX 3060 Laptop, 6 GB GDDR6, ~336 GB/s, 80 W TGP, sm_86 |
| VRAM free | 5.37 GB; 439 MB held by Xorg, `gnome-remote-desktop`, and a `neuriplo-kserve-runtime` |
| RAM | 38 GB total, 33 GB available. Speed unverified; DDR4-3200 assumed |
| Swap | 37 GB |
| Disk | 324 GB free |
| Stack | Ubuntu 24.04, driver 580.173 (CUDA 13 capable), `nvcc` 12.0 |
| Already local | 31 GB of Ollama blobs: `qwen3-coder:30b` Q4_K_M (18 GB), `gpt-oss:20b` MXFP4 (13 GB) |

Three consequences for the plan:

- **This host has two regimes, not one.** Full GPU offload is bounded by
  ~5.2 GB of model plus KV, which is the Gemma 4 E4B QAT slot the roadmap
  already named. Separately, 33 GB of available RAM makes MoE hybrid offload
  viable — expert tensors in RAM via llama.cpp `--n-cpu-moe`, attention,
  embeddings, and KV on the GPU — where decode cost scales with *active*
  parameters rather than total. `qwen3-coder:30b` is 30.5B total at ~3.3B
  active and is already on disk. This is the regime the Ryzen host structurally
  could not enter, and it is unmeasured.
- **The prompt-size finding gets its intervention here.** GPU prefill for a
  4B-class model is expected in the 1,000-2,000 tok/s range against the Ryzen
  host's ~49 tok/s. OpenCode's 7,876-token cold start would fall from 161 s to
  seconds. If the prompt-heavy agents become usable on identical weights and
  task, the finding is confirmed as a CPU-only artifact rather than a property
  of those agents. Estimated, not measured — that measurement *is* the Phase 4
  and 5 work.
- **`ollama show qwen3-coder:30b` lists `completion` only, without `tools`.**
  Per the Qwen2.5-Coder record that flag reflects the bundled template rather
  than the weights, but here it means Ollama's template for this tag will not
  produce tool calls at all. Serve the blob through `llama-server --jinja`, as
  the Ryzen runbook does, and screen tool-call capability before wiring an
  agent. `gpt-oss:20b` does advertise `tools` and `thinking`.

Backend selection is unchanged from the Ryzen host, for changed reasons. vLLM
and SGLang remain unusable: 6 GB of VRAM does not hold an unquantized 7B, and
while AVX-512 with VNNI means the vLLM CPU backend would now *build*, the
absence of AMX and `avx512_bf16` leaves it behind llama.cpp. llama.cpp is not
yet built on this host and needs `-DGGML_CUDA=ON`, which the Ryzen runbook's
CMake line omits.

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

First target: the owned i5-11400H laptop with an RTX 3060 6 GB, profiled in
the host note above, before any rented compute — the smaller slice that answers
the same question. Budget context upward from a low `--ctx-size` rather than
assuming the CPU host's value, and subtract the 439 MB the desktop session
already holds.

Run it as two ordered regimes rather than one:

1. **Full GPU offload**, bounded by ~5.2 GB of model plus KV. Gemma 4 E4B QAT
   (4.22 GB) is the pick, because it is the only checkpoint with a measured
   CPU-host baseline to compare against. Gemma 4 12B (6.72 GB) does not fit
   without partial offload.
2. **MoE hybrid offload**, experts in RAM via `--n-cpu-moe` with attention and
   KV on the GPU. `qwen3-coder:30b` (18 GB on disk, ~3.3B active) and
   `gpt-oss:20b` (13 GB, ~3.6B active) are both already local, so this regime
   costs no download and no rental.

**Correction to the 2026-08-21 plan.** That text called 26B A4B "out of reach"
and sized every candidate against VRAM alone. That was correct for the 14.5 GB
Ryzen host and is wrong here: with 33 GB of available RAM, total checkpoint size
stops being the binding constraint for MoE models and active-parameter count
takes over. Rented compute stays reserved for checkpoints that neither regime
holds — which is a smaller set than previously assumed.

That host also serves as the controlled intervention for the prompt-size
finding above: same model, same agents, same task, prefill faster by orders of
magnitude. If the prompt-heavy agents become usable there, the finding is
confirmed by intervention rather than by correlation across one host.

Exit evidence:

- The canonical checkpoint, license, quantization, chat template, context limit,
  and tool-call behavior are verified from current sources.
- Runtime version, flags, GPU, VRAM, RAM, observed memory, cold start, and
  throughput are recorded.
- The offload regime is named, and full-offload and MoE-hybrid runs are recorded
  as separate results. They differ in what bounds them and are not comparable to
  each other.
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
