"""Interactive runner. Runs main.py and speaks a JSON-lines protocol on stdout.

Messages sent:  {"t":"out","d":text} {"t":"err","d":text} {"t":"input"}
                {"t":"turtle","e":[events]} {"t":"error",...} {"t":"end","ok":bool}
stdin carries one line per answered input().
"""
import builtins
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_real = sys.__stdout__
_turtle_buf = []
MAX_OUT = 300_000
_sent = 0


def _send(obj):
    global _sent
    line = json.dumps(obj)
    _sent += len(line)
    if _sent > MAX_OUT:
        _flush_turtle()
        _real.write(json.dumps({"t": "err", "d": "\n[Stopped: your program printed way too much. Is a loop running forever?]\n"}) + "\n")
        _real.write(json.dumps({"t": "end", "ok": False, "reason": "output_limit"}) + "\n")
        _real.flush()
        os._exit(3)
    _real.write(line + "\n")
    _real.flush()


def _flush_turtle():
    if _turtle_buf:
        batch = list(_turtle_buf)
        _turtle_buf.clear()
        _send({"t": "turtle", "e": batch})


def _turtle_sink(ev):
    _turtle_buf.append(ev)
    if len(_turtle_buf) >= 200:
        _flush_turtle()


class _Stream:
    def __init__(self, kind):
        self.kind = kind

    def write(self, s):
        if s:
            _flush_turtle()
            _send({"t": self.kind, "d": s})
        return len(s)

    def flush(self):
        pass

    def isatty(self):
        return False


def _input(prompt=""):
    if prompt:
        sys.stdout.write(str(prompt))
    _flush_turtle()
    _send({"t": "input"})
    line = sys.stdin.readline()
    if not line:
        raise EOFError("input was closed")
    return line.rstrip("\r\n")


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        source = f.read()
    sys.stdout = _Stream("out")
    sys.stderr = _Stream("err")
    builtins.input = _input
    import turtle
    turtle._sink = _turtle_sink
    ok = True
    try:
        code = compile(source, "main.py", "exec")
        exec(code, {"__name__": "__main__"})
    except SystemExit:
        pass
    except KeyboardInterrupt:
        ok = False
    except BaseException as e:  # noqa: BLE001
        ok = False
        line = getattr(e, "lineno", None) if isinstance(e, SyntaxError) else None
        if line is None:
            for fr in reversed(traceback.extract_tb(e.__traceback__)):
                if fr.filename == "main.py":
                    line = fr.lineno
                    break
        exc_only = "".join(traceback.TracebackException.from_exception(e).format_exception_only()).strip()
        frames = [f"line {fr.lineno}, in {fr.name}" for fr in traceback.extract_tb(e.__traceback__)
                  if fr.filename == "main.py"]
        code_line = ""
        if line and 0 < line <= len(source.splitlines()):
            code_line = source.splitlines()[line - 1]
        _flush_turtle()
        _send({"t": "error", "type": type(e).__name__, "msg": str(e) if not isinstance(e, SyntaxError) else e.msg,
               "line": line, "code_line": code_line, "text": exc_only, "frames": frames})
    _flush_turtle()
    _send({"t": "end", "ok": ok})


if __name__ == "__main__":
    main()
