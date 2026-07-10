import os
import re

from jinja2 import Environment, FileSystemLoader


def escape_latex(value, diff=False):
    """
    Escape characters for LaTeX. Returns empty string for None/non-string values.
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)

    # Extract **text** and ~~text~~ to protect them during the main escape
    bold_parts = []
    del_parts = []

    def bold_repl(m):
        bold_parts.append(m.group(1))
        return f"BBBOLD{len(bold_parts) - 1}EEE"

    def del_repl(m):
        del_parts.append(m.group(1))
        return f"DDDEL{len(del_parts) - 1}EEE"

    value = re.sub(r"\*\*(.*?)\*\*", bold_repl, value)
    value = re.sub(r"~~(.*?)~~", del_repl, value)

    # Define escaping rules
    LATEX_SUBS = (
        (re.compile(r"\\"), r"\\textbackslash "),
        (re.compile(r"([{}_#%&$])"), r"\\\1"),
        (re.compile(r"~"), r"\~{}"),
        (re.compile(r"\^"), r"\^{}"),
        (re.compile(r'"'), r"''"),
        (re.compile(r"\.\.\.+"), r"\\ldots "),
    )

    for pattern, replacement in LATEX_SUBS:
        value = pattern.sub(replacement, value)

    # Restore bold parts and del parts
    for i, part in enumerate(bold_parts):
        escaped_part = part
        for pattern, replacement in LATEX_SUBS:
            escaped_part = pattern.sub(replacement, escaped_part)
        if diff:
            value = value.replace(f"BBBOLD{i}EEE", f"\\added{{{escaped_part}}}")
        else:
            value = value.replace(f"BBBOLD{i}EEE", f"\\textbf{{{escaped_part}}}")

    for i, part in enumerate(del_parts):
        escaped_part = part
        for pattern, replacement in LATEX_SUBS:
            escaped_part = pattern.sub(replacement, escaped_part)
        if diff:
            value = value.replace(f"DDDEL{i}EEE", f"\\deleted{{{escaped_part}}}")
        else:
            value = value.replace(f"DDDEL{i}EEE", "")

    return value


def get_jinja_env(diff=False):
    # Templates directory is in the parent of services/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, "templates")

    env = Environment(
        loader=FileSystemLoader(templates_dir),
        block_start_string="[%",
        block_end_string="%]",
        variable_start_string="[[",
        variable_end_string="]]",
        comment_start_string="[#",
        comment_end_string="#]",
        trim_blocks=True,
        lstrip_blocks=True,
    )

    env.filters["escape_latex"] = lambda val: escape_latex(val, diff=diff)
    return env


def render_resume_template(template_name: str, data: dict, diff=False) -> str:
    """
    Render a LaTeX template with the given data.
    """
    env = get_jinja_env(diff=diff)
    template = env.get_template(template_name)
    return template.render(**data)


def render_resume_template_from_string(tex_source: str, data: dict, diff=False) -> str:
    """
    Render a LaTeX template from a raw string with the given data.
    """
    env = get_jinja_env(diff=diff)
    template = env.from_string(tex_source)
    return template.render(**data)
