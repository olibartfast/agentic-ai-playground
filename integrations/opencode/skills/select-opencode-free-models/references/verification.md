# Verify Free Models

## Read the catalog

```sh
# Runtime catalog for the current account
opencode models | grep -E 'free|pickle'

# Interactive picker
opencode
# then /models
```

Documentation: <https://opencode.ai/docs/console/models/>.

## Probe one model

```sh
opencode run --archived --model opencode/deepseek-v4.1-flash-free \
  "Reply with exactly: OK"
```

The `--archived` flag keeps the probe out of normal session history. Use the
exact model ID and variant you intend to configure.

## Probe a set

```sh
chmod +x scripts/probe-free-models.sh
./scripts/probe-free-models.sh
./scripts/probe-free-models.sh deepseek-v4.1-flash-free inkling-2-small-free
```

The script prints `MODEL`, `STATUS`, and `DETAIL` columns. It does not modify
configuration.

## Interpret failures

| Output contains | Status | Next step |
| --- | --- | --- |
| `OK` and exit 0 | reachable | record the date |
| `Model unavailable` | unavailable | remove or replace |
| `not available in your country` | geo-blocked | replace; retry is useless |
| `429`, `quota`, `rate` | throttled | move role or lower fan-out |
| timeout | stalled | retry once, then replace |
| `unauthorized`, `auth` | credential problem | reconnect the provider |

## Record template

| Field | Example |
| --- | --- |
| Probe date | 2026-11-14 |
| Model | `opencode/deepseek-v4.1-flash-free` |
| Variant | `max` |
| Role | architect |
| Privacy class | zero-retention |
| Region result | reachable |
| Fallback | `opencode/glm-5.3-flash-free#high` |

Keep the record beside the agent configuration so a later failure has context.

## Verify an agent configuration

Read back the loaded agent and model:

```sh
opencode api get /api/agent
```

Confirm the ID, `model.providerID`, `model.id`, and `mode` for each role.

## Re-verification triggers

- a new long or expensive run;
- any model or provider error;
- a documentation change or deprecation notice;
- a free model being withdrawn;
- a change to the configured variant.
