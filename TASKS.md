# Task catalog

| # | id | what it tests | hidden blind spot |
|---|---|---|---|
| 1 | `allocate_minor_units` | Revenue split in kobo that always adds up | Largest-remainder allocation with a deterministic tie-break; models dump the leftover on the first/last recipient or round each share independently. |
| 2 | `billing_dates` | Monthly renewal dates for subscriptions anchored on the 29th-31st | Month-end clamping must be computed from the ORIGINAL anchor day, not from the previous renewal date (iterative clamping drifts: Jan 31 -> Feb 28 -> Mar 28). |
| 3 | `compose_middleware` | Koa/Express-style async middleware composer | Shared dispatch index lets a middleware call next() twice and silently run the wrong handler; sync throws escape as exceptions instead of rejections. |
| 4 | `deep_clone` | Deep clone a plugin config preserving undefined, Date and RegExp | JSON.parse(JSON.stringify(obj)) silently drops undefined properties, converts Date to strings, and converts RegExp to {}. Models must recognise the failures listed in the prompt and avoid all three, plus avoid shared references. |
| 5 | `extract_json` | Pull the first JSON object out of an LLM response | Greedy regex /{[\s\S]*}/ breaks on trailing braces; naive brace counting breaks on braces inside strings and on a malformed first candidate. |
| 6 | `idempotent_handler` | Idempotency wrapper for a payments webhook | Check-then-act across an await lets concurrent retries all run processFn; caching only successful results is not enough, and caching the promise must not poison the key on failure. |
| 7 | `promise_pool` | Concurrency-limited task runner for a rate-limited API | Batching with Promise.all respects the limit but wastes capacity (a slow task stalls its whole batch); a correct pool must also stop starting new work after the first failure. |
| 8 | `regex_filter` | Word filter: isFlagged and redact with RegExp | Using RegExp with the /g flag for isFlagged introduces statefulness via lastIndex: repeated calls on the same text oscillate between true and false. |
| 9 | `safe_redirect` | Open-redirect guard for the post-login ?next= parameter | Prefix checks (startsWith('/')) accept protocol-relative '//evil.com', backslash and tab tricks, userinfo '@' hosts and lookalike domains; CR/LF reaches the Location header. |
| 10 | `search_latest_wins` | Search-as-you-type: never show outdated results | Guarding by query value instead of call sequence (a Refresh re-runs the same query), and stale rejections still reaching onError. |
| 11 | `snowflake_dedupe` | Dedupe API records keyed by 64-bit Snowflake IDs | JSON.parse turns 64-bit integers into doubles above 2^53, so adjacent Snowflake IDs collapse into one and dedupe silently drops distinct rows. |
| 12 | `sse_parser` | Server-Sent Events parser for an LLM chat stream | Network chunks split events mid-line and even between CR and LF; value whitespace must be preserved except one leading space; comment-only blocks are not events. |
| 13 | `store_subscribe` | Tiny state store: subscribe/unsubscribe during dispatch | Mutating the listener array while iterating it, and splice(indexOf(fn)) removing the wrong listener when unsubscribe is called twice. |
| 14 | `template_interpolate` | Template string interpolation with literal values | Using re.sub() directly with string replacement causes backslashes in paths (e.g. C:\users\new) or regex backreferences (\1, \g<0>) to crash or corrupt output. Replacement must be treated literally via a callable. |
| 15 | `ttl_cache` | LRU cache with per-entry TTL | Updating an existing key at capacity evicts a different entry, and expired entries keep occupying slots so live entries get evicted instead. |
| 16 | `word_freq` | Word frequency counter: prototype safety | Using plain object dictionary counts[w] = (counts[w] || 0) + 1 corrupts on prototype-named words like 'toString' or '__proto__'. |
