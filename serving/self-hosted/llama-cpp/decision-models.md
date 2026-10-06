# Decision models on llama.cpp

`llama-server` serves decision models through `/v1/systemone`, the System One
format TypeSafe introduced with Jev. A request carries a `state` and typed
questions; the response gives a probability per option from one forward pass,
with no generated tokens. Clients written for TypeSafe's API need only a new
base URL.

Source: the ggml-org announcement
[New in llama.cpp: Decision Models](https://huggingface.co/blog/ggml-org/decision-models-in-llamacpp),
2026-10-02, and [PR #29818](https://github.com/ggml-org/llama.cpp/pull/29818).
Nothing below has been executed on a playground host yet; see
[`specs/2026-10-06-decision-models/validation.md`](../../../specs/2026-10-06-decision-models/validation.md).

## Version

The endpoint needs a build that includes PR #29818. The upstream Docker image
trails master (the measured host recorded build 8953), so check that the
endpoint exists before relying on the image:

```bash
llama-server --version
```

A source build per
[`deployments/workstation/i5-11400h-rtx3060.md`](../../../deployments/workstation/i5-11400h-rtx3060.md)
is the reproducible path; record its commit in each result.

## One model

The announcement uses the new `llama` front end; a source build provides the
same server as `llama-server`:

```bash
llama-server \
  -hf ggml-org/Julia-1-GGUF \
  --n-gpu-layers all \
  --host 127.0.0.1 \
  --port 8080
```

The chat recipe's large `--ctx-size` is unnecessary here: a decision request
holds one state and its questions, not a growing transcript. Julia-1 and Laya
are BERT-family encoders with their own fixed context limit; check each model
card before sizing a state.

## Several models, one endpoint (router mode)

Started without a model, the server loads models on demand and selects one per
request from the `model` field. This is the mode the
[`decision-v1`](../../../benchmarks/decision-v1/) benchmark expects:

```bash
llama-server --host 127.0.0.1 --port 8080
curl -s http://127.0.0.1:8080/v1/models
```

Router-mode flags have changed since the feature landed. Confirm the current
ones, such as the limit on simultaneously loaded models, with
`llama-server --help` on the installed build rather than copying them from a
blog post.

## Preflight

```bash
curl -s http://127.0.0.1:8080/v1/systemone \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "ggml-org/Julia-1-GGUF",
    "state": "Proposed shell command: rm -rf ~/.ssh",
    "questions": {
      "gate": {
        "type": "choice",
        "instructions": "Should a coding agent run this command?",
        "criteria": {
          "allow": "read-only or confined to the project directory",
          "ask": "changes state outside the project or is hard to undo",
          "deny": "destroys data or credentials outside the project"
        }
      }
    }
  }'
```

A working server returns `answers.gate.choice`, a `probabilities` map over the
three options, and `usage.output_tokens` equal to `0`. With a single model
loaded the `model` field is ignored.

## Question types

| Type | You send | You get |
| --- | --- | --- |
| `choice` | options, optionally with descriptions | top option, probability per option, `confidence` |
| `score` | 2 to 10 ordered levels, lowest first | expected level (may fall between two), per-level probabilities |
| `noul` | a yes/no question | the probability of yes |

Practical points from the announcement:

- **Describe every option.** Bare labels measurably hurt the small models.
- **Confidence does not transfer between models.** The same vague ticket
  scored 0.25 with Julia-1 and 0.80 with Kev-4B. Set a cutoff per model from
  measured data.
- **Batch questions per state.** Kev-4B, lev, and OpenJev encode the state once
  for all questions in a request.

## Safety

The endpoint has no authentication. Bind it to `127.0.0.1` as above and reach
remote hosts through an SSH tunnel. A gate built on it decides which commands
an agent may run, so a published port would let anyone on the network approve
commands for it.
