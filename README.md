# AI Code Assistant Playground

This repository serves as a personal playground and testbed for evaluating and comparing various AI-powered code assistants. The goal is to understand their strengths, weaknesses, usability, and performance across different programming languages and common development tasks, covering **both cloud-based services and locally hosted models**.

## Table of Contents

*   [Purpose](#purpose)
*   [Assistants Under Test (Front-Ends)](#assistants-under-test-front-ends)
*   [Local Model Backends & Setups](#local-model-backends--setups)
*   [Repository Structure](#repository-structure)
*   [Testing Methodology](#testing-methodology)
*   [Key Findings Summary](#key-findings-summary)
  

## Purpose

With the rapid evolution of AI in software development, numerous code assistants are available. This repository aims to provide a structured environment to:

*   Experiment with different AI coding tools (IDE extensions, plugins) hands-on.
*   Evaluate and compare cloud-based assistants (like GitHub Copilot) and assistants capable of using **locally hosted models** (like Continue.dev).
*   Assess the setup, management, and performance of various **local LLM runners** (Ollama, LM Studio, etc.).
*   Compare the quality and relevance of code suggestions from different models (cloud and local).
*   Evaluate features like code completion, generation, refactoring, debugging, and explanation across different setups.
*   Document setup processes, configurations, hardware requirements (for local models), and personal observations.

## Assistants Under Test (Front-Ends)

This section lists the primary AI code assistant tools (often IDE extensions or plugins) being evaluated. These are the interfaces used for interacting with the AI, whether the backend is cloud-based or local.

*   ✅ **Continue.dev:** [Website](https://continue.dev/) / [GitHub](https://github.com/continuedev/continue) - *Key tool for easily connecting to various local backends.*
*   ✅ **Windsurf(formerly Codeium):** [Website](https://codeium.com/) - *Primarily cloud-based.*
*   🔄 **GitHub Copilot:** [Website](https://github.com/features/copilot) - *Cloud-based (OpenAI models).*
*   🔄 **Tabnine:** [Website](https://www.tabnine.com/) - *Offers both cloud and local (self-hosted) options.*
*   🔄 **Amazon Q Developer (CodeWhisperer):** [Website](https://aws.amazon.com/q/developer/) - *Cloud-based (AWS models).*
*   📝 **Cody (Sourcegraph):** [Website](https://sourcegraph.com/cody) - *Cloud-based, context-aware.*
*   📝 **Cursor:** [Website](https://cursor.sh/) - *AI-first IDE (cloud models).*
*   📝 **Pieces for Developers:** [Website](https://pieces.app/) - *Offers local processing options.*
*   *(Add any other front-end tools you plan to test)*

**Legend:**
*   ✅ = Actively Testing / Tested
*   🔄 = In Progress / Setting Up
*   📝 = Planned / To Do

## Local Model Backends & Setups

A major part of this playground involves testing models run **locally** on personal hardware. This offers benefits like privacy, offline access, and customization. The following tools are used to run and manage these local models:

*   **Ollama:** [ollama.com](https://ollama.com/)
    *   **Type:** CLI tool & Background Server
    *   **Description:** Simplifies downloading and running various open-source LLMs (GGUF format). Provides an OpenAI-compatible API endpoint (usually `http://localhost:11434`). Very easy integration with tools like Continue.dev.
*   **LM Studio:** [lmstudio.ai](https://lmstudio.ai/)
    *   **Type:** GUI Application (Win/Mac/Linux)
    *   **Description:** User-friendly desktop app to discover, download (GGUF), and run models. Provides a built-in chat UI and an OpenAI-compatible API server (usually `http://localhost:1234`).
*   **GPT4All:** [gpt4all.io](https://gpt4all.io/)
    *   **Type:** GUI Application (Win/Mac/Linux)
    *   **Description:** Open-source, focuses on efficient CPU inference. Provides model downloads, chat UI, and an OpenAI-compatible API server.
*   **Jan:** [jan.ai](https://jan.ai/)
    *   **Type:** GUI Application (Win/Mac/Linux)
    *   **Description:** Open-source desktop app aiming for a versatile, local-first AI experience. Provides an OpenAI-compatible server.
*   **Text Generation WebUI (Oobabooga):** [GitHub](https://github.com/oobabooga/text-generation-webui)
    *   **Type:** Web Interface (Local)
    *   **Description:** Highly configurable Gradio-based UI. Supports multiple backends (llama.cpp, Transformers) and model formats. Provides an OpenAI-compatible API. More technical setup.
*   **llama.cpp:** [GitHub](https://github.com/ggerganov/llama.cpp)
    *   **Type:** Core C++ Library & CLI
    *   **Description:** Foundational engine for efficient inference (GGUF models), especially on CPU/Apple Silicon. Used by many other tools. Can run a basic server directly.
*   **Hugging Face Libraries (`transformers`, etc.):** [huggingface.co](https://huggingface.co/)
    *   **Type:** Python Libraries
    *   **Description:** Direct use of Python libraries for maximum control over model loading and inference. Requires coding and often wrapping in a custom API server (e.g., using FastAPI/Flask) for IDE integration.

**Local Models Tested:**
*   *(List specific models you are testing locally, e.g., `codellama:7b-instruct-gguf`, `starcoder2:3b`, `deepseek-coder:6.7b-base`, `Mistral-7B-Instruct-v0.2.Q5_K_M.gguf`)*

## Repository Structure

The repository is organized to keep tests and notes separate, primarily by the **front-end assistant tool** being used. Notes regarding local backend performance or setup are often found within the relevant assistant's directory (especially `continue_dev`).

```
/
├── .gitignore          # Specifies intentionally untracked files
├── LICENSE             # Project license (e.g., MIT)
├── README.md           # This file: Overview and summary
│
├── codeium/            # Tests and notes for Codeium (Cloud)
│   └── notes.md
│
├── continue_dev/       # Tests and notes for Continue.dev
│   ├── ollama_tests/     # Examples using Ollama backend
│   │   └── python_example.py
│   ├── lm_studio_tests/  # Examples using LM Studio backend
│   ├── config_examples/  # Sample config.json files
│   └── notes.md          # Observations (incl. local backend comparisons)
│
├── github_copilot/     # Tests and notes for GitHub Copilot (Cloud)
│   └── notes.md
│
└── (other_assistant_or_backend_folders...)/
    ├── ...
    └── notes.md
```

*   Each top-level directory often corresponds to one front-end AI code assistant.
*   Inside, subdirectories might hold code examples, test cases, or configurations, potentially separated by the backend used (e.g., cloud vs. Ollama vs. LM Studio).
*   A `notes.md` file within each assistant's directory contains detailed observations, setup instructions, comparisons, and findings related to that tool and the backends it was tested with.

## Testing Methodology

Evaluation involves using the assistants and backends for typical development workflows:

*   **Setup & Configuration:** Ease of installing assistants and setting up local backends (Ollama, LM Studio, etc.).
*   **Resource Usage:** Monitoring CPU, RAM, and VRAM consumption for local models.
*   **Performance:** Speed and responsiveness of suggestions/chat.
*   **Code Completion:** Quality and relevance of single/multi-line completions.
*   **Code Generation:** Creating functions, classes, tests based on prompts/comments.
*   **Refactoring & Debugging:** Usefulness of suggestions for improving or fixing code.
*   **Chat & Explanation:** Quality of interaction for explaining code or answering questions.
*   **Context Awareness:** How well the assistant uses project context (especially relevant for local models with limited context windows vs tools like Cody/Copilot).

Tests are performed in [mention your main languages, e.g., Python, JavaScript, Go] using [mention your main IDEs, e.g., VS Code, JetBrains IDEs]. Both cloud services and various local models (running via Ollama, LM Studio, etc.) connected through tools like Continue.dev are compared.

## Key Findings Summary

*(This section will evolve. Detailed notes are in the `notes.md` file within each relevant directory.)*

**Cloud Assistants:**
*   **GitHub Copilot:** [e.g., Strong general performance, good context, chat feature useful...]
*   **Codeium:** [e.g., Fast, good free tier, sometimes less accurate on complex tasks...]
*   ...

**Local Setups (via Continue.dev or similar):**
*   **Ollama:** [e.g., Very easy setup, reliable API, good model availability...]
*   **LM Studio:** [e.g., Excellent GUI for model management, stable API server...]
*   **Model Performance (Local):**
    *   `codellama:7b`: [e.g., Decent for completion, struggles with complex logic, fast on GPU...]
    *   `deepseek-coder:6.7b`: [e.g., Strong coding performance for its size, good instruction following...]
*   **General Local vs. Cloud:** [e.g., Local offers privacy but requires capable hardware; suggestion quality varies greatly by model size/type compared to top cloud models...]
