# Serving

Model sources expose an API boundary to agent integrations. They are grouped by
who operates the inference infrastructure, not by where the agent runs.

## Self-hosted runtimes

| Backend | Best fit |
| --- | --- |
| [llama.cpp / llama-server](self-hosted/llama-cpp/) | Quantized single-GPU experiments |
| [Ollama](self-hosted/ollama/) | Simple model management and serving |
| [LM Studio](self-hosted/lm-studio/) | Desktop-oriented model management and serving |
| [vLLM](self-hosted/vllm/) | High-throughput GPU serving |
| [SGLang](self-hosted/sglang/) | Optimized and model-specific GPU serving |

## Hosted gateways

| Backend | Best fit |
| --- | --- |
| [Anthropic API](hosted/anthropic/) | Vendor-hosted Anthropic models |
| [OpenRouter](hosted/openrouter/) | One managed API across multiple model providers |

OpenRouter belongs here because it is an inference gateway consumed by agents.
It does not run the agent itself, and it is not infrastructure for renting and
administering a GPU node.

“Self-hosted” does not mean “same machine.” Any runtime above can be deployed
on suitable infrastructure under [`deployments/`](../deployments/). From the
agent's perspective, a remote server reached through an SSH tunnel may still
appear at `127.0.0.1`.

All temporary remote deployments should bind privately and be reached through
an SSH tunnel. Add authentication and TLS before any public deployment.
