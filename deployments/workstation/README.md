# Personal workstation

Use a workstation when the selected model and context fit available GPU VRAM
and system RAM. Record GPU model, VRAM, RAM, storage, driver, runtime version,
quantization, and measured memory use.

Bind the endpoint to loopback unless another machine must connect. If LAN access
is required, add authentication and restrict it with the host firewall.

## Worked examples

- [Ryzen 7 5700U, CPU-only](ryzen-5700u-cpu-only.md) — llama.cpp built from
  source, no GPU, connected to OpenCode.
- [Intel i5-11400H + RTX 3060 Laptop](i5-11400h-rtx3060.md) — llama.cpp with
  CUDA, via both a source build and the upstream Docker image, running a
  30B MoE with expert tensors offloaded to system RAM.
