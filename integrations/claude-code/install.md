# Claude Code Installation Guide

## Prerequisites

Before installing Claude Code, ensure you have:
- Node.js (version 16 or higher)
- npm (comes with Node.js)
- A Claude API key from Anthropic

## Installation

Install Claude Code globally using npm:

```bash
npm install -g @anthropic-ai/claude-code
```

## Setup

1. **Get your Claude API key:**
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Create an account or sign in
   - Navigate to API Keys section
   - Create a new API key

2. **Set your API key:**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```
   
   Or add it to your shell profile (`.bashrc`, `.zshrc`, etc.):
   ```bash
   echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

## Usage

### Basic Usage

```bash
# Start Claude Code in the current directory
claude-code

# Start in a specific directory
claude-code /path/to/your/project

# Use a specific model
claude-code --model claude-3-sonnet-20240229
```

### Command Line Options

- `--model`: Specify the Claude model to use (default: claude-3-sonnet-20240229)
- `--port`: Specify the port number (default: 3000)
- `--host`: Specify the host address (default: localhost)
- `--help`: Show help information

### Examples

```bash
# Start with a different model
claude-code --model claude-3-haiku-20240307

# Start on a different port
claude-code --port 8080

# Start on all interfaces
claude-code --host 0.0.0.0
```

## Features

- **Code Analysis**: Analyze your codebase with Claude's understanding
- **Interactive Chat**: Have conversations about your code
- **File Navigation**: Browse and understand your project structure
- **Real-time Assistance**: Get help while coding

## Troubleshooting

### Common Issues

1. **"Command not found" error:**
   - Ensure Node.js and npm are properly installed
   - Try reinstalling: `npm uninstall -g @anthropic-ai/claude-code && npm install -g @anthropic-ai/claude-code`

2. **API key not found:**
   - Verify your API key is set correctly: `echo $ANTHROPIC_API_KEY`
   - Check that the key is valid in the Anthropic Console

3. **Port already in use:**
   - Use a different port: `claude-code --port 3001`
   - Or kill the process using the current port

4. **Permission denied:**
   - On Linux/macOS, you might need to use `sudo` for global installation
   - Or configure npm to use a different directory: `npm config set prefix ~/.npm-global`

### Getting Help

- Run `claude-code --help` for command line options
- Visit the [Claude Code documentation](https://github.com/anthropics/anthropic-cookbook/tree/main/examples/claude-code)
- Check the [Anthropic API documentation](https://docs.anthropic.com/)

## Uninstallation

To remove Claude Code:

```bash
npm uninstall -g @anthropic-ai/claude-code
```

## Version Information

Check your installed version:

```bash
claude-code --version
```

## License

Claude Code is provided by Anthropic. Please refer to Anthropic's terms of service and API usage guidelines.