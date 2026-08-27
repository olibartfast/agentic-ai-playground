# DeepSeek Harness (`dsh`)

[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) is an
open-source agent harness from DeepSeek AI. It is a Web UI and CLI agent, not a
model, and it is the client layer of this repository's routing model rather than
a model source.

Status in this playground: **measured once, on one host.** The
[2026-08-27 run](../../benchmarks/2026-08-27-dsh-agent-client/result.md)
reached a self-hosted llama-server endpoint with `dsh` **0.1.1-rc.2**, recorded
its prompt size against the four clients already in the matrix, and closed a
full tool-call loop.

What that run establishes, and nothing more:

| | |
| --- | --- |
| Prompt size | **10,475 tokens** — second of five, tied with OpenCode, ~2.1x Pi |
| Requests per invocation | **two** — a 123-token preliminary call, then the turn |
| Tool calls | **1 / 1**, the reference `calc.py` probe, loop closed |
| Version under test | `0.1.1-rc.2`, installed with `npm install -g @deepseek-ai/dsh` |

Everything *else* below is still read from the upstream repository and
documentation on 2026-08-23 at tag `dsh-v0.1.1-rc.2`, and is unverified here —
each such section says so. Upstream states that the project is a developer
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
  independently — if the prompt size can be measured first. **It now is: 10,475
  tokens, second of five and roughly 2.1x Pi.** So the premise holds in the
  direction that matters — the seam exists and prompt assembly *can* be swapped
  — but the shipped default is not itself a saving. Varying it is work still to
  be done, not a property `dsh` arrives with.
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

The 2026-08-27 run installed globally instead, so that the version under test is
pinned in the record rather than resolved fresh per invocation — prefer this for
anything that produces a benchmark number:

```bash
npm install -g @deepseek-ai/dsh   # 456 packages, 45 s; gave 0.1.1-rc.2
dsh --version
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

The 2026-08-27 run used exactly that shape with the endpoint's real alias and
window substituted, and the endpoint answered on the first attempt:

```yaml
llm-pi-ai:
  providers:
    local:
      apiKeyEnv: MODEL_API_KEY
      api: openai-completions
      baseURL: http://127.0.0.1:8080/v1
      defaultContextWindow: 65536      # the server's --ctx-size
      compat:
        supportsDeveloperRole: false
        maxTokensField: max_tokens
      models:
        - id: qwen3-coder-30b          # llama.cpp's --alias
          contextWindow: 65536

agent-default-model:
  provider: local
  model: qwen3-coder-30b
```

`MODEL_API_KEY` was set to `local`. llama-server ignores the value, but the
client refuses an unset one.

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

**Neither switch has been shown to be necessary against llama-server.** The
2026-08-27 run set both pre-emptively from this table and the endpoint answered
first try, so no failing request was ever observed and no switch was ever
isolated. The table above remains upstream's claim about symptoms, not this
repository's finding. Establishing which — if either — llama-server actually
needs means dropping them one at a time against a live endpoint, which no run
here has done.

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

### One invocation is two requests

Measured on 2026-08-27, a single `dsh --profile headless` invocation reached the
server **twice**, where Pi reached it once:

| Server task | Prompt tokens | Time | What it is |
| --- | --- | --- | --- |
| 6 | 123 | 2.39 s | a short preliminary call |
| 8 | 10,475 | 52.39 s | the agent turn |

This does not contradict the contract above — the second call is a separate
request, not an addition to the turn's prefix — but the contract does not
mention it either. **Budget an invocation at 10,598 prompt tokens across two
round trips, not the 10,475 headline.** On this host the extra call is noise
against a 52 s prefill; on a fast endpoint, or anywhere per-request latency
dominates, it is the larger of the two effects.

What the 123-token call *is* was not identifiable from server-side logs alone.
Upstream's `core/system-prompt` and session plugins are where to look, and
whether it can be disabled is unknown.

Note the cold-start caveat recorded for [OpenCode](../opencode/): on a slow
endpoint each one-shot invocation re-pays the full system-prompt prefill, while
an interactive session reuses the server's slot cache. Whichever path a
benchmark uses must be stated in its result record.

## Before this is usable as evidence

The first two items on this list are now answered by the
[2026-08-27 run](../../benchmarks/2026-08-27-dsh-agent-client/result.md); the
rest are not.

1. ~~**System prompt size.**~~ **Measured: 10,475 tokens**, server-side, on the
   trivial `ready` prompt — second of five clients and effectively tied with
   OpenCode's 10,369. `dsh` was not found to expose a count of its own the way
   `hermes prompt-size` does, so this is the server's number, read from
   `llama-server`'s slot timings. One measurement, one host, one version.
2. ~~**Tool-call behavior.**~~ **Loop closes, 1 / 1.** The reference `calc.py`
   probe returned `a + b + 1`, which is reachable only by actually reading the
   file, across two model turns. `dsh` joins Pi and OpenCode in closing a full
   loop on this host.
3. **Context-window override — still unmeasured.** The 2026-08-27 run set
   `defaultContextWindow` correctly from the start, so the 262,144-token route
   default was never exercised and its failure mode is still unobserved. This
   is *less* tested than it looks: getting it right once is not evidence about
   what getting it wrong does.
4. **Preview churn — standing.** The version is `0.1.1-rc`, and upstream warns
   in capitals about breaking changes. The measured figures above are pinned to
   `0.1.1-rc.2` and should be re-measured on any bump rather than carried
   forward.

Also unmeasured, and worth adding to this list rather than assuming:

5. **Whether either `compat` switch is required.** Both were set pre-emptively
   and never isolated — see the request-shape section above.
6. **Decode.** Every figure here is prefill-bound. No decode-rate comparison
   between `dsh` and any other client has been attempted.
7. **Quality.** Nothing measured here says whether `dsh` is a better or worse
   agent than the other four. It says what its scaffolding costs and that its
   loop closes.

This page is now a **working configuration** — the block under "Self-hosted
endpoint path" is the one that ran. It is not yet a characterization of `dsh`.

## Other surfaces

`dsh` ships packages for MCP, LSP, ACP, sandboxing, subagents, skills, hooks,
compaction, scheduling, and an E2B code runtime, plus a Python SDK. None has
been exercised here. Issues are disabled upstream; feedback goes through GitHub
Discussions.

[dsh-arch]: https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md
[dsh-catalog]: https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/config-catalog.md
[dsh-headless]: https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/headless/README.md
[boundaries]: ../../specs/tech-stack.md#api-and-integration-boundaries
