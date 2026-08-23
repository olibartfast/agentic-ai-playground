# Oh My Pi (`omp`)

[Oh My Pi](https://github.com/can1357/oh-my-pi) is a terminal coding agent:
a TUI, a one-shot mode, an SDK, an RPC surface, and an ACP surface over one
engine. MIT, TypeScript on Bun with a Rust N-API addon.

It is a fork of [Pi](../pi/), which this repository already tracks and has
already measured. That shared ancestry, not the feature list, is the reason it
is here.

Status in this playground: **candidate, nothing measured.** Everything below is
read from the upstream repository and documentation on 2026-08-23 at release
`v18.0.3`. No endpoint, tool call, prompt size, or benchmark result on this
hardware is claimed.

## Why it is tracked here

### The provider layer is shared with Pi and DeepSeek Harness

Three agents in this directory reach an endpoint through the same code
lineage. Upstream's own package manifests state it:

| Integration | Provider layer |
| --- | --- |
| [Pi](../pi/) | `@earendil-works/pi-ai` |
| [DeepSeek Harness](../dsh/) | depends on `@earendil-works/pi-ai` `^0.82.1` |
| Oh My Pi | forked as `@oh-my-pi/pi-ai` |

The consequence is practical: the `compat` block in `models.yml` here is
field-for-field the `compat` block in
[`dsh/settings.example.yaml`](../dsh/settings.example.yaml) —
`supportsStore`, `supportsDeveloperRole`, `supportsReasoningEffort`,
`maxTokensField`. A request-shape matrix measured once against the runtimes in
[`serving/self-hosted/`](../../serving/self-hosted/) is evidence for all three,
rather than three separate matrices. Divergence between forks is possible and
is itself worth recording, but the starting assumption is shared behaviour.

### It carries a tool-set lever

The [replan note](../../specs/roadmap.md#replan-note-2026-08-21) found that
agent prompt size, not agent quality, determined ranking on a CPU-only host.
That finding came from comparing four different agents, which cannot separate
"prompt size dominates" from "that agent is worse".

`omp` ships 31 built-in tools in the default namespace and a flag that pins the
active set:

```bash
omp --tools read,edit,bash,grep,glob -p "..."
```

Rarely used tools stay behind `xd://` devices rather than in the prompt. That
makes a single-harness sweep possible — same agent, same model, tool set as the
only independent variable. Pi has the same lever (`--tools`, `--exclude-tools`)
over a much smaller built-in set, so the two together span a wide range without
changing harness. Whether either flag actually moves the emitted system prompt
proportionally is exactly what the sweep would establish, and is unmeasured.

## Install

Prebuilt binaries, so there is no large dependency graph to resolve locally:

```bash
curl -fsSL https://omp.sh/install | sh   # macOS, Linux
brew install can1357/tap/omp
bun install -g @oh-my-pi/pi-coding-agent
nix run github:can1357/oh-my-pi
```

Requires Bun ≥ 1.3.14 for the npm path. Platforms with a shipped native addon
are `linux-x64`, `linux-arm64`, `darwin-x64`, `darwin-arm64`, and `win32-x64`;
x64 ships dual AVX2 and baseline binaries. Alpine/musl needs
`apk add libstdc++ libgcc` first.

## Self-hosted endpoint path

Local backends are declared providers with a `local` auth tag, which makes the
API key optional: Ollama, LM Studio, llama.cpp, vLLM, and LiteLLM. Anything
else that speaks an OpenAI-compatible `/v1/models` goes in
`~/.omp/agent/models.yml`. See
[`omp.models.example.yml`](omp.models.example.yml):

```yaml
providers:
  local:
    baseUrl: http://127.0.0.1:8080/v1
    api: openai-completions
    apiKey: $MODEL_API_KEY
    models:
      - id: gemma-4-e4b
        contextWindow: 32768
        maxTokens: 4096
```

Verify discovery, then assign the model to a role:

```bash
omp models local
```

Roles are the routing unit rather than a single default model: `default`,
`smol`, `slow`, `plan`, `commit`, `vision`, `designer`, `task`, `advisor`,
`tiny`. Set one without the picker in `~/.omp/agent/config.yml`:

```yaml
modelRoles:
  default: local/gemma-4-e4b
```

**Any benchmark record must state which role served the turn.** A run that does
not is unattributable, because `smol` and `task` can be pointed at different
models than `default` and are used for subagent fan-out.

### Context window

`contextWindow` and `maxTokens` are per-model fields and are validated as
positive when present. Typed runtime discovery can supply them instead —
`discovery.type` accepts `ollama`, `llama.cpp`, `lm-studio`,
`openai-models-list`, `proxy`, and `litellm`. Ollama discovery deliberately
uses the native `/api/tags` and `/api/show` endpoints rather than OpenAI
`/v1/models`, so it reads a served value rather than a card value.

This is the same trap recorded for [OpenCode](../opencode/), [Pi](../pi/), and
[DeepSeek Harness](../dsh/), handled one layer earlier. It is not a reason to
skip checking: LiteLLM fallback discovery is documented upstream as leaving
context and pricing unknown when management routes are unavailable, and nothing
here has been confirmed against a running server.

### Request shape for local backends

Upstream's [provider compat reference][omp-compat] already encodes local-server
behaviour that the other integrations in this directory had to discover by
running into it:

| Flag | Local-backend value | What it encodes |
| --- | --- | --- |
| `supportsNamedToolChoice` | `false` (llama.cpp, LM Studio) | object tool-pins are rejected; sends one tool plus `tool_choice: "required"` |
| `toolSchemaFlavor` | `"grammar"` | schema sanitised for grammar-constrained decoding |
| `emptyLengthFinishIsContextError` | Ollama | empty completion with `finish_reason: "length"` becomes a context-overflow error |
| `streamFirstEventTimeoutMs` | `0` | unbounded prefill, so model-load time is not a timeout |
| `replayReasoningContent` | `true` (incl. loopback URLs) | replays thinking so local chat templates rebuild `<think>` and keep KV-cache hits |
| `maxTokensField` | `"max_tokens"` for a named set | output-token field name, else `max_completion_tokens` |

`streamFirstEventTimeoutMs: 0` and `emptyLengthFinishIsContextError` are worth
noting against the CPU-only host in
[`deployments/workstation/`](../../deployments/workstation/): the first is the
long-prefill case this repository keeps hitting, and the second is the silent
truncation case.

Upstream states the same caution this repository applies to the
OpenAI-compatible label generally — a compat flag asserts a claim about the
endpoint rather than checking it. See [technical boundaries][boundaries] and
upstream's [endpoint constraints][omp-endpoint], which lists nine endpoint
families and warns that gateways may treat optional fields such as a default
`max_tokens` as routing hints.

## Non-interactive mode

`omp -p "task"` answers a single prompt and exits — the path that matters for
[`benchmarks/`](../../benchmarks/). Two other embeddings exist:
`omp --mode rpc` speaks NDJSON over stdio, and `omp acp` speaks the Agent
Client Protocol.

The cold-start caveat recorded for [OpenCode](../opencode/) applies unchanged:
each one-shot invocation re-pays the full system-prompt prefill, while an
interactive session reuses the server's slot cache. Whichever path a benchmark
uses must be stated in its result record.

## Before this is usable as evidence

Unmeasured here, in the order that decides whether it is worth continuing:

1. **System prompt size at the default tool set, and at each pinned set.**
   Phase 5 requires this measured and reported beside any result. With 31
   tools in the namespace this is expected to be large; the number, and how it
   moves under `--tools`, is the whole reason to run it.
2. **Tool-call behaviour** against a small local model, using the same probe as
   the other integrations here — a model that cannot emit the protocol wrapper
   prints the call as assistant text.
3. **Whether the shared `pi-ai` lineage holds in practice.** If one measured
   compat matrix does not transfer between `omp`, [Pi](../pi/), and
   [`dsh`](../dsh/), that divergence is the finding.
4. **Version churn.** Releases `v17.3.4` through `v18.0.3` all landed inside
   nine days. Pin an exact version in any result record; an unpinned row is
   not reproducible.

Do not treat this page as a working configuration until at least the first two
have a recorded run.

## Surfaces to keep out of a benchmark host

Several tools reach well past the workspace, and belong in an explicit decision
rather than a default:

- `computer` drives the host desktop — window enumeration, screenshots, native
  input, accessibility tree, clipboard.
- `browser` drives Puppeteer with stealth on by default, can attach to
  Electron apps over CDP, and can adopt existing Chrome tabs through a relay
  extension.
- `/collab` puts a live session on a third-party relay and returns a shareable
  link. Frames are documented as sealed client-side.
- `web_search` chains up to 23 providers, several of which are third-party
  APIs.

Upstream lists `github`, `security_scan`, `generate_image`, `tts`,
`checkpoint`, `rewind`, and the memory tools as setting-gated and off by
default. That is not the same as the four above. This repository's deployment
posture is loopback-only with no unauthenticated ports — see
[`deployments/`](../../deployments/) — and the browser, desktop, and relay
surfaces are the ones to review against it before an unattended run.

## Other surfaces

Memory backends with a local SQLite engine, MCP, LSP across 14 operations, DAP
across 28, subagents in isolated worktrees, an advisor model reviewing each
turn, and config inheritance from `.claude`, `.cursor`, `.windsurf`,
`.gemini`, `.codex`, `.cline`, `.github/copilot`, and `.vscode` on first run.
None has been exercised here.

[omp-compat]: https://github.com/can1357/oh-my-pi/blob/main/docs/provider-compat-reference.md
[omp-endpoint]: https://github.com/can1357/oh-my-pi/blob/main/docs/provider-endpoint-constraints.md
[boundaries]: ../../specs/tech-stack.md#api-and-integration-boundaries
