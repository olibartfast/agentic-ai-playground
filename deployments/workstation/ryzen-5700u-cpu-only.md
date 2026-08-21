# Ryzen 7 5700U — CPU-only llama.cpp runbook

A worked, measured example of the generic [workstation](README.md) checklist on
a laptop with no usable GPU. Reproduces an OpenAI-compatible endpoint on
loopback and connects it to OpenCode.

Results from this runbook are recorded under
[`benchmarks/`](../../benchmarks/) as
`2026-08-21-qwen2.5-coder-7b-cpu/result.md`.

## 1. Hardware baseline

Record the host before selecting a model. Measured 2026-08-21:

| Property | Value |
| --- | --- |
| CPU | AMD Ryzen 7 5700U, 8 cores / 16 threads, Zen 2 |
| Vector ISA | AVX2 only — no AVX-512, no AMX |
| GPU | Radeon Lucienne (gfx90c) iGPU, 0.5 GB aperture |
| RAM | 14.5 GB total, 9.6 GB available under a normal desktop |
| Swap | 4 GB |
| OS / kernel | Ubuntu 26.04 LTS, 7.0.0-29-generic |

Collect the same values with:

```bash
lscpu | grep -E 'Model name|^CPU\(s\)|Core\(s\)'
grep -o -m1 -E 'avx512[a-z0-9_]*' /proc/cpuinfo | sort -u   # empty = no AVX-512
free -m
lspci | grep -Ei 'vga|3d|display'
```

### Consequences

Inference is CPU-only and bound by DDR4 bandwidth, so decode speed scales as
roughly `memory bandwidth / model bytes`. Budget **model + KV cache under 8 GB**
to leave the desktop working.

vLLM and SGLang are not usable on this host. The vLLM x86 CPU backend targets
AVX-512 and loads bf16 rather than GGUF, so a 7B needs about 15 GB. The SGLang
CPU backend targets Intel AMX. ROCm does not support gfx90c. Run those backends
on rented GPUs under [`deployments/runpod`](../runpod/) instead, and do not
compare their numbers against this host.

## 2. Build llama.cpp

Packages are absent or stale; build from source. `libcurl4-openssl-dev` is
required for `-hf` downloads.

```bash
sudo apt install -y build-essential cmake git libcurl4-openssl-dev
git clone --depth 1 https://github.com/ggml-org/llama.cpp.git ~/repos/llama.cpp
cd ~/repos/llama.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON -DLLAMA_CURL=ON
cmake --build build --target llama-server llama-cli llama-bench -j "$(nproc)"
```

Verify, then export the path so tools such as `llmfit` stop hiding GGUF models
as "incompatible backend":

```bash
~/repos/llama.cpp/build/bin/llama-server --version
export LLAMA_CPP_PATH="$HOME/repos/llama.cpp/build/bin"
```

## 3. Obtain weights

Either download the GGUF:

```bash
~/repos/llama.cpp/build/bin/llama-server \
  -hf Qwen/Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M ...
```

Or reuse an existing Ollama blob and avoid a second copy on disk. Ollama stores
bare GGUF files under its blob directory:

```bash
ollama show qwen2.5-coder:7b            # confirm quantization is Q4_K_M
find /var/snap/ollama/common/models /home/"$USER"/.ollama/models \
  -name 'sha256-*' -size +1G 2>/dev/null -exec ls -la {} \;
```

Snap-packaged Ollama keeps blobs in `/var/snap/ollama/common/models/blobs/`.
They are root-owned but world-readable, so `llama-server -m` loads them
directly.

## 4. Serve

```bash
~/repos/llama.cpp/build/bin/llama-server \
  -m /var/snap/ollama/common/models/blobs/sha256-<digest> \
  --alias qwen2.5-coder-7b --jinja \
  --ctx-size 32768 --cache-type-k q8_0 --cache-type-v q8_0 \
  --flash-attn on --threads 8 --parallel 1 --cache-reuse 256 \
  --host 127.0.0.1 --port 8080
```

Flag rationale for this host:

- omit `--n-gpu-layers`; there is no GPU worth offloading to;
- `--threads 8` matches physical cores, SMT threads reduce throughput;
- `--cache-type-k/v q8_0` halves KV cache, keeping 32k context near 0.9 GB.
  This requires `--flash-attn on`: the server refuses to start otherwise with
  `quantized V cache requires flash_attn to be enabled`. Quantizing K alone
  works without it;
- `--alias` fixes the id returned by `/v1/models` so client configuration does
  not depend on the checkpoint filename;
- `--jinja` selects the model's embedded chat template, which is required for
  any tool-call parsing;
- `--parallel 1` because there is no headroom for concurrent slots;
- `--cache-reuse 256` amortizes prompt reprocessing across agent turns.

Validate:

```bash
curl -s http://127.0.0.1:8080/v1/models
curl -s http://127.0.0.1:8080/props |
  python3 -c 'import json,sys; d=json.load(sys.stdin);
print(d["default_generation_settings"]["n_ctx"])'
```

### Variant: Gemma 4 E4B QAT with MTP

Measured results for this configuration are recorded under
[`benchmarks/2026-08-21-gemma-4-e4b-cpu/`][gemma-result].

[gemma-result]: ../../benchmarks/2026-08-21-gemma-4-e4b-cpu/result.md

The second model evaluated on this host. Weights come from Hugging Face rather
than an Ollama blob, and the repository ships a Multi-Token Prediction drafter
that a recent `llama-server` discovers automatically from `-hf`, so no
`--model-draft` is passed:

```bash
~/repos/llama.cpp/build/bin/llama-server \
  -hf unsloth/gemma-4-E4B-it-qat-GGUF:UD-Q4_K_XL \
  --spec-type draft-mtp --spec-draft-n-max 4 \
  --alias gemma-4-e4b --no-mmproj --jinja \
  --ctx-size 65536 --cache-type-k q8_0 --cache-type-v q8_0 \
  --flash-attn on --threads 8 --parallel 1 --cache-reuse 256 \
  --host 127.0.0.1 --port 8080
```

Differences from the Qwen command above:

- `--no-mmproj` skips the 0.99 GB vision and audio tower, which `-hf` otherwise
  downloads and loads. It is dead weight for coding-agent work;
- `--ctx-size 65536` rather than 32768, because Hermes Agent refuses any model
  reporting less than 64,000 tokens. Gemma 4 is a 256K-context family, so the
  larger window is a real capability here rather than an overstatement — but
  every client's declared context limit must be raised to match, or prompts are
  packed and then silently cut;
- MTP accelerates generation only. Prefill is the binding cost for agent
  prompts on this host, so treat the drafter as a secondary measurement.

The model card's example passes `-fa off`. That cannot be combined with the
q8_0 V cache above; if the drafter or Gemma's sliding-window attention turns
out to need it, drop `--cache-type-v` at the same time.

Two log lines from a successful start on this host are worth reading rather
than ignoring:

```text
srv load_model: cache_reuse is not supported by this context, it will be disabled
llama_kv_cache: layer 0: sharing with layer 40. k = ..., v = ...
```

`--cache-reuse` is silently dropped. Gemma's interleaved sliding-window layers
share KV across layer pairs, and that context type does not support the reuse
path. The flag is harmless but inert, so every agent turn re-prefills its
prompt in full — on a host where prefill is already the binding cost, this
removes the one mitigation that made multi-turn agent loops tolerable with
Qwen. Measure turn two, not just turn one.

`Gemma4Assistant requires ctx_other to be set` appears as an error line during
startup, followed by `[spec] failed to measure draft model memory`. Both are
emitted during memory fitting and are not fatal; the drafter loads afterwards.
Do not confuse them with the V-cache failure, which is fatal and exits.

## 5. Connect OpenCode

Add a provider to `~/.config/opencode/opencode.json`. The model key must equal
the `--alias` value. See
[`integrations/opencode`](../../integrations/opencode/) for the template.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "local": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama-server (this laptop)",
      "options": {
        "baseURL": "http://127.0.0.1:8080/v1",
        "apiKey": "dummy"
      },
      "models": {
        "qwen2.5-coder-7b": {
          "name": "Qwen2.5-Coder 7B (laptop)",
          "limit": { "context": 32768, "output": 4096 }
        }
      }
    }
  }
}
```

`apiKey` is required by the client but unchecked, because the server was started
without `--api-key`. Restart OpenCode; configuration is read at startup only.

## 6. Shut down

```bash
pkill -f 'llama-server.*--port 8080'
```

## Known issues on this host

**Tool calls do not parse with Qwen2.5-Coder-7B Q4_K_M.** The correct official
Qwen2.5 tool template loads and asks for `<tool_call>{...}</tool_call>`, but the
model emits its own XML instead. Reproduced at `temperature: 0`, with `--jinja`,
and independently through Ollama, so it is a model limitation rather than a
server setting. Agent loops in OpenCode and Kilo Code will not function; chat
and fill-in-the-middle completion do. Verify any replacement model with the
tool-call check in the result record before wiring an agent to it.

**The `llama.cpp-tools` apt package shadows the source build.** Ubuntu
`resolute/universe` ships `8681+dfsg-1`, which installs `/usr/bin/llama-server`
ahead of `~/repos/llama.cpp/build/bin` on `PATH`. It is not a drop-in
substitute: its `--spec-type` accepts only the ngram variants, so `draft-mtp`
fails with `unknown speculative decoding type without draft model`, and it
loads the portable `libggml-cpu-haswell.so` rather than a `GGML_NATIVE=ON`
build tuned for this Zen 2 part. Prefer the source build for anything measured
here, if only so results stay comparable across runs:

```bash
export PATH="$HOME/repos/llama.cpp/build/bin:$PATH"
llama-server --version   # expect: commit bb4caa7, not "(Debian)"
```

**Ollama defaults to 4096 context** when `OLLAMA_CONTEXT_LENGTH` is unset,
silently truncating longer prompts regardless of the model's advertised window.
`llama-server --ctx-size` is explicit and is the reason to prefer it here.

**Snap confinement** prevents Ollama from reading `/tmp`, so `ollama create -f`
fails there. Keep Modelfiles under `$HOME`.

**`llmfit` rankings are unreliable for model selection.** Its score is a
speed-and-fit composite, not a capability measure, and its scraped metadata
misreports parameter counts and quantizations. With `LLAMA_CPP_PATH` unset it
hides GGUF models while surfacing MLX and bitsandbytes checkpoints this host
cannot load. Useful for memory arithmetic; not for choosing a model.
