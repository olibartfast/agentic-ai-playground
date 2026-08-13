# Model profiles

Model profiles contain requirements and decisions, not duplicated server or
client instructions. Record the exact checkpoint revision and verify its model
card before allocating cloud hardware.

| Profile | Intended first deployment | Status |
| --- | --- | --- |
| [Muse Glimmer](muse-glimmer/) | Quantized, single GPU | Candidate |
| [Nemotron 3.5 Lightning](nemotron-3.5-lightning/) | To be determined | Awaiting verification |
| [DeepSeek V4 Flash](deepseek-v4-flash/) | Multi-GPU or CPU offload | Candidate |
| [Inkling](inkling/) | High-end multi-GPU | Reference |

Every experiment record should include checkpoint, quantization, runtime
version, context size, GPU topology, command-line flags, and observed memory.

