

---

## Lexsi Safety Stack Integration

FrontierBench integrates the **Lexsi AI Safety stack** to demonstrate a full repair loop using real safety tooling:

### 4-Stage Pipeline (`lexsi_pipeline.py`)

| Stage | Tool | Action |
|---|---|---|
| 1 | **AuditKIT v1.1.3** | Baseline evaluation of broken starter code (BEFORE) |
| 2 | **CuratorKIT v0.1.22** | Curate failure traces → repair dataset (alpaca + sharegpt) |
| 3 | **AuditKIT v1.1.3** | Post-repair evaluation of reference solutions (AFTER) |
| 4 | **Delta Report** | `before_vs_after.json` — quantified safety improvement |

### Results

```
BEFORE :  0/15 tasks safe  (0%)   ← Broken starter code fails all tests
AFTER  : 15/15 tasks safe  (100%) ← Reference solutions pass all tests
DELTA  : +100% safety improvement
STACK  : AuditKIT 1.1.3 | CuratorKIT 0.1.22
```

### Outputs

- `lexsi_pipeline.py` — Full 4-stage Lexsi integration pipeline
- `lexsi_failures.jsonl` — Exported failure traces (15 repair pairs)
- `lexsi_repair_dataset/` — CuratorKIT-curated dataset (alpaca + sharegpt formats)
- `before_vs_after.json` — Machine-readable delta report
- `lexsi_provenance.json` — Pipeline fingerprint + timestamp

Run the pipeline:

```bash
python lexsi_pipeline.py
```

---

## Links

- **Live Leaderboard**: https://amazing200guy1-a11y.github.io/frontier-bench/
- **GitHub**: https://github.com/amazing200guy1-a11y/frontier-bench
- **Hackathon**: Lexsi Labs AI Safety & Alignment Hackathon 2026
