# Dataset Card: curatorkit_run

## Summary

- **Run timestamp**: 2026-11-01T20:22:30.936065Z
- **Wall clock time**: 2.2s
- **Pipeline config hash**: `5a4399e9252ea743`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 15 | 15 | — | 0 | 15 |
| SchemaGate | 15 | 15 | 0 | 0 | 15 |
| ExactDeduplicator | 15 | 15 | — | — | 15 |
| MinHashDeduplicator | 15 | 15 | — | — | 15 |
| TextCleaner | 15 | 15 | — | — | 15 |
| AlpacaExporter | — | 15 | — | — | 15 |
| ShareGPTExporter | — | 15 | — | — | 15 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 15/0 passed (N/A), 0 rejected
- **SchemaGate**: 15/15 passed (100.0%), 0 rejected


**Rejection reasons:**
  - None

## Deduplication

  - near_duplicates_removed: 0
  - surviving_count: 15

## Known Limitations

- MinHash threshold used: **0.85** — this is a starting point, not a universal answer. Adjust per domain (legal, medical, and other domain-specific corpora may need a lower threshold to avoid losing structurally similar but semantically valid examples).
- Table extraction requires `extract_tables: true` on the PDF reader and MinerU with GPU support. Disabled by default.
- Token counting uses a whitespace tokenizer by default. For exact LLM context window
  enforcement, enable `use_tiktoken: true` in the SchemaGate config.
- Both within-run (MinHash/Diversity) and cross-run (EmbeddingDeduplicator) deduplication
  are available. Cross-run dedup persists an embedding index across runs; use
  `embedding_reset_index: true` to start fresh.

## Reproduction

```bash
pip install curatorkit
curatorkit run pipeline.yaml --output-dir ./out/
```

## Tool Versions

- **curatorkit**: 0.1.22
- **python**: 3.12.10
