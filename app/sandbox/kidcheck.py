"""Automated check harness. Runs in its own subprocess.

stdin:  JSON {"source": <learner code>, "check": <python check snippet>}
stdout: JSON {"passed": bool, "message": str, "output": str, "turtle": {...}}

Names available inside a check snippet:
    source                    the learner's code (str)
    run(inputs=None, seed=None, allow_error=False) -> Result
    expect(condition, message)
    uses(concept)             True if the code uses a concept (see kidast.CONCEPTS)
    calls(name)               how many times a function/method name is called in the code
    defines(name)             True if the code defines a function/class with that name
    imports(module)           True if the code imports that module
    capture(fn, *args, inputs=None) -> (return_value, printed_text)
    norm(text)                lower-case and collapse whitespace
    CheckFail                 raise CheckFail("message") to fail with a custom message

Result fields: output, lines, ns, error, error_msg, turtle (dict of stats),
prompts (list of input prompts), and helpers r.has(text), r.fn(name), r.cls(name), r.var(name).
"""
import ast
import builtins
import contextlib
import io
import json
import os
import random
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kidast  # noqa: E402
import turtle as _turtle  # noqa: E402  (the shim in this folder)

_real_stdout = sys.stdout
_real_input = builtins.input
_real_sleep = time.sleep
LAST = None
SOURCE = ""


class CheckFail(Exception):
    pass


class OutOfInputs(Exception):
    pass


def norm(text):
    return " ".join(str(text).lower().split())


class Result:
    def __init__(self):
        self.output = ""
        self.ns = {}
        self.error = None
        self.error_msg = ""
        self.error_line = None
        self.turtle = {}
        self.prompts = []
        self.inputs_used = 0

    @property
    def lines(self):
        return [l for l in self.output.splitlines() if l.strip()]

    def has(self, text):
        return norm(text) in norm(self.output)

    def var(self, name):
        if name not in self.ns:
            raise CheckFail(f"I couldn't find a variable called `{name}`. Did you create it?")
        return self.ns[name]

    def fn(self, name):
        f = self.ns.get(name)
        if not callable(f):
            raise CheckFail(f"I couldn't find a function called `{name}`. Did you `def {name}(...)`?")
        return f

    def cls(self, name):
        c = self.ns.get(name)
        if not isinstance(c, type):
            raise CheckFail(f"I couldn't find a class called `{name}`. Did you write `class {name}:`?")
        return c


def _friendly_crash(r):
    where = f" on line {r.error_line}" if r.error_line else ""
    return f"Your program crashed{where} with {r.error}: {r.error_msg}"


def _make_input(queue, buf, r):
    def fake_input(prompt=""):
        buf.write(str(prompt))
        r.prompts.append(str(prompt))
        if not queue:
            raise OutOfInputs()
        v = queue.pop(0)
        r.inputs_used += 1
        buf.write(v + "\n")
        return v
    return fake_input


def run(inputs=None, seed=None, allow_error=False, source_override=None):
    src = source_override if source_override is not None else SOURCE
    r = Result()
    queue = [str(x) for x in (inputs or [])]
    buf = io.StringIO()
    _turtle._reset()
    random.seed(seed if seed is not None else 12345)
    ns = {"__name__": "__main__"}
    builtins.input = _make_input(queue, buf, r)
    time.sleep = lambda *a, **k: None
    try:
        code = compile(src, "main.py", "exec")
        with contextlib.redirect_stdout(buf):
            exec(code, ns)
    except SystemExit:
        pass
    except OutOfInputs:
        r.error = "OutOfInputs"
        r.error_msg = ("your program asked for more input than I expected. "
                       "Check that your loop stops when it should!")
    except SyntaxError as e:
        r.error = type(e).__name__
        r.error_msg = e.msg
        r.error_line = e.lineno
    except BaseException as e:  # noqa: BLE001 - we report every crash kindly
        r.error = type(e).__name__
        r.error_msg = str(e)
        for fr in reversed(traceback.extract_tb(e.__traceback__)):
            if fr.filename == "main.py":
                r.error_line = fr.lineno
                break
    finally:
        builtins.input = _real_input
        time.sleep = _real_sleep
    r.output = buf.getvalue()
    r.ns = ns
    r.turtle = _turtle._stats()
    global LAST
    LAST = r
    if r.error and not allow_error:
        raise CheckFail(_friendly_crash(r))
    return r


def capture(fn, *args, inputs=None):
    buf = io.StringIO()
    queue = [str(x) for x in (inputs or [])]
    dummy = Result()
    builtins.input = _make_input(queue, buf, dummy)
    time.sleep = lambda *a, **k: None
    try:
        with contextlib.redirect_stdout(buf):
            value = fn(*args)
    except OutOfInputs:
        raise CheckFail("Your function asked for more input than I expected.")
    except CheckFail:
        raise
    except Exception as e:  # noqa: BLE001
        name = getattr(fn, "__name__", "your function")
        raise CheckFail(f"When I called `{name}{args if len(args) != 1 else '(' + repr(args[0]) + ')'}` "
                        f"it crashed with {type(e).__name__}: {e}")
    finally:
        builtins.input = _real_input
        time.sleep = _real_sleep
    return value, buf.getvalue()


def expect(condition, message):
    if not condition:
        raise CheckFail(message)


def main():
    global SOURCE
    payload = json.loads(sys.stdin.read())
    SOURCE = payload["source"]
    tree = kidast.parse(SOURCE)
    out = {"passed": False, "message": "", "output": "", "turtle": {}}
    if tree is None:
        try:
            compile(SOURCE, "main.py", "exec")
        except SyntaxError as e:
            out["message"] = f"Python can't read line {e.lineno} yet: {e.msg}. Fix that first, then check again."
            out["error"] = "SyntaxError"
        _real_stdout.write(json.dumps(out))
        return

    concepts = kidast.detect_concepts(SOURCE, tree)
    call_counts = {}
    defined = set()
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            n = kidast._call_name(node)
            if n:
                call_counts[n] = call_counts.get(n, 0) + 1
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    scope = {
        "source": SOURCE, "tree": tree, "run": run, "expect": expect, "capture": capture,
        "norm": norm, "CheckFail": CheckFail,
        "uses": lambda c: concepts.get(c, 0) > 0,
        "calls": lambda name: call_counts.get(name, 0),
        "defines": lambda name: name in defined,
        "imports": lambda m: m in imported,
    }
    try:
        exec(compile(payload["check"], "check", "exec"), scope)
        out["passed"] = True
        out["message"] = scope.get("SUCCESS", "")
    except CheckFail as e:
        out["message"] = str(e)
    except Exception as e:  # noqa: BLE001 - a broken check should not look like the kid's fault
        out["message"] = f"(The checker itself had a problem: {type(e).__name__}: {e})"
        out["checker_error"] = True
    if LAST is not None:
        out["output"] = LAST.output[-3000:]
        out["turtle"] = LAST.turtle
    _real_stdout.write(json.dumps(out))


if __name__ == "__main__":
    main()
