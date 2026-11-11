# Hermes orchestration example

This is a versioned example, not an installed user configuration. For each role, create `~/.hermes/profiles/<role>/`, copy `config.example.yaml` there as `config.yaml`, and copy `SOUL.example.md` there as `SOUL.md`. Merge `config.example.yaml` into `~/.hermes/config.yaml`; preserve unrelated settings and provide credentials through Hermes' normal secret setup. Before enabling the profiles, replace existing fallback lists on the main agent and these profiles with the Meta/DeepSeek-only examples. Inspect auxiliary model routes too: if any explicitly names OpenAI or Anthropic, replace it with Meta/DeepSeek or remove the override so it inherits the main provider. Do not copy example files over a populated config wholesale.

Install the official plugin before selecting its backend:

```sh
hermes plugins install NousResearch/hermes-official-plugins#advanced-delegation --enable
```

The plugin supplies `profile_routes`; the backend selection fails closed if it is unavailable. `max_spawn_depth: 2` permits an orchestrator child to spawn leaf children. Set each delegate call's role to `orchestrator` only for the coordinator; leaf is the default for specialists. Profile routes share the selected profile's credentials and terminal policy, so list only profiles intended for delegation.

The configured primary and fallback providers are Meta and DeepSeek. `deepseek/deepseek-flash` is the provider's canonical Flash ID. Each sample profile has its own fallback list restricted to those providers. `muse-ember-1.0` was not present in the inspected Hermes Meta model cache; verify account availability before use. The example has not been installed or exercised against live endpoints.

Role instructions are in each `profiles/<role>/SOUL.example.md`. Hermes subagents inherit the parent's toolsets; role prompts do not enforce a worker-only write boundary. Review the diff before accepting delegated edits.
