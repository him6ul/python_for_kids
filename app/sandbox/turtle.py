"""A kid-friendly stand-in for the standard `turtle` module.

It computes the drawing itself (positions, circles, fills) and emits simple
events ("line", "move", "fill", "dot", "write", ...). In live mode the events
are streamed to the browser canvas; in check mode they are recorded so that
automated checks can inspect what was drawn.
"""
import math

_log = []          # every event, used by checks
_sink = None       # set by the live runner: callable(event_dict)
_turtles = []
_default = None
_screen = None
_colormode = 1.0
MAX_EVENTS = 60000

COLOR_NAMES = None  # browser understands CSS names; we pass them through


class Terminator(Exception):
    pass


def _emit(ev):
    if len(_log) >= MAX_EVENTS:
        if len(_log) == MAX_EVENTS:
            _log.append({"op": "limit"})
            if _sink:
                _sink({"op": "limit"})
        return
    _log.append(ev)
    if _sink:
        _sink(ev)


def _reset():
    """Used by the checker between runs."""
    global _default, _screen, _colormode
    _log.clear()
    _turtles.clear()
    _default = None
    _screen = None
    _colormode = 1.0


def _css(*args):
    if len(args) == 1:
        a = args[0]
        if isinstance(a, (tuple, list)) and len(a) == 3:
            args = tuple(a)
        else:
            return str(a)
    if len(args) == 3:
        r, g, b = args
        if _colormode == 1.0 and all(isinstance(v, (int, float)) and v <= 1 for v in (r, g, b)):
            r, g, b = r * 255, g * 255, b * 255
        return "rgb(%d,%d,%d)" % (int(r), int(g), int(b))
    raise ValueError("I don't understand that color. Try a name like 'red' or three numbers.")


class Turtle:
    def __init__(self, shape="classic", visible=True, **kw):
        self._id = len(_turtles)
        _turtles.append(self)
        self._x = 0.0
        self._y = 0.0
        self._h = 0.0
        self._pen = True
        self._pencolor = "black"
        self._fillcolor = "black"
        self._width = 1
        self._filling = False
        self._poly = []
        self._visible = visible
        self._speed = 3
        self._shape = shape
        _emit({"op": "new", "id": self._id, "shape": shape})

    # ---- movement -------------------------------------------------------
    def _goto(self, nx, ny):
        ev = {"id": self._id, "x1": round(self._x, 2), "y1": round(self._y, 2),
              "x2": round(nx, 2), "y2": round(ny, 2)}
        if self._pen:
            ev.update(op="line", c=self._pencolor, w=self._width, s=self._speed)
        else:
            ev.update(op="move", s=self._speed)
        _emit(ev)
        self._x, self._y = nx, ny
        if self._filling:
            self._poly.append((round(nx, 2), round(ny, 2)))

    def forward(self, distance):
        r = math.radians(self._h)
        self._goto(self._x + distance * math.cos(r), self._y + distance * math.sin(r))

    fd = forward

    def back(self, distance):
        self.forward(-distance)

    bk = backward = back

    def left(self, angle):
        self._h = (self._h + angle) % 360
        _emit({"op": "turn", "id": self._id, "h": round(self._h, 2)})

    lt = left

    def right(self, angle):
        self.left(-angle)

    rt = right

    def goto(self, x, y=None):
        if y is None:
            x, y = x
        self._goto(float(x), float(y))

    setpos = setposition = goto

    def setx(self, x):
        self._goto(float(x), self._y)

    def sety(self, y):
        self._goto(self._x, float(y))

    def setheading(self, angle):
        self._h = angle % 360
        _emit({"op": "turn", "id": self._id, "h": round(self._h, 2)})

    seth = setheading

    def home(self):
        self._goto(0.0, 0.0)
        self.setheading(0)

    def circle(self, radius, extent=None, steps=None):
        if extent is None:
            extent = 360
        frac = abs(extent) / 360
        if steps is None:
            steps = 1 + int(min(11 + abs(radius) / 6.0, 59.0) * frac)
        steps = max(1, int(steps))
        w = extent / steps
        w2 = 0.5 * w
        length = 2.0 * radius * math.sin(math.radians(w2))
        if radius < 0:
            length, w, w2 = -length, -w, -w2
        self._h = (self._h + w2) % 360
        for _ in range(steps):
            self.forward(length)
            self._h = (self._h + w) % 360
        self._h = (self._h - w2) % 360
        _emit({"op": "turn", "id": self._id, "h": round(self._h, 2)})

    def dot(self, size=None, *color):
        if size is None:
            size = max(self._width + 4, self._width * 2)
        c = _css(*color) if color else self._pencolor
        _emit({"op": "dot", "id": self._id, "x": round(self._x, 2), "y": round(self._y, 2), "r": size, "c": c})

    def stamp(self):
        _emit({"op": "stamp", "id": self._id, "x": round(self._x, 2), "y": round(self._y, 2),
               "h": self._h, "c": self._fillcolor, "shape": self._shape})
        return len(_log)

    def write(self, arg, move=False, align="left", font=("Arial", 8, "normal")):
        size = font[1] if isinstance(font, (tuple, list)) and len(font) > 1 else 8
        _emit({"op": "write", "id": self._id, "x": round(self._x, 2), "y": round(self._y, 2),
               "text": str(arg), "align": align, "size": size, "c": self._pencolor})

    # ---- pen ------------------------------------------------------------
    def penup(self):
        self._pen = False

    pu = up = penup

    def pendown(self):
        self._pen = True

    pd = down = pendown

    def isdown(self):
        return self._pen

    def pensize(self, width=None):
        if width is None:
            return self._width
        self._width = width

    width = pensize

    def pencolor(self, *args):
        if not args:
            return self._pencolor
        self._pencolor = _css(*args)

    def fillcolor(self, *args):
        if not args:
            return self._fillcolor
        self._fillcolor = _css(*args)

    def color(self, *args):
        if not args:
            return self._pencolor, self._fillcolor
        if len(args) == 2:
            self._pencolor, self._fillcolor = _css(args[0]), _css(args[1])
        else:
            self._pencolor = self._fillcolor = _css(*args)

    def begin_fill(self):
        self._filling = True
        self._poly = [(round(self._x, 2), round(self._y, 2))]

    def end_fill(self):
        if self._filling and len(self._poly) > 2:
            _emit({"op": "fill", "id": self._id, "pts": self._poly, "c": self._fillcolor})
        self._filling = False
        self._poly = []

    def filling(self):
        return self._filling

    # ---- state ----------------------------------------------------------
    def speed(self, s=None):
        if s is None:
            return self._speed
        names = {"fastest": 0, "fast": 10, "normal": 6, "slow": 3, "slowest": 1}
        self._speed = names.get(s, s) if isinstance(s, str) else s

    def shape(self, name=None):
        if name is None:
            return self._shape
        self._shape = name
        _emit({"op": "shape", "id": self._id, "shape": name})

    def shapesize(self, *a, **k):
        pass

    turtlesize = shapesize

    def hideturtle(self):
        self._visible = False
        _emit({"op": "hide", "id": self._id})

    ht = hideturtle

    def showturtle(self):
        self._visible = True
        _emit({"op": "show", "id": self._id})

    st = showturtle

    def isvisible(self):
        return self._visible

    def position(self):
        return (round(self._x, 2), round(self._y, 2))

    pos = position

    def xcor(self):
        return round(self._x, 2)

    def ycor(self):
        return round(self._y, 2)

    def heading(self):
        return round(self._h, 2)

    def distance(self, x, y=None):
        if y is None:
            x, y = x.pos() if isinstance(x, Turtle) else x
        return math.hypot(x - self._x, y - self._y)

    def towards(self, x, y=None):
        if y is None:
            x, y = x.pos() if isinstance(x, Turtle) else x
        return math.degrees(math.atan2(y - self._y, x - self._x)) % 360

    def clear(self):
        _emit({"op": "clear", "id": self._id})

    def reset(self):
        self.clear()
        self._x = self._y = self._h = 0.0

    def onclick(self, *a, **k):
        pass

    onrelease = ondrag = onclick

    def getscreen(self):
        return Screen()


Pen = RawTurtle = Turtle


class _Screen:
    def bgcolor(self, *args):
        if args:
            _emit({"op": "bg", "c": _css(*args)})

    def title(self, text):
        _emit({"op": "title", "text": str(text)})

    def colormode(self, mode=None):
        global _colormode
        if mode is None:
            return _colormode
        _colormode = mode

    def setup(self, *a, **k):
        pass

    def screensize(self, *a, **k):
        return (800, 600)

    def window_width(self):
        return 800

    def window_height(self):
        return 600

    def tracer(self, *a, **k):
        pass

    def update(self):
        pass

    def delay(self, *a, **k):
        pass

    def listen(self, *a, **k):
        pass

    def onkey(self, *a, **k):
        pass

    onkeypress = onkeyrelease = onclick = onscreenclick = ontimer = onkey

    def mainloop(self):
        _emit({"op": "done"})

    done = exitonclick = mainloop

    def bye(self):
        pass

    def clear(self):
        _emit({"op": "clearall"})

    clearscreen = resetscreen = clear

    def turtles(self):
        return list(_turtles)


def Screen():
    global _screen
    if _screen is None:
        _screen = _Screen()
    return _screen


def _t():
    global _default
    if _default is None:
        _default = Turtle()
    return _default


# ---- module-level functions (the "procedural" turtle API) ---------------
def _make(name):
    def f(*a, **k):
        return getattr(_t(), name)(*a, **k)
    f.__name__ = name
    return f


for _n in ["forward", "fd", "back", "bk", "backward", "left", "lt", "right", "rt", "goto",
           "setpos", "setposition", "setx", "sety", "setheading", "seth", "home", "circle",
           "dot", "stamp", "write", "penup", "pu", "up", "pendown", "pd", "down", "isdown",
           "pensize", "width", "pencolor", "fillcolor", "color", "begin_fill", "end_fill",
           "filling", "speed", "shape", "shapesize", "turtlesize", "hideturtle", "ht",
           "showturtle", "st", "isvisible", "position", "pos", "xcor", "ycor", "heading",
           "distance", "towards", "reset", "onclick"]:
    globals()[_n] = _make(_n)


def clear():
    _t().clear()


def bgcolor(*a):
    Screen().bgcolor(*a)


def title(t):
    Screen().title(t)


def colormode(m=None):
    return Screen().colormode(m)


def done():
    Screen().mainloop()


mainloop = exitonclick = done


def setup(*a, **k):
    pass


def tracer(*a, **k):
    pass


def update():
    pass


def listen(*a, **k):
    pass


def onkey(*a, **k):
    pass


onkeypress = onkeyrelease = onscreenclick = ontimer = onkey


def bye():
    pass


# ---- helpers used by automated checks -----------------------------------
def _stats():
    lines = [e for e in _log if e.get("op") == "line"]
    colors = {e["c"] for e in lines} | {e["c"] for e in _log if e.get("op") in ("fill", "dot")}
    dist = sum(math.hypot(e["x2"] - e["x1"], e["y2"] - e["y1"]) for e in lines)
    return {
        "lines": len(lines),
        "fills": sum(1 for e in _log if e.get("op") == "fill"),
        "dots": sum(1 for e in _log if e.get("op") == "dot"),
        "writes": [e["text"] for e in _log if e.get("op") == "write"],
        "colors": sorted(colors),
        "distance": round(dist, 1),
        "turtles": len(_turtles),
        "bg": next((e["c"] for e in reversed(_log) if e.get("op") == "bg"), None),
        "events": len(_log),
    }
