# Agent and assistant integrations

This directory documents every user-facing coding agent, IDE, and extension
evaluated by the playground. An integration may be a ready-to-use connection
to the serving layer or product notes that describe why a direct connection is
not currently available.

## Integration status

| Integration | Surface | Self-hosted endpoint path |
| --- | --- | --- |
| [OpenCode](opencode/) | CLI, TUI, desktop | OpenAI-compatible API |
| [Pi Agent](pi/) | CLI agent | OpenAI-compatible API |
| [Hermes Agent](hermes/) | CLI agent | OpenAI-compatible API, 64K context floor |
| [Kilo Code](kilocode/) | CLI, TUI | OpenAI-compatible API |
| [DeepSeek Harness](dsh/) | CLI agent, Web UI | OpenAI-compatible custom provider |
| [Oh My Pi](omp/) | CLI agent, TUI, SDK, ACP | OpenAI-compatible API, local auth tag |
| [Claude Code](claude-code/) | CLI agent | Anthropic Messages API or proxy |
| [Codex](codex/) | CLI agent | Responses API, OSS provider, or proxy |
| [Continue](continue/) | IDE extension | Native provider configuration |
| [VS Code over ACP](vscode-acp/) | IDE extension | Agent-supplied; ACP carries no models |
| [Aider](aider/) | CLI agent | Native provider or compatible API |
| [Cursor](cursor/) | IDE | Product-dependent provider support |
| [Google Antigravity](google-antigravity/) | IDE/platform | Product-dependent provider support |
| [GitHub Copilot](github-copilot/) | IDE and CLI | Product-managed models |
| [ForgeCode](forgecode/) | CLI agent | Product-specific configuration |
| [Trae](trae/) | IDE | Product-managed models |
| [Windsurf](windsurf/) | IDE | Product-managed models |

Endpoint wiring is only half of a workflow. For roles, delegation, and the
enforcement levers each harness offers, see
[Role agents across harnesses](../docs/role-agents.md).

Each integration should eventually record its supported protocol, direct or
proxied connection path, example configuration, authentication variables, and
known tool-calling limitations. Product notes and runnable configurations live
together so no tool appears privileged merely because its endpoint setup was
implemented first.
