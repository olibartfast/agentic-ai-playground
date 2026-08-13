# DeepSeek V4 Flash profile

Goal: compare a larger coding/agent model against the single-GPU baseline.

Treat this as a multi-GPU or CPU-offload experiment until the chosen checkpoint
and runtime prove otherwise. Verify the official model card and serving recipe,
then record topology and observed memory rather than relying on aggregate VRAM
alone.

Preferred serving paths: [`serving/vllm`](../../serving/vllm/) or
[`serving/sglang`](../../serving/sglang/).

