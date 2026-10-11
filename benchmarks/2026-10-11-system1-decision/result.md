# Experiment result — System One decision models on RTX 3060 6 GB

- Date: 2026-10-11
- Repository and commit: agentic-ai-playground, `feature/system1` at `df3d57b`
  (plus `benchmarks/decision-cv-v1/` and this result, committed here)
- Agent and version: n/a — benchmark runner is stdlib-only
  (`benchmarks/decision-v1/run.py`), no agent loop
- Routing scenario: self-hosted
- Main-agent source and model: none
- Subagent source(s) and model(s): none
- Model checkpoint and revision, when self-hosted:
  - `ggml-org/Julia-1-GGUF`, file `Julia-1-Q8_0.gguf` (161 MB)
  - `ggml-org/Laya-GGUF`, file `Laya-Q8_0.gguf` (429 MB)
  - `ggml-org/Kev-4B-GGUF`, file `Kev-4B-Q4_K_M.gguf` (2.9 GB)
  - All from HF cache, snapshot revisions pinned by the filenames above
- Quantization: Julia-1 Q8_0, Laya Q8_0, Kev-4B Q4_K_M
- Runtime and version, when self-hosted: source build of
  `~/repos/llama.cpp-system1` at `23b0202` (origin/master, includes PR #29818),
  `llama-server --version` reports **0.6.0-dev build 956**, single-model mode
  (`-m <file> --n-gpu-layers all --host 127.0.0.1 --port 8080`), one model at a time
- Deployment target: personal workstation with GPU — see the
  [i5-11400H + RTX 3060 runbook](../../deployments/workstation/i5-11400h-rtx3060.md)
- Hardware and topology, when self-hosted: Intel i5-11400H, RTX 3060 Laptop
  6144 MiB. Observed VRAM in use (`nvidia-smi`): **349 MiB** (Julia-1),
  **695 MiB** (Laya), **5029 MiB** (Kev-4B Q4_K_M, 776 MiB free — no room to
  co-locate a detector on this host)
- Context size: server default per model (Julia-1/Laya `n_ctx_slot = 8192`,
  Kev-4B `n_ctx_slot = 35840` as logged at load)
- Cold-start time: model load is seconds (largest: Kev-4B ~10 s to `listening`);
  runner-measured first-request latency per table below
- Prompt/output tokens: decision endpoint returns `usage.output_tokens == 0`
  on every request (verified in preflight); `input_tokens` 53 on the recipe's
  sample request
- Wall-clock time: 6 benchmark runs, each 36–39 sequential requests, minutes total
- Estimated cost: none — local hardware
- Tool calls attempted/succeeded: n/a
- Tests before/after: `run.py --validate-only` → 39 valid `decision-v1` cases
  (18 `shell_gate`, 12 `tool_select`, 9 `model_route`) and 36 valid
  `decision-cv-v1` cases (14 `cv_alert`, 10 `cv_second_pass`, 12 `cv_task_route`)
- Pass criteria met: host checks partially — single-model serving and both
  benchmarks measured for all three models (see validation update); **router
  mode was not tested** (no `/v1/models` listing, no `--model` selection)
- Notes: see below; per-case records alongside this file (`*-decision-v1.jsonl`,
  `*-decision-cv-v1.jsonl`)

## Why this run exists

The `feature/system1` packet added a serving recipe, a model profile, and the
`decision-v1` benchmark, all validated offline against a stub server only.
Every host check in
[`specs/2026-10-06-decision-models/validation.md`](../../specs/2026-10-06-decision-models/validation.md)
was open: no build with PR #29818 on the host, no proven `/v1/systemone`
response shape, no VRAM figure, no measured accuracy. This run closes all of
those except router mode. It also adds `benchmarks/decision-cv-v1/`, a
36-case CV-flavoured draft (construction-site alerting, detector second pass,
vision-task routing), because `decision-v1` only covers coding-agent
judgements and says nothing about neuriplo-style vision decisions.

## Preflight (recipe sample request)

`curl http://127.0.0.1:8080/v1/systemone` against Julia-1 returned
`answers.gate.choice = ask` (0.972 allow/ask/deny distribution,
`confidence` 0.958) with `usage.output_tokens == 0`, matching the shape the
recipe and the runner assume (`answers.<name>.probabilities` + `confidence`).
Note: the same state through `ghostgrid decide` (all three `decision-v1`
questions batched in one request) returned `deny` at 0.961 — batching the
questions changes the verdict, so single-question and batched numbers are not
directly comparable.

## decision-v1 — coding-agent judgements (39 cases)

### Julia-1 Q8_0

- Endpoint: `http://127.0.0.1:8080/v1/systemone`
- Cases scored: 39 of 39 (0 request errors)
- Overall accuracy: 0.487
- Unsafe allows (deny labelled, allow predicted): 0
- Confidence source: server
- Cold start: 0.178 s; warm p50 0.010 s, p95 0.150 s

| Family | Cases | Accuracy |
| --- | --- | --- |
| `model_route` | 9 | 0.444 |
| `shell_gate` | 18 | 0.444 |
| `tool_select` | 12 | 0.583 |

| Confidence cutoff | Coverage | Accuracy above cutoff |
| --- | --- | --- |
| 0.5 | 0.949 | 0.486 |
| 0.7 | 0.846 | 0.455 |
| 0.9 | 0.590 | 0.522 |

### Laya Q8_0

- Endpoint: `http://127.0.0.1:8080/v1/systemone`
- Cases scored: 39 of 39 (0 request errors)
- Overall accuracy: 0.667
- Unsafe allows (deny labelled, allow predicted): 5
- Confidence source: server
- Cold start: 0.214 s; warm p50 0.016 s, p95 0.046 s

| Family | Cases | Accuracy |
| --- | --- | --- |
| `model_route` | 9 | 0.667 |
| `shell_gate` | 18 | 0.556 |
| `tool_select` | 12 | 0.833 |

| Confidence cutoff | Coverage | Accuracy above cutoff |
| --- | --- | --- |
| 0.5 | 0.282 | 0.909 |
| 0.7 | 0.179 | 1.000 |
| 0.9 | 0.051 | 1.000 |

### Kev-4B Q4_K_M

- Endpoint: `http://127.0.0.1:8080/v1/systemone`
- Cases scored: 39 of 39 (0 request errors)
- Overall accuracy: 0.872
- Unsafe allows (deny labelled, allow predicted): 1
- Confidence source: server
- Cold start: 0.222 s; warm p50 0.136 s, p95 0.252 s

| Family | Cases | Accuracy |
| --- | --- | --- |
| `model_route` | 9 | 0.778 |
| `shell_gate` | 18 | 0.833 |
| `tool_select` | 12 | 1.000 |

| Confidence cutoff | Coverage | Accuracy above cutoff |
| --- | --- | --- |
| 0.5 | 0.615 | 1.000 |
| 0.7 | 0.410 | 1.000 |
| 0.9 | 0.077 | 1.000 |

## decision-cv-v1 — vision decisions, draft (36 cases)

Labels are the author's judgement on synthetic states, not measured
field data. Treat this as a smoke test of the question shapes, not as a
model ranking.

### Julia-1 Q8_0

- Cases scored: 36 of 36 (0 request errors)
- Overall accuracy: 0.556
- Unsafe allows: 0
- Cold start: 0.216 s; warm p50 0.011 s, p95 0.016 s

| Family | Cases | Accuracy |
| --- | --- | --- |
| `cv_alert` | 14 | 0.500 |
| `cv_second_pass` | 10 | 0.600 |
| `cv_task_route` | 12 | 0.583 |

| Confidence cutoff | Coverage | Accuracy above cutoff |
| --- | --- | --- |
| 0.5 | 0.861 | 0.548 |
| 0.7 | 0.667 | 0.583 |
| 0.9 | 0.528 | 0.632 |

### Laya Q8_0

- Cases scored: 36 of 36 (0 request errors)
- Overall accuracy: 0.556
- Unsafe allows: 0
- Cold start: 0.101 s; warm p50 0.018 s, p95 0.055 s

| Family | Cases | Accuracy |
| --- | --- | --- |
| `cv_alert` | 14 | 0.357 |
| `cv_second_pass` | 10 | 0.800 |
| `cv_task_route` | 12 | 0.583 |

| Confidence cutoff | Coverage | Accuracy above cutoff |
| --- | --- | --- |
| 0.5 | 0.417 | 0.600 |
| 0.7 | 0.111 | 1.000 |
| 0.9 | 0.056 | 1.000 |

### Kev-4B Q4_K_M

- Cases scored: 36 of 36 (0 request errors)
- Overall accuracy: 0.750
- Unsafe allows: 0
- Cold start: 0.364 s; warm p50 0.149 s, p95 0.327 s

| Family | Cases | Accuracy |
| --- | --- | --- |
| `cv_alert` | 14 | 0.714 |
| `cv_second_pass` | 10 | 0.600 |
| `cv_task_route` | 12 | 0.917 |

| Confidence cutoff | Coverage | Accuracy above cutoff |
| --- | --- | --- |
| 0.5 | 0.694 | 0.760 |
| 0.7 | 0.417 | 0.867 |
| 0.9 | 0.028 | 1.000 |

## Reading

- **Small models are not actionable.** Julia-1 (0.487/0.556) is near chance;
  its confidence does not separate right from wrong answers. Laya (0.667) has
  the only calibrated confidence of the small two, but **5 unsafe allows** on
  `shell_gate` disqualify it as a permission gate at any cutoff with usable
  coverage (0.5 → 28% coverage).
- **Kev-4B is usable as an assistant, not an authority.** 0.872 coding / 0.750
  CV, perfect `tool_select` (12/12) and strong task routing (11/12), 61.5%
  coverage at 1.000 accuracy behind a 0.5 cutoff — but still 1 unsafe allow,
  and `cv_alert` 0.714 is not safety-grade. Route and second-opinion behind a
  cutoff; never auto-escalate or auto-allow from it.
- **Latency tiers match the profile.** ~10–18 ms warm for the encoders,
  ~140–150 ms for Kev-4B. Kev-4B at 5 GB leaves no room beside a detector on
  this 6 GB host — deployment is either/or, or the detector moves elsewhere.
- **Not established:** router mode (untested — single-model servers only),
  Kev-4B Q8_0 (downloaded, not run — Q4_K_M already saturates VRAM),
  `decision-cv-v1` label quality (draft, n=36, synthetic states).

## Next actions

1. Test router mode (`/v1/models` listing + per-request `--model`) before
   claiming the benchmark's expected mode works.
2. Review `decision-cv-v1` labels as a separate benchmark version if they are
   to be trusted; do not edit cases in place.
3. A neuriplo `DecisionTask` (if any) should expose task routing and
   accept/review behind a per-model cutoff, never autonomous safety
   escalation — see the platform evaluation in the merge notes.
