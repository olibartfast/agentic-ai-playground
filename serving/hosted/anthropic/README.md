# Anthropic API

The Anthropic API is a vendor-hosted model source. Agents such as Claude Code
can select different Anthropic models for main-agent and subagent roles without
operating an inference runtime.

Keep authentication and model-routing configuration with the relevant
[`integration`](../../../integrations/). This directory describes the source's
place in the architecture rather than duplicating client setup.
