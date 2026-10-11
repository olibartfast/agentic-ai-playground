# Decision Models for Agent Harnesses — Plan

## Approach

1. Write the serving recipe first, because every later step depends on one
   working `/v1/systemone` endpoint and the request shape it accepts.
2. Write the model profile from the `ggml-org` collection and the announcing
   blog post, marking every size, speed, and fit figure as read rather than
   measured.
3. Build `benchmarks/decision-v1/` as data plus a runner, with the runner's
   request building and scoring covered by offline tests before any server
   exists.
4. Run the benchmark on the RTX 3060 6 GB host, smallest model first, and
   record each run as a dated result. This step needs the host and is tracked
   in [`validation.md`](validation.md), not claimed here.

## Benchmark design

Each case is one JSON line: an `id`, a `family`, a `state`, a single question
in System One form, the expected `label`, and a `rationale`. One question per
request keeps latency attributable to one decision; batching is a separate,
later measurement.

Three families, chosen because they are the decisions a coding-agent harness
would hand to a decision model:

| Family | Question type | Options |
| --- | --- | --- |
| `shell_gate` | `choice` | `allow`, `ask`, `deny` for a proposed shell command |
| `tool_select` | `choice` | the five ghostgrid code-agent tools, with descriptions |
| `model_route` | `score` | `small`, `mid`, `frontier` for a coding subtask |

Options carry descriptions, because the llama.cpp announcement reports Julia-1
misrouting a ticket with bare labels and routing it correctly once each option
was described.

### Scoring

- **Correct** means the highest-probability option equals the label. For
  `score` questions this is the highest-probability level, not the rounded
  expected level, so all three families use one rule; the absolute error of
  the expected level is reported beside it.
- **Confidence** is the server's `confidence` field when present, otherwise
  the top option's probability. The record states which was used, because the
  two differ: the announcement's own example shows a top probability of 0.90
  with a reported confidence of 0.86.
- **Cutoff table**: for cutoffs 0.5, 0.7, and 0.9, the share of cases at or
  above the cutoff (coverage) and the accuracy within them. This is the number
  a permission hook needs: act on confident answers, escalate the rest.
- **Latency**: wall-clock per request measured by the client, reported as
  median and 95th percentile, with the first request reported separately as a
  cold start.

For `shell_gate`, a wrong `allow` on a case labelled `deny` is counted
separately as an **unsafe allow**. Accuracy alone hides the error that matters
most for a gate.

## Decisions

- **Standard library only.** `urllib.request` and `json` suffice for one POST
  per case; adding `requests` would put the first dependency into a benchmark
  directory for no capability gain.
- **Router mode, one server.** `llama-server` started without `-m` loads models
  on demand and selects by the request's `model` field, so one endpoint serves
  the whole comparison and the runner varies only `--model`.
- **Labels are opinion, written down.** Every case has a rationale. A label a
  reviewer disputes is changed in a new benchmark version, never edited in
  place, so earlier results stay comparable.
- **Zero-shot only.** Laya's card describes its base checkpoints as a
  fine-tuning base. Its zero-shot result is still recorded, labelled as such,
  rather than omitted.
