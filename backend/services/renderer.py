import os
import re
from jinja2 import Environment, FileSystemLoader

def escape_latex(value):
    """
    Escape characters for LaTeX.
    """
    if not isinstance(value, str):
        return value
    
    # Define escaping rules
    LATEX_SUBS = (
        (re.compile(r'\\'), r'\\textbackslash '),
        (re.compile(r'([{}_#%&$])'), r'\\\1'),
        (re.compile(r'~'), r'\~{}'),
        (re.compile(r'\^'), r'\^{}'),
        (re.compile(r'"'), r"''"),
        (re.compile(r'\.\.\.+'), r'\\ldots '),
    )

    for pattern, replacement in LATEX_SUBS:
        value = pattern.sub(replacement, value)
    
    return value

def get_jinja_env():
    # Templates directory is in the parent of services/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')
    
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        block_start_string='[%',
        block_end_string='%]',
        variable_start_string='[[',
        variable_end_string=']]',
        comment_start_string='[#',
        comment_end_string='#]',
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    env.filters['escape_latex'] = escape_latex
    return env

def render_resume_template(template_name: str, data: dict) -> str:
    """
    Render a LaTeX template with the given data.
    """
    env = get_jinja_env()
    template = env.get_template(template_name)
    return template.render(**data)

def render_resume_template_from_string(tex_source: str, data: dict) -> str:
    """
    Render a LaTeX template from a raw string with the given data.
    """
    env = get_jinja_env()
    template = env.from_string(tex_source)
    return template.render(**data)
