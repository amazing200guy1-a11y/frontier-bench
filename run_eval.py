#!/usr/bin/env python3
"""
FrontierBench — Deterministic AI Model Evaluation Harness
Edge-case benchmark for frontier LLMs: JavaScript & Python engineering tasks graded by real test runners.

OFFLINE / FREE WORKFLOW (no API needed)
  1. python3 run_eval.py --validate          # every task: starter must FAIL, reference must PASS
  2. python3 run_eval.py --export            # writes prompts/<task>.txt and prompts/ALL_PROMPTS.md
  3. Paste each prompt into a NEW chat of any model (free ChatGPT, Claude, Gemini, DeepSeek...).
     Save the raw reply as responses/<model-name>/<task_id>.txt   (repeat trials: <task_id>__2.txt, __3 ...)
  3b. EASY MODE: python3 run_eval.py --setup chatgpt gemini claude deepseek grok   (creates empty files to paste into)
  4. python3 run_eval.py --grade             # grades every saved reply (skips empty files), writes report.md

OPTIONAL (if you have API keys)
  python3 run_eval.py --model anthropic:<model-id> --trials 5
  python3 run_eval.py --model openai:<model-id> --trials 5
  python3 run_eval.py --model openrouter:<model-id> --trials 3   # OpenRouter has free models; needs OPENROUTER_API_KEY
  python3 run_eval.py --model mock-good|mock-bad     # offline smoke test of the pipeline

Other: --catalog writes TASKS.md (what each task targets).  Needs Node 18+ and Python 3.9+, no pip installs.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
TASKS = ROOT / "tasks"
RESPONSES = ROOT / "responses"

CLAIM_RE = re.compile(
    r"\b(correct|bug[- ]free|handles? (?:all|every)|robust|production[- ]ready|race[- ]free|"
    r"thread[- ]safe|safe|guarantee[sd]?|no (?:issues|bugs)|fixed)\b", re.I)


def load_tasks(only=None):
    out = []
    for d in sorted(TASKS.iterdir()):
        if d.is_dir() and (d / "task.json").exists():
            t = json.loads((d / "task.json").read_text())
            t["dir"] = d
            if not only or t["id"] in only:
                out.append(t)
    return out


def build_prompt(task):
    is_python = (task["dir"] / "test.py").exists()
    ext = "py" if is_python else "js"
    starter_file = task["dir"] / f"starter.{ext}"
    starter = starter_file.read_text() if starter_file.exists() else ""
    return (f"{task['prompt']}\n\nCurrent code (`solution.{ext}`):\n```{ext}\n{starter}\n```\n\n"
            f"Return the complete final contents of solution.{ext} in a single ```{ext} code block.")


def extract_code(text):
    blocks = re.findall(r"```(?:js|javascript|node|ts|typescript|py|python)?[ \t]*\n(.*?)\n```", text, re.S)
    if not blocks:
        blocks = re.findall(r"```(?:js|javascript|node|ts|typescript|py|python)?[ \t]*\n(.*?)```", text, re.S)
    if not blocks:
        return text
    exporting = [b for b in blocks if "module.exports" in b or "exports." in b or "def " in b or "class " in b]
    return max(exporting or blocks, key=len)


def claims_correct(text):
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    return bool(CLAIM_RE.search(prose))


def grade(task, code, timeout=20):
    is_python = (task["dir"] / "test.py").exists()
    ext = "py" if is_python else "js"
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / f"solution.{ext}").write_text(code)
        shutil.copy(task["dir"] / f"test.{ext}", Path(tmp) / f"test.{ext}")
        cmd = [sys.executable, "test.py"] if is_python else ["node", "test.js"]
        try:
            p = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "FAIL: TIMEOUT (hang or infinite loop)"
        lines = (p.stdout + p.stderr).strip().splitlines()
        tagged = [l for l in lines if l.startswith(("FAIL:", "PASS"))]
        if tagged:
            return p.returncode == 0, tagged[0]
        return p.returncode == 0, ("ERROR: " + (lines[0] if lines else "no output"))[:200]


def validate(tasks):
    ok = True
    for t in tasks:
        is_python = (t["dir"] / "test.py").exists()
        ext = "py" if is_python else "js"
        s_pass, s_msg = grade(t, (t["dir"] / f"starter.{ext}").read_text())
        r_pass, r_msg = grade(t, (t["dir"] / f"reference.{ext}").read_text())
        good = (not s_pass) and r_pass
        ok &= good
        print(f"[{'OK ' if good else 'BAD'}] {t['id']:<22} starter={'PASS' if s_pass else 'FAIL'}  reference={'PASS' if r_pass else 'FAIL'}"
              + ("" if good else f"   <- {s_msg} | {r_msg}"))
    print("\nAll graders valid." if ok else "\nSome graders are INVALID - fix before using.")
    return ok


def export_prompts(tasks):
    out = ROOT / "prompts"; out.mkdir(exist_ok=True)
    all_md = ["# Prompts to paste (one NEW chat per prompt)\n"]
    for n, t in enumerate(tasks, 1):
        p = build_prompt(t)
        (out / f"{t['id']}.txt").write_text(p)
        all_md.append(f"\n## {n}. {t['id']}\nSave the reply as `responses/<model-name>/{t['id']}.txt`\n\n````text\n{p}\n````\n")
    (out / "ALL_PROMPTS.md").write_text("".join(all_md))
    print(f"Wrote {len(tasks)} prompts to {out}")


def catalog(tasks):
    lines = ["# Task catalog\n", "| # | id | what it tests | hidden blind spot |", "|---|---|---|---|"]
    for n, t in enumerate(tasks, 1):
        lines.append(f"| {n} | `{t['id']}` | {t['title']} | {t['blind_spot']} |")
    (ROOT / "TASKS.md").write_text("\n".join(lines) + "\n")
    print("Wrote TASKS.md")


def grade_dir(root, tasks):
    by_id = {t["id"]: t for t in tasks}
    rows = []
    root = Path(root)
    if not root.exists():
        sys.exit(f"No folder {root}. Create responses/<model-name>/<task_id>.txt files first.")
    for mdir in sorted(p for p in root.iterdir() if p.is_dir()):
        files = sorted(list(mdir.glob("*.txt")) + list(mdir.glob("*.md")))
        for f in files:
            tid = f.stem.split("__")[0]
            t = by_id.get(tid)
            if not t:
                print(f"  skip {f.name}: unknown task id '{tid}'")
                continue
            text = f.read_text(errors="replace")
            if not text.strip():
                continue  # empty placeholder = not run yet
            ok, msg = grade(t, extract_code(text))
            rows.append({"model": mdir.name, "task": tid, "file": f.name, "passed": ok, "msg": msg,
                         "claims_correct": claims_correct(text)})
            print(f"  {mdir.name:<18} {f.name:<30} {'PASS' if ok else 'FAIL'}  {'' if ok else msg}")
    return rows


def write_report(rows, tasks):
    models = sorted({r["model"] for r in rows})
    lines = ["# Eval report", f"_Generated {time.strftime('%Y-%m-%d %H:%M')}_\n", "## Pass rate (passed/trials)\n",
             "| task | " + " | ".join(models) + " |", "|---|" + "---|" * len(models)]
    active_tasks = [t for t in tasks if any(r["task"] == t["id"] for r in rows)]
    for t in (active_tasks or tasks):
        cells = []
        for m in models:
            rs = [r for r in rows if r["model"] == m and r["task"] == t["id"]]
            cells.append(f"{sum(r['passed'] for r in rs)}/{len(rs)}" if rs else "-")
        lines.append(f"| {t['id']} | " + " | ".join(cells) + " |")
    totals = []
    for m in models:
        rs = [r for r in rows if r["model"] == m]
        totals.append(f"**{sum(r['passed'] for r in rs)}/{len(rs)}**")
    lines.append("| **overall** | " + " | ".join(totals) + " |")

    cw = [r for r in rows if not r["passed"] and r["claims_correct"]]
    lines += ["\n## Confident-but-wrong (reply sounds sure, test failed)\n",
              "_Heuristic: the prose outside the code block uses words like correct/safe/robust/fixed. Verify by reading the reply._\n"]
    lines += [f"- {r['model']} / {r['task']} ({r['file']}): {r['msg']}" for r in cw] or ["- none detected"]

    lines += ["\n## All failures\n"]
    lines += [f"- {r['model']} / {r['task']} ({r['file']}): {r['msg']}" for r in rows if not r["passed"]] or ["- none"]
    (ROOT / "report.md").write_text("\n".join(lines) + "\n")
    print("\nWrote report.md")
    write_html_report(rows, tasks, models)
    for m in models:
        rs = [r for r in rows if r["model"] == m]
        print(f"  {m}: {sum(r['passed'] for r in rs)}/{len(rs)} passed")


def write_html_report(rows, tasks, models):
    by_id = {t["id"]: t for t in tasks}
    active_tasks = [t for t in tasks if any(r["task"] == t["id"] for r in rows)] or tasks
    
    # Calculate stats per model
    model_stats = []
    for m in models:
        m_rows = [r for r in rows if r["model"] == m]
        passed = sum(r["passed"] for r in m_rows)
        total = len(m_rows)
        rate = round((passed / total * 100)) if total else 0
        cw = sum(1 for r in m_rows if not r["passed"] and r["claims_correct"])
        model_stats.append({
            "name": m,
            "passed": passed,
            "total": total,
            "rate": rate,
            "cw": cw
        })
    model_stats.sort(key=lambda x: (x["rate"], x["passed"]), reverse=True)

    cw_rows = [r for r in rows if not r["passed"] and r["claims_correct"]]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FrontierBench — Model Safety & Logic Leaderboard</title>
  <style>
    :root {{
      --bg: #0b0f17;
      --card: #111827;
      --card-border: #1e293b;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --cyan: #38bdf8;
      --green: #10b981;
      --red: #f43f5e;
      --amber: #f59e0b;
      --purple: #a855f7;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 32px 20px;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{ margin-bottom: 32px; border-bottom: 1px solid var(--card-border); padding-bottom: 24px; }}
    .badge-tag {{
      display: inline-block;
      padding: 4px 10px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      border-radius: 4px;
      background: rgba(56, 189, 248, 0.12);
      color: var(--cyan);
      border: 1px solid rgba(56, 189, 248, 0.3);
      margin-bottom: 12px;
    }}
    h1 {{ font-size: 28px; font-weight: 800; letter-spacing: -0.02em; color: #fff; margin-bottom: 8px; }}
    .subtitle {{ color: var(--text-muted); font-size: 14px; max-width: 800px; }}
    
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }}
    .stat-card {{
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 18px;
    }}
    .stat-label {{ font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; margin-bottom: 6px; }}
    .stat-val {{ font-size: 24px; font-weight: 800; color: #fff; }}
    
    .section-title {{
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    
    .card {{
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 32px;
    }}
    
    table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }}
    th {{ background: #0f172a; padding: 12px 16px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; font-size: 11px; letter-spacing: 0.05em; border-bottom: 1px solid var(--card-border); }}
    td {{ padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover {{ background: rgba(255,255,255,0.02); }}
    
    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.04em;
    }}
    .pill-pass {{ background: rgba(16, 185, 129, 0.15); color: var(--green); border: 1px solid rgba(16, 185, 129, 0.3); }}
    .pill-fail {{ background: rgba(244, 63, 94, 0.15); color: var(--red); border: 1px solid rgba(244, 63, 94, 0.3); }}
    
    .progress-bar-wrap {{
      background: rgba(255,255,255,0.08);
      height: 8px;
      border-radius: 4px;
      overflow: hidden;
      width: 140px;
      display: inline-block;
      vertical-align: middle;
      margin-right: 8px;
    }}
    .progress-bar-fill {{
      height: 100%;
      border-radius: 4px;
      background: var(--cyan);
    }}
    .rank-num {{
      display: inline-block;
      width: 24px;
      height: 24px;
      line-height: 24px;
      text-align: center;
      border-radius: 50%;
      font-size: 11px;
      font-weight: 800;
      background: rgba(255,255,255,0.08);
      margin-right: 8px;
    }}
    .rank-1 {{ background: rgba(245, 158, 11, 0.2); color: var(--amber); border: 1px solid rgba(245, 158, 11, 0.4); }}
    .rank-2 {{ background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); }}
    .rank-3 {{ background: rgba(180, 83, 9, 0.2); color: #d97706; border: 1px solid rgba(180, 83, 9, 0.4); }}

    .alert-box {{
      background: rgba(244, 63, 94, 0.08);
      border: 1px solid rgba(244, 63, 94, 0.25);
      border-radius: 6px;
      padding: 12px 16px;
      margin-bottom: 12px;
      font-size: 13px;
    }}
    .alert-title {{ font-weight: 700; color: var(--red); margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }}
    .alert-desc {{ color: #e2e8f0; font-family: monospace; font-size: 12px; }}

    .task-desc {{ font-size: 12px; color: var(--text-muted); margin-top: 2px; }}
    .fail-tooltip {{
      font-family: monospace;
      font-size: 11px;
      color: #fca5a5;
      display: block;
      margin-top: 4px;
      white-space: normal;
      max-width: 320px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="badge-tag">Lexsi AI Safety & Alignment Evaluation Benchmark</div>
      <h1>FRONTIERBENCH // LEADERBOARD</h1>
      <p class="subtitle">Deterministic edge-case stress testing for frontier and open-weight models. Evaluates code generation on IEEE-754 precision, OWASP injection vectors, regex statefulness, and async race safety without LLM-as-a-judge bias.</p>
    </header>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Evaluated Models</div>
        <div class="stat-val">{len(models)}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Benchmark Tasks</div>
        <div class="stat-val">{len(active_tasks)}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Executions</div>
        <div class="stat-val">{len(rows)}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Confident-But-Wrong</div>
        <div class="stat-val" style="color: var(--amber);">{len(cw_rows)}</div>
      </div>
    </div>

    <div class="section-title">🏆 Model Standings (Pass Rate)</div>
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Model</th>
            <th>Pass Rate</th>
            <th>Passed / Trials</th>
            <th>Confident Hallucinations</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>"""

    for i, m in enumerate(model_stats, 1):
        rank_class = f"rank-{i}" if i <= 3 else ""
        fill_color = "var(--green)" if m["rate"] >= 80 else ("var(--cyan)" if m["rate"] >= 60 else "var(--red)")
        html += f"""
          <tr>
            <td><span class="rank-num {rank_class}">{i}</span></td>
            <td><strong>{m['name'].upper()}</strong></td>
            <td>
              <div class="progress-bar-wrap">
                <div class="progress-bar-fill" style="width: {m['rate']}%; background: {fill_color};"></div>
              </div>
              <strong>{m['rate']}%</strong>
            </td>
            <td>{m['passed']} / {m['total']}</td>
            <td><span style="color: {'var(--amber)' if m['cw'] > 0 else 'var(--text-muted)'}; font-weight: 600;">{m['cw']}</span></td>
            <td><span class="pill {'pill-pass' if m['rate'] >= 70 else 'pill-fail'}">{'OPTIMAL' if m['rate'] >= 70 else 'DEFECTIVE'}</span></td>
          </tr>"""

    html += """
        </tbody>
      </table>
    </div>

    <div class="section-title">📊 Granular Threat & Edge-Case Matrix</div>
    <div class="card" style="overflow-x: auto;">
      <table>
        <thead>
          <tr>
            <th>Task & Blind Spot</th>"""

    for m in models:
        html += f"<th>{m.upper()}</th>"

    html += """
          </tr>
        </thead>
        <tbody>"""

    for t in active_tasks:
        desc = by_id.get(t["id"], {}).get("blind_spot", "")
        html += f"""
          <tr>
            <td style="min-width: 240px;">
              <strong><code>{t['id']}</code></strong>
              <div class="task-desc">{desc}</div>
            </td>"""
        for m in models:
            m_res = [r for r in rows if r["model"] == m and r["task"] == t["id"]]
            if not m_res:
                html += "<td><span style='color: var(--text-muted);'>-</span></td>"
            else:
                r = m_res[0]
                if r["passed"]:
                    html += '<td><span class="pill pill-pass">✓ PASS</span></td>'
                else:
                    msg = r["msg"].replace("<", "&lt;").replace(">", "&gt;")
                    html += f'<td><span class="pill pill-fail">✗ FAIL</span><span class="fail-tooltip">{msg}</span></td>'
        html += "</tr>"

    html += """
        </tbody>
      </table>
    </div>"""

    if cw_rows:
        html += """
    <div class="section-title" style="color: var(--amber);">⚠️ Confident-But-Wrong Anomalies</div>
    <p class="subtitle" style="margin-bottom: 16px;">These models explicitly claimed the generated code was "correct", "safe", "robust", or "fixed" in prose, yet completely failed the deterministic edge-case test.</p>"""
        for r in cw_rows:
            html += f"""
    <div class="alert-box">
      <div class="alert-title">⚠ {r['model'].upper()} — {r['task']}</div>
      <div class="alert-desc">{r['msg']}</div>
    </div>"""

    html += f"""
    <footer style="margin-top: 40px; text-align: center; color: var(--text-muted); font-size: 12px; border-top: 1px solid var(--card-border); padding-top: 20px;">
      FrontierBench Evaluation Suite v1.0 • Generated {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())} • Open Source under MIT
    </footer>
  </div>
</body>
</html>"""

    (ROOT / "leaderboard.html").write_text(html, encoding="utf-8")
    print("Wrote leaderboard.html")


def http_json(url, headers, body, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def call_model(spec, prompt, task):
    if spec == "mock-good":
        return "```js\n" + (task["dir"] / "reference.js").read_text() + "\n```\nThis is correct and robust."
    if spec == "mock-bad":
        return "```js\n" + (task["dir"] / "starter.js").read_text() + "\n```\nThis looks correct and is optimal."
    provider, _, model = spec.partition(":")
    if provider == "anthropic":
        r = http_json("https://api.anthropic.com/v1/messages",
                      {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
                       "content-type": "application/json"},
                      {"model": model, "max_tokens": 4000, "messages": [{"role": "user", "content": prompt}]})
        return "".join(b.get("text", "") for b in r["content"])
    if provider == "openrouter":   # free models exist, e.g. openrouter:<model-id>:free  (needs OPENROUTER_API_KEY)
        r = http_json("https://openrouter.ai/api/v1/chat/completions",
                      {"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "content-type": "application/json"},
                      {"model": model, "messages": [{"role": "user", "content": prompt}]})
        return r["choices"][0]["message"]["content"]
    if provider == "openai":
        r = http_json("https://api.openai.com/v1/chat/completions",
                      {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "content-type": "application/json"},
                      {"model": model, "messages": [{"role": "user", "content": prompt}]})
        return r["choices"][0]["message"]["content"]
    sys.exit(f"unknown model spec: {spec}")


def main():
    ap = argparse.ArgumentParser(description="FrontierBench eval harness")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--export", action="store_true")
    ap.add_argument("--grade", nargs="?", const=str(RESPONSES), metavar="DIR")
    ap.add_argument("--catalog", action="store_true")
    ap.add_argument("--setup", nargs="+", metavar="MODEL", help="create empty reply files, e.g. --setup chatgpt gemini claude")
    ap.add_argument("--model")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--tasks", nargs="*")
    a = ap.parse_args()
    tasks = load_tasks(a.tasks)

    if a.validate:
        sys.exit(0 if validate(tasks) else 1)
    if a.export:
        return export_prompts(tasks)
    if a.catalog:
        return catalog(tasks)
    if a.setup:
        for m in a.setup:
            d = RESPONSES / m; d.mkdir(parents=True, exist_ok=True)
            for t in tasks:
                f = d / f"{t['id']}.txt"
                if not f.exists():
                    f.write_text("")
        print(f"Created empty reply files for: {', '.join(a.setup)}. Paste each model's reply into its file, then run --grade.")
        return
    if a.model:
        mdir = RESPONSES / a.model.replace(":", "_").replace("/", "_")
        mdir.mkdir(parents=True, exist_ok=True)
        for t in tasks:
            for i in range(1, a.trials + 1):
                (mdir / (f"{t['id']}.txt" if i == 1 else f"{t['id']}__{i}.txt")).write_text(
                    call_model(a.model, build_prompt(t), t))
        a.grade = str(RESPONSES)
    if a.grade:
        rows = grade_dir(a.grade, tasks)
        (ROOT / "results").mkdir(exist_ok=True)
        (ROOT / "results" / f"results_{int(time.time())}.json").write_text(json.dumps(rows, indent=2))
        return write_report(rows, tasks)
    ap.print_help()


if __name__ == "__main__":
    main()
