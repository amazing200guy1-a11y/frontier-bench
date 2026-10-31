import re

def render_template(template: str, context: dict[str, str]) -> str:
    for key, value in context.items():
        pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
        template = re.sub(pattern, str(value), template)
    return template
