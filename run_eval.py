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
    for m in models:
        rs = [r for r in rows if r["model"] == m]
        print(f"  {m}: {sum(r['passed'] for r in rs)}/{len(rs)} passed")


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
