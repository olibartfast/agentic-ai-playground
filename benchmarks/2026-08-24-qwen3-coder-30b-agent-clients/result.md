# Experiment result

- Date: 2026-08-24
- Repository and commit: agentic-ai-playground, branch `master` at `d5ddbee`
- Agent and version: OpenCode 1.18.21, Hermes Agent 0.10.0, Kilo 7.3.46. Pi was
  **not installed** on this host and was not measured
- Routing scenario: self-hosted
- Main-agent source and model: llama-server / Qwen3-Coder 30B-A3B Instruct
- Subagent source(s) and model(s): none
- Model checkpoint and revision, when self-hosted: Ollama blob
  `sha256-1194192cf2a187eb02722edcc3f77b11d21f537048ce04b67ccf8ba78863006a`
  for `qwen3-coder:30b`, 18.6 GB
- Quantization: Q4_K_M weights; q8_0 K and V cache
- Runtime and version, when self-hosted:
  `ghcr.io/ggml-org/llama.cpp:server-cuda`, build 8953 (`434b2a1ff`)
- Deployment target: personal workstation with GPU — see the
  [i5-11400H + RTX 3060 runbook](../../deployments/workstation/i5-11400h-rtx3060.md)
- Hardware and topology, when self-hosted: Intel i5-11400H, RTX 3060 Laptop
  6144 MiB, 38 GB RAM. MoE hybrid offload, `-ngl 99 --n-cpu-moe 46`
- Context size: **65536**, raised from the 32768 used in the
  [2026-08-23 backend probe](../2026-08-23-qwen3-coder-30b-cuda-moe/result.md)
  specifically to clear Hermes' floor. Confirmed via `/props`
- Cold-start time: not re-measured; see the prior record
- Prompt/output tokens: see the agent prompt-size table — the binding result
- Wall-clock time: see below
- Estimated cost: none — local hardware
- Tool calls attempted/succeeded: **1 / 1** through a complete OpenCode agent
  loop. Kilo emitted a structured tool call unprompted
- Tests before/after: not applicable; suite not yet built
- Pass criteria met: **yes for the integration goal** — three of the four
  clients in this repository reach the local endpoint and answer. Not a suite
  run
- Notes: see below

## What this run establishes

The [2026-08-23 record](../2026-08-23-qwen3-coder-30b-cuda-moe/result.md) left
two things open: whether an agent loop closes on this host, and whether the
prompt-heavy clients that were unusable on the Ryzen laptop become usable with
a GPU. Both are answered here, and the answer is yes for both.

## The context floor drove the serve configuration

Hermes enforces a hard 64,000-token minimum. The prior run served 32768, which
Hermes refuses before contacting the endpoint. Qwen3-Coder-30B-A3B reports a
trained context of **262144** (`ollama show`), so declaring 65536 is a true
statement about the weights rather than the overstatement the
[Qwen2.5-Coder-7B record](../2026-08-21-qwen2.5-coder-7b-cpu/result.md) warns
about — that model's real window was 32K and claiming 64K would have replaced
an explicit refusal with silent truncation.

Raising context is not free. The KV cache at 65536 with q8_0 K and V costs
about 3.4 GB against 1.7 GB at 32768, and that VRAM comes out of the expert
tensors the GPU was holding:

| Configuration | VRAM | Prefill | Decode @ ~5.5k ctx |
| --- | --- | --- | --- |
| 32768, `--n-cpu-moe 42` (prior run) | 5516 MiB | 272.1 tok/s | 11.3 tok/s |
| 65536, `--n-cpu-moe 46` (this run) | 5692 MiB | 239.4 tok/s | 9.2 tok/s |

Roughly 12% of prefill and 19% of decode, paid to make one client usable. On a
host serving a single agent at a time that is the right trade; on a host where
Hermes is not in use, prefer 32768.

Short-context decode at this configuration measured 12.7 / 13.1 / 12.7 tok/s
across three runs, against 13.4-13.9 at the prior configuration. As in the
prior record, decode degrades with KV depth and must be quoted with it.

### A cold-start decode figure that is not real

The first request after load returned **3.8 tok/s**. Re-measuring after the
server settled gave 12.7-13.1 on identical prompts. With `--no-mmap` the
18.6 GB of weights are faulted into RAM on demand, and this host was
simultaneously holding a k3s/KServe cluster resident (~8 GB across
`k3d-neuriplo-server-0`, `neuriplo-kserve`, and `k3s`), leaving 2.7 GB free and
1.6 GB of swap in use at that moment. Discard the first measurement after any
load on this host; it reports memory settling, not inference speed.

## Agent prompt size, measured rather than estimated

Every client was given the same trivial prompt — *"Reply with exactly the word:
ready"* — so that the number below is the client's own scaffolding and nothing
else. Prompt sizes are read from `llama-server` slot timings, attributed by
running the clients strictly in sequence against an otherwise idle server.

| Client | Version | Prompt tokens | Prefill | Outcome |
| --- | --- | --- | --- | --- |
| OpenCode | 1.18.21 | **10,369** | 54.0 s @ 192.0 tok/s | answered |
| Hermes | 0.10.0 | **13,238** | 69.4 s @ 190.9 tok/s | answered, 1m19s wall |
| Kilo | 7.3.46 | **15,588** | 83.2 s @ 187.3 tok/s | answered, plus an unprompted tool call |
| Pi | — | not installed | — | not measured |

Two corrections to figures carried in this repository:

- OpenCode ships **10,369** tokens here, not the 7,876 recorded on the Ryzen
  host. The client version differs (1.18.21 against 1.18.20), so this is a
  moving target and should be re-measured per version rather than quoted from
  an older record.
- Hermes ships **13,238** tokens with 28 tools enabled. The Ryzen record's
  16-19k was an estimate derived from `hermes prompt-size` byte counts at
  roughly 3.5-4 bytes per token; the measured value is below that range.

The ordering the Ryzen record found — Pi smallest, then OpenCode, then Hermes —
does **not** hold here. Kilo, unmeasured on the Ryzen host, ships the largest
prompt of the three, and Hermes sits between it and OpenCode.

### The prompt-size finding is confirmed as hardware-dependent

This is the direct test the roadmap asked for. On the Ryzen host at ~49 tok/s
of prefill, OpenCode's cold start was 161 s and the client was cancelled before
first token; Hermes and Kilo were never viable. At ~190 tok/s here, every one
of them answers, with cold starts of 54-83 s.

The clients did not change and the task did not change. Only prefill throughput
did. That confirms the Ryzen finding as an artifact of CPU-only inference
rather than a property of those agents — which is exactly what the roadmap
predicted, and the prediction is now tested rather than assumed.

What has *not* changed is that prompt size still sets time to first token.
Kilo's 15,588 tokens cost 83 s before a single output token can exist. The
tradeoff is softened by a GPU, not removed.

## A complete agent loop

Confirmed at the level that matters — the loop closing — through OpenCode
against a `calc.py` whose `add` returns `a + b + 1` rather than the obvious
`a + b`, so a correct answer is impossible without reading the file:

```text
$ opencode run --model llama.cpp/qwen3-coder-30b \
    "Read calc.py and tell me what the add function returns. Use your read tool."

→ Read calc.py
The add function in calc.py returns the sum of its two parameters plus 1.
Specifically, it takes two arguments `a` and `b` and returns `a + b + 1`.
```

Correct tool selected, file actually read, correct answer. **This is the
reference agent-loop result for this host.**

Note on its cost: this invocation re-prefilled only 22-118 tokens per turn,
because `llama-server`'s slot cache still held OpenCode's system prompt from
the preceding run. A genuinely cold `opencode run` pays the full 54 s. The
Ryzen record's guidance therefore still applies — prefer a TUI session, or at
least consecutive runs, over isolated `run` invocations.

### Kilo's wider tool set still costs

Asked only to reply with one word, Kilo invoked a `kilo-config` skill first and
appended a paragraph about Kilo configuration:

```text
> code · qwen3-coder-30b
→ Skill "kilo-config"
ready
I've reviewed the Kilo configuration reference. ...
```

This reproduces the Ryzen record's finding about Kilo's `code` agent on a model
four times larger, and it is worth separating from the earlier failure: on
Qwen2.5-Coder-7B the call was emitted as fenced text and the wrong tool was
chosen. Here the call is structurally valid and executes. The behavior is
over-eagerness, not a parsing failure — but it still spends a second turn of
7,127 prefilled tokens on an unrequested action.

## Client configuration used

Endpoint `http://127.0.0.1:8080/v1`, model id `qwen3-coder-30b` (the server's
`--alias`), declared context 65536 everywhere.

OpenCode `~/.config/opencode/opencode.json` and Kilo `~/.config/kilo/kilo.jsonc`
take the same provider schema:

```json
"llama.cpp": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "llama-server (local)",
  "options": { "baseURL": "http://127.0.0.1:8080/v1", "apiKey": "dummy" },
  "models": {
    "qwen3-coder-30b": {
      "name": "Qwen3-Coder 30B-A3B (local)",
      "limit": { "context": 65536, "output": 8192 }
    }
  }
}
```

Selected per run with `--model llama.cpp/qwen3-coder-30b`, leaving each client's
default untouched.

Hermes 0.10.0 needed a different approach and is documented on the
[Hermes integration page](../../integrations/hermes/). Its `--provider` is now a
fixed enum with no `custom:<name>` form, and `-m local/qwen3-coder-30b` sends
the whole string as a model name to the configured default provider:

```text
HTTP 400: The supported API model names are deepseek-v4-pro, ... but you
passed local/qwen3-coder-30b.
```

Routing comes from the global `model:` block, so a profile was used to avoid
repointing the existing default:

```bash
hermes profile create llamacpp --clone
llamacpp chat -q "Reply with exactly the word: ready"
```

**The profile must not be named `local`.** `local` is a bash builtin and
shadows the generated `~/.local/bin` wrapper, so `local chat` fails with *"can
only be used in a function"*.

## Deviations from `benchmarks/README.md`

Only step 1, endpoint health and model discovery, was executed, plus the
`calc.py` tool-call probe. Steps 2 through 6 were not attempted.

Prompt-size attribution is by execution order against an idle server rather
than by per-client instrumentation. The clients were run sequentially and
nothing else held the endpoint, but this is inference from log ordering and not
a direct measurement of what each client sent.

Pi was not installed on this host, so the four-agent matrix is incomplete. Its
provider file was written to `~/.pi/agent/models.json` in advance but nothing
was verified against it.

These numbers are not comparable to the 2026-08-21 Ryzen records for the
reasons given in the prior host record — different model, different hardware,
different backend regime. The prompt-size comparison above is the exception and
is deliberate: it holds the client and task fixed and varies only the endpoint,
which is what makes it a test rather than a coincidence.

## Next actions

1. Install Pi and complete the four-agent matrix. It is the smallest-prompt
   client in the repository and the only one whose figure here is missing.
2. Re-measure OpenCode's prompt size per version. The 7,876 → 10,369 change
   across two patch releases means any quoted figure needs a version attached.
3. Run the actual suite from [`benchmarks/README.md`](../README.md) steps 2-6.
   Three clients now reach the endpoint and close loops, so the blocker is the
   missing suite rather than the hardware.
4. Decide the default serve context. 65536 costs 12% of prefill to support one
   client; if Hermes is not being evaluated, 32768 with `--n-cpu-moe 42` is the
   faster configuration.
5. Trim Kilo's tool set before judging it. `kilo --agent ask` narrows the
   surface that produced the unprompted skill call, and remains unmeasured.
