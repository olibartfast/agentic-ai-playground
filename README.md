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

| Tool                           | Type                  | Links                                                                                                                                                                                                 |
| ------------------------------ | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Trae**                       | IDE                   | [Notes](trae/notes.md), [Website](https://www.trae.ai/)                                                                                                                                               |
| **Supermaven**                 | IDE Plugin            | [Notes](supermaven/notes.md), [Website](https://supermaven.com/)                                                                                                                                      |
| **Continue.dev**               | IDE Plugin            | [Website](https://continue.dev/), [GitHub](https://github.com/continuedev/continue)                                                                                                                   |
| **GitHub Copilot**             | IDE Plugin            | [Notes](github_copilot/notes.md), [Website](https://github.com/features/copilot)                                                                                                                      |
| **Windsurf**                   | IDE Plugin            | [Website](https://codeium.com/)                                                                                                                                                                       |
| **Tabnine**                    | IDE Plugin            | [Website](https://www.tabnine.com/)                                                                                                                                                                   |
| **Amazon Q Developer**         | IDE Plugin            | [Notes](amazon_q/notes.md), [Website](https://aws.amazon.com/q/developer/)                                                                                                                            |
| **Ampcode (Sourcegraph)**      | IDE Plugin/CLI        | [Website](https://sourcegraph.com/cody)                                                                                                                                                               |
| **Cursor**                     | IDE                   | [Website](https://cursor.sh/)                                                                                                                                                                         |
| **Refact.ai**                  | IDE Plugin/CLI        | [Website](https://refact.ai/), [GitHub](https://github.com/smallcloudai/refact)                                                                                                                       |
| **DeepSeek Coder**             | IDE Plugin/API        | [GitHub](https://github.com/deepseek-ai/DeepSeek-Coder)                                                                                                                                               |
| **Google AI Studio**           | Browser-Based IDE     | [Website](https://aistudio.google.com/), [Gemini API Docs](https://ai.google.dev/)                                                                                                                    |
| **SmolAgents (Hugging Face)**  | CLI Agent             | [GitHub](https://github.com/huggingface/smolagents), [Course](https://learn.deeplearning.ai/courses/building-code-agents-with-hugging-face-smolagents)                                                |
| **aider**                      | CLI Agent             | [Notes](aider/notes.md), [GitHub](https://github.com/Aider-AI/aider)                                                                                                                                  |
| **OpenHands**                  | Agent                 | [GitHub](https://github.com/All-Hands-AI/OpenHands)                                                                                                                                                   |
| **JetBrains AI Assistant**     | IDE Plugin            | [Plugin](https://plugins.jetbrains.com/plugin/22282-jetbrains-ai-assistant), [Docs](https://www.jetbrains.com/help/clion/ai-assistant-in-jetbrains-ides.html)                                         |
| **ADK Sample Agents**          | Multi-Agent Framework | [Samples Repo](https://github.com/google/adk-samples), [Docs](https://google.github.io/adk-docs/), [Python SDK](https://github.com/google/adk-python), [Java SDK](https://github.com/google/adk-java) |
| **Claude Code**                | CLI Agent             | [Install Guide](claude_code/install.md), [GitHub](https://github.com/anthropics/anthropic-cookbook/tree/main/examples/claude-code)                                                                   |
| **Goose**                      | Desktop App/CLI Agent | [GitHub](https://github.com/block/goose), [Docs](https://block.github.io/goose/)                                                                                                                      |
| **OpenCode**                   | TUI/Desktop App/CLI   | [GitHub](https://github.com/anomalyco/opencode), [Website](https://opencode.ai)                                                                                                                       |
| **OpenClaw**                   | Personal AI Assistant | [GitHub](https://github.com/openclaw/openclaw), [Website](https://openclaw.ai)                                                                                                                        |


**Note on Agents:**  
AI agents like aider, OpenHands, Refact.ai's AI Agent, Hugging Face's SmolAgents, and ADK-based sample agents differ from traditional assistants by autonomously handling multi-step tasks (e.g., scaffolding a project, refactoring a codebase, or automating CI/CD pipelines). These are evaluated for their ability to execute complex workflows, integrate with tools (e.g., Git, Docker), and manage multi-file contexts.

## Local & Remote Model Backends

These are the platforms used to run local LLMs or access remote models, enabling privacy-focused or flexible cloud-assisted coding.

| Backend                       | Links                                                                                                      |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Ollama**                    | [ollama.com](https://ollama.com/)                                                                          |
| **LM Studio**                 | [lmstudio.ai](https://lmstudio.ai/)                                                                        |
| **GPT4All**                   | [gpt4all.io](https://gpt4all.io/)                                                                          |
| **Jan**                       | [jan.ai](https://jan.ai/)                                                                                  |
| **llama.cpp**                 | [GitHub](https://github.com/ggerganov/llama.cpp)                                                           |
| **Refact Hosting**            | [Website](https://docs.refact.ai/guides/version-specific/self-hosted/)                                     |
| **Hugging Face Transformers** | [Website](https://huggingface.co/docs/transformers), [GitHub](https://github.com/huggingface/transformers) |
| **OpenRouter**                | [openrouter.ai](https://openrouter.ai), [Docs](https://openrouter.ai/docs)                                 |


## Resources

### General AI Coding

* [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
* [Ollama Getting Started](https://ollama.com/docs)
* [Refact.ai Documentation](https://docs.refact.ai/)
* [DeepSeek Coder Documentation](https://coder.deepseek.com/docs)
* [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers)
* [Google AI Studio Quickstart](https://ai.google.dev/)
* [Gemini API Docs](https://ai.google.dev/)
* [OpenRouter Docs](https://openrouter.ai/docs)

### AI Agents

* [Microsoft AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners)
* [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction)
* [Building Code Agents with SmolAgents](https://learn.deeplearning.ai/courses/building-code-agents-with-hugging-face-smolagents)
* [Gemini CLI: Code and Create with an Open Source Agent](https://learn.deeplearning.ai/courses/gemini-cli-code-and-create-with-an-open-source-agent/information)
* [NVIDIA NAT: Making Agents Reliable](https://www.deeplearning.ai/short-courses/nvidia-nat-making-agents-reliable/)
* [Agentic AI](https://learn.deeplearning.ai/courses/agentic-ai/information)
* [Claude Code: A Highly Agentic Coding Assistant](https://www.deeplearning.ai/short-courses/claude-code-a-highly-agentic-coding-assistant/)
* [Design, Develop and Deploy Multi-Agent Systems with CrewAI](https://www.deeplearning.ai/courses/design-develop-and-deploy-multi-agent-systems-with-crewai/)
* [AutoGen](https://github.com/microsoft/autogen)
* [CrewAI](https://github.com/joaomdmoura/crewAI)
* [LangChain Agents](https://python.langchain.com/v0.1/docs/modules/agents/)
* [Refact.ai AI Agent Guide](https://docs.refact.ai/ai-agent/)
* [ADK Sample Agents](https://github.com/google/adk-samples)

## MCP Resources

- [VS Code MCP extension docs](https://code.visualstudio.com/mcp)
- [Hugging Face MCP Course – Unit 2: Continue Client](https://huggingface.co/learn/mcp-course/en/unit2/continue-client)

## Agent swarms docs
- https://www.anthropic.com/engineering/multi-agent-research-system
