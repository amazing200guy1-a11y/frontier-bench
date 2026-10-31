# Eval report
_Generated 2026-10-31 12:41_

## Pass rate (passed/trials)

| task | chatgpt | claude | deepseek | gemini | grok | llama | mistral |
|---|---|---|---|---|---|---|---|
| allocate_minor_units | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 |
| billing_dates | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | - | - |
| extract_json | 1/1 | 1/1 | 1/1 | 0/1 | 0/1 | - | - |
| regex_filter | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| safe_redirect | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 | 0/1 | 1/1 |
| search_latest_wins | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 |
| snowflake_dedupe | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 1/1 | 1/1 |
| **overall** | **4/7** | **6/7** | **6/7** | **5/7** | **3/7** | **4/5** | **5/5** |

## Confident-but-wrong (reply sounds sure, test failed)

_Heuristic: the prose outside the code block uses words like correct/safe/robust/fixed. Verify by reading the reply._

- grok / allocate_minor_units (allocate_minor_units.txt): FAIL: Missing expected exception (RangeError).
- grok / search_latest_wins (search_latest_wins.txt): FAIL: older response for the SAME query must not overwrite a newer one

## All failures

- chatgpt / regex_filter (regex_filter.txt): FAIL: repeat isFlagged call with same text must also return true (RegExp /g statefulness bug)
- chatgpt / safe_redirect (safe_redirect.txt): FAIL: should block (backslash) "/\\evil.com"
- chatgpt / snowflake_dedupe (snowflake_dedupe.txt): FAIL: ids must keep full precision and dedupe exactly
- claude / snowflake_dedupe (snowflake_dedupe.txt): FAIL: ids must keep full precision and dedupe exactly
- deepseek / snowflake_dedupe (snowflake_dedupe.txt): FAIL: ids must keep full precision and dedupe exactly
- gemini / extract_json (extract_json.txt): FAIL: brace inside string
- gemini / safe_redirect (safe_redirect.txt): FAIL: should block (tab inside //) "/\t/evil.com"
- grok / allocate_minor_units (allocate_minor_units.txt): FAIL: Missing expected exception (RangeError).
- grok / extract_json (extract_json.txt): FAIL: brace inside string
- grok / search_latest_wins (search_latest_wins.txt): FAIL: older response for the SAME query must not overwrite a newer one
- grok / snowflake_dedupe (snowflake_dedupe.txt): FAIL: ids must keep full precision and dedupe exactly
- llama / safe_redirect (safe_redirect.txt): FAIL: should block (tab inside //) "/\t/evil.com"
