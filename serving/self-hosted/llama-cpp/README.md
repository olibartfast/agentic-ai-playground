# llama.cpp server

Replace the placeholders only after checking the selected model profile:

```bash
llama-server \
  -hf '<org>/<model-gguf>:<quant>' \
  --ctx-size 65536 \
  --n-gpu-layers all \
  --flash-attn on \
  --parallel 1 \
  --host 127.0.0.1 \
  --port 8080
```

## Docker

The upstream image serves the same binary and takes the same arguments, so a
working command line ports over unchanged apart from paths:

```bash
docker run -d --name llama-cuda --gpus all \
  -v '<host-gguf-dir>':/models:ro \
  -p 127.0.0.1:8080:8080 \
  ghcr.io/ggml-org/llama.cpp:server-cuda \
  -m /models/'<model.gguf>' \
  --host 0.0.0.0 --port 8080
```

Bind the published port to `127.0.0.1` as above. `--host 0.0.0.0` applies
inside the container's own network namespace and does not widen host exposure;
writing `-p 8080:8080` would.

Tags exist per backend (`server-cuda`, `server-vulkan`, `server-intel`, and a
CPU `server`). The image trails master, so check `--help` inside the container
before copying a recently added flag from a source-build command.

## Validate

Validate locally with `curl http://127.0.0.1:8080/v1/models`. For an existing
Pi-agent walkthrough, see [`pi-agent.md`](pi-agent.md). For a measured host
comparing a CUDA source build against this image, see
[`deployments/workstation/i5-11400h-rtx3060.md`](../../../deployments/workstation/i5-11400h-rtx3060.md).
