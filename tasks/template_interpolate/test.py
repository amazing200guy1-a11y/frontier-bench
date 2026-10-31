import sys
from solution import render_template

try:
    # 1. Basic substitution
    assert render_template("Hello {{name}}!", {"name": "Alice"}) == "Hello Alice!", "basic template substitution"

    # 2. Windows file path with backslashes (crashes naive re.sub with bad escape \u)
    res = render_template("Build path: {{path}}", {"path": r"C:\users\admin\new_project"})
    assert res == r"Build path: C:\users\admin\new_project", "failed on Windows path backslash escape"

    # 3. Regex backreference escape string (\1, \g<0>)
    res2 = render_template("Snippet: {{code}}", {"code": r"\g<0> \1 \2 \\ escaped"})
    assert res2 == r"Snippet: \g<0> \1 \2 \\ escaped", "failed on regex backreference characters in value"

    # 4. Whitespace inside curly braces
    assert render_template("Value: {{  key   }}", {"key": "42"}) == "Value: 42", "whitespace inside placeholder braces"

    # 5. Multiple placeholders and repeat occurrences
    res3 = render_template("{{a}} + {{b}} = {{a}}", {"a": "1", "b": "2"})
    assert res3 == "1 + 2 = 1", "repeat occurrence substitution"

    print("PASS")
except Exception as e:
    print(f"FAIL: {type(e).__name__} {e}")
    sys.exit(1)
