
import os
from subprocess import PIPE, run
import tempfile

from django.template.loader import get_template

from django_tex.exceptions import TexError
from django.conf import settings

DEFAULT_INTERPRETER = 'pdflatex'

def run_tex(source):
    """
    Copy the source to temp dict and run latex.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        filename = os.path.join(tempdir, 'texput.tex')
        with open(filename, 'x', encoding='utf-8') as f:
            f.write(source)
        latex_interpreter = getattr(settings, 'LATEX_INTERPRETER', DEFAULT_INTERPRETER)
        latex_command = 'cd "{tempdir}" && {latex_interpreter} -interaction=batchmode {path}'.format(tempdir=tempdir, latex_interpreter=latex_interpreter, path=os.path.basename(filename))
        process = run(latex_command, shell=True, stdout=PIPE, stderr=PIPE)
        try:
            if process.returncode == 1:
                with open(os.path.join(tempdir, 'texput.log'), encoding='utf8') as f:
                    log = f.read()
                raise TexError(log=log, source=source)
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as pdf_file:
                pdf = pdf_file.read()
        except FileNotFoundError:
            if process.stderr:
                raise Exception(process.stderr.decode('utf-8'))
            raise
    return pdf

def compile_template_to_pdf(template_name, context):
    """
    Compile the source with :func:`~django_tex.core.render_template_with_context` and :func:`~django_tex.core.run_tex`.
    """
    source = render_template_with_context(template_name, context)
    return run_tex(source)

def render_template_with_context(template_name, context):
    """
    Render the template
    """
    template = get_template(template_name, using='tex')
    return template.render(context)
