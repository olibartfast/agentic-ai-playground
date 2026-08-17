# Qwen3.8 27B profile

Goal: evaluate the newest Qwen open-weight release that is small enough to serve
locally, alongside the existing single-GPU baseline.

Recorded from the official model card and `QwenLM/Qwen3.8` on 2026-08-17;
re-verify before allocating hardware:

- canonical checkpoint `Qwen/Qwen3.8-27B`, released 2026-08-14, Apache-2.0;
- 27B dense parameters, not a mixture-of-experts checkpoint;
- native vision-language input (images and video), so prompts and benchmarks
  must state whether the image path is exercised;
- 262,144-token native context, longer only with YaRN scaling;
- an FP8 checkpoint and community GGUF conversions are published separately from
  the base repository, and each conversion needs its own verification.

The sibling `Qwen/Qwen3.8-2.4T-A95B` release is a frontier-scale MoE model and
is out of scope for local inference here.

Verify before writing a launch command:

- minimum runtime versions for the reasoning and tool-call parsers;
- chat template and thinking-effort controls;
- observed VRAM at the context size actually used, rather than the upstream
  reference command, which documents four-way tensor parallelism at full
  context.

Preferred serving paths:
[`serving/self-hosted/llama-cpp`](../../serving/self-hosted/llama-cpp/) for a
quantized single-GPU run, or
[`serving/self-hosted/vllm`](../../serving/self-hosted/vllm/) and
[`serving/self-hosted/sglang`](../../serving/self-hosted/sglang/) for FP8 or
full-precision serving.
