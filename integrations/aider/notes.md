# Aider

**Aider** is a command-line AI coding assistant that allows you to pair program with LLMs to edit code in your local git repository. It is known for its high performance on the SWE-bench benchmark.

## Key Features
- **Git Integration**: Automatically commits changes with descriptive messages.
- **Multi-file Edits**: Can understand and modify multiple files in a single request.
- **Model Flexibility**: Works with GPT-4o, Claude 3.5 Sonnet, DeepSeek Coder, and others.
- **Voice Coding**: Supports voice input.

## Installation

Requires Python installed.

```bash
# Install via pip (recommended to use pipx or a venv)
pip install aider-chat

# Or use pipx
pipx install aider-chat
```

## Usage

Run inside a git repository:

```bash
export OPENAI_API_KEY=your-key-here
aider
```

Or with Anthropic:

```bash
export ANTHROPIC_API_KEY=your-key-here
aider --sonnet
```

## Commands
- `/add <file>`: Add a file to the chat context.
- `/drop <file>`: Remove a file from the chat context.
- `/undo`: Undo the last commit/change.
- `/diff`: Show the diff of the last changes.
