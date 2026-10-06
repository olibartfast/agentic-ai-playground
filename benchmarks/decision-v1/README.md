# decision-v1

Measures how accurately a decision model answers the small judgements a coding
agent's harness makes, and at which confidence it can be trusted to act
without a human. Spec:
[`specs/2026-10-06-decision-models/`](../../specs/2026-10-06-decision-models/).

The model is reached through the System One `/v1/systemone` API, so the same
run works against `llama-server`, `laya-serve`, or TypeSafe's hosted Jev by
changing `--base-url`.

## Contents

| File | Purpose |
| --- | --- |
| [`questions.json`](questions.json) | One System One question per family, options described |
| [`cases.jsonl`](cases.jsonl) | 39 labelled cases, each with a written rationale |
| [`run.py`](run.py) | Standard-library runner and scorer |
| [`tests/`](tests/) | Offline tests, including a local stub server |

| Family | Type | Cases | Options |
| --- | --- | --- | --- |
| `shell_gate` | `choice` | 18 | `allow`, `ask`, `deny` |
| `tool_select` | `choice` | 12 | the five ghostgrid code-agent tools |
| `model_route` | `score` | 9 | `small`, `mid`, `frontier` |

Labels are the author's judgement, not agreement with another model. Disagree
with one? Change it in a new benchmark version rather than editing this one, so
earlier results stay comparable.

## Run

Start a server per
[`serving/self-hosted/llama-cpp/decision-models.md`](../../serving/self-hosted/llama-cpp/decision-models.md),
then:

```bash
python3 benchmarks/decision-v1/run.py --validate-only
python3 benchmarks/decision-v1/run.py \
  --model ggml-org/Julia-1-GGUF \
  --out julia-1.jsonl
```

Omit `--model` for a single-model server. For an endpoint that needs a bearer
token, put it in an environment variable and pass the variable's name with
`--api-key-env`; the token never appears on the command line.

The runner prints a Markdown summary to paste into a dated result under
[`benchmarks/`](../), together with the fields of
[`result-template.md`](../result-template.md) that apply: checkpoint,
quantization, runtime build, hardware, and observed VRAM.

## Reading the result

- **Unsafe allows** counts `deny` cases answered `allow`. A gate with any is not
  ready, whatever its accuracy.
- **Cutoff table** gives, per confidence cutoff, the share of cases the model
  answers at or above it and the accuracy on those. A permission hook acts on
  those and asks the user about the rest.
- **Confidence** comes from the server's `confidence` field where present, else
  the top option's probability. The summary says which. Cutoffs are not
  comparable across models.
- **Cold start** is the first request, which in router mode includes loading
  the model. Warm latency excludes it.

## Tests

```bash
python3 -m unittest discover -s benchmarks/decision-v1/tests
```
