# Optional free OpenCode models

OpenCode Console serves a rotating free tier. Free removes cost, not risk:
privacy terms, regional availability, request caps, and remaining lifetime
differ per model. This page records an **optional** free mapping for the role
agents. The committed [`.opencode/agent/`](../../.opencode/agent/) roles keep
their existing models; adopt this mapping only when you choose to run the
workflow on the free tier.

Verified 2026-11-14 against the `opencode` provider with archived probes. Free
models are time-limited; treat this page as a snapshot. The IDs require the
OpenCode Console provider to be connected (`/connect`); the self-hosted
provider examples in [README.md](README.md) use different keys.

## Optional role mapping

| Role | Alternative model | Privacy |
| --- | --- | --- |
| `architect` | `opencode/deepseek-v4.1-flash-free#max` | zero-retention |
| `orchestrator` | `opencode/glm-5.3-flash-free#high` | zero-retention |
| `planner` | `opencode/deepseek-v4.1-flash-free#high` | zero-retention |
| `implementer` | `opencode/nemotron-3.5-super-vl-free#high` | trial, logged |
| `implementer-local` | `opencode/nemotron-3.5-lightning-free` | trial, logged |
| `reviewer` | `opencode/minimax-m3.1-flash-free#high` | zero-retention |
| `explore` | `opencode/glm-5.3-flash-free#low` | zero-retention |

These are alternatives, not defaults. To opt in, change the `model:` line in
the matching role file (or copy the role file into a separate profile) and
re-probe. Do not change the committed baseline unless you intend to adopt the
free mapping for the whole workflow.

The worker roles in this mapping are the only trial-logged roles. Use it for
public or disposable code; apply the substitution below for confidential code.

## Privacy-first substitution

| Role | Replacement | Privacy |
| --- | --- | --- |
| `implementer` | `opencode/minimax-m3.1-flash-free#high` | zero-retention |
| `implementer-local` | `opencode/minimax-m3.1-flash-free#low` | zero-retention |

With these two changes every role is zero-retention. Review stays on GLM and
architecture/planning on DeepSeek, so the reviewer remains independent of the
implementer.

## Verified set

| Model | Result | Note |
| --- | --- | --- |
| `deepseek-v4.1-flash-free` | reachable | zero-retention, variants low/high/max |
| `glm-5.3-flash-free` | reachable | zero-retention, low/high/max |
| `minimax-m3.1-flash-free` | reachable | zero-retention, low through max |
| `nemotron-3.5-super-vl-free` | reachable | trial logged, none through xhigh |
| `nemotron-3.5-lightning-free` | reachable | trial logged, no variants |
| `longcat-2.5-free` | reachable | zero-retention, China-hosted, 100 req/day |
| `flint-40b-free` | reachable | may improve the model, 30-day retention |
| `beam-free` | reachable | no training, 30-day retention, geo-restricted |
| `mimo-v2.6-flash-free` | reachable | may improve the model |
| `iceman-free` | reachable | retained and used for improvement |
| `big-pickle` | reachable | may improve the model |
| `inkling-2-small-free` | geo-blocked | "not available in your country" |
| `nemotron-3-ultra-free` | unavailable | listed in docs, absent at runtime |

Two failures matter. Inkling was `active` in the catalog but blocked in this
region, and Nemotron 3 Ultra appeared in the documentation but not in the
runtime catalog. A catalog row is not proof of reachability.

## Probe before relying

```sh
opencode run --archived --model opencode/deepseek-v4.1-flash-free \
  "Reply with exactly: OK"
```

Interpret `OK` as reachable, `Model unavailable` as absent or unentitled, and
`not available in your country` as a geo-block that retrying cannot fix. Use
`--archived` so probes stay out of session history.

The batch script is
[skills/select-opencode-free-models/scripts/probe-free-models.sh](skills/select-opencode-free-models/scripts/probe-free-models.sh).

## Caveats

- **Free is temporary.** Any model can be withdrawn or deprecated.
- **Region matters.** Inkling 2 Small Free is blocked in the EU and several
  other regions. A working catalog entry does not prove access.
- **Trial endpoints log.** The Nemotron free endpoints are NVIDIA trials; do
  not submit personal or confidential data.
- **Retention differs.** Beam keeps inputs for 30 days; Flint keeps them for 30
  days and may use them for improvement; Inkling retains and may train.
- **Request caps differ.** LongCat 2.5 Free is limited to 100 requests per day
  and is hosted in China, so it is a poor fit for fan-out.
- **Docs lag runtime.** Verify both the documentation and the live catalog.
- **Variants are model-specific.** A wrong variant fails at request time.
- **Tool-calling is separate from availability.** A model that answers `OK` can
  still fail to emit tool calls. Probe a real file read as in
  [README.md](README.md#tool-calling-check).

## Related

- [OpenCode Console models](https://opencode.ai/docs/console/models/): catalog,
  privacy, pricing, and deprecations.
- [Role agents across harnesses](../../docs/role-agents.md): role boundaries
  and handoff contracts.
- [OpenCode integration](README.md): endpoint and provider configuration.
- [select-opencode-free-models](skills/select-opencode-free-models/SKILL.md):
  reusable verification workflow and probe script.
