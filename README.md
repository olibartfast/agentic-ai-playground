# Agentic AI Playground

An experiment workspace for comparing coding agents, model backends, and the
infrastructure that connects them.

The repository separates five concerns so that an agent can be tested against
different models without changing the serving or cloud setup:

```text
model recipe -> inference server -> OpenAI-compatible API -> coding agent
                                                            -> benchmark task
```

## Repository map

| Area | Purpose |
| --- | --- |
| [`models/`](models/) | Model-specific requirements and experiment profiles |
| [`serving/`](serving/) | llama.cpp, vLLM, SGLang, and managed API backends |
| [`clients/`](clients/) | Coding-agent configurations such as OpenCode and Hermes |
| [`cloud/`](cloud/) | Provider-neutral deployment and secure-access runbooks |
| [`benchmarks/`](benchmarks/) | Repeatable coding, tool-calling, and inference evaluations |
| [`experiments/`](experiments/) | Agent-framework examples and runnable prototypes |
| [`assistants/`](assistants/) | Notes for IDEs, extensions, and coding-agent products |

GPU kernel development and low-level inference optimization are intentionally
out of scope; this repository consumes inference runtimes and evaluates agent
systems built on top of them.

## Current model candidates

The initial comparison tracks four model profiles:

- [Muse Glimmer](models/muse-glimmer/) for a single-GPU experiment.
- [Nemotron 3.5 Lightning](models/nemotron-3.5-lightning/) pending a verified
  public model card and serving recipe.
- [DeepSeek V4 Flash](models/deepseek-v4-flash/) for multi-GPU or offloaded
  inference experiments.
- [Inkling](models/inkling/) as a large-scale serving reference rather than the
  default development backend.

Model requirements change quickly. Each profile separates verified inputs from
assumptions that must be checked before renting hardware.

## Recommended experiment flow

1. Pick a profile under [`models/`](models/).
2. Start the appropriate backend from [`serving/`](serving/).
3. Confirm `/v1/models` and `/v1/chat/completions` before involving an agent.
4. Connect OpenCode or Hermes using [`clients/`](clients/).
5. Keep a temporary remote endpoint behind an SSH tunnel.
6. Run the scenarios in [`benchmarks/`](benchmarks/) and record configuration,
   latency, tool reliability, and cost.

Start with a managed API or a single-GPU model. Move to a multi-GPU node only
after the client and benchmark loop works end to end.

## Existing notes

The original tool notes remain available while they are progressively folded
into the new taxonomy:

- CLI agents: [Aider](aider/notes.md), [Claude Code](claude_code/),
  [Codex](codex/), [ForgeCode](forgecode/), and
  [GitHub Copilot](github_copilot/notes.md).
- IDEs and extensions: [Continue](continue_dev/), [Cursor](cursor/),
  [Google Antigravity](google_antigravity/), [Trae](trae/), and
  [Windsurf](windsurf/).
- Backends and providers: [llama-server](llama-server/notes.md),
  [Ollama](ollama/notes.md), and [OpenRouter](openrouter/notes.md).
- Protocols and examples: [A2A](a2a-protocol/) and
  [LangGraph ReAct agent](ai-agents-langgraph/).

## Evaluation principles

- Use the same repository snapshot and prompt for every model.
- Record model revision, quantization, context limit, runtime, GPU, and flags.
- Test tool calls independently from text quality.
- Compare warm and cold startup separately.
- Never expose an unauthenticated inference port to the public internet.
- Stop cloud GPU instances when an experiment ends.

## Resources

- [OpenCode](https://opencode.ai/)
- [Hermes Agent](https://github.com/NousResearch/hermes-agent)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [vLLM](https://docs.vllm.ai/)
- [SGLang](https://docs.sglang.ai/)
- [Hugging Face model hub](https://huggingface.co/models)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Agent2Agent protocol](https://a2a-protocol.org/)
