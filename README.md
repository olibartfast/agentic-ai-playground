# Agentic AI Playground

An experiment workspace for comparing coding agents, model sources, and the
infrastructure that connects them.

The repository separates six concerns so that an agent can be tested against
different models without conflating the agent, endpoint, runtime, and compute
location:

```text
coding agent -> model source/API -> model
                    |
                    +-> self-hosted runtime -> workstation or rented GPU
```

Here, **self-hosted** means that you operate the model endpoint. It can run on
your personal machine or remotely on AWS, RunPod, NVIDIA Brev, or another GPU
provider. A loopback URL reached through an SSH tunnel does not imply that the
model is physically local.

## Repository map

| Area | Purpose |
| --- | --- |
| [`models/`](models/) | Model-specific requirements and experiment profiles |
| [`serving/`](serving/) | Hosted model sources and self-hosted inference runtimes |
| [`integrations/`](integrations/) | Coding agents, IDEs, extensions, and serving-layer configurations |
| [`deployments/`](deployments/) | Workstation, AWS, RunPod, Brev, and secure-access runbooks |
| [`benchmarks/`](benchmarks/) | Repeatable coding, tool-calling, and inference evaluations |
| [`experiments/`](experiments/) | Agent-framework examples and runnable prototypes |

See [Architecture and routing scenarios](docs/architecture.md) for managed,
gateway, hybrid, and fully self-hosted examples.

Project intent, technical boundaries, delivery order, and active feature
contracts live under [`specs/`](specs/). Start with the
[roadmap](specs/roadmap.md) before adding another model, runtime, integration,
or deployment recipe.

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
2. Choose a hosted source or self-hosted runtime under [`serving/`](serving/).
3. For self-hosting, choose compute under [`deployments/`](deployments/).
4. Validate the endpoint's native API contract before involving an agent.
5. Connect a coding agent using [`integrations/`](integrations/).
6. Keep a temporary remote endpoint behind an SSH tunnel.
7. Run the scenarios in [`benchmarks/`](benchmarks/) and record configuration,
   latency, tool reliability, and cost.

Start with a managed API or a single-GPU model. Move to a multi-GPU node only
after the client and benchmark loop works end to end.

## Integrations and existing notes

All coding-agent and IDE material is grouped under
[`integrations/`](integrations/), including OpenCode, Hermes, Claude Code,
Codex, Continue, Aider, Cursor, Google Antigravity, GitHub Copilot, ForgeCode,
Trae, and Windsurf.

Serving notes are grouped with their backends: [llama.cpp and
llama-server](serving/self-hosted/llama-cpp/),
[Ollama](serving/self-hosted/ollama/), and the hosted
[OpenRouter gateway](serving/hosted/openrouter/). Protocol and framework
examples remain under [A2A](a2a-protocol/) and the
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
