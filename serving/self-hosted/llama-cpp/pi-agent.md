# llama-server + Pi Agent

Local or cloud-hosted LLM inference via an OpenAI-compatible API, connected to the [Pi coding agent](https://github.com/earendil-works/pi).

Reference: [HuggingFace – Local Agents with llama.cpp](https://huggingface.co/docs/hub/agents-local#local-agents-with-llamacpp)

---

## 1. Install Pi

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

The older `@mariozechner/pi-coding-agent` package is deprecated on npm and its GitHub URL now returns 404. See [`integrations/pi/`](../../../integrations/pi/) for the version note.

---

## 2. Run llama-server

Choose one of the options below. All expose an OpenAI-compatible API — only the `base_url` and `api_key` differ in the Pi config.

### Option A – Local Docker (CUDA)

Requires [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

```bash
docker run --gpus all -p 8080:8080 \
  ghcr.io/ggml-org/llama.cpp:server-cuda \
  -hf <org/model-GGUF:quant> \
  --jinja \
  --host 0.0.0.0 --port 8080 \
  -ngl 99
```

Pick a model that fits in your VRAM — for a 6 GB GPU, `Q4_K_M` quants of ≤7B models work well.  
Browse compatible models: https://huggingface.co/models?apps=llama.cpp&sort=trending

### Option B – HuggingFace Serverless Inference API (managed)

No server to run. HuggingFace hosts the model.

- API base: `https://api-inference.huggingface.co/models/<org/model>/v1`
- API key: your HuggingFace token (`hf_...`) from https://huggingface.co/settings/tokens
- Free tier available; rate-limited.

### Option C – Together.ai

- API base: `https://api.together.xyz/v1`
- API key: from https://api.together.xyz/settings/api-keys
- Wide model selection, competitive pricing, no setup.

### Option D – Groq

- API base: `https://api.groq.com/openai/v1`
- API key: from https://console.groq.com/keys
- Very fast inference; free tier available.

### Option E – RunPod (self-hosted GPU cloud)

Deploy the llama.cpp server Docker image as a RunPod pod:

1. Go to https://runpod.io and create a pod with a GPU of your choice.
2. Use the template `ghcr.io/ggml-org/llama.cpp:server-cuda` as the Docker image.
3. Set the container start command:
   ```
   -hf <org/model-GGUF:quant> --jinja --host 0.0.0.0 --port 8080 -ngl 99
   ```
4. Expose port `8080`.
5. API base: `https://<pod-id>-8080.proxy.runpod.net/v1`
6. API key: any non-empty string (llama-server does not require auth by default).

---

## 3. Configure Pi

Edit `~/.pi/agent/models.json`:

```json
{
  "providers": {
    "llama-cpp": {
      "baseUrl": "<base_url from option above>",
      "api": "openai-completions",
      "apiKey": "<api_key>",
      "models": [
        {
          "id": "<model-id>"
        }
      ]
    }
  }
}
```

**`base_url` / `model-id` quick reference:**

| Option | baseUrl | model-id example |
|---|---|---|
| Local Docker | `http://localhost:8080/v1` | `ggml-org-gemma-3-4b-it-gguf` |
| HuggingFace | `https://api-inference.huggingface.co/models/<org/model>/v1` | same as HF repo name |
| Together.ai | `https://api.together.xyz/v1` | `meta-llama/Llama-3-8b-chat-hf` |
| Groq | `https://api.groq.com/openai/v1` | `llama3-8b-8192` |
| RunPod | `https://<pod-id>-8080.proxy.runpod.net/v1` | any string |

### Vision support

For vision-capable models add `"input": ["text", "image"]` to the model entry:

```json
"models": [
  {
    "id": "<model-id>",
    "input": ["text", "image"]
  }
]
```

---

## 4. Run Pi

```bash
cd /your/project
pi
```
