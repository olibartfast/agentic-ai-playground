
# Install Ollama

Download and install from [https://ollama.com/download](https://ollama.com/download):

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Start Ollama

Start the Ollama service:

```bash
ollama serve
```

In another terminal, verify that Ollama is running:

```bash
ollama -v
```

## Pull a Model

Pull a model, for example `codestral:22b` (choose a quantized version that fits in your system RAM).  
You can check for available tags [here](https://ollama.com/library/codestral/tags):

```bash
ollama pull codestral:22b
```

## Set Ollama in continue.dev

Edit your configuration file located at:

```bash
$HOME/.continue/config.yaml
```

Add the following under the `models` key:

```yaml
models:
  - name: Codestral Ollama
    provider: ollama
    model: codestral:22b
```

