# Experiment result

- Date: 2026-08-21
- Repository and commit: agentic-ai-playground, branch
  `agent/qwen3-8-27b-profile`
- Agent and version: raw HTTP probe against the endpoint, plus interactive Pi
  0.84.2 and OpenCode 1.18.20 sessions observed from the server side. The
  scripted `calc.py` tool-call probe was **not** run — see deviations
- Routing scenario: self-hosted
- Main-agent source and model: llama-server / Gemma 4 E4B Instruct QAT
- Subagent source(s) and model(s): none
- Model checkpoint and revision, when self-hosted:
  `unsloth/gemma-4-E4B-it-qat-GGUF:UD-Q4_K_XL`, snapshot
  `8c5a9e4fd5482e2be20fe0bf013b4c262a8f4265`, 4.22 GB, plus the repo-root MTP
  drafter `mtp-gemma-4-E4B-it.gguf` (56 MB) auto-discovered from `-hf`
- Quantization: quantization-aware-trained Q4_0 weights repacked UD-Q4_K_XL;
  q8_0 K and V cache
- Runtime and version, when self-hosted: llama.cpp commit `bb4caa7`, built from
  source with GCC 15.2.0, `GGML_NATIVE=ON`. **Not** the Ubuntu
  `llama.cpp-tools 8681+dfsg-1` package, which cannot load the MTP drafter
- Deployment target: personal workstation, CPU-only — see the
  [Ryzen 5700U runbook](../../deployments/workstation/ryzen-5700u-cpu-only.md)
- Hardware and topology, when self-hosted: AMD Ryzen 7 5700U, 8 cores /
  16 threads, AVX2 without AVX-512; 14.5 GB RAM, ~10 GB available at launch; no
  usable GPU
- Context size: 65536 for the throughput probes, then **32768** for the
  end-to-end run after 65536 was found to push the host into swap. Both
  confirmed via `/props`
- Cold-start time: ~7 s from launch to `listening`, weights in page cache
- Prompt/output tokens: see the prefill table below; the binding measurement
- Wall-clock time: see below
- Estimated cost: none — local hardware
- Tool calls attempted/succeeded: **2 / 2** isolated, **1 / 1** through a
  complete Pi agent loop
- Tests before/after: not applicable; suite not yet built
- Pass criteria met: **yes for Pi**, no for the prompt-heavy agents. One agent
  loop completed end to end with a correct answer; OpenCode, Kilo Code, and
  Hermes remain blocked on prefill cost, not on model capability
- Notes: see below

## Measured throughput

Reported by `llama-server` slot timings, single slot, no concurrency, compared
against the [Qwen2.5-Coder-7B run](../2026-08-21-qwen2.5-coder-7b-cpu/result.md)
on the same host and runtime:

| Metric | Gemma 4 E4B | Qwen2.5-Coder-7B | Change |
| --- | --- | --- | --- |
| Generation | **13–20 tok/s** | 7.9 tok/s | ~2x faster |
| Prompt / prefill | **~49 tok/s** | 32.7 tok/s | ~1.5x faster |

Generation is a range rather than a point because Multi-Token Prediction is
active and its benefit varies with how predictable the output is:

```text
draft acceptance = 0.42637 (249 accepted / 584 generated), mean len = 2.71
```

43% of drafted tokens were accepted. MTP is doing real work, and it accelerates
generation only — it cannot touch prefill.

## Tool calling works

The blocking question from the Qwen run, answered in the affirmative. The probe
is deliberately minimal — 82 prompt tokens, one `read` function, `temperature`
0, no agent prompt — so that nothing but the weights is under test:

```json
{"finish_reason": "tool_calls",
 "tool_calls": [{"function": {"name": "read",
                              "arguments": "{\"path\":\"/tmp/calc.py\"}"}}],
 "content": ""}
```

Correct function, correct argument, well-formed wrapper, empty `content`.
Identical output at `tool_choice: "auto"` and `"required"`. Server-side latency
was 5.7 s.

This is the exact inverse of
[Qwen2.5-Coder-7B](../2026-08-21-qwen2.5-coder-7b-cpu/result.md), which emitted
the correct inner payload as assistant text in all five parsers and could not
be coerced by `tool_choice` or by prompt. On the same host, same runtime, same
quantization strategy, Gemma 4 E4B produces the protocol wrapper natively.

Scope of the claim: this establishes that the weights can emit a syntactically
valid tool call. It does not establish that an agent loop completes — that the
call is executed, the result fed back, and a correct final answer produced. See
next actions.

### A complete agent loop, end to end

Tool calling was then confirmed at the level that actually matters — the loop
closing — through [Pi](../../integrations/pi/) at `--ctx-size 32768`, on a
`calc.py` whose `add` returns `a + b + 1` rather than the obvious `a + b`, so
that a correct answer cannot be produced without reading the file:

```text
$ pi -p --provider local --model gemma-4-e4b --no-session \
    "Read calc.py and tell me what the add function returns. Use your read tool."

The `add` function in `calc.py` returns `a + b + 1`.

real  0m39.846s
```

Server-side, two turns totalling 35.3 s:

| Turn | Prompt tokens | Prefill | Generated | Total |
| --- | --- | --- | --- | --- |
| 1 — issue the `read` call | 1,370 | 25.2 s @ 54.4 tok/s | 81 @ 18.3 tok/s | 29.5 s |
| 2 — answer from the result | 61 (cache hit) | 1.3 s @ 46.0 tok/s | 92 @ 20.7 tok/s | 5.7 s |

This is the reference result for the host: **a small local model driving a real
agent loop to a correct answer in 40 seconds, CPU-only.** Note also that
prefill returned to 54.4 tok/s once the context dropped to 32768 and the host
stopped swapping, against ~32 tok/s at 65536 — confirming the diagnosis above.

Turn 2 is the shape of every subsequent turn in a session: the system prompt is
already resident, so only the tail is prefilled and the turn is
generation-bound. Turn one is the tax; the session is not.

### MTP acceptance is much higher on tool calls than on prose

| Output kind | Draft acceptance | Mean draft len | Generation |
| --- | --- | --- | --- |
| Tool-call JSON | **0.79** | 4.17 | **27 tok/s** |
| Conversational prose | 0.36–0.43 | 2.44–2.71 | 10–20 tok/s |

Structured output is predictable, so the drafter is right far more often. This
matters for agent workloads specifically: the tokens an agent spends on tool
calls are the cheapest tokens the model generates. It also means a generation
figure quoted from a chat benchmark understates agent-loop throughput.

## Prefill cost dominates, and it is set by the agent's prompt

The headline result. Prefill runs at a near-constant ~49 tok/s regardless of
client, so **time to first token is a direct function of how many tokens the
agent's system prompt ships**:

| Client | Prompt tokens | Prefill wall-clock | Outcome |
| --- | --- | --- | --- |
| Raw `/v1/chat/completions` | 17 | 0.3 s | answered immediately |
| Pi 0.84.2 | **1,370** (measured) | 25 s | **completed the task in 40 s** |
| OpenCode 1.18.20 | **7,876** | 145–161 s | cancelled before first token |
| Hermes (`prompt-size`) | ~16–19k | 5–6 min | not attempted |

A bare `Hi` typed into OpenCode never produced output. The server log shows the
request was still prefilling the system prompt when the client gave up:

```text
task 486  prompt processing, n_tokens = 2048, progress = 0.26, t = 41.84 s / 48.94 t/s
          stop: cancel task, id_task = 486
```

26% complete after 42 s. The model was not failing, and the configuration was
not wrong — 7,876 tokens at 48.9 tok/s is 161 s of arithmetic before the first
output token can exist. Read against the Qwen record, this is the same
"prompt scaffolding is a cost" finding, but the cost is wall-clock rather than
imitation of few-shot examples, and it is large enough to make the agent look
broken.

Pi's 1,370 tokens are measured directly from an isolated single-turn run.
OpenCode's 7,876 is confirmed as the request the operator described as an
unanswered `Hi`, cancelled mid-prefill. Hermes' figure is derived from
`hermes prompt-size` — 20,928 B of system prompt plus 44,758 B of tool schema
across 27 tools — converted at roughly 3.5–4 bytes per token, and is the only
estimate in the table. Kilo Code was not measured.

Pi is not better engineered than the others; it is **narrower**. Four built-in
tools against Hermes' 27. On a hosted endpoint that breadth is close to free
and buys real capability, which is why the larger agents are more widely
adopted. At 54 tok/s of prefill it inverts: prompt size becomes the dominant
cost of every cold start. The finding generalizes past this model — **agent
prompt size is a hardware-dependent cost, and CPU-only inference reverses the
usual tradeoff.**

### A 65,536-token KV cache pushes this host into swap

Serving at `--ctx-size 65536` left the machine at 9.7 GB used with **1.9 GB of
swap in use**. Prefill degraded from ~49 tok/s early in the session to ~32
tok/s later, and generation from 13–20 tok/s to ~10 tok/s. The cause is memory
pressure, not context length as such.

Consequence for this host: 65536 is affordable only in the sense that it loads.
Sustained agent work wants 32768, which is also what the Qwen run used and
therefore the context at which the two records are comparable. The tradeoff is
Hermes, which refuses anything under 64,000 tokens — but Hermes ships roughly
16–19k prompt tokens and was never viable here on prefill grounds either.

Any throughput figure in this record taken late in the session is depressed by
swap and should be treated as a floor.

### Within-session caching works and changes the guidance

Follow-up turns in an established session re-prefill only the diverging tail.
Observed prompt evals after the first turn were 10, 13, 28, 34, and 63 tokens,
with responses landing in 15–25 s.

The practical consequence is that `opencode run ...` is the wrong entry point
on this host: each invocation is a cold start that re-pays the full 161 s. The
TUI pays it once:

```bash
opencode -m local/gemma-4-e4b
```

Note that `--cache-reuse` is separately reported as disabled at load
(`cache_reuse is not supported by this context`) because Gemma's interleaved
sliding-window layers share KV across layer pairs. That flag governs reuse
*after* a divergence and is not what makes the above work; llama-server's
common-prefix slot cache is unaffected.

## Serving configuration

```bash
~/repos/llama.cpp/build/bin/llama-server \
  -hf unsloth/gemma-4-E4B-it-qat-GGUF:UD-Q4_K_XL \
  --spec-type draft-mtp --spec-draft-n-max 4 \
  --alias gemma-4-e4b --no-mmproj --jinja \
  --ctx-size 65536 --cache-type-k q8_0 --cache-type-v q8_0 --flash-attn on \
  --threads 8 --parallel 1 \
  --host 127.0.0.1 --port 8080
```

Two flag facts established by reproducing the failures:

- `--cache-type-v q8_0` requires `--flash-attn on`. The model card's `-fa off`
  example cannot be combined with it; the server exits with
  `quantized V cache requires flash_attn to be enabled`.
- `Gemma4Assistant requires ctx_other to be set` and
  `[spec] failed to measure draft model memory` are emitted during memory
  fitting and are **not** fatal. The drafter loads afterwards.

`--ctx-size 65536` rather than the Qwen run's 32768, because Hermes Agent
refuses any model reporting under 64,000 tokens. Gemma 4 is a 256K-context
family, so this is a real capability rather than an overstatement — but every
client's declared context limit must equal the serve flag or prompts are packed
and then silently truncated.

## Agent configuration status

All four clients are configured against `http://127.0.0.1:8080/v1` as
`gemma-4-e4b`, context 65536. Configurations are recorded on each integration
page and are reusable with any other model.

| Client | Configured | Reached endpoint | Tool call parsed |
| --- | --- | --- | --- |
| Raw `/v1/chat/completions` | n/a | yes | **yes — 2/2** |
| [Pi](../../integrations/pi/) | yes | yes | **yes — full loop, 40 s** |
| [OpenCode](../../integrations/opencode/) | yes | yes | cancelled in prefill |
| [Kilo Code](../../integrations/kilocode/) | yes | not yet | not measured |
| [Hermes](../../integrations/hermes/) | yes | not yet | not measured |

Hermes is expected to reach the model for the first time on this backend: the
64,000-token floor that excluded it from the Qwen run is cleared at
`--ctx-size 65536`. That expectation is untested.

A caution on model ids: `gemma-4-e4b` is this laptop's llama-server alias. If
the same client config also carries a similarly named model on a different
host — a LAN or remote endpoint — selecting the wrong one while that host is
down produces a client-side timeout that closely resembles a local failure.
Distinguish endpoints by provider key, and read the alias from `/v1/models`
rather than from memory.

## Deviations from `benchmarks/README.md`

Only step 1, endpoint health and model discovery, was executed. Steps 2 through
6 were not attempted, and neither was the `calc.py` tool-call probe used for
the Qwen agent matrix. These numbers are a runtime and prefill-cost probe, not
a suite run, and must not be compared against future suite results.

## Next actions

1. ~~Complete one agent loop end to end.~~ **Done — 40 s, correct answer.**
   The next step on this host is the real suite from
   [`benchmarks/README.md`](../README.md) steps 2–6, which this run still has
   not touched, run through Pi at `--ctx-size 32768`.
2. Move the agent comparison to rented GPU. Prompt size, not model capability,
   is what makes OpenCode, Kilo Code, and Hermes unusable here, and no local
   configuration change reaches it. See
   [`deployments/runpod/`](../../deployments/runpod/). Target the models this
   host structurally cannot hold — Gemma 4 12B (6.72 GB) and 26B A4B
   (14.25 GB, ~4B active). Record those as separate experiments; they are not
   comparable to this one.
3. Trim the prompt-heavy agents before concluding they are unusable in general.
   `kilo --agent ask` and `hermes -t file,terminal,todo` both attack the
   dominant term and neither has been measured. `hermes prompt-size` gives a
   byte breakdown without contacting a model and is the right instrument.
4. Instrument prompt size per agent rather than inferring it from the server
   log, so the prefill table can drop its attribution caveat.

**E2B is not a next action.** Its only real argument was that a smaller model
might succeed at tool calling where a larger one failed — the Qwen-shaped
worry. E4B emits tool calls correctly, so that argument is spent, and E2B's
remaining benefit acts on the model term while the prompt term dominates.
