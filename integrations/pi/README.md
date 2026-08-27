# Pi Agent

[Pi](https://github.com/earendil-works/pi) is a CLI coding agent with
built-in `read`, `bash`, `edit`, and `write` tools. It reads provider
definitions from `~/.pi/agent/models.json` and speaks the OpenAI completions
API, so any runtime in [`serving/self-hosted/`](../../serving/self-hosted/) can
back it.

For the llama.cpp variant of this setup, including cloud and managed endpoint
options, see the [llama.cpp Pi walkthrough][llama-cpp-pi].

[llama-cpp-pi]: ../../serving/self-hosted/llama-cpp/pi-agent.md

## 1. Install

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
pi --version
```

Pi moved organisation: `@mariozechner/pi-coding-agent` is deprecated on npm
("please use @earendil-works/pi-coding-agent instead going forward"), last
published `0.73.1` on 2026-05-07, and `github.com/mariozechner/pi-coding-agent`
now returns 404. The measurements recorded on this page were taken against the
`0.73.x` line under the old package name; the current line is `0.84.x` and has
not been re-measured here.

## 2. Serve a model with Ollama

Ollama exposes an OpenAI-compatible API on port 11434 whenever the daemon runs;
no extra flag is required. Confirm the endpoint and the exact model identifier
before editing any configuration:

```bash
ollama list
curl -s http://localhost:11434/v1/models
```

The `id` field of that response is the string Pi expects — it carries the tag,
for example `qwen2.5-coder:7b`, not `qwen2.5-coder`.

## 3. Configure the provider

Add an `ollama` provider to `~/.pi/agent/models.json`, keeping any providers
already present. See [`pi.models.example.json`](pi.models.example.json).

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        { "id": "qwen2.5-coder:7b" }
      ]
    }
  }
}
```

`apiKey` must be non-empty because the OpenAI client requires the header. Ollama
ignores its value.

## 4. Verify

```bash
pi --list-models ollama
```

The model must appear with a provider column of `ollama`. Ignore the reported
context length: Pi prints its own catalog default, while Ollama truncates to the
model's `num_ctx`. Check the real value with `ollama show <model>` and override
it in a Modelfile if agent prompts are being silently cut.

## 5. Run

Pi keeps its own default provider in `~/.pi/agent/settings.json`, which the
steps above do not change. Select the local endpoint per run:

```bash
cd /your/project
pi --provider ollama --model qwen2.5-coder:7b
```

Add `-p` for a single non-interactive prompt, and `--no-session` to avoid
writing a session file while probing.

## Local llama-server (Gemma 4 E4B)

The same agent against llama.cpp instead of Ollama. Add a second provider —
providers merge by key, so `ollama` above is untouched:

```json
"local": {
  "baseUrl": "http://127.0.0.1:8080/v1",
  "api": "openai-completions",
  "apiKey": "none",
  "models": [
    { "id": "gemma-4-e4b" }
  ]
}
```

The `id` must equal the server's `--alias`, which is what `/v1/models` returns.
See the [Gemma 4 E4B serve command][gemma-serve] for the matching invocation.

```bash
pi --provider local --model gemma-4-e4b
```

Pi reports this model's context as 128K in `--list-models`. That is Pi's own
catalog default, not a value read from the endpoint; the served window is
whatever `--ctx-size` was passed.

[gemma-serve]: ../../deployments/workstation/ryzen-5700u-cpu-only.md#variant-gemma-4-e4b-qat-with-mtp

## Local llama-server (Qwen3-Coder 30B-A3B, GPU host)

A third provider alongside `ollama` and `local` above — providers merge by key.
Verified 2026-08-26 on Pi 0.84.3:

```json
"local": {
  "baseUrl": "http://127.0.0.1:8080/v1",
  "api": "openai-completions",
  "apiKey": "none",
  "models": [{ "id": "qwen3-coder-30b" }]
}
```

```bash
pi --list-models local
pi -p --provider local --model qwen3-coder-30b --no-session "your prompt"
```

The `id` must equal the server's `--alias`. `--list-models` reports 128K of
context for this model; that is Pi's catalog default, not a value read from the
endpoint. Serve command and measured throughput are in the
[i5-11400H + RTX 3060 runbook][rtx3060-runbook].

Pi closed a full agent loop against this model — correct tool selected, file
actually read, correct answer — recorded in the
[2026-08-26 result][agents-2026-08-26].

[rtx3060-runbook]: ../../deployments/workstation/i5-11400h-rtx3060.md

## Version note: the 1,370-token figure is stale

The prompt sizes quoted on this page and in the Ryzen records were measured on
Pi **0.84.2**. On **0.84.3** the same trivial prompt ships **4,953 tokens** —
3.6x larger — measured against a local GPU endpoint in the
[2026-08-26 record][agents-2026-08-26].

Pi remains the cheapest client in this repository to cold-start, by a wide
margin over OpenCode (10,369), Kilo (15,588), and Hermes (21,936). The claim
that it is *narrower* rather than better engineered is unaffected. Only the
absolute number moved, and it moved enough that reproducing the Ryzen result on
current Pi should budget roughly 3.6x the prefill that record describes.

That measurement did not isolate version from host, so treat 4,953 as "current
Pi on this host" rather than as a property of 0.84.3 everywhere.

[agents-2026-08-26]: ../../benchmarks/2026-08-26-agent-client-prompt-sizes/result.md

## Tool-calling check

Transport working is not the same as the agent loop working. Confirm the model
emits structured tool calls before trusting any result from it:

```bash
pi -p --provider ollama --model qwen2.5-coder:7b --no-session \
  "Read calc.py and tell me what the add function returns. Use your read tool."
```

A working model reads the file and answers. A model that cannot emit the
protocol wrapper prints the call as assistant text and stops on the first turn:

```text
{"name": "read", "arguments": {"path": ".../calc.py"}}
```

This is a model limitation, not a Pi or Ollama misconfiguration. Note that
`ollama show` lists `tools` under Capabilities based on the prompt template
alone; it does not indicate that the weights honor it.

Measured outcome for `qwen2.5-coder:7b` on this path: **0 of 1 tool calls
parsed** — see the [Qwen2.5-Coder-7B CPU result][qwen-result].

The same probe against `gemma-4-e4b` on llama-server **passes**: the loop
closes and Pi answers correctly in 40 s wall clock on a CPU-only laptop, of
which 25 s is prefilling Pi's 1,370-token system prompt and 5.7 s is the second
turn. See the [Gemma 4 E4B CPU result][gemma-result]. Pi is currently the only
one of the four agents in this repository that completes an agent loop on that
host, and the reason is prompt size rather than agent quality.

[gemma-result]: ../../benchmarks/2026-08-21-gemma-4-e4b-cpu/result.md

[qwen-result]: ../../benchmarks/2026-08-21-qwen2.5-coder-7b-cpu/result.md
