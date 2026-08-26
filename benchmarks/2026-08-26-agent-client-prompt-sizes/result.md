# Experiment result

- Date: 2026-08-26
- Repository and commit: agentic-ai-playground, branch `master` at `b49aacb`
- Agent and version: **Pi 0.84.3, OpenCode 1.18.22, Hermes Agent 0.20.5,
  Kilo 7.3.46.** All four measured — the first complete matrix in this
  repository
- Routing scenario: self-hosted
- Main-agent source and model: llama-server / Qwen3-Coder 30B-A3B Instruct
- Subagent source(s) and model(s): none
- Model checkpoint and revision, when self-hosted: Ollama blob
  `sha256-1194192cf2a187eb02722edcc3f77b11d21f537048ce04b67ccf8ba78863006a`
- Quantization: Q4_K_M weights; q8_0 K and V cache
- Runtime and version, when self-hosted:
  `ghcr.io/ggml-org/llama.cpp:server-cuda`, build 8953 (`434b2a1ff`)
- Deployment target: personal workstation with GPU — see the
  [i5-11400H + RTX 3060 runbook](../../deployments/workstation/i5-11400h-rtx3060.md)
- Hardware and topology, when self-hosted: RTX 3060 Laptop 6144 MiB,
  `-ngl 99 --n-cpu-moe 46`, 5692 MiB VRAM in use
- Context size: 65536, identical to the
  [2026-08-24 run](../2026-08-24-qwen3-coder-30b-agent-clients/result.md) so the
  two are directly comparable
- Cold-start time: not re-measured
- Prompt/output tokens: see the table — the entire point of this run
- Wall-clock time: 25 s to 2m35s per cold start, by client
- Estimated cost: none — local hardware
- Tool calls attempted/succeeded: **1 / 1** through a complete Pi agent loop
- Tests before/after: not applicable; suite not yet built
- Pass criteria met: **yes for the integration goal** — all four clients reach
  the endpoint and answer. Not a suite run
- Notes: see below

## Why this run exists

The [2026-08-24 record](../2026-08-24-qwen3-coder-30b-agent-clients/result.md)
listed two next actions: install Pi to complete the matrix, and re-measure
prompt sizes per client version because they had already moved once. Pi is now
installed and three of the four clients changed version, so both were done at
once against an unchanged serve configuration.

## Agent prompt size, all four clients

Identical trivial prompt to every client — *"Reply with exactly the word:
ready"* — so the number is the client's own scaffolding and nothing else.
Serving configuration was unchanged between clients, and each client was run
individually with the server's slot timings read immediately afterwards, so
**attribution is direct rather than inferred from ordering** as it was on
2026-08-24.

| Client | Version | Prompt tokens | Prefill | Outcome |
| --- | --- | --- | --- | --- |
| Pi | 0.84.3 | **4,953** | 25.5 s @ 194.1 tok/s | answered |
| OpenCode | 1.18.22 | **10,369** | 53.0 s @ 195.7 tok/s | answered |
| Kilo | 7.3.46 | **15,588** | 80.5 s @ 193.6 tok/s | answered |
| Hermes | 0.20.5 | **21,936** | 113.3 s @ 193.7 tok/s | answered, 2m35s wall |

Prefill throughput is flat at 193-196 tok/s across all four, which is the point:
**time to first token is set almost entirely by prompt size on this host.** The
spread between the smallest and largest client is 4.4x in tokens and 4.4x in
seconds.

Two clients also issue a small secondary request per session — OpenCode 536
tokens, Hermes 237 — most likely session-title generation. They are cheap and
are excluded from the figures above.

### What changed since 2026-08-24

| Client | Then | Now | Change |
| --- | --- | --- | --- |
| Pi | not installed | 4,953 | first measurement |
| OpenCode | 10,369 (1.18.21) | 10,369 (1.18.22) | unchanged |
| Kilo | 15,588 (7.3.46) | 15,588 (7.3.46) | unchanged, same version |
| Hermes | 13,238 (0.10.0) | **21,936** (0.20.5) | **+66%** |

Hermes grew by 8,698 tokens across ten minor versions, adding 44 seconds to
every cold start on this host. That single change reorders the table: on
2026-08-24 Kilo shipped the largest prompt, and it now ships the second
largest without having changed at all.

This is the concrete case for the rule the previous record proposed — that a
prompt-size figure is only meaningful with a client version attached. Two of
four clients were stable across the interval and one moved 66%, which is not
predictable from the version numbers alone.

### Pi is the smallest, but not as small as the Ryzen record implies

Pi ships 4,953 tokens at 0.84.3 against the **1,370** recorded for 0.84.2 on
the [Ryzen host](../2026-08-21-gemma-4-e4b-cpu/result.md) — 3.6x larger. Pi
remains by a wide margin the cheapest client to cold-start here, and the Ryzen
record's central claim still holds: it is narrower, not better engineered.

But the 1,370 figure should not be quoted for current Pi. The two measurements
differ in patch version and in host, and this run did not isolate which
accounts for the growth. Anyone reproducing the Ryzen result on current Pi
should expect roughly 3.6x the prefill cost that record describes.

### The ordering the Ryzen record found is restored, with a caveat

Pi smallest, Hermes largest, as on the Ryzen host. That ordering was inverted
in the 2026-08-24 run only because Hermes was two months behind. The underlying
observation — that agents designed for hosted endpoints spend prompt budget on
tool breadth because prefill is nearly free there — survives every measurement
this repository has taken.

## A complete agent loop through Pi

The repository's reference tool-call probe, against a `calc.py` whose `add`
returns `a + b + 1` rather than the obvious `a + b`:

```text
$ pi -p --provider local --model qwen3-coder-30b --no-session \
    "Read calc.py and tell me what the add function returns. Use your read tool."

Based on the code I read from calc.py, the `add` function takes two parameters
`a` and `b`, and returns the sum of `a`, `b`, and 1 (i.e., `a + b + 1`).
```

Correct, and reached only by actually reading the file. Pi now joins OpenCode
in closing a full loop on this host.

Server-side the two turns prefilled only 22 and 61 tokens, because
`llama-server`'s slot cache still held Pi's system prompt from the preceding
run. A genuinely cold invocation pays the full 25.5 s first.

### Kilo's unprompted tool call did not reproduce

On 2026-08-24, asked only to reply with one word, Kilo invoked a `kilo-config`
skill and appended a paragraph about Kilo configuration. The identical command
on the identical Kilo version this time returned `ready` and nothing else.

The behavior is therefore **non-deterministic**, not a reliable property of
Kilo's `code` agent. The previous record should be read as one observation
rather than a characterization, and any claim about tool-set breadth causing
spurious calls needs repeated trials before it is stated as a finding.

## Hermes 0.20.5 restores user-defined providers

The [Hermes integration page](../../integrations/hermes/) documented a profile
workaround because 0.10.0 made `--provider` a fixed enum with no `custom:`
form. On 0.20.5 the flag accepts *"Built-in or a user-defined name from
`providers:` in config.yaml"*, so the local endpoint is selected directly:

```bash
hermes chat -q "Reply with exactly the word: ready" \
  --provider local -m qwen3-coder-30b
```

This is simpler than the profile and leaves the configured default untouched
just as well. The profile route still works and remains preferable when an
isolated history, `.env`, or SOUL.md is wanted; it is no longer required merely
to reach a local endpoint.

Three CLI shapes across three versions — `--provider custom:<name>`, then a
closed enum, then user-defined names again — is a strong argument for checking
`--help` against the installed build rather than trusting any record here.

## Deviations from `benchmarks/README.md`

Only step 1, endpoint health and model discovery, plus the `calc.py` tool-call
probe. Steps 2 through 6 were not attempted; the suite still does not exist.

Prefill seconds are specific to this host and serve configuration. Prompt
**token counts** are client-side and portable; the seconds are not.

The GPU was shared with an unrelated job for part of this session. All figures
above were taken after it exited, against a server started fresh on an
otherwise idle GPU.

## Next actions

1. Build the suite. Every client in the repository now reaches the endpoint and
   two of them close agent loops, so `benchmarks/coding-agent-v1/` is the only
   thing standing between this host and a real comparison. This is Phase 2 and
   it has been the blocker in four consecutive records.
2. Re-run the Kilo spurious-call observation several times before treating it
   as a finding, or drop it.
3. Attach client versions to every prompt-size figure already in the
   repository, including the Ryzen records, now that one client has moved 66%
   in two months.
4. Isolate whether Pi's 1,370 → 4,953 growth is version or host. Running
   0.84.3 against the Ryzen endpoint would settle it.
