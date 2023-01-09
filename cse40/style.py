import contextlib
import os
import sys

from flake8.api import legacy as flake8

import cse40.code
import cse40.question
import cse40.utils

# For codes, see:
# flake8: https://flake8.pycqa.org/en/latest/user/error-codes.html
# pycodestyle: https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes
STYLE_OPTIONS = {
    'max_line_length': 100,
    'max_doc_length': 100,
    'select': 'E,W,F',
    'show_source': True,
    'color': 'never',
    'ignore': [
        # Don't force continuation line alignment.
        'E128',

        # Allow spaces around parameter/keyword equals.
        'E251',

        # Don't force two spaces between functions/class.
        # We only want one space.
        'E302',
        'E305',

        # Allow lambdas to be assigned into a local variable.
        'E731',

        # PEP-8 recommends breaking a line before a binary operator.
        # This was a recent reversal of idiomatic Python.
        # W503 enforces the old style, while W504 enforces the new style.
        'W503',
    ]
}

class Style(cse40.question.Question):
    """
    A question that can be added to assignments that checks style.
    """

    def __init__(self, path, max_points = 5, replacement_name = 'assignment.py'):
        super().__init__("Style", max_points)
        self._path = path
        self._replacement_name = replacement_name

    def score_question(self, *args, **kwargs):
        error_count, style_output = check_style(self._path,
                replace_output_path = self._replacement_name)

        if (error_count == 0):
            self.add_message("Style is clean!")
            self.full_credit()
        else:
            self.add_message("Code has %d style issues (shown below)."
                    + " Note that line numbers will be offset because of iPython notebooks."
                    % (error_count))
            self.add_message("--- Style Output BEGIN ---")
            self.add_message("\n".join(style_output))
            self.add_message("--- Style Output END ---")
            self.score = max(0, self.max_points - error_count)

def check_style(path, replace_output_path = None):
    cleanup_paths = []

    if (path.endswith('.py')):
        pass
    elif (path.endswith('.ipynb')):
        contents = cse40.code.extract_notebook_code(path)

        temp_path = cse40.utils.get_temp_path(prefix = 'style_', suffix = '_notebook')
        cleanup_paths.append(temp_path)
        with open(temp_path, 'w') as file:
            file.write(contents)

        if (replace_output_path is None):
            replace_output_path = path

        path = temp_path
    else:
        raise ValueError("Can only check style on .py or .ipynb files, got '%s'." % (path))

    path = os.path.realpath(path)

    output_path = cse40.utils.get_temp_path(prefix = 'style_', suffix = '_output')
    cleanup_paths.append(output_path)

    # argparse (used by flake8) will look for a program name on sys.argv[0].
    if (len(sys.argv) == 0):
        sys.argv = ['']

    style_guide = flake8.get_style_guide(**STYLE_OPTIONS)

    with open(output_path, 'w') as file:
        with contextlib.redirect_stdout(file):
            report = style_guide.check_files([path])

    with open(output_path, 'r') as file:
        lines = file.readlines()

    lines = [line.rstrip() for line in lines]

    if (replace_output_path is not None):
        lines = [line.replace(path, replace_output_path) for line in lines]

    for path in cleanup_paths:
        cse40.utils.remove_dirent(path)

    return (report._application.result_count, lines)

def main(path):
    count, lines = check_style(path)
    print("Found %d style errors." % (count))

    if (count > 0):
        print('---')
        print("\n".join(lines))
        print('---')

    sys.exit(count)

def _load_args(args):
    args.pop(0)
    if (len(args) != 1 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 -m cse40.style <py or ipynb path>", file = sys.stderr)
        sys.exit(1)

    path = os.path.abspath(args.pop(0))

    return path

if (__name__ == '__main__'):
    main(_load_args(sys.argv))
