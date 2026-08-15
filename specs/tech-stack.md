# Technical Boundaries

Status: reconstructed brownfield constitution, 2026-08-15. Existing behavior
and executable checks take precedence where this draft and the repository
disagree.

## Repository Shape

The repository is documentation-first and separates these stable concerns:

| Area | Responsibility |
| --- | --- |
| `models/` | Checkpoint requirements and model-specific experiment decisions |
| `serving/` | Hosted sources and user-operated inference runtimes |
| `integrations/` | Coding-agent, IDE, and extension configuration |
| `deployments/` | Workstation and rented-compute runbooks |
| `benchmarks/` | Versioned task contracts, fixtures, validation, and results |
| `experiments/` | Runnable agent-framework prototypes |
| `specs/` | Project constitution, roadmap, and active feature contracts |

Do not collapse model source, model identity, runtime, and compute placement
into one concept. A self-hosted endpoint may execute locally or on remote
compute reached through a loopback SSH tunnel.

## Current Formats and Tools

- Markdown is the durable format for guidance, specifications, and results.
- Mermaid may be used for architecture diagrams that benefit from a visual.
- Git commits and branches carry specifications and implementation together.
- JSON and YAML are used for example client configuration.
- Python 3 is present in legacy prototypes. Those prototypes have local
  dependencies and are not a root-level application stack.
- Shell commands and `curl` are used for setup and endpoint preflight examples.
- The repository has no root package manager, application framework, database,
  CI workflow, or universal test command today.

## API and Integration Boundaries

- Prefer a documented native agent protocol when available.
- OpenAI-compatible APIs are the common self-hosted baseline, but compatibility
  must be tested rather than inferred from the label.
- Anthropic Messages and OpenAI Responses paths remain explicit when an agent
  requires them; a proxy is not assumed to be lossless.
- Verify model discovery, authentication, chat formatting, streaming if used,
  and tool calls independently.
- Keep model identifiers and endpoint URLs configurable. Never commit API keys
  or tokens.

## Safety and Operational Constraints

- Temporary inference servers bind to loopback and remote access uses an SSH
  tunnel.
- Public exposure requires authentication, TLS, and an explicit production
  design; it is outside the current roadmap.
- Cloud instructions must include a shutdown or termination step and enough
  storage/topology detail to avoid preventable cost.
- Hardware selection follows a verified model profile and current primary
  documentation, not naming analogy or aggregate VRAM alone.

## Benchmark Constraints

- Every comparable run uses the same versioned task pack and fixture revision.
- Prompts, initial state, tool permissions, timeouts, and pass criteria are part
  of the benchmark contract.
- Each coding scenario starts from a clean prepared fixture so an earlier task
  cannot silently affect a later score.
- Static or executable validators should decide mechanical outcomes; a written
  rubric must identify any result that still needs human judgment.
- Raw output and failures are reported honestly. A passing unit test does not
  imply that every manual or protocol check passed.
- Result records use repository-relative links and contain no secrets.

## Rules for New Automation

- Start with portable, inspectable scripts and standard-library Python where it
  is sufficient.
- Scope dependencies to the experiment or tool that needs them. Adding a
  root-level dependency or framework requires an explicit spec decision.
- Scripts that prepare benchmark state must not mutate the canonical fixture.
- Destructive or chargeable operations require an explicit command and must not
  occur as a side effect of documentation validation.
- Add the nearest focused checks with each script; define a root-wide toolchain
  only when more than one maintained area needs it.

## Explicit Non-Choices

- No root web framework, frontend framework, ORM, or database is selected.
- No cloud provider is the default deployment target.
- No agent, gateway, runtime, or model is the project-wide default winner.
- No container or infrastructure-as-code layer is required for the first
  reproducible benchmark pack.
- Legacy prototypes are not silently promoted to maintained reference
  implementations; modernization requires a dedicated feature packet.
