# Muse Glimmer profile

Goal: establish the inexpensive single-GPU baseline for coding-agent tests.

Before launch, verify the canonical model repository, supported GGUF
quantization, chat template, context limit, and tool-call behavior. Begin with a
conservative context size and one request at a time; increase context only after
the end-to-end benchmark succeeds.

Preferred serving path: [`serving/llama-cpp`](../../serving/llama-cpp/).

