# Serving

Inference backends expose a stable API boundary to agent integrations. They are
grouped by who operates the inference infrastructure.

## Self-hosted runtimes

| Backend | Best fit |
| --- | --- |
| [llama.cpp / llama-server](llama-cpp/) | Quantized single-GPU and local experiments |
| [Ollama](ollama/) | Simple local model management and serving |
| [vLLM](vllm/) | High-throughput GPU serving |
| [SGLang](sglang/) | Optimized and model-specific GPU serving |

## Hosted gateways

| Backend | Best fit |
| --- | --- |
| [OpenRouter](hosted/openrouter/) | One managed API across multiple model providers |

OpenRouter belongs here because it is an inference gateway consumed by agents.
It does not run the agent itself, and it is not infrastructure for renting and
administering a GPU node.

All temporary remote deployments should bind privately and be reached through
an SSH tunnel. Add authentication and TLS before any public deployment.
