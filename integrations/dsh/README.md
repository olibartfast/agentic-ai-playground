# DeepSeek Harness (`dsh`)

[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) is an
open-source agent harness from DeepSeek AI. It is a Web UI and CLI agent, not a
model, and it is the client layer of this repository's routing model rather than
a model source.

Status in this playground: **candidate, nothing measured.** Everything below is
read from the upstream repository and documentation on 2026-08-23 at tag
`dsh-v0.1.1-rc.2`. No endpoint, tool call, prompt size, or benchmark result on
this hardware is claimed. Upstream states that the project is a developer
preview with compatibility-breaking changes expected, so re-read the sources
before relying on any field name here.

## Why it is tracked here

Every other CLI agent in this directory is a fixed program that is pointed at an
endpoint. `dsh` composes itself from plugins at boot: upstream's
[architecture notes][dsh-arch]
state that the model adapter, tool registry, session log, and the agent loop
itself are plugins, with no privileged core to patch.

That matters for two open questions in this repository:

- The [replan note](../../specs/roadmap.md#replan-note-2026-08-21) found that
  agent prompt size, not agent quality, determined ranking on a CPU-only host.
  A harness whose prompt assembly is a replaceable plugin is a way to vary that
  independently — if the prompt size can be measured first.
- Phase 5 requires each compared agent to document protocol, authentication,
  model mapping, and tool limitations. `dsh` documents a custom
  OpenAI-compatible route with explicit request-shape switches, which is
  unusually close to what that phase asks for.

It is also DeepSeek's own harness, so expect it to be tuned for DeepSeek models
in the same way [Claude Code](../claude-code/open-models.md) is tuned for
Claude.

## Install and run

Requires Node.js. The Web UI binds loopback by default:

```bash
npx @deepseek-ai/dsh web
```

That starts the Web UI at `http://127.0.0.1:3080` and opens a browser; pass
`--no-open` to suppress that. The invoking directory is the default workspace
root, but a fresh Web UI has no workspace selected until one is added.

A source checkout needs `pnpm`:

```bash
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

## Self-hosted endpoint path

`dsh` reaches a user-operated runtime as a **custom provider** on the
`llm-pi-ai` route: Settings → Models → **Add a custom provider**, supplying a
lowercase provider ID, base URL, API protocol, credential, and at least one
model. The provider ID is permanent — sessions, defaults, and credential
references key on it — so renaming means adding a new provider and deleting the
old one.

The same route can be written directly in `$DSH_HOME/settings.yaml`. See
[`settings.example.yaml`](settings.example.yaml):

```yaml
llm-pi-ai:
  providers:
    local:
      apiKeyEnv: MODEL_API_KEY
      api: openai-completions
      baseURL: http://127.0.0.1:8080/v1
      compat:
        supportsDeveloperRole: false
        maxTokensField: max_tokens
      models:
        - id: gemma-4-e4b
```

Credentials are write-only from the UI and stored in
`$DSH_HOME/.credentials.yaml`; settings retain only a reference. `apiKeyEnv`
reads the value from the environment instead, which is the form to prefer here.
As with [OpenCode](../opencode/) and [Pi](../pi/), the model `id` must be the
string the endpoint returns — llama.cpp's `--alias`, or Ollama's tagged name —
not the model card's name.

**Model discovery** uses the OpenAI-compatible `GET /models`. Upstream's
**Fetch available models** button queries the base URL and credential currently
in the form; endpoints without that route need models entered by hand.

### Set the context window explicitly

A hand-declared model that neither its entry nor the installed catalog sizes
inherits the route's `defaultContextWindow`, which upstream's [config
catalog][dsh-catalog] documents as **262,144** and calls "a guess by
construction". `defaultMaxTokens` is 32,768 on the same footing. Set
`contextWindow` per model, or `defaultContextWindow` per route, to the
`--ctx-size` the server was actually started with.

This is the same trap recorded for [OpenCode](../opencode/) and Ollama, one
order of magnitude larger: an overstated limit lets the client pack prompts the
server truncates. Whether `dsh` truncates silently or errors has not been
tested here.

### Request shape is the thing to test first

Upstream is explicit that a reachable address with a valid key still refuses
every request when the request shape differs, because the adapter infers shape
from the endpoint URL and addresses an unrecognized host as if it were OpenAI.
Two switches account for most of it:

| Symptom | Switch |
| --- | --- |
| Gateway refuses every request | `compat.supportsDeveloperRole: false` |
| Server only knows `max_tokens` | `compat.maxTokensField: max_tokens` |
| Only reasoning models fail | `compat.supportsDeveloperRole: false` |
| Reasoning wire format differs | `compat.thinkingFormat: deepseek` |

`compat` on the route is the default for its models; a model's own `compat`
wins field by field. A key written with no value is refused rather than ignored.
Upstream notes that a switch states a claim about the endpoint rather than
checking it, which is the same caution this repository applies to the
OpenAI-compatible label generally — see [technical boundaries][boundaries].

The full switch list lives under `PiAiCompatProfile` in upstream's generated
[config catalog][dsh-catalog].

### Image input

A hand-entered model is treated as text-only, and attaching an image is refused
before sending. Declare it per model with `input: [text, image]`, or once per
route with `defaultInput`. Neither checks the endpoint.

## Headless mode

`dsh --profile headless "task"` is the non-interactive path, and the one that
matters for [`benchmarks/`](../../benchmarks/). Upstream's
[headless bundle][dsh-headless]
documents the contract:

- one fresh persisted session per invocation, submitted as an ordinary user
  message, with no interactive follow-up;
- the last non-empty assistant message is written to stdout;
- exit 0 when the final `turn/end` completed, otherwise 1, with a terminal
  error's code and message on stderr and stderr otherwise empty;
- no listening port is opened;
- the runner adds nothing to the request prefix, so it contributes no KV-cache
  prefix of its own.

Upstream's `BENCHMARK.md` points instead at the Python SDK and a `jsonrpc-agent`
minimal variant, using separate workspaces and session IDs per task.

Note the cold-start caveat recorded for [OpenCode](../opencode/): on a slow
endpoint each one-shot invocation re-pays the full system-prompt prefill, while
an interactive session reuses the server's slot cache. Whichever path a
benchmark uses must be stated in its result record.

## Before this is usable as evidence

Unmeasured here, in the order that decides whether it is worth continuing:

1. **System prompt size.** Phase 5 requires this measured and reported beside
   any result. `dsh` assembles prompt sections and tool schemas in a
   `core/system-prompt` plugin; whether it exposes a token count the way
   `hermes prompt-size` does is unknown. Measure server-side prompt tokens if it
   does not.
2. **Tool-call behavior** against a small local model, using the same probe as
   the other integrations here — a model that cannot emit the protocol wrapper
   prints the call as assistant text.
3. **Context-window override.** The 262,144-token route default above must be
   corrected for any local server, and the failure mode when it is not has not
   been observed here.
4. **Preview churn.** The version is `0.1.1-rc`, and upstream warns in capitals
   about breaking changes. Pin a version in any result record.

Do not treat this page as a working configuration until at least the first two
have a recorded run.

## Other surfaces

`dsh` ships packages for MCP, LSP, ACP, sandboxing, subagents, skills, hooks,
compaction, scheduling, and an E2B code runtime, plus a Python SDK. None has
been exercised here. Issues are disabled upstream; feedback goes through GitHub
Discussions.

[dsh-arch]: https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md
[dsh-catalog]: https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/config-catalog.md
[dsh-headless]: https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/headless/README.md
[boundaries]: ../../specs/tech-stack.md#api-and-integration-boundaries
