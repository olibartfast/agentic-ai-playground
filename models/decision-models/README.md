# Decision models profile

Goal: find the smallest decision model that makes a coding agent's gating,
tool-selection, and routing decisions accurately enough to act on, served on
the owned RTX 3060 6 GB host.

A decision model does not generate text. It reads a state once and returns a
probability for each option of each question (`choice`, `score`, `noul`). The
API is TypeSafe's System One format; llama.cpp serves it at `/v1/systemone`.
Serving recipe:
[`serving/self-hosted/llama-cpp/decision-models.md`](../../serving/self-hosted/llama-cpp/decision-models.md).

## Checkpoints

Recorded 2026-10-06 from the ggml-org
[Decision models collection](https://huggingface.co/collections/ggml-org/decision-models)
and its announcement post. Speed is the announcement's median time to answer
one question on one RTX PRO 6000, not a playground measurement.

| Model | Size | Based on | Languages | Images | License | Speed |
| --- | --- | --- | --- | --- | --- | --- |
| `ggml-org/Julia-1-GGUF` | 144M | mmBERT-small | 50+ | no | Apache 2.0 | 3 ms |
| `ggml-org/Laya-GGUF` | 421M | ModernBERT-large | English | no | Apache 2.0 | 5 ms |
| `ggml-org/Kev-4B-GGUF` | 4B | Qwen3.5-4B-Base | English | no | Apache 2.0 | 12 ms |
| `ggml-org/lev-GGUF` | 4B | Qwen3.5-4B | English | no | Apache 2.0 | 36 ms |
| `ggml-org/OpenJev-GGUF` | 27B | Qwen3.8-27B | en, de, fr, hi, zh, ja | yes | CC BY-NC 4.0 | 43 ms |
| `ggml-org/Clef-GGUF` | 27B | Qwen3.8-27B | English | yes | Apache 2.0 | not published |

**OpenJev is non-commercial.** Do not use it for work outside personal
experiments; Clef is the permissively licensed 27B image-capable option.

## Fit on the RTX 3060 6 GB host

Estimated from parameter count, not measured. The host has about 5.2 GB usable
after the desktop session ([host note](../../specs/roadmap.md#host-note-2026-08-23)).

| Model | Expected regime |
| --- | --- |
| Julia-1, Laya | Full GPU offload with room to spare; also plausible on CPU |
| Kev-4B, lev | Full GPU offload at 4- to 8-bit quantization; record observed VRAM |
| OpenJev, Clef | Do not fit; partial offload of a 27B dense model is out of scope |

Run order follows size: Julia-1, then Laya, then Kev-4B. lev is a second 4B
candidate only if Kev-4B leaves a gap worth testing.

## Known limitations to check against

- **Laya is a fine-tuning base.** Its model card reports the base checkpoints
  near chance on its own typed-decisions benchmark zero-shot, below a
  majority-class baseline; the headline score comes from a checkpoint
  fine-tuned on that benchmark's training split. Record Laya's zero-shot result
  as such.
- **Laya's English checkpoint leaves roughly 320 tokens for the state.** Long
  tool output must be summarized or truncated before it is scored.
- **Many-option questions degrade the small models.** Laya's card reports
  option labels sharing a fixed token budget, with accuracy falling sharply
  near 77 options. Tool selection with a large tool set should be split
  coarse-then-fine.
- **Confidence is model-specific.** A cutoff measured for one model says
  nothing about another.

## Hosted reference

TypeSafe's Jev is the hosted model the API was designed for. It is reachable by
changing the base URL, but sends the state to a third party. No playground run
uses it yet.
