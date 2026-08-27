# OpenCode

[OpenCode](https://opencode.ai) is a CLI and TUI coding agent. It reaches any
OpenAI-compatible endpoint through the `@ai-sdk/openai-compatible` provider
package, so every runtime under
[`serving/self-hosted/`](../../serving/self-hosted/) can back it.

## Generic self-hosted endpoint

Copy [`opencode.example.json`](opencode.example.json) to the project being
evaluated, replace the model identifier with the name returned by `/v1/models`,
and export `MODEL_API_KEY`. Keep the endpoint on loopback when using the SSH
tunnel from the cloud runbook.

## Ollama on the same machine

Ollama serves an OpenAI-compatible API on port 11434 whenever the daemon runs;
no extra flag is required. Read the exact model identifier from the endpoint
rather than guessing it — it carries the tag:

```bash
curl -s http://localhost:11434/v1/models
```

Merge [`opencode.ollama.example.json`](opencode.ollama.example.json) into
`~/.config/opencode/opencode.json` for a machine-wide provider, or into the
project's `opencode.json` to scope it to one repository. Providers merge by key,
so an added block leaves existing ones intact.

```json
"ollama": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Ollama (this laptop)",
  "options": {
    "baseURL": "http://127.0.0.1:11434/v1",
    "apiKey": "ollama"
  },
  "models": {
    "qwen2.5-coder:7b": {
      "name": "Qwen2.5-Coder 7B (Ollama)",
      "limit": { "context": 32768, "output": 4096 }
    }
  }
}
```

Set `limit.context` from `ollama show <model>`, not from the model card. Ollama
truncates to its own `num_ctx`, and an overstated limit makes OpenCode pack
prompts that are silently cut before the model sees them.

`apiKey` must be present because the OpenAI client requires the header. Ollama
ignores its value.

## Local llama-server (Gemma 4 E4B)

The same schema against llama.cpp rather than Ollama. The model key must equal
the server's `--alias`:

```json
"local": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "llama-server (this laptop)",
  "options": {
    "baseURL": "http://127.0.0.1:8080/v1",
    "apiKey": "dummy"
  },
  "models": {
    "gemma-4-e4b": {
      "name": "Gemma 4 E4B QAT (laptop)",
      "limit": { "context": 65536, "output": 8192 }
    }
  }
}
```

`limit.context` must match the `--ctx-size` the server was started with, not
Gemma 4's 256K native window. The rule is the same one that applies to Ollama's
`num_ctx` above: an overstated limit is truncated silently rather than
rejected. See the [Gemma 4 E4B serve command][gemma-serve].

[gemma-serve]: ../../deployments/workstation/ryzen-5700u-cpu-only.md#variant-gemma-4-e4b-qat-with-mtp

## Local llama-server (Qwen3-Coder 30B-A3B, GPU host)

The same schema against a GPU host serving a 30B MoE with expert tensors
offloaded to system RAM. Verified 2026-08-26 on OpenCode 1.18.22:

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

Verify with a grep anchored to the provider key:

```bash
opencode models | grep '^llama\.cpp/'
```

A bare `grep llama` matches hosted models such as
`deepinfra/meta-llama/Llama-3.3-70B-Instruct-Turbo` and will look like success
even when the local provider failed to load.

Serve command and measured throughput are in the
[i5-11400H + RTX 3060 runbook][rtx3060-runbook].

[rtx3060-runbook]: ../../deployments/workstation/i5-11400h-rtx3060.md

### Prompt size is a wall-clock cost on a slow endpoint

OpenCode ships a **7,876-token** system prompt. Against a CPU-only endpoint
prefilling at roughly 49 tok/s, that is **161 seconds before the first output
token of any reply**, including a bare `Hi`. Measured on Gemma 4 E4B — see the
[result record][gemma-result].

The failure mode is easy to misread as a broken configuration: the client shows
no output, and the request is usually cancelled while the server is still
prefilling. Check the server log before changing any setting.

Prefer the TUI over `opencode run` on such endpoints. Each `run` invocation is
a cold start that re-pays the full prefill, while a TUI session keeps the
prefix in the server's slot cache and re-evaluates only the diverging tail —
observed at 10–63 tokens per follow-up turn:

```bash
opencode -m local/gemma-4-e4b
```

Compare with [Pi](../pi/), whose prompt is 3–13x smaller and which stays
interactive on the same endpoint. When benchmarking agents against a small
local model, prompt size is a confound that must be controlled for.

[gemma-result]: ../../benchmarks/2026-08-21-gemma-4-e4b-cpu/result.md

## Verify and run

```bash
opencode models | grep ollama
cd /your/project
opencode run --model ollama/qwen2.5-coder:7b "your prompt"
```

Omitting a top-level `"model"` key leaves OpenCode's default untouched, so the
local endpoint is selected per run with `--model`.

## Tool-calling check

A reachable endpoint does not mean a working agent loop. Probe it against a file
the model must actually open:

```bash
opencode run --model ollama/qwen2.5-coder:7b \
  "Read calc.py and tell me what the add function returns. Use your read tool."
```

A model that cannot emit the protocol wrapper prints the call as assistant text
and stops. Measured for `qwen2.5-coder:7b`, 80 s wall clock, no file read:

```text
{"name": "read", "arguments": {"filePath": "/path/to/calc.py", ...}}
```

Note the placeholder path. The model did not fail to resolve it so much as
copy it: OpenCode's system prompt ships few-shot examples containing that exact
string, visible with `strings ~/.opencode/bin/opencode | grep 'path/to'`. The
same weights behind [Pi Agent](../pi/), whose prompt carries no such examples,
returned the correct absolute path on this task.

Read this as a caution when evaluating small local models here: a richer agent
prompt gives a pattern-matching model more to imitate, so output differences
between agents may reflect prompt design rather than model capability. See the
[Qwen2.5-Coder-7B CPU result][qwen-result] for the full finding across four
parsers.

[qwen-result]: ../../benchmarks/2026-08-21-qwen2.5-coder-7b-cpu/result.md
