# Serving

Inference backends expose a stable OpenAI-compatible boundary to clients.

| Backend | Best fit |
| --- | --- |
| [llama.cpp](llama-cpp/) | Quantized single-GPU and local experiments |
| [vLLM](vllm/) | High-throughput GPU serving |
| [SGLang](sglang/) | Optimized and model-specific GPU serving |

All temporary remote deployments should bind privately and be reached through
an SSH tunnel. Add authentication and TLS before any public deployment.

