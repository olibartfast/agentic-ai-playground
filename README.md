# AI Code Assistant Playground

This repository serves as a playground and testing ground for evaluating and comparing various AI-powered code assistants.

## Purpose

* **Experiment** with AI coding tools, including IDE extensions, CLI-based assistants, and autonomous agents.
* **Compare** cloud-based assistants (e.g., GitHub Copilot, Google AI Studio) with locally hosted models (e.g., via Ollama, Hugging Face Transformers) and agent-based tools (e.g., aider, SmolAgents).
* **Evaluate** setup complexity, resource usage, code quality, and feature sets (e.g., completion, refactoring, task automation).
* **Document** configurations, hardware requirements, and observations to guide developers in selecting tools.
* **Explore** AI agents in coding, such as autonomous task execution and multi-tool integration, to highlight their role in modern workflows.

## Assistants & Agents (Front-Ends)

This section lists the AI code assistants and agents under evaluation, categorized by their interface (IDE plugins, CLI tools, or standalone agents). Assistants provide suggestions or completions, while agents can autonomously execute multi-step tasks.

| Tool                           | Type                  | Description                                                                                                                                                     | Links                                                                                                                                                                                                 |
| ------------------------------ | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Continue.dev**               | IDE Plugin            | Open-source IDE extension for local and cloud models, supporting VS Code and JetBrains.                                                                         | [Website](https://continue.dev/), [GitHub](https://github.com/continuedev/continue)                                                                                                                   |
| **GitHub Copilot**             | IDE Plugin            | Cloud-based assistant with enhanced context awareness and multi-language support.                                                                               | [Website](https://github.com/features/copilot)                                                                                                                                                        |
| **Windsurf(formerly Codeium)** | IDE Plugin            | Cloud/local hybrid for code suggestions, with improved local model support.                                                                                     | [Website](https://codeium.com/)                                                                                                                                                                       |
| **Tabnine**                    | IDE Plugin            | AI-powered completion with local and cloud model options, emphasizing privacy.                                                                                  | [Website](https://www.tabnine.com/)                                                                                                                                                                   |
| **Amazon Q Developer**         | IDE Plugin            | AWS’s assistant for coding, debugging, and cloud integration.                                                                                                   | [Website](https://aws.amazon.com/q/developer/)                                                                                                                                                        |
| **Cody (Sourcegraph)**         | IDE Plugin            | Context-aware assistant leveraging project-wide codebases for precise suggestions.                                                                              | [Website](https://sourcegraph.com/cody)                                                                                                                                                               |
| **Cursor**                     | IDE                   | AI-native IDE with advanced code generation and real-time collaboration features.                                                                               | [Website](https://cursor.sh/)                                                                                                                                                                         |
| **Refact.ai**                  | IDE Plugin/CLI        | Open-source assistant for code completion, refactoring, and automation, with self-hosted options. Supports 25+ languages and integrates with VS Code/JetBrains. | [Website](https://refact.ai/), [GitHub](https://github.com/smallcloudai/refact)                                                                                                                       |
| **DeepSeek Coder**             | IDE Plugin/API        | AI assistant leveraging DeepSeek’s code-focused models for completion and generation, with API and local model support.                                         | [GitHub](https://github.com/deepseek-ai/DeepSeek-Coder)                                                                                                                                               |
| **Google AI Studio**           | Browser-Based IDE     | Cloud-based IDE for prototyping with Gemini models, supporting code generation, completion, and multimodal inputs.                                              | [Website](https://aistudio.google.com/), [Gemini API Docs](https://ai.google.dev/)                                                                                                                    |
| **SmolAgents (Hugging Face)**  | CLI Agent             | Lightweight, task-driven AI agent framework for coding tasks like refactoring and testing, built on Hugging Face models.                                        | [GitHub](https://github.com/huggingface/smolagents), [Course](https://learn.deeplearning.ai/courses/building-code-agents-with-hugging-face-smolagents)                                                |
| **aider**                      | CLI Agent             | Autonomous coding agent for editing codebases, with improved multi-file handling.                                                                               | [GitHub](https://github.com/Aider-AI/aider)                                                                                                                                                           |
| **OpenHands**                  | Agent                 | Open-source agent (formerly OpenDevin) for complex software development tasks, integrating with Git and Docker.                                                 | [GitHub](https://github.com/All-Hands-AI/OpenHands)                                                                                                                                                   |
| **JetBrains AI Assistant**     | IDE Plugin            | AI-powered assistant integrated into JetBrains IDEs (e.g., CLion) offering intelligent code completion, chat, doc/test generation.                              | [Plugin](https://plugins.jetbrains.com/plugin/22282-jetbrains-ai-assistant), [Docs](https://www.jetbrains.com/help/clion/ai-assistant-in-jetbrains-ides.html)                                         |
| **ADK Sample Agents**          | Multi-Agent Framework | Sample multi-agent applications using Google’s Agent Development Kit (ADK) for Python and Java.                                                                 | [Samples Repo](https://github.com/google/adk-samples), [Docs](https://google.github.io/adk-docs/), [Python SDK](https://github.com/google/adk-python), [Java SDK](https://github.com/google/adk-java) |

**Note on Agents:**
AI agents like aider, OpenHands, Refact.ai’s AI Agent, Hugging Face’s SmolAgents, and ADK-based sample agents differ from traditional assistants by autonomously handling multi-step tasks (e.g., scaffolding a project, refactoring a codebase, or automating CI/CD pipelines). These are evaluated for their ability to execute complex workflows, integrate with tools (e.g., Git, Docker), and manage multi-file contexts.

## Local Model Backends & Setups

These are the platforms used to run local LLMs, enabling privacy-focused or offline coding assistance.

| Backend                       | Description                                                                                               | Links                                                                                                      |
| ----------------------------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Ollama**                    | Lightweight LLM runner for local models, with enhanced GPU support.                                       | [ollama.com](https://ollama.com/)                                                                          |
| **LM Studio**                 | GUI-based platform for running LLMs, with improved model quantization.                                    | [lmstudio.ai](https://lmstudio.ai/)                                                                        |
| **GPT4All**                   | Open-source LLM runner with an expanded model hub.                                                        | [gpt4all.io](https://gpt4all.io/)                                                                          |
| **Jan**                       | Local AI platform for coding and chat, with better multi-model support.                                   | [jan.ai](https://jan.ai/)                                                                                  |
| **llama.cpp**                 | High-performance LLM inference engine, optimized for low-resource devices.                                | [GitHub](https://github.com/ggerganov/llama.cpp)                                                           |
| **Refact Hosting**            | Self-hosted backend for Refact.ai, supporting fine-tuned models on private codebases.                     | [Website](https://docs.refact.ai/guides/version-specific/self-hosted/)                                     |
| **Hugging Face Transformers** | Framework for running and fine-tuning code-focused LLMs locally, compatible with Hugging Face Hub models. | [Website](https://huggingface.co/docs/transformers), [GitHub](https://github.com/huggingface/transformers) |

**Local Models Tested (Examples):**

* `codestral` (Mistral-based, optimized for code)
* `codellama` (Meta AI’s code-focused model)
* `deepseek-coder` (e.g., DeepSeek-Coder-6.7B, DeepSeek-R-33B)
* `starcoder2` (BigCode’s updated model)
* `gemma` (Google’s lightweight code model, e.g., CodeGemma)

## Repository Structure

```
├── codeium/
│   └── notes.md
├── continue_dev/
│   ├── ollama_tests/
│   ├── lm_studio_tests/
│   ├── config_examples/
│   └── notes.md
├── github_copilot/
│   └── notes.md
├── refact/
│   ├── self_hosted_tests/
│   ├── plugin_tests/
│   ├── config_examples/
│   └── notes.md
├── deepseek_coder/
│   ├── api_tests/
│   ├── local_tests/
│   ├── config_examples/
│   └── notes.md
├── huggingface/
│   ├── smolagents_tests/
│   ├── transformers_tests/
│   ├── config_examples/
│   └── notes.md
├── google_ai_studio/
│   ├── prompt_tests/
│   ├── api_tests/
│   ├── starter_app_tests/
│   ├── config_examples/
│   └── notes.md
├── jetbrains_ai_assistant/
│   ├── clion_tests/
│   ├── config_examples/
│   └── notes.md
├── adk_samples/
│   ├── python/
│   ├── java/
│   └── notes.md
```

## Testing Workflow

* **Setup & Configuration**
* **Resource Usage**
* **Performance**
* **Code Completion**
* **Code Generation**
* **Refactoring & Debugging**
* **Chat & Explanation**
* **Context Awareness**
* **Automation (Agents)**

## Resources

### General AI Coding

* [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
* [Ollama Getting Started](https://ollama.com/docs)
* [Refact.ai Documentation](https://docs.refact.ai/)
* [DeepSeek Coder Documentation](https://coder.deepseek.com/docs)
* [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers)
* [Google AI Studio Quickstart](https://ai.google.dev/)
* [Gemini API Docs](https://ai.google.dev/)

### AI Agents

* [Microsoft AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners)
* [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction)
* [Building Code Agents with SmolAgents](https://learn.deeplearning.ai/courses/building-code-agents-with-hugging-face-smolagents)
* [AutoGen](https://github.com/microsoft/autogen)
* [CrewAI](https://github.com/joaomdmoura/crewAI)
* [LangChain Agents](https://python.langchain.com/v0.1/docs/modules/agents/)
* [Refact.ai AI Agent Guide](https://docs.refact.ai/ai-agent/)
* [ADK Sample Agents](https://github.com/google/adk-samples)

