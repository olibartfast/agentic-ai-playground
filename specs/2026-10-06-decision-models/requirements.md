# Decision Models for Agent Harnesses — Requirements

Status: in progress, 2026-10-06. Branch `feature/system1`.

## Problem

An agent harness makes many small judgements per step that are not text
generation: whether a shell command should run, which tool fits an intent,
whether a subtask can leave the frontier model. Today the playground can only
answer those with a chat model, which spends one forward pass per output token
and returns prose that has to be parsed.

*Decision models* answer by scoring the options you supply. TypeSafe's Jev
introduced the System One API: a request carries a `state` and typed questions
(`choice`, `score`, `noul`) and the response carries a probability per option,
from one forward pass and with no output tokens. Since llama.cpp PR #29818
(announced 2026-10-02), `llama-server` serves the same `/v1/systemone`
contract for open GGUF checkpoints, so a self-hosted decision model now sits
behind the same interface as the hosted one.

Nothing in the repository yet says which of these checkpoints fits the owned
RTX 3060 6 GB host, or how accurate any of them is on the decisions a coding
agent actually makes. Published comparisons use benchmarks unrelated to agent
harnesses, and one widely cited set uses frontier-model agreement as its
reference labels rather than human judgement.

## Scope

- A serving recipe for `/v1/systemone` on llama.cpp, in router mode so several
  decision models share one loopback endpoint.
- A model profile covering the decision checkpoints published in the
  `ggml-org` collection, with license, input modality, and fit against the
  6 GB host stated as estimates until measured.
- A versioned benchmark, `benchmarks/decision-v1/`, made of hand-labelled
  coding-agent decisions in three families — shell-command gating, tool
  selection, and model routing — and a standard-library runner that reports
  accuracy, confidence calibration, latency, and accuracy at confidence
  cutoffs.
- Offline tests for the runner's request building and scoring.

## Out of scope

- Wiring a decision model into a coding agent's permission hooks. That needs a
  measured confidence cutoff per model first, which is what this packet
  produces; the hook integration is a later packet.
- Fine-tuning. Laya's own model card says its base checkpoints are near chance
  zero-shot and are meant to be fine-tuned; this packet measures zero-shot
  behaviour only and records that limitation.
- Image questions. Only OpenJev and Clef accept images, both are 27B, and
  neither fits the 6 GB host without heavy offload.
- Hosted Jev. The runner accepts any `/v1/systemone` base URL, but no hosted
  run is planned in this packet.

## Constraints

- The benchmark labels are the author's judgement, not model agreement. Each
  case states the label and why, so a reviewer can dispute it.
- No case may depend on a live repository, network, or secret.
- The runner uses only the Python standard library, per
  [`tech-stack.md`](../tech-stack.md) "Rules for New Automation".
- The server binds to `127.0.0.1`; remote use goes through the documented SSH
  tunnel.
- Model and hardware claims separate what was read from a model card or blog
  from what was executed on the host.
- OpenJev is CC BY-NC 4.0; the profile must flag it as unsuitable for
  commercial work.
