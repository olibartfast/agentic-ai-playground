# Experiment result

- Date: 2026-08-27
- Repository and commit: agentic-ai-playground, branch `master` at `bb5978e`
- Agent and version: **DeepSeek Harness (`dsh`) 0.1.1-rc.2**, measured against a
  **Pi 0.84.3** control re-run on the same server process
- Routing scenario: self-hosted
- Main-agent source and model: llama-server / Qwen3-Coder 30B-A3B Instruct
- Subagent source(s) and model(s): none
- Model checkpoint and revision, when self-hosted: Ollama blob
  `sha256-1194192cf2a187eb02722edcc3f77b11d21f537048ce04b67ccf8ba78863006a`,
  18.6 GB — identical to the 2026-08-24 and 2026-08-26 records
- Quantization: Q4_K_M weights; q8_0 K and V cache
- Runtime and version, when self-hosted:
  `ghcr.io/ggml-org/llama.cpp:server-cuda`, build **b10588 (`70adb1b4c`)** —
  **not** the build 8953 (`434b2a1ff`) of the prior records. The tag is rolling
  and the image moved. See "Comparability" below
- Deployment target: personal workstation with GPU — see the
  [i5-11400H + RTX 3060 runbook](../../deployments/workstation/i5-11400h-rtx3060.md)
- Hardware and topology, when self-hosted: Intel i5-11400H, RTX 3060 Laptop
  6144 MiB, 38 GB RAM. `-ngl 99 --n-cpu-moe 46 --no-mmap`, **5692 MiB VRAM in
  use** — the same figure the 2026-08-26 run recorded
- Context size: 65536, confirmed via `/props`. Identical to the two prior runs
- Cold-start time: 55 s to first `listening on` after `docker run`
- Prompt/output tokens: see the tables — the binding result
- Wall-clock time: 58.7 s (`dsh` cold one-shot), 26.9 s (Pi control cold
  one-shot), 28.5 s (`dsh` tool-call probe, warm slot cache)
- Estimated cost: none — local hardware
- Tool calls attempted/succeeded: **1 / 1** through a complete `dsh` agent loop
- Tests before/after: not applicable; suite not yet built
- Pass criteria met: **yes.** `dsh` reaches the endpoint, answers, and closes a
  full read-tool loop. Items 1 and 2 of the integration page's "before this is
  usable as evidence" list are now measured
- Notes: see below

## Why this run exists

[`integrations/dsh/`](../../integrations/dsh/README.md) has stood at "candidate,
nothing measured" since 2026-08-23, with every claim read from upstream rather
than observed. It named the two things that had to be measured before `dsh`
could be compared to anything: **system prompt size** and **tool-call
behaviour**. Both are measured here, against the unchanged serve configuration
of the [2026-08-26 prompt-size matrix](../2026-08-26-agent-client-prompt-sizes/result.md).

## Agent prompt size, `dsh` against the recorded four

Identical trivial prompt to every client — *"Reply with exactly the word:
ready"* — so the number is the client's own scaffolding and nothing else. The
four existing rows are carried from 2026-08-26; the `dsh` row and the Pi control
were measured today.

| Client | Version | Prompt tokens | Prefill | Outcome |
| --- | --- | --- | --- | --- |
| Pi | 0.84.3 | 4,953 | 25.5 s @ 194.1 tok/s | answered |
| Pi *(control, today)* | 0.84.3 | *5,003* | *25.3 s @ 198.1 tok/s* | *answered* |
| **dsh** | **0.1.1-rc.2** | **10,475** | **52.4 s @ 199.9 tok/s** | **answered** |
| OpenCode | 1.18.22 | 10,369 | 53.0 s @ 195.7 tok/s | answered |
| Kilo | 7.3.46 | 15,588 | 80.5 s @ 193.6 tok/s | answered |
| Hermes | 0.20.5 | 21,936 | 113.3 s @ 193.7 tok/s | answered |

**`dsh` lands second, effectively tied with OpenCode.** The gap is 106 tokens —
1.0% — which is inside the drift the Pi control shows for a client whose version
did not change. The honest statement is that `dsh` and OpenCode are
indistinguishable at this resolution, and that both cost roughly **2.1x Pi**.

That is a result worth stating plainly: the harness whose selling point is that
prompt assembly is a replaceable plugin ships a default prompt twice the size of
the smallest client measured here. The plugin seam is an opportunity, not a
delivered saving.

## Comparability, and why the control run exists

The `server-cuda` tag is rolling and the image is now build b10588 rather than
the 8953 of both prior records. That invalidates a naive comparison of seconds,
so Pi — unchanged at 0.84.3 — was re-run as a control on the same server
process:

| | 2026-08-26 (build 8953) | today (build b10588) | delta |
| --- | --- | --- | --- |
| Pi prompt tokens | 4,953 | 5,003 | +50 (+1.0%) |
| Pi prefill | 25.5 s @ 194.1 tok/s | 25.3 s @ 198.1 tok/s | +2.1% tok/s |

The +50 tokens is workspace-dependent scaffolding, not a version change — the
control ran from a different directory. **Prefill throughput moved 2%, so the
tables are comparable and the `dsh` row can be read against the recorded four.**
Prompt-token counts are a property of the client and are build-independent
regardless.

Pinning the digest rather than the `server-cuda` tag would remove this whole
paragraph from future runs. Recommend it.

## `dsh` issues a second, separate request

Unlike Pi, which produced exactly one server task, a single `dsh --profile
headless` invocation produced **two**:

| Task | Prompt tokens | Time | What it is |
| --- | --- | --- | --- |
| 6 | 123 | 2.39 s | a short preliminary call |
| 8 | 10,475 | 52.39 s | the agent turn |

The 123-token call is small enough not to matter for prefill cost on this host,
but it is a second round trip on every invocation and it is not something the
other four clients do. Its purpose was not identified from server-side logs
alone; upstream's `core/system-prompt` and session plugins are where to look.
**Do not treat 10,475 as the whole cost of a `dsh` turn — the invocation costs
10,598 prompt tokens across two requests.**

## A complete agent loop through `dsh`

The repository's reference tool-call probe, against a `calc.py` whose `add`
returns `a + b + 1` rather than the obvious `a + b`:

```text
$ dsh --profile headless \
    "Read calc.py and tell me what the add function returns. Use your read tool."

Based on the content of calc.py, I can see that the `add` function takes two
parameters `a` and `b`, and returns their sum plus 1 (i.e., `a + b + 1`).
```

Correct, and reachable only by actually reading the file. Server-side the loop
is visible as two model turns:

| Task | Prompt tokens | Output tokens | Turn |
| --- | --- | --- | --- |
| 26 | 2,435 | 48 | emits the tool call |
| 85 | 147 | 63 | consumes the tool result, answers |

`dsh` joins Pi and OpenCode in closing a full loop on this host. The 2,435
figure is not a cold cost — `llama-server`'s slot cache still held `dsh`'s
system prompt from the preceding run, so only the divergent suffix was
prefilled. A genuinely cold invocation pays the full 52.4 s first.

## Configuration that worked

`$DSH_HOME/settings.yaml`, which is
[`settings.example.yaml`](../../integrations/dsh/settings.example.yaml) with the
endpoint's real alias and window:

```yaml
llm-pi-ai:
  providers:
    local:
      apiKeyEnv: MODEL_API_KEY
      api: openai-completions
      baseURL: http://127.0.0.1:8080/v1
      defaultContextWindow: 65536
      compat:
        supportsDeveloperRole: false
        maxTokensField: max_tokens
      models:
        - id: qwen3-coder-30b
          contextWindow: 65536

agent-default-model:
  provider: local
  model: qwen3-coder-30b
```

Both `compat` switches were set pre-emptively from the integration page and the
endpoint answered on the first attempt. **They were therefore never tested
against a failing request** — whether either is actually required against
llama-server is still unmeasured, and the integration page should not claim they
are. `MODEL_API_KEY` was set to `local`; llama-server ignores the value but the
client refuses an unset one.

Installed with `npm install -g @deepseek-ai/dsh` (456 packages, 45 s) rather
than the `npx` form the integration page shows, so the version under test is
pinned in this record: **0.1.1-rc.2**.

## What this does not establish

- **Prompt-size stability.** One measurement per client. `dsh` is a
  developer preview at `0.1.1-rc.2` whose upstream warns in capitals about
  breaking changes; this number should be re-measured on any version bump.
- **The context-window trap.** `defaultContextWindow` was set correctly from the
  start, so the documented 262,144-token default was never exercised. Item 3 of
  the integration page's list is still unmeasured.
- **Decode.** Every figure here is prefill-bound. No decode-rate comparison
  between clients was attempted, and on this host decode degrades with KV depth
  and must be quoted with it.
- **Quality.** Nothing here says `dsh` is a better or worse agent than the other
  four. It says what its scaffolding costs and that its loop closes.

## Next actions

1. Update [`integrations/dsh/README.md`](../../integrations/dsh/README.md) —
   items 1 and 2 of "before this is usable as evidence" are answered, and the
   page's "candidate, nothing measured" status line is now wrong.
2. Pin the llama.cpp image by digest in the runbook so the comparability
   paragraph above is never needed again.
3. Identify the 123-token preliminary request, and whether it can be disabled.
4. Re-measure the whole matrix on one build if seconds — not just tokens — are
   ever to be compared across records.
