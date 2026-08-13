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

Validate locally with `curl http://127.0.0.1:8080/v1/models`. For an existing
Pi-agent walkthrough, see [`pi-agent.md`](pi-agent.md).
