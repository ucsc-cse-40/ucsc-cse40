"""
Utilities for extracting and working with Python source code.
"""

import ast
import importlib
import json
import os
import types
import uuid
import re

import cse40.utils

AST_NODE_WHITELIST = [ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef]
ESCAPE = "\a"  # a terminal bell
PATTERN = re.compile(r"^ *\"\\u0007(.*?)(\\n)?\",?$")


def extract_code(path):
    """
    Gets the source code out of a path (to either a notebook or vanilla python).
    """

    code = None

    if path.endswith(".ipynb"):
        code = extract_notebook_code(path)
    elif path.endswith(".py"):
        with open(path, "r") as file:
            lines = file.readlines()
        lines = [line.rstrip() for line in lines]

        code = "\n".join(lines) + "\n"
    else:
        raise ValueError("Unknown extension for extracting code: '%s'." % (path))

    return code


class SourceLine:
    """
    A line in a source block
    """

    def __init__(self, val):
        self.val = val

    def encode(self):
        """prepend an escape character sequence"""
        return ESCAPE + self.val


class SourceCell:
    """
    A Notebook source block
    """

    def __init__(self, d):

        self.d = {}

        for k, v in d.items():
            if k != "source":
                self.d[k] = v

        self.d["source"] = list(map(SourceLine, d["source"]))

    def encode(self):
        return self.d


def object_hook(obj):
    """
    During JSON -> Python, decoding,
    post-process each python object returned to us.
    """

    if isinstance(obj, dict):
        if "cell_type" in obj and obj["cell_type"] == "code":
            return SourceCell(obj)

    return obj


def post_process(line):
    """
    "ESCAPEsource_line", -> source_line
    anything_else -> \n
    """
    result = PATTERN.search(line)

    if result is None:
        return '"#\\n",'
    else:
        return f'"{result.group(1)}\\n",'


class NotebookEncoder(json.JSONEncoder):
    """
    Python -> JSON encoder
    """

    def default(self, obj):
        """
        Handle an object that isn't recognized by the default implementation
        """

        if isinstance(obj, (SourceCell, SourceLine)):
            return obj.encode()

        return json.JSONEncoder.default(self, obj)


def extract_notebook_code(path):
    """
    Extract all the code cells from an iPython notebook.
    A concatenation of all the cells (with a newline between each cell) will be output.
    """

    with open(path, "r") as f:
        notebook = json.load(f, object_hook=object_hook)

    escaped_json = NotebookEncoder(indent=1).encode(notebook)
    replaced_json = (
        '{"source": [\n'
        + "\n".join(map(post_process, escaped_json.split("\n")))
        + '\n"#\\n"\n]}'
    )

    with open("tmp", "w") as f:
        f.write(replaced_json)

    replaced_notebook = json.loads(replaced_json)
    source = "".join(replaced_notebook["source"])
    # print(source)
    return source


def import_path(path, module_name=None):
    if module_name is None:
        module_name = str(uuid.uuid4()).replace("-", "")

    # If it's a notebook, extract the code first and put it in a temp file.
    if path.endswith(".ipynb"):
        source_code = extract_code(path)
        path = cse40.utils.get_temp_path(suffix=".py")
        with open(path, "w") as file:
            file.write(source_code)

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def sanitize_and_import_path(path):
    """
    Get the code from a source file, sanitize it, exec it, and return it as a namespace (module).
    Sanitization in this context means removing things that are not
    imports, functions, constants, and classes.
    A "constant" will be considered an assignment where the LHS is a single variable all in caps.
    """

    filename = os.path.basename(path)
    source_code = extract_code(path)

    return sanitize_and_import_code(source_code, filename)


def sanitize_and_import_code(source_code, filename):
    """
    See sanitize_and_import_path().
    """

    module_ast = sanitize_code(source_code)

    globals_defs = {}
    exec(compile(module_ast, filename=filename, mode="exec"), globals_defs)

    return types.SimpleNamespace(**globals_defs)


def sanitize_code(source_code):
    module_ast = ast.parse(source_code)

    keep_nodes = []
    for node in module_ast.body:
        if type(node) in AST_NODE_WHITELIST:
            keep_nodes.append(node)
            continue

        if not isinstance(node, ast.Assign):
            continue

        if (len(node.targets) != 1) or (not isinstance(node.targets[0], ast.Name)):
            continue

        if node.targets[0].id != node.targets[0].id.upper():
            continue

        keep_nodes.append(node)

    module_ast.body = keep_nodes
    return module_ast
