import re

def render_template(template: str, context: dict[str, str]) -> str:
    """Safely renders template replacing {{key}} with literal values from context."""
    if not isinstance(template, str) or not isinstance(context, dict):
        return ""

    for key, value in context.items():
        if not isinstance(key, str):
            continue
        str_val = str(value) if value is not None else ""
        pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
        # A callable replacement prevents re.sub from treating backslashes as regex backreferences
        template = re.sub(pattern, lambda _: str_val, template)

    return template
