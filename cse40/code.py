"""
Utilities for extracting and working with Python source code.
"""

import ast
import importlib
import json
import os
import types
import uuid

import cse40.utils

AST_NODE_WHITELIST = [ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef]

def extract_code(path):
    """
    Gets the source code out of a path (to either a notebook or vanilla python).
    """

    code = None

    if (path.endswith('.ipynb')):
        code = extract_notebook_code(path)
    elif (path.endswith('.py')):
        with open(path, 'r') as file:
            lines = file.readlines()
        lines = [line.rstrip() for line in lines]

        code = "\n".join(lines) + "\n"
    else:
        raise ValueError("Unknown extension for extracting code: '%s'." % (path))

    return code

def extract_notebook_code(path):
    """
    Extract all the code cells from an iPython notebook.
    A concatenation of all the cells (with a newline between each cell) will be output.
    """

    with open(path, 'r') as file:
        notebook = json.load(file)

    contents = []

    for cell in notebook['cells']:
        if (cell['cell_type'] != 'code'):
            continue

        contents.append((''.join(cell['source'])))

    return "\n".join(contents) + "\n"

def import_path(path, module_name = None):
    if (module_name is None):
        module_name = str(uuid.uuid4()).replace('-', '')

    # If it's a notebook, extract the code first and put it in a temp file.
    if (path.endswith('.ipynb')):
        source_code = extract_code(path)
        path = cse40.utils.get_temp_path(suffix = '.py')
        with open(path, 'w') as file:
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
    exec(compile(module_ast, filename = filename, mode = "exec"), globals_defs)

    return types.SimpleNamespace(**globals_defs)

def sanitize_code(source_code):
    module_ast = ast.parse(source_code)

    keep_nodes = []
    for node in module_ast.body:
        if (type(node) in AST_NODE_WHITELIST):
            keep_nodes.append(node)
            continue

        if (not isinstance(node, ast.Assign)):
            continue

        if ((len(node.targets) != 1) or (not isinstance(node.targets[0], ast.Name))):
            continue

        if (node.targets[0].id != node.targets[0].id.upper()):
            continue

        keep_nodes.append(node)

    module_ast.body = keep_nodes
    return module_ast
