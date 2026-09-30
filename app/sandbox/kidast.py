"""Static analysis of a learner's code: which concepts it uses and how complex it is.

Shared by the check harness (inside the sandbox subprocess) and the server's
analytics, so it must only depend on the standard library.
"""
import ast

CONCEPTS = [
    "output", "variables", "input", "strings", "fstrings", "math", "types",
    "conditions", "random", "while_loops", "for_loops", "turtle", "lists",
    "functions", "dicts", "classes",
]

CONCEPT_LABELS = {
    "output": "Printing", "variables": "Variables", "input": "Input",
    "strings": "Strings", "fstrings": "f-strings", "math": "Math",
    "types": "Types & Conversion", "conditions": "If / Else", "random": "Randomness",
    "while_loops": "While Loops", "for_loops": "For Loops", "turtle": "Turtle Graphics",
    "lists": "Lists", "functions": "Functions", "dicts": "Dictionaries", "classes": "Classes",
}

STR_METHODS = {"upper", "lower", "title", "strip", "split", "join", "replace", "find",
               "startswith", "endswith", "count", "isdigit", "isalpha", "capitalize",
               "center", "ljust", "rjust", "format", "swapcase", "index"}
LIST_METHODS = {"append", "pop", "remove", "insert", "sort", "reverse", "extend", "clear"}
DICT_METHODS = {"items", "keys", "values", "get", "setdefault", "update"}


def parse(source):
    try:
        return ast.parse(source)
    except SyntaxError:
        return None


def _call_name(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def detect_concepts(source, tree=None):
    """Return {concept: count} for every concept that appears in the code."""
    tree = tree or parse(source)
    found = {c: 0 for c in CONCEPTS}
    if tree is None:
        return found
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _call_name(node)
            if name == "print":
                found["output"] += 1
            elif name == "input":
                found["input"] += 1
            elif name in ("int", "float", "str", "bool", "type", "isinstance"):
                found["types"] += 1
            elif name in ("round", "abs", "min", "max", "sum", "pow") or (
                    isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "math"):
                found["math"] += 1
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in STR_METHODS:
                    found["strings"] += 1
                if node.func.attr in LIST_METHODS:
                    found["lists"] += 1
                if node.func.attr in DICT_METHODS:
                    found["dicts"] += 1
            if name in ("list",):
                found["lists"] += 1
            if name in ("dict",):
                found["dicts"] += 1
        elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            found["variables"] += 1
        elif isinstance(node, ast.JoinedStr):
            found["fstrings"] += 1
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            found["strings"] += 0  # plain literals are too common to count
        elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div,
                                                                  ast.FloorDiv, ast.Mod, ast.Pow)):
            found["math"] += 1
        elif isinstance(node, (ast.If, ast.IfExp)):
            found["conditions"] += 1
        elif isinstance(node, ast.While):
            found["while_loops"] += 1
        elif isinstance(node, ast.For):
            found["for_loops"] += 1
        elif isinstance(node, (ast.List, ast.ListComp)):
            found["lists"] += 1
        elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice):
            found["strings"] += 1
        elif isinstance(node, (ast.Dict, ast.DictComp)):
            found["dicts"] += 1
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            found["functions"] += 1
        elif isinstance(node, ast.ClassDef):
            found["classes"] += 1
    if "random" in imports:
        found["random"] += 1 + sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call)
                                   and isinstance(n.func, ast.Attribute)
                                   and isinstance(n.func.value, ast.Name) and n.func.value.id == "random")
    if "turtle" in imports:
        found["turtle"] += 1
    return found


def uses(source, concept, tree=None):
    return detect_concepts(source, tree).get(concept, 0) > 0


def metrics(source):
    """Size and complexity numbers for a piece of code."""
    tree = parse(source)
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    comments = sum(1 for l in source.splitlines() if l.strip().startswith("#"))
    m = {"lines": len(lines), "comments": comments, "syntax_ok": tree is not None,
         "functions": 0, "classes": 0, "branches": 0, "loops": 0, "max_depth": 0,
         "cyclomatic": 1, "names": 0, "calls": 0}
    if tree is None:
        return m
    names = set()

    def depth(node, d=0):
        best = d
        for child in ast.iter_child_nodes(node):
            nd = d + 1 if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try,
                                              ast.FunctionDef, ast.ClassDef)) else d
            best = max(best, depth(child, nd))
        return best

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            m["functions"] += 1
        elif isinstance(node, ast.ClassDef):
            m["classes"] += 1
        elif isinstance(node, (ast.If, ast.IfExp)):
            m["branches"] += 1
            m["cyclomatic"] += 1
        elif isinstance(node, (ast.For, ast.While)):
            m["loops"] += 1
            m["cyclomatic"] += 1
        elif isinstance(node, ast.BoolOp):
            m["cyclomatic"] += len(node.values) - 1
        elif isinstance(node, ast.ExceptHandler):
            m["cyclomatic"] += 1
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, ast.Call):
            m["calls"] += 1
    m["names"] = len(names)
    m["max_depth"] = depth(tree)
    return m


def complexity_score(source):
    """0-100 score combining size, structure, and concept breadth."""
    m = metrics(source)
    if not m["syntax_ok"]:
        return 0
    c = detect_concepts(source)
    breadth = sum(1 for v in c.values() if v)
    score = (min(m["lines"], 120) / 120) * 25 \
        + min(m["cyclomatic"], 25) / 25 * 25 \
        + min(breadth, 12) / 12 * 30 \
        + min(m["functions"] * 4 + m["classes"] * 8, 12) / 12 * 10 \
        + min(m["max_depth"], 5) / 5 * 10
    return round(score)
