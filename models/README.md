# Model profiles

Model profiles contain requirements and decisions, not duplicated server or
client instructions. Record the exact checkpoint revision and verify its model
card before allocating cloud hardware.

A model is independent of its source. The same open-weight model may be reached
through a hosted gateway such as OpenRouter or loaded into a self-hosted runtime
on a workstation or rented GPU. Proprietary models are normally available only
through their vendor or an authorized gateway.

| Profile | Intended first deployment | Status |
| --- | --- | --- |
| [Muse Glimmer](muse-glimmer/) | Quantized, single GPU | Candidate |
| [Qwen3.8 27B](qwen3.8-27b/) | Quantized single GPU or FP8 | Candidate |
| [Nemotron 3.5 Lightning](nemotron-3.5-lightning/) | To be determined | Awaiting verification |
| [DeepSeek V4 Flash](deepseek-v4-flash/) | Multi-GPU or CPU offload | Candidate |
| [Inkling](inkling/) | High-end multi-GPU | Reference |

Every experiment record should include checkpoint, quantization, runtime
version, context size, GPU topology, command-line flags, and observed memory.

## Costs

Self-hosted profiles are priced in rented GPU hours; hosted models are priced
per token. Record both in a benchmark result so runs stay comparable.

Prices below are per million tokens, recorded 2026-08-22 from vendor and
OpenRouter model pages. Verify them before budgeting a run: list prices move,
several current rates are explicitly promotional, and a gateway's listing can
differ from the vendor's own. Third-party pricing trackers disagreed with the
vendor pages on several of these models, so treat only the vendor or gateway
page as authoritative.

### Meta Muse Spark 1.2 (Meta Model API)

From the [Muse Spark model page](https://developer.meta.com/ai/models/muse-spark/),
1M-token context, two variants that differ only in data handling and price:

| Variant | Input | Cached input | Output |
| --- | --- | --- | --- |
| `muse-spark-1.2-contributor` | $0.10 | $0.002 | $0.20 |
| `muse-spark-1.2` | $1.25 | $0.15 | $4.25 |

The contributor variant is roughly 12x cheaper on input and 21x cheaper on
output because its traffic is used to improve Meta's products. Do not send
private repository content through it; keep it for public-code benchmarks and
throwaway scenarios.

### Frontier tier

Reachable with a single key through
[`serving/hosted/openrouter`](../serving/hosted/openrouter/), except where the
row names a vendor API:

| Model | Input | Cached input | Output | Context |
| --- | --- | --- | --- | --- |
| Claude Opus 5 | $5.00 | $0.50 | $25.00 | 200K |
| GPT-5.6 Sol (OpenAI direct) | $4.00 | $0.40 | $20.00 | 1.05M |
| Kimi K3 | $2.60 | $0.29 | $13.00 | 1M |
| Gemini 3.1 Pro Preview | $2.00 | — | $12.00 | 1M |
| Claude Sonnet 5 | $2.00 | $0.20 | $10.00 | 200K |
| GLM 5.3 | $1.40 | $0.26 | $4.40 | 1M |
| Muse Spark 1.2 | $1.25 | $0.15 | $4.25 | 1M |

GPT-5.6 Sol's rate is promotional through 2026-11-21, and a request above 272K
input tokens is billed at 2x input and 1.5x output for the whole request — a
long-context agent run is not priced by the headline row. Anthropic cache writes
cost 1.25x input; OpenAI's do too.

### Mid tier

Where a coding-agent loop is usually cheap enough to run repeatedly:

| Model | Input | Cached input | Output | Context |
| --- | --- | --- | --- | --- |
| GPT-5.6 Terra | $2.00 | $0.20 | $12.00 | 1.05M |
| Claude Haiku 4.5 | $1.00 | $0.10 | $5.00 | 200K |
| Gemini 3 Flash Preview | $0.50 | — | $3.00 | 1M |
| Qwen3.8 27B | $0.40 | $0.15 | $3.00 | 1M |
| Gemini 3.7 Flash | $0.375 | — | $1.875 | 1.05M |
| DeepSeek V4 Flash Vision Exp | $0.22 | — | $0.66 | 1M |
| GPT-5.6 Luna | $0.20 | $0.02 | $1.20 | 1.05M |
| Muse Spark 1.2 Contributor | $0.10 | $0.002 | $0.20 | 1M |
| DeepSeek V4 Flash | $0.06 | $0.012 | $0.12 | 1M |

"Mid tier" here means vendor positioning, not measured quality. GPT-5.6 Terra is
named a mid-tier model but is priced at frontier rates; Muse Spark Contributor
is a frontier model at mid-tier prices, paid for with your traffic. DeepSeek
publishes several V4 Flash listings at very different rates, so pin the exact
variant. Gemini 3.7 Flash's batch variant lists at 75% below the interactive
rate.

Copy exact slugs from each model's page rather than from these tables; names
here are for comparison only. Verified slugs at recording time:
`openai/gpt-5.6-sol`, `openai/gpt-5.6-terra`, `openai/gpt-5.6-luna`,
`anthropic/claude-opus-5`, `anthropic/claude-sonnet-5`,
`anthropic/claude-haiku-4.5`, `google/gemini-3.1-pro-preview`,
`google/gemini-3-flash-preview`, `moonshotai/kimi-k3`, `z-ai/glm-5.3`,
`qwen/qwen3.8-27b`, `deepseek/deepseek-v4-flash`, `meta/muse-spark-1.2`.

### Reading these numbers for agent workloads

Output price matters less than it looks: the agent loop resends a growing
transcript, so total input tokens usually exceed output by an order of
magnitude. Compare candidates on cached-input price first, then output, and
confirm the client actually enables prompt caching — without it the cached
column never applies and the effective input cost is 5x to 10x the cached rate.

Two of the profiles here, [Qwen3.8 27B](qwen3.8-27b/) and
[DeepSeek V4 Flash](deepseek-v4-flash/), can be reached either way. Running the
same benchmark through OpenRouter first gives a token-cost figure to compare
against the GPU-hour cost of self-hosting the same checkpoint.
