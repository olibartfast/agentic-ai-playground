# Ollama

Ollama provides local model installation and an API backend used by several
agent integrations.

## Install on Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Pull and run a model

```bash
ollama run gpt-oss:20b
```

See the relevant entry under [`integrations/`](../../integrations/) for
client-specific configuration.
