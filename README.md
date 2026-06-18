# choreography-agent-loop

An agentic generate → verify → revise loop for designing Buddhist devotional dance choreography using Claude as the LLM backbone.

## How it works

```
Generate ──► Parse ──► Verify ──► (pass?) ──► done
                          │
                        (fail)
                          │
                       Revise ──► Parse ──► Verify ──► ...
```

1. **Generate** — Claude produces a markdown choreography table covering all six narrative phases.
2. **Parse** — the table rows are parsed into `SegmentAnnotation` objects (time window, formation, actions, intent, lyric text).
3. **Verify** — each phase is scored against its `PhaseContract` (motifs, intents, formation, lyric anchors) and hard requirements are checked (e.g. `DHARMA_WHEEL` in phase C, `PRAYER_PALMS`/`KNEEL` in phase E, `FINAL_TABLEAU` in phase F).
4. **Revise** — if the score is below 80 or hard requirements fail, targeted feedback is fed back to Claude and the weak phases are rewritten.
5. The loop repeats up to `--max-iter` times, keeping the best-scoring candidate.

## Narrative phases

| Phase | Time | Character |
|-------|------|-----------|
| A | 0–43 s | Opening grief — bowed, kneeling, sacred shock |
| B | 28–135 s | Remembrance — compassion, devotion, gentle searching |
| C | 135–162 s | Who will continue? DHARMA_WHEEL motif, resolve |
| D | 154–218 s | Crisis — temptation, confusion, pleading appeal |
| E | 218–268 s | Collective prayer → awakening → vow |
| F | 260–344 s | Final unity — Dharma endures, FINAL_TABLEAU |

## Installation

```bash
pip install -e .
```

Requires Python ≥ 3.11 and an `ANTHROPIC_API_KEY` environment variable.

## Usage

```bash
# Full auto-loop (generate + verify + revise)
python main.py

# Feed an existing candidate choreography
python main.py --candidate my_choreo.txt

# Use a custom contract
python main.py --contract my_contract.json

# Save output and cap iterations
python main.py --output result.txt --max-iter 3

# Print the default contract and exit
python main.py --show-contract

# Suppress per-iteration logs
python main.py --quiet
```

Or via the installed script:

```bash
choreo-loop --max-iter 3 --output result.txt
```

## Module overview

| File | Role |
|------|------|
| `main.py` | CLI entry point |
| `loop.py` | Orchestrates the generate/verify/revise cycle |
| `generator.py` | LLM prompts for initial generation and revision |
| `verifier.py` | Scores a parsed trace against a piece contract |
| `parser.py` | Converts markdown table rows into `SegmentAnnotation` objects |
| `schema.py` | Dataclasses: `SegmentAnnotation`, `PieceContract`, `VerifierResult`, etc. |
| `contract_builder.py` | Builds the default Buddhist dance contract |
| `ontology.py` | Controlled vocabulary for motifs, formations, intents |
| `annotate_video.py` | Standalone video annotation helper |
| `annotator.py` | Annotation utilities |
| `llm_client.py` | Thin wrapper around the Anthropic SDK |

## Scoring

Each phase score is a weighted sum:

```
score = 0.35 × motif_score
      + 0.25 × lyric_score
      + 0.20 × intent_score
      + 0.20 × formation_score
```

The piece passes when the weighted average across all phases ≥ 80/100 **and** all hard requirements are satisfied.
