# Experiment result

- Date: 2026-08-23
- Repository and commit: agentic-ai-playground, branch `master` at `ef7d830`
- Agent and version: raw HTTP probes against `/v1/chat/completions`. **No agent
  client was involved** — see deviations
- Routing scenario: self-hosted
- Main-agent source and model: llama-server / Qwen3-Coder 30B-A3B Instruct
- Subagent source(s) and model(s): none
- Model checkpoint and revision, when self-hosted: the Ollama blob for
  `qwen3-coder:30b`,
  `/usr/share/ollama/.ollama/models/blobs/sha256-1194192cf2a187eb02722edcc3f77b11d21f537048ce04b67ccf8ba78863006a`,
  18.6 GB, pulled 2025-08-07. No upstream Hugging Face revision is recorded by
  Ollama, so this checkpoint is identified by digest only
- Quantization: Q4_K_M weights; q8_0 K and V cache
- Runtime and version, when self-hosted: **two runtimes, deliberately
  compared** — llama.cpp commit `95b8e33` built from source with CUDA
  (`GGML_NATIVE=ON`, `GGML_CUDA=ON`, `CMAKE_CUDA_ARCHITECTURES=86`, `nvcc`
  12.0.140 with gcc-12.4.0 as host compiler), and
  `ghcr.io/ggml-org/llama.cpp:server-cuda` reporting build 8953 (`434b2a1ff`)
- Deployment target: personal workstation with GPU — see the
  [i5-11400H + RTX 3060 runbook](../../deployments/workstation/i5-11400h-rtx3060.md)
- Hardware and topology, when self-hosted: Intel i5-11400H, 6 cores /
  12 threads, AVX-512 with VNNI; RTX 3060 Laptop, 6144 MiB, sm_86; 38 GB RAM,
  33 GB available; driver 580.173.02. MoE hybrid offload — attention,
  embeddings, and KV on the GPU, expert tensors in system RAM
- Context size: 32768, confirmed via `/props` on both runtimes
- Cold-start time: 28 s (source) and 33 s (Docker) from launch to `listening`,
  weights in page cache
- Prompt/output tokens: 5,532 prompt / 16 output on the throughput probe; see
  the tables below
- Wall-clock time: 20.3 s to first token on the throughput probe, tuned
  configuration
- Estimated cost: none — local hardware
- Tool calls attempted/succeeded: **2 / 2** isolated, one per runtime. **No
  agent loop was closed**
- Tests before/after: not applicable; suite not yet built
- Pass criteria met: **partially** — step 1 of `benchmarks/README.md` only.
  This is a backend and offload probe, not a suite run
- Notes: see below

## What this run establishes

Three things, all narrow:

1. The MoE hybrid offload regime the roadmap named as unmeasured now has
   numbers on this host.
2. `qwen3-coder:30b` emits well-formed tool calls when served through
   `llama-server`, contradicting what `ollama show` advertises.
3. A CUDA source build and the upstream Docker image perform equivalently here,
   which removes a reason to prefer one on speed grounds.

It establishes nothing about agent-loop behavior, and the numbers are not
comparable to the two Ryzen records. See deviations before reusing any figure.

## Measured throughput

Reported by `llama-server` slot timings, single slot, no concurrency, on an
identical 5,532-token prompt at `temperature: 0`. **One sample per row.**

| Configuration | VRAM | Prefill | Decode @ 5.5k ctx |
| --- | --- | --- | --- |
| Source, `--cpu-moe`, mmap | 3250 MiB | 199.0 tok/s | 10.9 tok/s |
| Source, `--n-cpu-moe 42`, `--load-mode none` | 5516 MiB | **272.1 tok/s** | 11.3 tok/s |
| Docker, `--n-cpu-moe 42`, `--no-mmap` | 5516 MiB | **274.5 tok/s** | 10.2 tok/s |

The probe prompt is 220 generated function definitions followed by a counting
question, produced by:

```python
prompt = 'You are reviewing a codebase. Here is context:\n' + '\n'.join(
    f'def function_{i}(alpha, beta):\n    result = alpha * {i} + beta\n    return result'
    for i in range(220))
prompt += '\n\nHow many functions are defined above? Answer with just the number.'
```

The model answered `220` — correct — on the tuned configuration. Correctness
was verified only for this one trivially checkable prompt and says nothing
about coding capability.

### Tuning the offload split is worth 37% of prefill

`--cpu-moe` keeps all 48 layers' expert tensors on the CPU and left 2.9 GB of
VRAM idle. Moving the last 6 layers' experts onto the card with
`--n-cpu-moe 42` filled VRAM to 5516 MiB and took prefill from 199 to 272
tok/s. Decode moved from 10.9 to 11.3 tok/s, which is within noise.

The gain is concentrated in prefill because prefill is compute-bound across all
expert tensors, while decode is bound by reading the ~3.3B active parameters
per token from DDR4. Moving 6 of 48 layers off the memory path is a 12.5%
reduction in that read, and the measurement does not clearly resolve it.

`--n-cpu-moe 42` is a fit, not a constant. It is invalidated by any change to
model, quantization, context size, or KV cache type.

### Decode depends on KV depth, so quote it with a context

Three consecutive short-prompt runs against the Docker server:

| Run | Decode | Tokens |
| --- | --- | --- |
| 1 | 13.8 tok/s | 111 |
| 2 | 13.4 tok/s | 111 |
| 3 | 13.9 tok/s | 115 |

Roughly 4% spread, and 30% faster than the ~10.2 tok/s the same server produced
once 5,532 tokens were resident. Any decode figure quoted from this record must
carry its context depth or it is not comparable to anything.

That 4% spread is also the reason the source-versus-Docker decode difference
(11.3 against 10.2) should **not** be read as real: it rests on one sample each
and is close to the observed run-to-run variation. The honest statement is that
the two runtimes were not distinguished by this experiment.

## Tool calling works, contradicting `ollama show`

The roadmap flagged that `ollama show qwen3-coder:30b` lists `completion`
without `tools`, and predicted that Ollama's template for this tag would not
produce tool calls at all. Served through `llama-server`, it does. Identical
output on both runtimes:

```json
{"finish_reason": "tool_calls",
 "tool_calls": [{"function": {"name": "get_weather",
                              "arguments": "{\"city\":\"Paris\"}"}}],
 "content": ""}
```

Correct function, correct argument, well-formed wrapper, empty `content`. The
probe is deliberately minimal — one function, ~30 prompt tokens, no agent
prompt, `temperature: 0`.

This is the third data point on the repository's recurring question, and it
resolves the same way as
[Gemma 4 E4B](../2026-08-21-gemma-4-e4b-cpu/result.md) rather than
[Qwen2.5-Coder-7B](../2026-08-21-qwen2.5-coder-7b-cpu/result.md). It also
sharpens the rule: the Qwen2.5-Coder record concluded that a missing `tools`
flag *may* reflect the bundled template rather than the weights. Here that is
confirmed directly — same weights, tool calls absent through Ollama's serving
path and present through `llama-server --jinja`. **`ollama show` describes
Ollama's template, not the model's capability, and is not evidence either way.**

Scope of the claim: this establishes that the weights emit a syntactically
valid tool call. It does **not** establish that an agent loop closes. The Gemma
record needed a separate end-to-end run to show that, and no equivalent run was
performed here.

## Source build against Docker image

Both were configured identically and produced statistically indistinguishable
throughput and identical VRAM use. The differences that matter are operational,
not performance:

| | Source build | Docker image |
| --- | --- | --- |
| Setup | ~13 min compile | 3.61 GB pull |
| Version | any commit; `95b8e33` here | build 8953, trails master |
| CPU backend | `-march=native` | `libggml-cpu-icelake.so` |
| mmap override flag | `--load-mode none` | `--no-mmap` only |

One assumption was tested and failed: the image does **not** ship a
lowest-common-denominator CPU backend. llama.cpp builds several CPU variants
and dispatches at runtime, and on this host the container selects the Icelake
variant, which carries AVX-512 and VNNI. Since expert tensors run on the CPU in
this regime, a crippled CPU backend would have shown up plainly in prefill. It
did not.

The practical consequence is that `GGML_NATIVE=ON` is not the reason to build
from source on a host like this one. Version control over the binary is — the
image lacked `--load-mode`, which is exactly the flag the server's own startup
warning recommends.

## Serving configuration

```bash
BLOB=/usr/share/ollama/.ollama/models/blobs/sha256-1194192cf2a187eb02722edcc3f77b11d21f537048ce04b67ccf8ba78863006a
~/repos/llama.cpp/build/bin/llama-server \
  -m "$BLOB" \
  --alias qwen3-coder-30b \
  -ngl 99 --n-cpu-moe 42 --load-mode none \
  --ctx-size 32768 --cache-type-k q8_0 --cache-type-v q8_0 \
  --flash-attn on --threads 6 --parallel 1 --cache-reuse 256 \
  --host 127.0.0.1 --port 8080
```

The Docker equivalent differs only in `--no-mmap` for `--load-mode none`, the
`/models` bind mount, and `--host 0.0.0.0` inside the container's namespace
with the published port bound to `127.0.0.1`. Both are recorded in the
[runbook](../../deployments/workstation/i5-11400h-rtx3060.md).

Two flag facts confirmed on this host:

- `--jinja` did not need to be passed; it is the default in current builds. It
  was required explicitly on the Ryzen host, so older command lines carry it
  redundantly.
- `failed to fit params to free device memory: n_gpu_layers already set by user
  to 99, abort` is emitted at startup on both runtimes. It is llama.cpp
  declining to auto-fit because `-ngl` was explicit, not an allocation failure.

## Deviations from `benchmarks/README.md`

Only step 1, endpoint health and model discovery, was executed. Steps 2 through
6 were not attempted. No agent client was configured, connected, or measured.

**These numbers are not comparable to the two Ryzen records**, and the
comparison is tempting enough to state the reasons explicitly:

- different model — Qwen3-Coder 30B-A3B here, against Gemma 4 E4B and
  Qwen2.5-Coder-7B there;
- different prompt — the 5,532-token synthetic above, against those runs'
  agent system prompts;
- different backend regime — CUDA hybrid offload, against CPU-only.

Three variables move at once. The observation that prefill here (272 tok/s) is
roughly 5x the Ryzen host's Gemma figure (~49 tok/s) is therefore **indicative
of the host change only in the loosest sense** and must not be reported as a
speedup measurement. A clean comparison requires running one identical model
and prompt on both hosts, which this experiment did not do.

## Bearing on the roadmap's prefill estimate

The *Host note, 2026-08-23* projected 1,000-2,000 tok/s of GPU prefill and
predicted OpenCode's 7,876-token cold start would fall "from 161 s to seconds."

Measured prefill in the MoE hybrid regime is 272 tok/s, which would put that
cold start near 29 s. Better by roughly 5x, and not the order of magnitude the
estimate implied.

This does not falsify the estimate, because the estimate was written for a
4B-class model held entirely in VRAM — the *other* regime the same note
describes. It does establish that the two regimes have materially different
prefill characteristics, and that the prompt-size intervention is only partly
delivered by the hybrid one: in hybrid offload prefill remains bound by CPU
expert compute, which is precisely what the GPU was supposed to remove.

The full-GPU Gemma 4 E4B slot remains the configuration that would test the
roadmap's estimate as written, and it is untested on this host.

## Next actions

1. Run the same probe prompt through the full-GPU Gemma 4 E4B configuration on
   this host. That is the direct test of the roadmap's 1,000-2,000 tok/s
   estimate and the only way to separate "GPU" from "hybrid offload" in these
   numbers.
2. Close an agent loop against `qwen3-coder-30b`. Tool-call syntax is
   confirmed; loop completion is not, and the Gemma record shows the two are
   distinct results. Pi is the cheapest client to try first at 1,370 prompt
   tokens.
3. Replace single samples with `llama-bench` runs. Every throughput figure here
   is n=1 apart from the short-context decode triple, which is why the
   source-versus-Docker question could not be settled.
4. Screen `gpt-oss:20b`, already on disk at 13.8 GB and advertising both
   `tools` and `thinking`. It is the other MoE candidate for this regime and is
   unmeasured.
5. Sweep `--n-cpu-moe` rather than accepting the first fit. 42 was chosen by
   one VRAM observation; the prefill gain between 48 and 42 suggests the curve
   is worth mapping, and lower context would free VRAM for more expert layers.
