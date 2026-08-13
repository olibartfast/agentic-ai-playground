# vLLM server

Use the launch flags from the selected checkpoint's current model card. A
minimal connectivity template is:

```bash
vllm serve '<org>/<model>' \
  --host 127.0.0.1 \
  --port 8000 \
  --tensor-parallel-size '<gpu-count>' \
  --api-key "$MODEL_API_KEY" \
  --trust-remote-code
```

The command is not a model-specific production recipe. Confirm precision,
parsers, distributed backend, and tensor-parallel support before launch.

