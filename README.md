# AI Code Assistant Playground

This repository serves as a playground and testbed for evaluating and comparing various AI-powered code assistants.

## Purpose

- **Experiment** with AI coding tools, including IDE extensions, CLI-based assistants, and autonomous agents.
- **Compare** cloud-based assistants (e.g., GitHub Copilot) with locally hosted models (e.g., via Ollama) and agent-based tools (e.g., aider).
- **Evaluate** setup complexity, resource usage, code quality, and feature sets (e.g., completion, refactoring, task automation).
- **Document** configurations, hardware requirements, and observations to guide developers in selecting tools.
- **Explore** AI agents in coding, such as autonomous task execution and multi-tool integration, to highlight their role in modern workflows.

## Assistants (Front-Ends, tentative list)

This section lists the primary AI code assistant tools (often IDE extensions or plugins) being evaluated. These are the interfaces used for interacting with the AI, whether the backend is cloud-based or local.

| Tool | Type | Description | Links |
|------|------|-------------|-------|
| **Continue.dev** | IDE Plugin | Open-source IDE extension for local and cloud models. | [Website](https://continue.dev/), [GitHub](https://github.com/continuedev/continue) |
| **GitHub Copilot** | IDE Plugin | Cloud-based assistant for code completion and chat. | [Website](https://github.com/features/copilot) |
| **Windsurf (Codeium)** | IDE Plugin | Cloud/local hybrid for code suggestions. | [Website](https://codeium.com/) |
| **Tabnine** | IDE Plugin | AI-powered completion with local model support. | [Website](https://www.tabnine.com/) |
| **Amazon Q Developer** | IDE Plugin | AWS’s assistant for coding and debugging. | [Website](https://aws.amazon.com/q/developer/) |
| **Cody (Sourcegraph)** | IDE Plugin | Context-aware assistant for project-wide coding. | [Website](https://sourcegraph.com/cody) |
| **Cursor** | IDE | AI-native IDE with advanced code generation. | [Website](https://cursor.sh/) |
| **aider** | CLI Agent | Autonomous coding agent for editing codebases. | [GitHub](https://github.com/Aider-AI/aider) |
| **OpenDevin** | Agent | Open-source agent for software development tasks. | [GitHub](https://github.com/OpenDevin/OpenDevin) |

**Note on Agents:**  
AI agents like aider and OpenDevin differ from traditional assistants by autonomously handling multi-step tasks (e.g., scaffolding a project, refactoring a codebase). These are evaluated for their ability to execute complex workflows, integrate with tools (e.g., Git, Docker), and manage multi-file contexts.

## Local Model Backends & Setups (tentative list)
These are the platforms used to run local LLMs, enabling privacy-focused or offline coding assistance.

| Backend | Description | Links |
|---------|-------------|-------|
| **Ollama** | Lightweight LLM runner for local models. | [ollama.com](https://ollama.com/) |
| **LM Studio** | GUI-based platform for running LLMs. | [lmstudio.ai](https://lmstudio.ai/) |
| **GPT4All** | Open-source LLM runner with model hub. | [gpt4all.io](https://gpt4all.io/) |
| **Jan** |  Local AI platform for coding and chat. | [jan.ai](https://jan.ai/) |
| **llama.cpp** |High-performance LLM inference engine. | [GitHub](https://github.com/ggerganov/llama.cpp) |

**Local Models Tested:**
*   (specific models locally tested, e.g., `codestral`, `codellama`, `deepseek-coder`...)

## (Planned) Repository Structure
```
...
│
├── windsurf/            # Tests and notes for Codeium (Cloud)
│   └── notes.md
│
├── continue_dev/       # Tests and notes for Continue.dev
│   ├── ollama_tests/     # Examples using Ollama backend
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
...
```

## (Planned) Testing Workflow

*   **Setup & Configuration:** Ease of installing assistants and setting up local backends (Ollama, LM Studio, etc.).
*   **Resource Usage:** Monitoring CPU, RAM, and VRAM consumption for local models.
*   **Performance:** Speed and responsiveness of suggestions/chat.
*   **Code Completion:** Quality and relevance of single/multi-line completions.
*   **Code Generation:** Creating functions, classes, tests based on prompts/comments.
*   **Refactoring & Debugging:** Usefulness of suggestions for improving or fixing code.
*   **Chat & Explanation:** Quality of interaction for explaining code or answering questions.
*   **Context Awareness:** How well the assistant uses project context (especially relevant for local models with limited context windows vs tools like Cody/Copilot).

## Resources

### General AI Coding
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)  
- [Ollama Getting Started](https://ollama.com/docs)  

### AI Agents
- [Microsoft AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners): Intro to agent concepts.  
- [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction): Practical agent workflows.  
- [AutoGen](https://github.com/microsoft/autogen): Multi-agent collaboration for coding.  
- [CrewAI](https://github.com/joaomdmoura/crewAI): Task-driven agent framework.  
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/): Custom agents for coding tasks.
