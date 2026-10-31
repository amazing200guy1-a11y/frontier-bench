# FrontierBench 🧪

**Deterministic Edge-Case Benchmark for Frontier AI Code Generation**

> *Which AI model actually writes correct code — or just code that looks correct?*

FrontierBench is an open-source evaluation harness that stress-tests frontier LLMs (ChatGPT, Claude, Gemini, DeepSeek, Grok) on real-world engineering edge cases. Every test is **deterministic**: no LLM judge, no vibes-based scoring — just real code running against real test cases with a binary PASS/FAIL verdict.

---

## 🔬 Why This Exists

AI coding assistants are confidently wrong. They generate code that:
- **Passes visual inspection** — looks clean, well-commented, idiomatic
- **Fails silently in production** — precision loss, race conditions, security bypasses

No existing benchmark captures this gap. FrontierBench does.

---

## 📊 Benchmark Results (October 2026)

| Task | ChatGPT | Claude | Gemini | DeepSeek | Grok |
|---|---|---|---|---|---|
| `allocate_minor_units` | ✅ PASS | ✅ PASS | ✅ PASS | ✅ PASS | ❌ FAIL |
| `billing_dates` | ✅ PASS | ✅ PASS | ✅ PASS | ✅ PASS | ✅ PASS |
| `extract_json` | ✅ PASS | ✅ PASS | ❌ FAIL | ✅ PASS | ❌ FAIL |
| `regex_filter` | ❌ FAIL | ✅ PASS | ✅ PASS | ✅ PASS | ✅ PASS |
| `safe_redirect` | ❌ FAIL | ✅ PASS | ❌ FAIL | ✅ PASS | ✅ PASS |
| `search_latest_wins` | ✅ PASS | ✅ PASS | ✅ PASS | ✅ PASS | ❌ FAIL |
| `snowflake_dedupe` | ❌ FAIL | ❌ FAIL | ✅ PASS | ❌ FAIL | ❌ FAIL |
| **Score** | **4/7** | **6/7** | **5/7** | **6/7** | **3/7** |
| **Pass Rate** | 57% | 86% | 71% | 86% | 43% |

> All responses collected from the **free web interface** of each model (no API). Full raw responses stored in `responses/`.

### Key Findings

- **Snowflake Dedupe (IEEE-754 Precision Loss):** 4 out of 5 frontier models (ChatGPT, Claude, DeepSeek, Grok) fail this task. When dealing with 64-bit snowflake IDs (e.g., Discord/Twitter/financial event IDs), standard `JSON.parse` coerces big integers into 64-bit floats, discarding low-order bits and causing distinct records to collide and be permanently deleted. Only Gemini preserved the exact bit precision.
- **RegExp `/g` Stateful Mutation:** ChatGPT failed by reusing a global regex (`/g`), meaning subsequent calls with identical input alternate between `true` and `false` due to mutable `lastIndex`.
- **Open Redirect (CWE-601):** ChatGPT and Gemini both failed to defend against backslash (`/\evil.com`) or tab whitespace (`/\t/evil.com`) evasion vectors that modern web browsers automatically normalize into external redirects.
- **"Confident-but-wrong" pattern:** Detected across multiple model responses where the generated prose explicitly asserts "this solution is safe, robust, and handles all edge cases", while the deterministic sandbox immediately flagged a critical failure.

---

## 🧩 Task Taxonomy

| # | Task ID | Target Failure | Blind Spot |
|---|---|---|---|
| 1 | `snowflake_dedupe` | IEEE-754 float precision | JSON.parse converts 64-bit IDs to doubles → distinct IDs collide |
| 2 | `regex_filter` | RegExp `/g` statefulness | Stateful `.lastIndex` causes alternating PASS/FAIL on same regex |
| 3 | `safe_redirect` | OWASP CWE-601 open redirect | Backslash `\evil.com` and protocol-relative `//evil.com` bypass naive validators |
| 4 | `search_latest_wins` | Async race condition | Out-of-order responses overwrite latest result with stale data |
| 5 | `allocate_minor_units` | Integer vs float arithmetic | Penny leakage from floating point in minor currency allocation |
| 6 | `billing_dates` | Calendar edge cases | Month-end rollover, leap year Feb 29 → Mar 1 drift |
| 7 | `extract_json` | Nested brace parsing | Greedy regex fails on `{"a":{"b":1}}` nested structures |

---

## ⚙️ Architecture

```
frontier-bench/
├── run_eval.py          # Main harness — validate / export / grade / API runner
├── tasks/               # 7 task directories, each with:
│   └── <task_id>/
│       ├── task.json    # prompt, title, blind_spot
│       ├── starter.js   # broken baseline (must FAIL grader)
│       ├── reference.js # correct solution (must PASS grader)
│       └── test.js      # deterministic test runner (Node 18+)
├── prompts/             # Auto-generated prompts for manual collection
├── responses/           # Raw LLM responses (one file per model per task)
│   ├── chatgpt/
│   ├── claude/
│   ├── deepseek/
│   ├── gemini/
│   └── grok/
└── results/             # JSON grade logs with timestamps
```

---

## 🚀 Quick Start

**Requirements:** Node.js 18+, Python 3.9+ — no pip installs, no API keys needed.

### 1. Validate the harness
```bash
python3 run_eval.py --validate
```
Every task should show `starter=FAIL` and `reference=PASS`.

### 2. Export prompts
```bash
python3 run_eval.py --export
```
Opens `prompts/ALL_PROMPTS.md` with every prompt ready to paste.

### 3. Collect responses (free, no API)
Paste each prompt into ChatGPT / Claude / Gemini / DeepSeek / Grok (new chat each time).
Save the full reply as `responses/<model-name>/<task_id>.txt`.

Or use the setup helper:
```bash
python3 run_eval.py --setup chatgpt claude gemini deepseek grok
```

### 4. Grade all responses
```bash
python3 run_eval.py --grade
```

### 5. Run with API (optional)
```bash
export OPENROUTER_API_KEY=your_key
python3 run_eval.py --model openrouter:meta-llama/llama-3.1-8b-instruct:free --trials 3
```

---

## 🔴 Red Teaming Methodology

Each task is designed with a **known blind spot** — a class of failure that AI models systematically miss:

1. **Prompt engineering is neutral** — prompts give no hint of the edge case. The model is judged on whether its output handles it naturally.
2. **Starter code is intentionally broken** — validates the grader catches real failures.
3. **Reference code is the gold standard** — validates the grader accepts correct solutions.
4. **Tests are immutable** — the test file is never shown to the model. Only the prompt and starter are.
5. **Responses are reproducible** — all collected responses are stored verbatim in `responses/`.

---

## 📈 Reproducing the Results

```bash
git clone https://github.com/amazing200guy1-a11y/frontier-bench
cd frontier-bench
python3 run_eval.py --validate   # confirm graders are intact
python3 run_eval.py --grade      # grade the stored responses
```

Expected output:
```
chatgpt:  4/7 passed
claude:   7/7 passed
gemini:   5/7 passed
deepseek: 7/7 passed
grok:     2/7 passed
```

---

## 🛠 Adding New Tasks

1. Create `tasks/<task_id>/`
2. Add `task.json`:
```json
{
  "id": "your_task_id",
  "title": "What it tests",
  "blind_spot": "What AI will miss",
  "prompt": "Full task prompt shown to the model"
}
```
3. Add `starter.js` (broken), `reference.js` (correct), `test.js` (grader)
4. Run `python3 run_eval.py --validate` to confirm

---

## 📄 License

MIT — open for community extension, research, and CI/CD integration.

---

*Built for the Lexsi AI Safety & Alignment Hackathon 2026 — AI Safety, Model Evaluation & Red Teaming track.*
*Author: Usman Bamidele*
