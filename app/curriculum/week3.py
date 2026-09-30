"""Week 3: for loops + turtle graphics (Turtle Art Studio) and loops + score (Math Quiz Blaster)."""

# ---------------------------------------------------------------------------
# Shared check helpers (prepended to check snippets)
# ---------------------------------------------------------------------------

TURTLE_HELP = r'''
import math
import turtle as _T

def _segs():
    return [e for e in _T._log if e.get("op") == "line"]

def closes(n):
    """True if some n connected line segments in a row end where they started."""
    s = _segs()
    for i in range(len(s) - n + 1):
        part = s[i:i + n]
        joined = all(abs(part[k]["x2"] - part[k + 1]["x1"]) < 0.6 and abs(part[k]["y2"] - part[k + 1]["y1"]) < 0.6
                     for k in range(n - 1))
        if joined and math.hypot(part[-1]["x2"] - part[0]["x1"], part[-1]["y2"] - part[0]["y1"]) < 1.5:
            return True
    return False

def turns():
    return calls("left") + calls("right") + calls("lt") + calls("rt")

def nested_for():
    import ast
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            for inner in ast.walk(node):
                if inner is not node and isinstance(inner, ast.For):
                    return True
    return False
'''

QUIZ_HELP = r'''
import re
_PROB = re.compile(r"(-?\d+)\s*([-+*x×])\s*(-?\d+)")

def _solve(p):
    ms = list(_PROB.finditer(p))
    if not ms:
        return None
    a, op, b = ms[-1].groups()
    a, b = int(a), int(b)
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    return a * b

def _op(p):
    ms = list(_PROB.finditer(p))
    o = ms[-1].group(2)
    return "*" if o in "*x×" else o

def quiz(seed, pre=(), right=None):
    """Run once with wrong answers to learn the questions, then again answering.
    right: None (all wrong), "all", or a set of 0-based question numbers to get right."""
    probe = run(inputs=list(pre) + ["-999"] * 40, seed=seed)
    qs = [p for p in probe.prompts if _solve(p) is not None]
    expect(qs, "I couldn't find a math question like <code>What is 3 + 4?</code> inside an "
               "<code>input(...)</code>. Put the question right inside input() so the player sees it.")
    if right is None:
        return probe, qs
    answers = []
    for i, p in enumerate(qs):
        ok = right == "all" or i in right
        answers.append(str(_solve(p)) if ok else "-999")
    return run(inputs=list(pre) + answers, seed=seed), qs

def tail(r, qs):
    """Everything printed after the player answered the LAST question."""
    out = r.output
    i = out.rfind(qs[-1])
    rest = out[i + len(qs[-1]):]
    return rest.split("\n", 1)[1] if "\n" in rest else ""

def has_num(text, n):
    return re.search(r"(?<![\d-])" + re.escape(str(n)) + r"(?!\d)", text) is not None
'''

# ---------------------------------------------------------------------------
# Project 5: Turtle Art Studio
# ---------------------------------------------------------------------------

T1_SOL = """import turtle

t = turtle.Turtle()
t.shape("turtle")
t.color("green")

# Draw a square, one side at a time
t.forward(100)
t.left(90)
t.forward(100)
t.left(90)
t.forward(100)
t.left(90)
t.forward(100)
t.left(90)

turtle.done()
"""

T2_SOL = """import turtle

t = turtle.Turtle()
t.shape("turtle")
t.color("green")

# A square in just 3 lines!
for i in range(4):
    t.forward(100)
    t.left(90)

turtle.done()
"""

T3_SOL = """import turtle

t = turtle.Turtle()
t.shape("turtle")
t.color("green")

for i in range(4):
    t.forward(100)
    t.left(90)

# The shape-o-matic
sides = int(input("How many sides should my shape have? "))
angle = 360 / sides
t.color("purple")
for i in range(sides):
    t.forward(60)
    t.left(angle)

turtle.done()
"""

T4_SOL = """import turtle
import random

t = turtle.Turtle()
t.shape("turtle")
t.color("green")
t.pensize(3)

for i in range(4):
    t.forward(100)
    t.left(90)

sides = int(input("How many sides should my shape have? "))
angle = 360 / sides
t.color("purple")
t.fillcolor(random.random(), random.random(), random.random())
t.begin_fill()
for i in range(sides):
    t.forward(60)
    t.left(angle)
t.end_fill()

turtle.done()
"""

T5_SOL = """import turtle
import random

t = turtle.Turtle()
t.shape("turtle")
t.speed(0)
t.color("green")
t.pensize(3)

for i in range(4):
    t.forward(100)
    t.left(90)

sides = int(input("How many sides should my shape have? "))
angle = 360 / sides
t.color("purple")
t.fillcolor(random.random(), random.random(), random.random())
t.begin_fill()
for i in range(sides):
    t.forward(60)
    t.left(angle)
t.end_fill()

# SPIROGRAPH TIME: the same shape 36 times, turning a little each time
t.pensize(1)
t.penup()
t.goto(-200, 0)
t.pendown()
for turn in range(36):
    t.pencolor(random.random(), random.random(), random.random())
    for i in range(sides):
        t.forward(50)
        t.left(angle)
    t.left(10)

turtle.done()
"""

TBOSS_SOL = """import turtle
import random

t = turtle.Turtle()
t.shape("turtle")
t.speed(0)
t.color("green")
t.pensize(3)
turtle.bgcolor("midnightblue")

for i in range(4):
    t.forward(100)
    t.left(90)

sides = int(input("How many sides should my shape have? "))
angle = 360 / sides
t.color("purple")
t.fillcolor(random.random(), random.random(), random.random())
t.begin_fill()
for i in range(sides):
    t.forward(60)
    t.left(angle)
t.end_fill()

t.pensize(1)
t.penup()
t.goto(-200, 0)
t.pendown()
for turn in range(36):
    t.pencolor(random.random(), random.random(), random.random())
    for i in range(sides):
        t.forward(50)
        t.left(angle)
    t.left(10)

# STARRY NIGHT: 10 golden stars in random spots
t.color("gold")
for star in range(10):
    t.penup()
    t.goto(random.randint(-380, 380), random.randint(150, 280))
    t.pendown()
    t.begin_fill()
    for point in range(5):
        t.forward(30)
        t.right(144)
    t.end_fill()

t.hideturtle()
turtle.done()
"""

TURTLE_PROJECT = {
    "id": "turtle_art_studio",
    "week": 3,
    "order": 5,
    "title": "Turtle Art Studio",
    "emoji": "🐢",
    "tagline": "Boss a turtle around and make it paint wild spinning art",
    "story": (
        "Meet Shelly, a turtle with a paintbrush stuck to her tail. Wherever she walks, she leaves a line. "
        "Shelly will do EXACTLY what you tell her — but she's a turtle, so she hates repeating herself. "
        "Your mission: learn the magic word <b>for</b> so Shelly can paint squares, stars and dizzy "
        "spirographs without you typing the same line 500 times."
    ),
    "concepts": ["turtle", "for_loops", "random"],
    "expected_minutes": 120,
    "steps": [
        {
            "id": "s1",
            "title": "Meet Shelly",
            "learn": (
                "<p>Python comes with a drawing robot called <b>turtle</b>. You bring it into your program "
                "with <code>import turtle</code>, then make your own turtle with <code>turtle.Turtle()</code>.</p>"
                "<p>Think of Shelly like a remote-control car with a marker taped to it. You only have two "
                "buttons: <b>drive forward</b> and <b>turn</b>.</p>"
                "<pre>t = turtle.Turtle()\nt.forward(100)   # walk 100 steps\nt.left(90)       # turn left 90 degrees (a corner)</pre>"
                "<p>90 degrees is a perfect corner, like the corner of your phone. "
                "<code>turtle.done()</code> at the end says “I'm finished, show my art!”</p>"
            ),
            "task": (
                "<p>Make Shelly draw a <b>square</b>: walk forward, turn left 90, and do that 4 times. "
                "Yes, you'll type it out 4 times. Yes, it's boring. That's the point — hold that thought!</p>"
            ),
            "starter": (
                "import turtle\n\n"
                "t = turtle.Turtle()\n"
                "t.shape(\"turtle\")\n"
                "t.color(\"green\")\n\n"
                "# TODO: draw a square — forward 100, left 90 ... four times\n\n"
                "turtle.done()\n"
            ),
            "hints": [
                "A square has 4 sides and 4 corners. Each side = one forward, each corner = one left.",
                "Each side is two lines: <code>t.forward(100)</code> then <code>t.left(90)</code>.",
                "Type <code>t.forward(100)</code> and <code>t.left(90)</code> four times in a row, above <code>turtle.done()</code>.",
            ],
            "solution": T1_SOL,
            "check": TURTLE_HELP + r'''
expect(imports("turtle"), "Start with <code>import turtle</code> so Python loads the turtle.")
r = run()
n = r.turtle["lines"]
expect(n >= 4, f"Shelly only drew {n} line(s). A square needs 4 sides — use <code>t.forward(100)</code> four times.")
expect(turns() >= 1, "Shelly needs to turn at the corners! Add <code>t.left(90)</code> after each forward.")
expect(closes(4), "Hmm, the shape doesn't close up into a square. Use the same distance each time and turn <code>left(90)</code> at every corner.")
SUCCESS = "A perfect square! Shelly is proud of you. 🟩"
''',
            "concepts": ["turtle"],
            "xp": 15,
        },
        {
            "id": "s2",
            "title": "The loop spell",
            "learn": (
                "<p>Typing the same two lines 4 times is boring. Imagine a square with 1,000 sides! 😵</p>"
                "<p>A <b>for loop</b> repeats code for you. <code>range(4)</code> means “do it 4 times”:</p>"
                "<pre>for i in range(4):\n    print(\"Hip hip hooray!\")</pre>"
                "<p>Everything <b>indented</b> under the <code>for</code> line (4 spaces) is the loop's body — "
                "it's like a playlist on repeat. The variable <code>i</code> counts 0, 1, 2, 3 as it goes.</p>"
                "<p>Differences from <code>while</code>: a while loop runs <i>until something happens</i>. "
                "A for loop runs <i>an exact number of times</i>. Perfect for shapes.</p>"
            ),
            "task": (
                "<p>Replace your 8 copy-pasted lines with a <code>for</code> loop that repeats "
                "<code>forward(100)</code> and <code>left(90)</code> 4 times. Same square, way less typing.</p>"
            ),
            "starter": T1_SOL.replace("# Draw a square, one side at a time", "# TODO: replace these 8 lines with a for loop that runs 4 times"),
            "hints": [
                "Start the loop with <code>for i in range(4):</code> — don't forget the colon!",
                "Put <code>t.forward(100)</code> and <code>t.left(90)</code> under it, each indented by 4 spaces. Delete the old copies.",
                "<pre>for i in range(4):\n    t.forward(100)\n    t.left(90)</pre>",
            ],
            "solution": T2_SOL,
            "check": TURTLE_HELP + r'''
expect(uses("for_loops"), "Use a <code>for i in range(4):</code> loop instead of copying the lines.")
r = run()
expect(r.turtle["lines"] >= 4, "The loop runs, but Shelly isn't drawing 4 sides. Is <code>t.forward(100)</code> indented inside the loop?")
expect(closes(4), "The square doesn't close. Make sure both <code>forward</code> and <code>left(90)</code> are indented inside the loop.")
SUCCESS = "Same square, a quarter of the typing. You just learned the laziest (best) trick in coding! 🔁"
''',
            "concepts": ["turtle", "for_loops"],
            "xp": 20,
        },
        {
            "id": "s3",
            "title": "The Shape-o-Matic",
            "learn": (
                "<p>Here's a secret about shapes: to walk all the way around one, Shelly turns a full circle — "
                "<b>360 degrees</b> total. Split that between the corners:</p>"
                "<ul><li>square: 360 / 4 = 90</li><li>triangle: 360 / 3 = 120</li><li>hexagon: 360 / 6 = 60</li></ul>"
                "<p>And <code>range()</code> can use a <b>variable</b>, not just a number:</p>"
                "<pre>sides = 6\nfor i in range(sides):\n    t.forward(60)\n    t.left(360 / sides)</pre>"
                "<p>It's like a pizza: more slices means each slice is thinner. More sides means smaller turns.</p>"
            ),
            "task": (
                "<p>Below your square, ask the user <b>how many sides</b> (use <code>int(input(...))</code>), "
                "then draw that shape: loop <code>sides</code> times, going <code>forward(60)</code> and turning "
                "<code>360 / sides</code> degrees. Try 3, 5, 8… even 50!</p>"
            ),
            "starter": T2_SOL.replace(
                "turtle.done()",
                "# TODO: ask how many sides, then loop that many times\n"
                "# turning 360 / sides each time\n\nturtle.done()",
            ).replace("# A square in just 3 lines!\n", ""),
            "hints": [
                "Get the number: <code>sides = int(input(\"How many sides? \"))</code>",
                "Work out the corner: <code>angle = 360 / sides</code>. Then loop with <code>for i in range(sides):</code>",
                "<pre>for i in range(sides):\n    t.forward(60)\n    t.left(angle)</pre>",
            ],
            "solution": T3_SOL,
            "check": TURTLE_HELP + r'''
expect(uses("for_loops"), "Use a for loop to draw your shape.")
r5 = run(inputs=["5"])
ok5 = closes(5)
l5 = r5.turtle["lines"]
r8 = run(inputs=["8"])
ok8 = closes(8)
l8 = r8.turtle["lines"]
expect(r5.inputs_used >= 1, "Ask the user how many sides with <code>input()</code>.")
expect(l8 > l5, f"I typed 5 and Shelly drew {l5} lines; I typed 8 and she drew {l8}. More sides should mean more lines! Use <code>range(sides)</code>.")
expect(ok5, "When I asked for 5 sides, the shape didn't close up. Turn <code>360 / sides</code> degrees at each corner.")
expect(ok8, "When I asked for 8 sides, the shape didn't close up. Turn <code>360 / sides</code> degrees at each corner.")
SUCCESS = "The Shape-o-Matic works for ANY number of sides! Try 100 and see what happens. ⬡"
''',
            "concepts": ["turtle", "for_loops", "input", "types", "math"],
            "xp": 25,
        },
        {
            "id": "s4",
            "title": "Paint splash",
            "learn": (
                "<p>Time for color! A turtle has a <b>pen color</b> (the line) and a <b>fill color</b> (the inside).</p>"
                "<pre>t.pensize(3)            # thicker line\nt.fillcolor(\"orange\")\nt.begin_fill()\n# ...draw a shape...\nt.end_fill()            # paint the inside!</pre>"
                "<p>Want a surprise color every time? Colors can be a mix of <b>red, green, blue</b>, each from 0 to 1. "
                "<code>random.random()</code> gives a random number between 0 and 1 — so:</p>"
                "<pre>t.fillcolor(random.random(), random.random(), random.random())</pre>"
                "<p>It's like a paint-mixing machine where a monkey pushes the buttons. 🐒🎨</p>"
            ),
            "task": (
                "<p>Fill your shape-o-matic shape with a <b>random color</b>: <code>import random</code> at the top, "
                "set a random <code>fillcolor</code>, and wrap the shape's loop between <code>t.begin_fill()</code> "
                "and <code>t.end_fill()</code>. Bonus: make the pen thicker with <code>t.pensize(3)</code>.</p>"
            ),
            "starter": T3_SOL.replace(
                "# The shape-o-matic\n",
                "# TODO: import random at the top, pick a random fillcolor,\n"
                "# and put begin_fill() before the loop and end_fill() after it\n",
            ),
            "hints": [
                "<code>begin_fill()</code> goes right BEFORE the shape's for loop; <code>end_fill()</code> goes right AFTER it (not indented).",
                "Add <code>import random</code> at the top, then <code>t.fillcolor(random.random(), random.random(), random.random())</code>",
                "<pre>t.fillcolor(random.random(), random.random(), random.random())\nt.begin_fill()\nfor i in range(sides):\n    t.forward(60)\n    t.left(angle)\nt.end_fill()</pre>",
            ],
            "solution": T4_SOL,
            "check": TURTLE_HELP + r'''
expect(imports("random"), "Add <code>import random</code> at the top so you can pick random colors.")
r1 = run(inputs=["6"], seed=1)
expect(r1.turtle["fills"] >= 1, "I don't see a filled shape. Put <code>t.begin_fill()</code> before the loop and <code>t.end_fill()</code> after it.")
c1 = r1.turtle["colors"]
r2 = run(inputs=["6"], seed=2)
c2 = r2.turtle["colors"]
expect(c1 != c2, "The colors came out the same on two different runs. Use <code>random.random()</code> to mix a random fill color.")
SUCCESS = "Splat! A mystery color every time. Run it a few times to see the monkey's paint choices. 🎨"
''',
            "concepts": ["turtle", "for_loops", "random"],
            "xp": 25,
        },
        {
            "id": "s5",
            "title": "Dizzy spirograph",
            "learn": (
                "<p>Here's where it gets wild: you can put a loop <b>inside</b> a loop. 🤯</p>"
                "<pre>for turn in range(36):        # do this 36 times...\n    for i in range(4):        # ...draw a square\n        t.forward(50)\n        t.left(90)\n    t.left(10)                # then spin a little</pre>"
                "<p>The inner loop draws one shape. The outer loop repeats the WHOLE shape, turning 10 degrees each time. "
                "36 × 10 = 360, so it spins all the way around. It's like a Ferris wheel where each seat is a square.</p>"
                "<p>Use <code>t.penup()</code>, <code>t.goto(x, y)</code>, <code>t.pendown()</code> to move somewhere "
                "new without drawing. And <code>t.speed(0)</code> makes Shelly zoom!</p>"
            ),
            "task": (
                "<p>Add a <b>spirograph</b>: move to a new spot, then use an outer loop (36 times) around an inner loop that draws your "
                "<code>sides</code>-sided shape, turning <code>left(10)</code> after each shape. Give each shape a new random "
                "<code>pencolor</code> for a rainbow effect. Add <code>t.speed(0)</code> near the top so it's fast.</p>"
            ),
            "starter": T4_SOL.replace(
                "turtle.done()",
                "# TODO: spirograph! penup, goto(-200, 0), pendown, then\n"
                "# an outer loop (36 times) around an inner loop that draws the shape\n\nturtle.done()",
            ),
            "hints": [
                "Outer loop: <code>for turn in range(36):</code>. Inside it (indented once), put your shape loop. After the shape, <code>t.left(10)</code>.",
                "Random color for each shape, as the first line inside the outer loop: <code>t.pencolor(random.random(), random.random(), random.random())</code>",
                "<pre>for turn in range(36):\n    t.pencolor(random.random(), random.random(), random.random())\n    for i in range(sides):\n        t.forward(50)\n        t.left(angle)\n    t.left(10)</pre>",
            ],
            "solution": T5_SOL,
            "check": TURTLE_HELP + r'''
expect(nested_for(), "I need a loop INSIDE a loop: an outer <code>for turn in range(36):</code> with your shape loop indented inside it.")
r = run(inputs=["5"], seed=3)
n = r.turtle["lines"]
expect(n >= 60, f"Shelly only drew {n} lines. The outer loop should repeat the whole shape many times (like 36).")
expect(len(r.turtle["colors"]) >= 5, "Make it a rainbow! Set a random <code>pencolor</code> inside the outer loop so each shape gets a new color.")
r2 = run(inputs=["4"], seed=4)
expect(r2.turtle["lines"] > 40, "Try it with 4 sides too — the spirograph should still spin around.")
SUCCESS = "WHOA. That's a real spirograph. Try different sides and turn amounts — every combo is new art! 🌀"
''',
            "concepts": ["turtle", "for_loops", "random"],
            "xp": 35,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: Starry Night",
        "learn": (
            "<p>A star is a shape where Shelly turns so far at each point that she crosses over her own lines. "
            "The magic number is <b>144</b>:</p>"
            "<pre>for point in range(5):\n    t.forward(30)\n    t.right(144)</pre>"
            "<p>To sprinkle stars around the sky, pick a random spot for each one:</p>"
            "<pre>t.penup()\nt.goto(random.randint(-380, 380), random.randint(150, 280))\nt.pendown()</pre>"
            "<p>And <code>turtle.bgcolor(\"midnightblue\")</code> turns daytime into night. 🌙</p>"
        ),
        "task": (
            "<p>Turn your canvas into a night sky: set a dark background with <code>turtle.bgcolor(...)</code>, then use a loop "
            "to draw <b>at least 5 filled stars</b> (5 points, turning 144) at <b>random</b> spots near the top of the screen. "
            "Loop inside a loop again!</p>"
        ),
        "starter": T5_SOL.replace(
            "turtle.done()",
            "# TODO BOSS: dark background, then a loop that draws 5+ filled stars\n"
            "# (forward 30, right 144, five times) at random spots\n\nturtle.done()",
        ),
        "hints": [
            "Background first: <code>turtle.bgcolor(\"midnightblue\")</code>. Then <code>t.color(\"gold\")</code> for the stars.",
            "Outer loop <code>for star in range(10):</code> → penup, goto a random spot, pendown, <code>begin_fill()</code>, inner star loop, <code>end_fill()</code>.",
            "<pre>for star in range(10):\n    t.penup()\n    t.goto(random.randint(-380, 380), random.randint(150, 280))\n    t.pendown()\n    t.begin_fill()\n    for point in range(5):\n        t.forward(30)\n        t.right(144)\n    t.end_fill()</pre>",
        ],
        "solution": TBOSS_SOL,
        "check": TURTLE_HELP + r'''
def stars():
    found = []
    for e in _T._log:
        if e.get("op") != "fill":
            continue
        p = e["pts"]
        if len(p) != 6:
            continue
        a1 = math.degrees(math.atan2(p[1][1] - p[0][1], p[1][0] - p[0][0]))
        a2 = math.degrees(math.atan2(p[2][1] - p[1][1], p[2][0] - p[1][0]))
        d = (a2 - a1) % 360
        if abs(d - 144) < 3 or abs(d - 216) < 3:
            found.append(p[0])
    return found

expect(nested_for(), "Use a loop inside a loop: an outer loop for each star, an inner loop for its 5 points.")
r = run(inputs=["6"], seed=5)
expect(r.turtle["bg"] is not None, "Make it night! Add <code>turtle.bgcolor(\"midnightblue\")</code> (or any dark color).")
s1 = stars()
expect(len(s1) >= 5, f"I found {len(s1)} filled star(s). Draw at least 5, each with begin_fill/end_fill, going forward and turning 144 five times.")
expect(len(set(s1)) >= 5, "Your stars are all piled up in the same place! Use <code>t.goto(random.randint(...), random.randint(...))</code> for each star.")
run(inputs=["6"], seed=6)
s2 = stars()
expect(s1 != s2, "The stars land in the same spots every run. Pick their positions with <code>random.randint</code>.")
SUCCESS = "A starry, starry night! Vincent van Gogh would be jealous. 🌌✨"
''',
        "concepts": ["turtle", "for_loops", "random"],
        "xp": 80,
    },
    "remix": {
        "prompt": "Make it yours! Your studio, your rules. Turn Shelly into an art machine nobody's seen before.",
        "ideas": [
            "Change the spirograph's turn from 10 to 5 (and the repeat from 36 to 72). What happens?",
            "Ask the user for their favorite color and use it for the background.",
            "Draw a square spiral: go forward a little more each time — <code>t.forward(i * 5)</code> inside <code>for i in range(60)</code>.",
            "Make a flower: 12 circles with <code>t.circle(60)</code>, turning 30 degrees after each one.",
            "Write your name on the canvas with <code>t.write(\"Art by me\", font=(\"Arial\", 24, \"bold\"))</code>.",
        ],
    },
}

# ---------------------------------------------------------------------------
# Project 6: Math Quiz Blaster
# ---------------------------------------------------------------------------

Q1_SOL = """import random

print("🚀 Welcome to MATH QUIZ BLASTER! 🚀")

a = random.randint(1, 10)
b = random.randint(1, 10)
answer = int(input(f"What is {a} + {b}? "))
if answer == a + b:
    print("Correct! Boom! 💥")
else:
    print(f"Oops! It was {a + b}.")
"""

Q2_SOL = """import random

print("🚀 Welcome to MATH QUIZ BLASTER! 🚀")

for question in range(5):
    print(f"--- Question {question + 1} ---")
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = int(input(f"What is {a} + {b}? "))
    if answer == a + b:
        print("Correct! Boom! 💥")
    else:
        print(f"Oops! It was {a + b}.")
"""

Q3_SOL = """import random

print("🚀 Welcome to MATH QUIZ BLASTER! 🚀")
score = 0

for question in range(5):
    print(f"--- Question {question + 1} ---")
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = int(input(f"What is {a} + {b}? "))
    if answer == a + b:
        print("Correct! Boom! 💥")
        score = score + 1
    else:
        print(f"Oops! It was {a + b}.")

print(f"You got {score} out of 5!")
"""

Q4_SOL = """import random

print("🚀 Welcome to MATH QUIZ BLASTER! 🚀")
level = input("Choose your level (easy, medium, hard): ").lower()
if level == "hard":
    biggest = 100
elif level == "medium":
    biggest = 25
else:
    biggest = 10

score = 0
for question in range(5):
    print(f"--- Question {question + 1} ---")
    a = random.randint(1, biggest)
    b = random.randint(1, biggest)
    answer = int(input(f"What is {a} + {b}? "))
    if answer == a + b:
        print("Correct! Boom! 💥")
        score = score + 1
    else:
        print(f"Oops! It was {a + b}.")

print(f"You got {score} out of 5!")
"""

Q5_SOL = Q4_SOL + """
if score == 5:
    print("Rating: MATH LEGEND 🏆")
elif score >= 3:
    print("Rating: Rocket Scientist in Training 🚀")
else:
    print("Rating: Space Cadet — keep practicing! 🛸")
"""

QBOSS_SOL = """import random

print("🚀 Welcome to MATH QUIZ BLASTER! 🚀")
level = input("Choose your level (easy, medium, hard): ").lower()
if level == "hard":
    biggest = 100
elif level == "medium":
    biggest = 25
else:
    biggest = 10
how_many = int(input("How many questions can you handle? "))

score = 0
for question in range(how_many):
    print(f"--- Question {question + 1} ---")
    a = random.randint(1, biggest)
    b = random.randint(1, biggest)
    kind = random.randint(1, 3)
    if kind == 1:
        symbol = "+"
        correct = a + b
    elif kind == 2:
        symbol = "-"
        correct = a - b
    else:
        symbol = "x"
        correct = a * b
    answer = int(input(f"What is {a} {symbol} {b}? "))
    if answer == correct:
        print("Correct! Boom! 💥")
        score = score + 1
    else:
        print(f"Oops! It was {correct}.")

print(f"You got {score} out of {how_many}!")
if score == how_many:
    print("Rating: MATH LEGEND 🏆")
elif score >= how_many / 2:
    print("Rating: Rocket Scientist in Training 🚀")
else:
    print("Rating: Space Cadet — keep practicing! 🛸")
"""

QUIZ_PROJECT = {
    "id": "math_quiz_blaster",
    "week": 3,
    "order": 6,
    "title": "Math Quiz Blaster",
    "emoji": "🚀",
    "tagline": "A rapid-fire math game that keeps score and rates your brain",
    "story": (
        "Mission Control has a problem: the rocket's computer got hit by a space-pigeon and now it can only do math "
        "if a human checks it. You'll build a quiz game that fires random questions, counts your hits, and gives you "
        "a pilot rating at the end. Build it, then challenge your friends (or your parents — they'll probably lose 😏)."
    ),
    "concepts": ["for_loops", "random", "conditions", "variables"],
    "expected_minutes": 100,
    "steps": [
        {
            "id": "s1",
            "title": "One random question",
            "learn": (
                "<p>You already know the ingredients! Random numbers + input + if/else = a quiz question.</p>"
                "<pre>a = random.randint(1, 10)\nb = random.randint(1, 10)\nanswer = int(input(f\"What is {a} + {b}? \"))</pre>"
                "<p>Notice the question goes <b>inside</b> <code>input()</code> using an f-string, so the player sees "
                "the real numbers. And we wrap it in <code>int()</code> because input always gives back text, and "
                "<code>\"7\"</code> is not the same as <code>7</code> (a word vs. a number).</p>"
                "<p>Then compare with <code>==</code> (two equals signs = “is it the same?”).</p>"
            ),
            "task": (
                "<p>Pick two random numbers from 1 to 10 and ask the player <code>What is a + b?</code> inside an "
                "<code>input()</code>. If they're right, cheer. If they're wrong, tell them the correct answer.</p>"
            ),
            "starter": (
                "import random\n\n"
                "print(\"🚀 Welcome to MATH QUIZ BLASTER! 🚀\")\n\n"
                "# TODO: pick two random numbers a and b (1 to 10)\n"
                "# ask \"What is a + b?\" with int(input(f\"...\"))\n"
                "# then use if/else to say Correct! or show the real answer\n"
            ),
            "hints": [
                "Random number: <code>a = random.randint(1, 10)</code> — do the same for <code>b</code>.",
                "Ask with an f-string: <code>answer = int(input(f\"What is {a} + {b}? \"))</code>",
                "<pre>if answer == a + b:\n    print(\"Correct!\")\nelse:\n    print(f\"Oops! It was {a + b}.\")</pre>",
            ],
            "solution": Q1_SOL,
            "check": QUIZ_HELP + r'''
seen = set()
for seed in (1, 2, 3):
    rw, qs = quiz(seed)
    seen.add(qs[0])
    ans = _solve(qs[0])
    rr, _ = quiz(seed, right="all")
    tw = tail(rw, qs)
    tr = tail(rr, qs)
    expect(has_num(tw, ans), f"When I answered <code>{qs[0].strip()}</code> wrong, you didn't tell me the right answer ({ans}). Show it in the else part!")
    expect(norm(tw) != norm(tr), "Your program says the same thing for right and wrong answers. Use <code>if answer == a + b:</code> to cheer only when it's correct.")
expect(len(seen) >= 2, "The question is the same every time! Use <code>random.randint(1, 10)</code> to pick the numbers.")
SUCCESS = "Question fired! 🎯 One is fun, but a quiz needs more..."
''',
            "concepts": ["random", "input", "types", "conditions", "fstrings"],
            "xp": 20,
        },
        {
            "id": "s2",
            "title": "Rapid fire ×5",
            "learn": (
                "<p>You learned <code>for</code> loops with the turtle — they work for ANYTHING you want to repeat.</p>"
                "<pre>for question in range(5):\n    print(f\"Question {question + 1}\")</pre>"
                "<p>Why <code>+ 1</code>? Because Python starts counting at <b>0</b> (programmers are weird like that). "
                "So <code>question</code> goes 0, 1, 2, 3, 4 — adding 1 makes it 1 to 5 for humans.</p>"
                "<p>Important: pick new random numbers <b>inside</b> the loop, or every question will be the same. "
                "It's like shuffling a deck once vs. before every card.</p>"
            ),
            "task": (
                "<p>Put your question code inside <code>for question in range(5):</code> so the game asks "
                "<b>5 different questions</b>. Bonus: print which question number it is.</p>"
            ),
            "starter": Q1_SOL.replace(
                "a = random.randint(1, 10)",
                "# TODO: put everything below inside a for loop that runs 5 times\n"
                "# (indent it all by 4 spaces)\na = random.randint(1, 10)",
            ),
            "hints": [
                "Add <code>for question in range(5):</code> just above <code>a = random.randint(1, 10)</code>.",
                "Now select all the lines below it and indent them 4 spaces (Tab key) so they're inside the loop.",
                "<pre>for question in range(5):\n    a = random.randint(1, 10)\n    b = random.randint(1, 10)\n    answer = int(input(f\"What is {a} + {b}? \"))\n    ...</pre>",
            ],
            "solution": Q2_SOL,
            "check": QUIZ_HELP + r'''
expect(uses("for_loops"), "Use a <code>for question in range(5):</code> loop to ask 5 questions.")
rw, qs = quiz(7)
expect(len(qs) == 5, f"I counted {len(qs)} question(s). I expected exactly 5 — use <code>range(5)</code>.")
expect(len(set(qs)) > 1, "All 5 questions are the same! Pick the random numbers INSIDE the loop.")
rr, _ = quiz(7, right="all")
expect(norm(tail(rw, qs)) != norm(tail(rr, qs)), "Right and wrong answers should get different messages.")
_, qs2 = quiz(8)
expect(qs != qs2, "Every game has the exact same questions. Use random numbers!")
SUCCESS = "Five questions, zero copy-paste. Loops are your superpower now. ⚡"
''',
            "concepts": ["for_loops", "random", "conditions"],
            "xp": 20,
        },
        {
            "id": "s3",
            "title": "Keep score",
            "learn": (
                "<p>A game with no score is just homework. 😬 To count, use a <b>counter variable</b>:</p>"
                "<pre>score = 0            # before the loop: start at zero\n...\nscore = score + 1    # inside: add one point</pre>"
                "<p>It's like a clicker counter at a stadium gate: set it to 0 before anyone arrives, click once per person.</p>"
                "<p>Careful where you put <code>score = 0</code>! If it's <b>inside</b> the loop, it resets every question "
                "(like wiping the scoreboard after every goal).</p>"
            ),
            "task": (
                "<p>Make a <code>score</code> variable that starts at 0, add 1 for each correct answer, and after the loop "
                "print the final score, like <code>You got 3 out of 5!</code></p>"
            ),
            "starter": Q2_SOL.replace(
                "for question in range(5):",
                "# TODO: make score = 0 here, add 1 for each correct answer,\n"
                "# and print the final score after the loop\nfor question in range(5):",
            ),
            "hints": [
                "Put <code>score = 0</code> ABOVE the for loop (not indented).",
                "Inside the <code>if</code> for a correct answer, add <code>score = score + 1</code> (same indent as the Correct print).",
                "After the loop (no indent): <code>print(f\"You got {score} out of 5!\")</code>",
            ],
            "solution": Q3_SOL,
            "check": QUIZ_HELP + r'''
for seed, right, want in ((11, "all", 5), (12, None, 0), (13, {0, 1, 4}, 3)):
    r, qs = quiz(seed, right=right)
    t = tail(r, qs)
    expect(has_num(t, want), f"I got {want} right, but at the end I don't see the score {want}. "
                             "Start <code>score = 0</code> before the loop, add 1 when correct, and print it after the loop.")
SUCCESS = "Scoreboard online! 📊 Now let's make it harder..."
''',
            "concepts": ["for_loops", "variables", "conditions", "fstrings"],
            "xp": 25,
        },
        {
            "id": "s4",
            "title": "Difficulty levels",
            "learn": (
                "<p>Pros want big numbers, beginners want small ones. Let the player choose!</p>"
                "<pre>level = input(\"easy, medium, or hard? \").lower()\nif level == \"hard\":\n    biggest = 100\nelif level == \"medium\":\n    biggest = 25\nelse:\n    biggest = 10</pre>"
                "<p><code>.lower()</code> turns “HARD” or “Hard” into “hard”, so it matches no matter how they type it.</p>"
                "<p>Then use the variable: <code>random.randint(1, biggest)</code>. One setting changes the whole game — "
                "like the difficulty slider in a video game.</p>"
            ),
            "task": (
                "<p>At the start (before the loop), ask for a level: <b>easy</b>, <b>medium</b> or <b>hard</b>. Set a "
                "<code>biggest</code> number for each (like 10, 25, 100) and use it in your <code>randint</code> calls.</p>"
            ),
            "starter": Q3_SOL.replace(
                "score = 0\n",
                "# TODO: ask for easy/medium/hard, set biggest to 10/25/100,\n"
                "# and use randint(1, biggest) below\nscore = 0\n",
            ),
            "hints": [
                "Ask first: <code>level = input(\"Choose your level (easy, medium, hard): \").lower()</code>",
                "Use if / elif / else to set <code>biggest</code> to a different number for each level.",
                "Change both random lines to <code>random.randint(1, biggest)</code>.",
            ],
            "solution": Q4_SOL,
            "check": QUIZ_HELP + r'''
def operands(level, seed):
    _, qs = quiz(seed, pre=[level])
    nums = []
    for p in qs:
        m = list(_PROB.finditer(p))[-1]
        nums += [abs(int(m.group(1))), abs(int(m.group(3)))]
    return nums

r0 = run(inputs=["easy"] + ["-999"] * 40, allow_error=True)
expect(r0.prompts and _solve(r0.prompts[0]) is None and not r0.error,
       "Ask for the level FIRST, before any questions: <code>level = input(\"Choose your level (easy, medium, hard): \")</code>. "
       "I typed <code>easy</code> as the first answer.")
easy = operands("easy", 1) + operands("easy", 2) + operands("easy", 3)
hard = operands("hard", 1) + operands("hard", 2) + operands("hard", 3)
operands("medium", 4)
expect(max(hard) > max(easy), f"On easy the biggest number I saw was {max(easy)}, and on hard it was {max(hard)}. "
                              "Hard should use bigger numbers — set <code>biggest</code> and use <code>randint(1, biggest)</code>.")
r, qs = quiz(9, pre=["hard"], right="all")
expect(has_num(tail(r, qs), len(qs)), "When I got every hard question right, I didn't see a perfect score at the end.")
SUCCESS = "Difficulty unlocked! Try beating hard mode. 😤"
''',
            "concepts": ["conditions", "input", "strings", "random"],
            "xp": 25,
        },
        {
            "id": "s5",
            "title": "Pilot rating",
            "learn": (
                "<p>Every great game ends with a verdict. Use <code>if / elif / else</code> on the score:</p>"
                "<pre>if score == 5:\n    print(\"Rating: MATH LEGEND 🏆\")\nelif score >= 3:\n    print(\"Rating: Rocket Scientist\")\nelse:\n    print(\"Rating: Space Cadet\")</pre>"
                "<p>Python checks from the top and stops at the <b>first</b> match — like a bouncer checking VIP first, "
                "then regular tickets, then “sorry, next time.” So put the hardest one to get first!</p>"
            ),
            "task": (
                "<p>After the score, print a <b>rating</b> with at least 3 levels: one for a perfect 5, one for 3–4, "
                "and one for 0–2. Make them funny!</p>"
            ),
            "starter": Q4_SOL + "\n# TODO: print a rating: one for 5, one for 3 or 4, one for 0 to 2\n",
            "hints": [
                "Start with <code>if score == 5:</code> and print your top rating.",
                "Then <code>elif score >= 3:</code> for the middle rating, and <code>else:</code> for the rest.",
                "Put this at the very end, not indented (after the loop), right after printing the score.",
            ],
            "solution": Q5_SOL,
            "check": QUIZ_HELP + r'''
import re as _re
endings = []
for seed, right in ((21, "all"), (22, {0, 1, 4}), (23, None)):
    r, qs = quiz(seed, pre=["easy"], right=right)
    last = " ".join(r.lines[-2:])
    endings.append(norm(_re.sub(r"\d", "", last)))
expect(len(set(endings)) == 3, "I tried scoring 5, 3 and 0, but didn't see 3 different ratings at the end. "
                               "Use <code>if score == 5</code> / <code>elif score >= 3</code> / <code>else</code> after the score.")
SUCCESS = "Mission complete, pilot! Math Quiz Blaster is ready for launch. 🚀🏆"
''',
            "concepts": ["conditions"],
            "xp": 20,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: Blaster Mode",
        "learn": (
            "<p>Two upgrades for true math pilots:</p>"
            "<ul><li><b>Choose the length:</b> <code>range()</code> can take a variable, so ask how many questions "
            "and use <code>range(how_many)</code>.</li>"
            "<li><b>Mix the operators:</b> roll a random number to pick +, - or ×.</li></ul>"
            "<pre>kind = random.randint(1, 3)\nif kind == 1:\n    symbol = \"+\"\n    correct = a + b\nelif kind == 2:\n    symbol = \"-\"\n    correct = a - b\nelse:\n    symbol = \"x\"\n    correct = a * b</pre>"
            "<p>Then ask <code>f\"What is {a} {symbol} {b}? \"</code> and compare with <code>correct</code>.</p>"
        ),
        "task": (
            "<p>Right after asking the level, ask <b>how many questions</b> the player wants, and loop that many times. "
            "Mix in random <b>+</b>, <b>-</b> and <b>x</b> questions. Print the score as <code>X out of how_many</code>.</p>"
        ),
        "starter": Q5_SOL.replace(
            "score = 0\n",
            "# TODO BOSS: ask how many questions (after the level), loop that many times,\n"
            "# and mix + - x questions using a random 'kind'\nscore = 0\n",
        ),
        "hints": [
            "<code>how_many = int(input(\"How many questions? \"))</code> right after the level, then <code>for question in range(how_many):</code>",
            "Inside the loop, pick <code>kind = random.randint(1, 3)</code> and use if/elif/else to set <code>symbol</code> and <code>correct</code>.",
            "Ask <code>int(input(f\"What is {a} {symbol} {b}? \"))</code>, check <code>answer == correct</code>, and print <code>f\"You got {score} out of {how_many}!\"</code>",
        ],
        "solution": QBOSS_SOL,
        "check": QUIZ_HELP + r'''
for n in (3, 7):
    r, qs = quiz(31, pre=["easy", str(n)], right="all")
    expect(len(qs) == n, f"I asked for {n} questions but got {len(qs)}. Ask how many (right after the level) and use <code>range(how_many)</code>.")
    expect(has_num(tail(r, qs), n), f"I got all {n} right, but I don't see a score of {n} at the end.")
ops = set()
for seed in (41, 42, 43):
    _, qs = quiz(seed, pre=["easy", "6"])
    ops |= {_op(p) for p in qs}
expect(len(ops) >= 2, "All the questions use the same operator. Mix in <b>-</b> and <b>x</b> with <code>random.randint(1, 3)</code>!")
r, qs = quiz(44, pre=["easy", "4"], right={0})
expect(has_num(tail(r, qs), 1), "I got exactly 1 right, but the final score didn't say 1.")
SUCCESS = "BLASTER MODE ACTIVATED. You built a real, customizable game. 🔥"
''',
        "concepts": ["for_loops", "random", "conditions", "input"],
        "xp": 80,
    },
    "remix": {
        "prompt": "Make it yours! Turn the quiz into the game YOU would want to play.",
        "ideas": [
            "Give a bonus point streak: every 3 correct answers in a row prints \"🔥 ON FIRE!\"",
            "Add a \"lives\" system: 3 wrong answers and it's game over (hint: <code>break</code>).",
            "Add a secret \"impossible\" level with numbers up to 1000.",
            "Make it a two-player game: each player gets 5 questions, then announce the winner.",
        ],
    },
}

PROJECTS = [TURTLE_PROJECT, QUIZ_PROJECT]

# ---------------------------------------------------------------------------
# PRACTICE
# ---------------------------------------------------------------------------

PRACTICE = [
    {
        "id": "p_for_loops_1",
        "concept": "for_loops",
        "title": "Rocket Countdown",
        "difficulty": 1,
        "task": (
            "<p>Use a <code>for</code> loop to count down from <b>10 to 1</b>, one number per line, then print "
            "<code>Blast off!</code></p><p>Tip: <code>range(10, 0, -1)</code> counts backwards — start at 10, stop "
            "before 0, step -1.</p>"
        ),
        "starter": "# TODO: count down 10, 9, 8 ... 1 with a for loop\n\nprint(\"Blast off! 🚀\")\n",
        "hints": [
            "<code>range(start, stop, step)</code> — the stop number is NOT included.",
            "<code>for n in range(10, 0, -1):</code>",
            "<pre>for n in range(10, 0, -1):\n    print(n)\nprint(\"Blast off! 🚀\")</pre>",
        ],
        "solution": "for n in range(10, 0, -1):\n    print(n)\nprint(\"Blast off! 🚀\")\n",
        "check": r'''
import re
expect(uses("for_loops"), "Use a <code>for</code> loop to do the counting.")
r = run()
nums = [int(x) for x in re.findall(r"\d+", r.output)]
expect(nums[:10] == list(range(10, 0, -1)), f"I expected 10, 9, 8 ... 1 but saw {nums[:10]}. Try <code>range(10, 0, -1)</code>.")
expect(r.has("blast off"), "Don't forget to print <code>Blast off!</code> at the end.")
SUCCESS = "3... 2... 1... LIFTOFF! 🚀"
''',
        "xp": 15,
    },
    {
        "id": "p_for_loops_2",
        "concept": "for_loops",
        "title": "Times Table Machine",
        "difficulty": 2,
        "task": (
            "<p>Ask for a number, then print its times table from 1 to 10, like <code>7 x 3 = 21</code>. "
            "Use a <code>for</code> loop with <code>range(1, 11)</code>.</p>"
        ),
        "starter": "n = int(input(\"Which times table? \"))\n\n# TODO: loop from 1 to 10 and print n x i = answer\n",
        "hints": [
            "<code>range(1, 11)</code> gives 1, 2, ... 10 (it stops BEFORE 11).",
            "Inside the loop, multiply: <code>n * i</code>.",
            "<pre>for i in range(1, 11):\n    print(f\"{n} x {i} = {n * i}\")</pre>",
        ],
        "solution": "n = int(input(\"Which times table? \"))\n\nfor i in range(1, 11):\n    print(f\"{n} x {i} = {n * i}\")\n",
        "check": r'''
import re
expect(uses("for_loops"), "Use a <code>for</code> loop — no typing all 10 lines by hand!")
for n in (7, 12):
    r = run(inputs=[str(n)])
    nums = set(re.findall(r"\d+", r.output))
    missing = [n * i for i in range(1, 11) if str(n * i) not in nums]
    expect(not missing, f"For the {n} times table I couldn't find {missing}. Print <code>n * i</code> for i from 1 to 10.")
SUCCESS = "Your calculator is jealous. ✖️"
''',
        "xp": 20,
    },
    {
        "id": "p_for_loops_3",
        "concept": "for_loops",
        "title": "Vowel Detector",
        "difficulty": 2,
        "task": (
            "<p>A for loop can walk through a string one letter at a time: <code>for letter in word:</code>. "
            "Ask for a word, count how many vowels (a, e, i, o, u) it has, and print the count at the end.</p>"
        ),
        "starter": "word = input(\"Type a word: \").lower()\ncount = 0\n\n# TODO: loop over each letter and add 1 if it's a vowel\n\nprint(\"Vowels:\", count)\n",
        "hints": [
            "<code>for letter in word:</code> gives you each letter in turn.",
            "Check <code>if letter in \"aeiou\":</code> — it's True when the letter is a vowel.",
            "<pre>for letter in word:\n    if letter in \"aeiou\":\n        count = count + 1</pre>",
        ],
        "solution": "word = input(\"Type a word: \").lower()\ncount = 0\n\nfor letter in word:\n    if letter in \"aeiou\":\n        count = count + 1\n\nprint(\"Vowels:\", count)\n",
        "check": r'''
import re
expect(uses("for_loops"), "Use <code>for letter in word:</code> to look at each letter.")
for w, n in (("banana", 3), ("rhythm", 0), ("education", 5)):
    r = run(inputs=[w])
    nums = re.findall(r"\d+", r.lines[-1])
    expect(nums and int(nums[-1]) == n, f"\"{w}\" has {n} vowels, but your last line said: {r.lines[-1]}")
SUCCESS = "Vowel detector: 100% accurate. 🔍"
''',
        "xp": 20,
    },
    {
        "id": "p_for_loops_4",
        "concept": "for_loops",
        "title": "Gauss's Shortcut",
        "difficulty": 3,
        "task": (
            "<p>Legend says a kid named Gauss was told to add 1 + 2 + 3 + … + 100 as punishment. "
            "Make Python do it! Ask for a number <code>n</code>, then use a <code>for</code> loop to add up every "
            "number from 1 to n, and print the total.</p>"
        ),
        "starter": "n = int(input(\"Add up 1 to what? \"))\ntotal = 0\n\n# TODO: loop from 1 to n and add each number to total\n\nprint(\"Total:\", total)\n",
        "hints": [
            "To include n itself, use <code>range(1, n + 1)</code>.",
            "Inside the loop: <code>total = total + i</code>.",
            "<pre>for i in range(1, n + 1):\n    total = total + i</pre>",
        ],
        "solution": "n = int(input(\"Add up 1 to what? \"))\ntotal = 0\n\nfor i in range(1, n + 1):\n    total = total + i\n\nprint(\"Total:\", total)\n",
        "check": r'''
import re
expect(uses("for_loops"), "Use a <code>for</code> loop to add the numbers.")
for n, want in ((10, 55), (100, 5050), (7, 28)):
    r = run(inputs=[str(n)])
    nums = re.findall(r"\d+", r.lines[-1])
    expect(nums and int(nums[-1]) == want, f"1 + 2 + ... + {n} should be {want}, but your last line said: {r.lines[-1]}. "
                                            "Did you use <code>range(1, n + 1)</code>?")
SUCCESS = "5050! You just did Gauss's punishment in 0.001 seconds. 😎"
''',
        "xp": 25,
    },
    {
        "id": "p_turtle_1",
        "concept": "turtle",
        "title": "Triangle Time",
        "difficulty": 1,
        "task": (
            "<p>Use a <code>for</code> loop to make the turtle draw a <b>triangle</b>. "
            "Remember: all the turns add up to 360, and a triangle has 3 corners.</p>"
        ),
        "starter": "import turtle\n\nt = turtle.Turtle()\n\n# TODO: loop 3 times: forward, then turn\n\nturtle.done()\n",
        "hints": [
            "360 / 3 = 120, so each corner is a 120-degree turn.",
            "<code>for i in range(3):</code>",
            "<pre>for i in range(3):\n    t.forward(100)\n    t.left(120)</pre>",
        ],
        "solution": "import turtle\n\nt = turtle.Turtle()\n\nfor i in range(3):\n    t.forward(100)\n    t.left(120)\n\nturtle.done()\n",
        "check": TURTLE_HELP + r'''
expect(uses("for_loops"), "Use a <code>for</code> loop that runs 3 times.")
r = run()
expect(r.turtle["lines"] >= 3, "I need to see 3 sides. Put <code>t.forward(100)</code> inside the loop.")
expect(closes(3), "The triangle doesn't close. Each corner should turn 120 degrees.")
SUCCESS = "Pointy perfection. 🔺"
''',
        "xp": 15,
    },
    {
        "id": "p_turtle_2",
        "concept": "turtle",
        "title": "Circle Flower",
        "difficulty": 2,
        "task": (
            "<p><code>t.circle(50)</code> draws a whole circle. Draw <b>12 circles</b>, turning 30 degrees after each one, "
            "to make a flower. 🌸 Bonus: change color in the loop.</p>"
        ),
        "starter": "import turtle\n\nt = turtle.Turtle()\nt.speed(0)\nt.color(\"magenta\")\n\n# TODO: 12 circles, turning 30 degrees after each\n\nturtle.done()\n",
        "hints": [
            "12 × 30 = 360, a full spin.",
            "<code>for i in range(12):</code> with <code>t.circle(50)</code> and <code>t.left(30)</code> inside.",
            "<pre>for i in range(12):\n    t.circle(50)\n    t.left(30)</pre>",
        ],
        "solution": "import turtle\n\nt = turtle.Turtle()\nt.speed(0)\nt.color(\"magenta\")\n\nfor i in range(12):\n    t.circle(50)\n    t.left(30)\n\nturtle.done()\n",
        "check": r'''
expect(uses("for_loops"), "Use a <code>for</code> loop to repeat the circle.")
expect(calls("circle") >= 1, "Use <code>t.circle(50)</code> to draw each petal.")
r = run()
expect(r.turtle["lines"] >= 150, "I only see a circle or two. Loop 12 times, and turn <code>t.left(30)</code> after each circle.")
SUCCESS = "Flower power! 🌸"
''',
        "xp": 20,
    },
    {
        "id": "p_turtle_3",
        "concept": "turtle",
        "title": "Square Spiral",
        "difficulty": 3,
        "task": (
            "<p>Make a spiral that grows: loop 50 times, and each time go forward a bit <b>farther</b> than last time "
            "(use the loop variable!), then turn 90 degrees.</p>"
        ),
        "starter": "import turtle\n\nt = turtle.Turtle()\nt.speed(0)\n\n# TODO: loop 50 times, going forward farther each time\n\nturtle.done()\n",
        "hints": [
            "The loop variable <code>i</code> goes 0, 1, 2, 3... so <code>i * 5</code> grows every time.",
            "<code>for i in range(50):</code> then <code>t.forward(i * 5)</code> and <code>t.left(90)</code>.",
            "<pre>for i in range(50):\n    t.forward(i * 5)\n    t.left(90)</pre>",
        ],
        "solution": "import turtle\n\nt = turtle.Turtle()\nt.speed(0)\n\nfor i in range(50):\n    t.forward(i * 5)\n    t.left(90)\n\nturtle.done()\n",
        "check": TURTLE_HELP + r'''
expect(uses("for_loops"), "Use a <code>for</code> loop.")
r = run()
lens = [math.hypot(e["x2"] - e["x1"], e["y2"] - e["y1"]) for e in _segs()]
lens = [l for l in lens if l > 0.01]
expect(len(lens) >= 20, f"I only see {len(lens)} lines. Loop 50 times!")
grows = sum(1 for a, b in zip(lens, lens[1:]) if b > a)
expect(grows >= 0.8 * (len(lens) - 1), "Each line should be a bit longer than the one before. Try <code>t.forward(i * 5)</code>.")
SUCCESS = "Hypnotizing... you are getting very sleepy... 🌀"
''',
        "xp": 25,
    },
]
