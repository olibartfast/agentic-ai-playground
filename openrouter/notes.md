# Setting Up OpenRouter API Key

## 1. Create an Account on OpenRouter

- Visit [OpenRouter](https://openrouter.ai/) and sign up for a new account.

## 2. Create and Store Your API Key

- After logging in, navigate to the API section.
- Generate a new API key.
- **Important:** Store your API key securely. Do not share it publicly.

## 3. Enable OpenRouter API Key in Applications

## a. Enable on Continue.dev
Here’s a **cleaned-up, markdown-friendly version** of your OpenRouter setup instructions for Continue.dev, with improved formatting and clarity. This version uses standard Markdown (not MDX/JSX Tabs), so it will render well on GitHub, Notion, or most Markdown viewers.

[OpenRouter](https://openrouter.ai/) is a unified interface for commercial and open-source models, giving you access to the best models at the best prices.

## Steps

1. **Sign up for OpenRouter:**  
   [Create an account here](https://openrouter.ai/signup).

2. **Create your API key:**  
   Go to the [API keys page](https://openrouter.ai/keys) and generate a new key.  
   **Store your API key securely.**

3. **Choose a model:**  
   Browse the [list of supported models](https://openrouter.ai/models).

4. **Configure Continue.dev:**  
   Edit your `~/.continue/config.json` (or `config.yaml`) to include your OpenRouter model.

---

## Example Configuration

### YAML (`config.yaml`)

```yaml
models:
  - name: OpenRouter LLaMA 70 8B
    provider: openrouter
    model: meta-llama/llama-3-70b-instruct
    apiBase: https://openrouter.ai/api/v1
    apiKey: <YOUR_OPEN_ROUTER_API_KEY>
```

### JSON (`config.json`)

```json
{
  "models": [
    {
      "title": "OpenRouter LLaMA 70 8B",
      "provider": "openrouter",
      "model": "meta-llama/llama-3-70b-instruct",
      "apiBase": "https://openrouter.ai/api/v1",
      "apiKey": "<YOUR_OPEN_ROUTER_API_KEY>"
    }
  ]
}
```

---

## Advanced: Provider Preferences & Model Routing

To utilize features such as provider preferences or model routing, include parameters inside the `models[].requestOptions.extraBodyProperties` field.

**Example: Prevent prompt compression**

### YAML

```yaml
models:
  - name: Example Model
    provider: exampleProvider
    model: example-model
    requestOptions:
      extraBodyProperties:
        transforms: []
```

### JSON

```json
{
  "models": [
    {
      "title": "Example Model",
      "provider": "exampleProvider",
      "model": "example-model",
      "requestOptions": {
        "extraBodyProperties": {
          "transforms": []
        }
      }
    }
  ]
}
```

---

**Learn more about available settings in the [OpenRouter documentation](https://openrouter.ai/docs).**


## b. Enable on GitHub Copilot

GitHub Copilot now supports custom model providers, including OpenRouter and Ollama.  
You can use OpenRouter to access a wide range of models with your Copilot extension.

---

## 1. Prerequisites

- **GitHub Copilot extension** installed in your editor (VS Code, Neovim, etc.)
- **OpenRouter account** and API key ([sign up here](https://openrouter.ai/signup))


## 2. Configure Copilot to Use OpenRouter

### For VS Code

1. **Open Command Palette** (`Ctrl+Shift+P` or `Cmd+Shift+P`).
2. Search for and select:  
   `Copilot: Set Custom Model Provider`
3. Enter the following URL as the provider endpoint:

   ```
   https://openrouter.ai/api/v1
   ```

4. When prompted for an API key, paste your OpenRouter API key.

5. (Optional) **Choose a model**  
   You may be able to specify a model in the settings or via the Copilot interface.  
   Example model: `meta-llama/llama-3-70b-instruct`

---

## 4. Advanced: Set Model via Environment Variable

Some Copilot clients allow you to set the model and API key via environment variables.  
Add these to your shell profile (`.bashrc`, `.zshrc`, etc.):

```sh
export COPILOT_CUSTOM_API_URL="https://openrouter.ai/api/v1"
export COPILOT_CUSTOM_API_KEY="<YOUR_OPENROUTER_API_KEY>"
export COPILOT_CUSTOM_MODEL="meta-llama/llama-3-70b-instruct"  # Optional
```

Restart your editor after setting these.

---

## 5. Start Using Copilot

- Use Copilot as usual.  
- Your completions will now be powered by the selected OpenRouter model.

---

## Notes

- **Model selection**: You can browse available models at [OpenRouter Models](https://openrouter.ai/models).
- **API key security**: Never share your API key publicly.
- **Performance**: Model quality and speed may vary depending on your selected model.
