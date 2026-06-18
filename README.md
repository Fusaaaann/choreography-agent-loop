# choreography-agent-loop

An agentic generate → verify → revise loop for designing devotional dance choreography using Claude as the LLM backbone.

## How it works

```
Generate ──► Parse ──► Verify ──► (pass?) ──► done
                          │
                        (fail)
                          │
                       Revise ──► Parse ──► Verify ──► ...
```

1. **Generate** — Claude produces a markdown choreography table covering all narrative phases.
2. **Parse** — the table rows are parsed into `SegmentAnnotation` objects (time window, formation, actions, intent, lyric text).
3. **Verify** — each phase is scored against its `PhaseContract` (motifs, intents, formation, lyric anchors) and hard requirements are checked.
4. **Revise** — if the score is below 80 or hard requirements fail, targeted feedback is fed back to Claude and the weak phases are rewritten.
5. The loop repeats up to `--max-iter` times, keeping the best-scoring candidate.

## Configuration

The piece contract (phases, lyric anchors, motif requirements, etc.) lives in **`default_contract.json`**, which is git-ignored so piece-specific details stay local.

To get started:

```bash
cp default_contract.example.json default_contract.json
# edit default_contract.json with your piece details
```

Or pass any contract file directly at runtime:

```bash
python main.py --contract my_contract.json
```

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

# Print the loaded contract and exit
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
| `contract_builder.py` | Loads the default contract from `default_contract.json` |
| `ontology.py` | Controlled vocabulary for motifs, formations, intents |
| `annotate_video.py` | Standalone video annotation helper |
| `annotator.py` | Annotation utilities |
| `llm_client.py` | Thin wrapper around the Anthropic SDK |
| `default_contract.json` | **Git-ignored** — your piece's contract data |
| `default_contract.example.json` | Committed template to copy from |

## Scoring

Each phase score is a weighted sum:

```
score = 0.35 × motif_score
      + 0.25 × lyric_score
      + 0.20 × intent_score
      + 0.20 × formation_score
```

The piece passes when the weighted average across all phases ≥ 80/100 **and** all hard requirements are satisfied.
