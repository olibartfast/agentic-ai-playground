# Experiment result

- Date: 2026-08-21
- Repository and commit: agentic-ai-playground, branch
  `agent/qwen3-8-27b-profile`
- Agent and version: direct HTTP probes against the endpoint, plus end-to-end
  probes through Pi 0.84.1, OpenCode 1.18.20, and Kilo Code 7.4.20; Hermes
  Agent was configured but refused the model — see the agent matrix
- Routing scenario: self-hosted
- Main-agent source and model: llama-server / Qwen2.5-Coder-7B-Instruct
- Subagent source(s) and model(s): none
- Model checkpoint and revision, when self-hosted: GGUF extracted from the
  Ollama tag `qwen2.5-coder:7b` (4,683,074,048 bytes,
  `sha256-60e05f2100071479f596b964f89f510f057ce397ea22f2833a0cfe029bfc2463`);
  upstream equivalent `Qwen/Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M`
- Quantization: Q4_K_M weights, q8_0 K and V cache
- Runtime and version, when self-hosted: llama.cpp `b1-bb4caa7`, built from
  source with GCC 15.2.0, `GGML_NATIVE=ON`
- Deployment target: personal workstation, CPU-only — see the
  [Ryzen 5700U runbook](../../deployments/workstation/ryzen-5700u-cpu-only.md)
- Hardware and topology, when self-hosted: AMD Ryzen 7 5700U, 8 cores /
  16 threads, AVX2 without AVX-512; 14.5 GB RAM, 9.6 GB available; no usable
  GPU (gfx90c iGPU, 0.5 GB aperture)
- Context size: 32768
- Cold-start time: not isolated; endpoint answered within the retry window on
  first load from page cache
- Prompt/output tokens: 42 / 120 on the speed probe
- Wall-clock time: see measured throughput below
- Estimated cost: none — local hardware
- Tool calls attempted/succeeded: **5 / 0** across five parsers — see findings
- Tests before/after: not applicable; suite not yet built
- Pass criteria met: **no** — see findings
- Notes: see below

## Measured throughput

Reported by `llama-server` `timings`, warm, single request, no concurrency:

| Metric | llama.cpp | Ollama 0.32.14 |
| --- | --- | --- |
| Generation | **7.9 tok/s** | 3.9 tok/s |
| Prompt / prefill | **32.7 tok/s** | not reported |

Identical weights on both runtimes. The roughly 2x gap is attributed to
`--threads 8`, `--flash-attn on`, and q8_0 KV cache; it was not decomposed per
flag. Prefill at 32.7 tok/s implies about five minutes to first token on a
10,000-token agent prompt, which is the dominant cost for agent use rather than
generation speed.

## Agent matrix

Every client below was configured against the same Ollama endpoint,
`http://127.0.0.1:11434/v1`, serving the same `qwen2.5-coder:7b`. Each was given
the same task: read a local `calc.py` and report what its `add` function
returns. All configurations are recorded under
[`integrations/`](../../integrations/) and are reusable with any other model.

| Client | Version | Reached endpoint | Tool call parsed | Wall clock | Failure |
| --- | --- | --- | --- | --- | --- |
| Raw HTTP (`/v1/chat/completions`) | Ollama 0.32.14 | yes | **no** | 8 s | bare JSON, no wrapper |
| [Pi](../../integrations/pi/) | 0.84.1 | yes | **no** | 51 s | bare JSON; correct path |
| [OpenCode](../../integrations/opencode/) | 1.18.20 | yes | **no** | 80 s | bare JSON; placeholder path |
| [Kilo Code](../../integrations/kilocode/) | 7.4.20 | yes | **no** | 66 s | fenced JSON; wrong tool |
| [Hermes](../../integrations/hermes/) | installed | **n/a** | **n/a** | 2 s | refused: needs 64K context |

Chat without tools works everywhere it was tried: Pi, OpenCode, and the raw
endpoint all return ordinary prose to a plain greeting. Only the tool path
fails. Configuration is therefore not the variable — see the root-cause finding.

Hermes never reached the model. It enforces a minimum 64,000-token context
window and this model reports 32,768, so it exits before issuing a request. The
error suggests raising `model.context_length`, but that key is global and would
also misdescribe the primary provider; and the model's true trained window is
32K, so declaring 64K would trade a clean refusal for silent truncation. Left
unset deliberately.

## Findings

### Tool calling fails

The blocking result. `/props` confirms the server loaded the official Qwen2.5
tool template, which instructs the model to return
`<tool_call>{"name": ..., "arguments": ...}</tool_call>`.

Given one `run_bash` function and `tool_choice: "auto"`, the response carried
`finish_reason: "stop"` and `tool_calls: null` in every attempt:

```text
temp 0.0  ```xml
          <function name="run_bash" arguments='{"command": "ls /etc"}'/>
temp 0.2  (identical to temp 0.0)
temp 0.8  ```xml
          <{"name": "run_bash", "arguments": {"command": "ls /etc"}}>
```

The same request through Ollama's `/api/chat` also returned no parsed calls,
emitting bare JSON without the wrapper:

```text
content: '{"name": "run_bash", "arguments": {"command": "ls /etc"}}'
```

A third probe drove the [Pi coding agent](../../integrations/pi/) against
Ollama's OpenAI-compatible endpoint on `http://localhost:11434/v1`, asking it to
read a local file with its built-in `read` tool. Pi received assistant text, not
a tool call, and the loop ended on the first turn after 51 s wall clock:

```text
{"name": "read", "arguments": {"path": ".../calc.py"}}
```

The path was correct and absolute, so tool selection and argument construction
are sound; only the wrapper is missing.

A fourth probe repeated the same task through
[OpenCode](../../integrations/opencode/) 1.18.20 against the same Ollama
endpoint. Same failure mode, 80 s wall clock, with an additional degradation:

```text
{"name": "read", "arguments": {"filePath": "/path/to/calc.py", "lines": 50, "offset": 1}}
```

The model matched OpenCode's `read` schema — `filePath`, `lines`, `offset` —
but emitted the literal placeholder `/path/to/calc.py` instead of resolving the
file it had been asked about. Under Pi's leaner prompt it produced the correct
absolute path. The cause is not the schema; see the next finding.

The model selects the correct function and arguments but will not emit the
protocol wrapper. Because four independent parsers fail — llama.cpp, Ollama's
native `/api/chat`, and both Pi and OpenCode over Ollama's OpenAI-compatible
endpoint — this is a model limitation at this quantization, not a server
setting. `--jinja` did not change the outcome.

`ollama show qwen2.5-coder:7b` lists `tools` under Capabilities. That flag
reflects the bundled prompt template, not whether the weights honor it, and must
not be read as evidence of working tool calls.

A fifth probe used [Kilo Code](../../integrations/kilocode/) 7.4.20, an
OpenCode fork, against the same endpoint and task. Same wrapper failure at 66 s,
compounded by wrong tool selection — it chose `suggest` over `read` and ignored
the task:

```json
{
  "name": "suggest",
  "arguments": {
    "suggestion": "It looks like you're working in a specific directory. ..."
  }
}
```

Interactive use degrades further still. In the Kilo TUI a bare `hello`
returned no greeting, but an unrequested subagent call — `{"name": "general",
... "subagent_type": "explore"}` — at 65 s and 6.3 tok/s. The same model under
the OpenCode TUI answered `Hi` with ordinary text. Kilo's `code` agent exposes
a wider tool set, and a pattern-matching model answers any input, including a
greeting, with tool-call-shaped JSON. Tool-set breadth is therefore a cost
rather than a feature at this model scale, and single-turn probes understate
the problem.

Consequence: OpenCode, Kilo Code, and Pi receive assistant text where they
expect tool calls, so no file is read or edited and the agent loop does not
advance. All three are now confirmed by direct measurement.

### Root cause is the weights, not the runtime, template, or agent

The preceding probes all carried agent system prompts, leaving open whether
prompt size or scaffolding caused the failure. A minimal request isolates it.

Ollama's bundled template is correct. `ollama show --template` confirms that a
populated `.Tools` injects an explicit instruction to return the call
`within <tool_call></tool_call> with NO other text`.

A hand-built request to `/v1/chat/completions` — 172 prompt tokens, one `read`
function passed in the `tools` field, `temperature` 0, no agent prompt — still
returned the payload as `content`, with `tool_calls` null and `finish_reason`
`stop`:

```text
{"name": "read", "arguments": {"path": "/tmp/calc.py"}}
```

Two escalations changed nothing, byte for byte:

| Variation | Result |
| --- | --- |
| `tool_choice: "required"` | identical bare JSON, `tool_calls` null |
| System prompt demanding the `<tool_call>` wrapper | identical bare JSON |

The model emits exactly the *inner* payload the template asks for and omits the
delimiters. It cannot be forced by the API and cannot be coached by prompt.
Runtime, template, transport, and agent are all eliminated: the failure is in
the weights at this quantization.

Practical consequence: no client-side configuration recovers this model for
agent use. Only a different model, or a parser that scrapes bare JSON out of
assistant text, would change the outcome — and the latter would still inherit
the argument-fidelity and tool-selection failures recorded above.

### A few-shot agent prompt is copied verbatim by a weak model

The placeholder path above was not invented. OpenCode's system prompt ships
few-shot examples containing that exact string, recoverable from the shipped
binary with `strings`:

```text
- **Path Construction:** ... For example, if the project root is
  /path/to/project/ and the file is foo/bar/baz.txt, the final path you must
  use is /path/to/project/foo/bar/baz.txt.
[tool_call: read for absolute_path '/path/to/tests/test_auth.py']
[tool_call: read for absolute_path '/path/to/requirements.txt']
[tool_call: write to create /path/to/someFile.test.ts with the test code]
```

The model reproduced the placeholder from its own context instead of resolving
the working directory. Pi's prompt carries no such examples, so the same weights
resolved the real path on the same task and the same endpoint. Two observations
follow.

First, argument *names* were correct in both probes. OpenCode's examples use
`absolute_path`, while the model emitted `filePath`, `lines`, and `offset` —
the real schema. Schema comprehension is intact; the failure is confined to
argument values and to the call wrapper.

Second, the examples demonstrate tool calls as bracketed prose,
`[tool_call: read for absolute_path '...']`, rather than as structured output.
For a model already unable to emit the protocol wrapper, this models the wrong
target and plausibly reinforces the primary failure. This was not isolated with
a controlled prompt and remains a hypothesis, unlike the placeholder copying,
which is directly evidenced.

The general caution: prompt scaffolding designed to *teach* tool use to capable
models becomes text to *imitate* for models that pattern-match. A richer agent
prompt can therefore make a weak model look worse than a leaner one on identical
weights. When comparing agents on a small local model, differences in output may
reflect prompt design rather than model capability, and agent-to-agent
comparisons must control for it.

## Deviations from `benchmarks/README.md`

Only step 1, endpoint health and model discovery, was executed. Steps 2 through
6 were not attempted because they require tool calls, which fail above, and
because `benchmarks/coding-agent-v1/` does not exist yet — see
`specs/2026-08-15-coding-agent-test-suite/plan.md`. These numbers are therefore
a runtime and capability probe, not a suite run, and must not be compared
against future suite results.

## Next actions

1. **Partly done — see the
   [Gemma 4 E4B CPU result](../2026-08-21-gemma-4-e4b-cpu/result.md).** That
   run confirms Gemma 4 E4B **does** emit well-formed tool calls on this host,
   and completed a full Pi agent loop in 40 s — the inverse of the result
   below. Original plan follows.

   Re-run the tool-call probe against Gemma 4 **E4B** QAT
   (`unsloth/gemma-4-E4B-it-qat-GGUF:UD-Q4_K_XL`, 4.22 GB plus a 56 MB MTP
   draft). It advertises native structured tool use, and its interleaved
   sliding-window attention should prefill long agent prompts better than full
   attention.

   E4B rather than the 12B originally named here: prefill is the binding cost
   at roughly five minutes to first token, and it scales with active
   parameters, so 12B moves the wrong way. E4B is about 4B active against this
   model's 7.6B. Sizes compared on this host, all UD-Q4_K_XL:

   | Variant | File | Verdict |
   | --- | --- | --- |
   | E2B | 2.62 GB | fallback if E4B prefill is still intolerable |
   | **E4B** | **4.22 GB** | fits the 8 GB model-plus-KV budget with room |
   | 12B | 6.72 GB | prefill regresses against the baseline above |
   | 26B A4B | 14.25 GB | does not fit 14.5 GB of RAM, despite ~4B active |

   Do not substitute the 3.22 GB `UD-Q2_K_XL`. These are quantization-aware
   checkpoints trained at 4-bit; requantizing to 2-bit discards the property
   that makes them worth choosing.

   All four agents are already configured against this model on
   `http://127.0.0.1:8080/v1` as `gemma-4-e4b` — see each integration page.
   Hermes is testable this round for the first time: Gemma 4 is a 256K-context
   family, so serving at `--ctx-size 65536` clears the 64,000-token floor that
   excluded it above. Every client's declared context limit was raised to 65536
   to match, and must stay equal to the serve flag.
2. Measure whether the bundled MTP draft delivers useful speculative decoding
   on CPU. It can only help generation, never prefill.
3. Keep Qwen2.5-Coder-7B for fill-in-the-middle completion, where the `insert`
   capability works and 7.9 tok/s is adequate.
