"""Week 1: Robot Buddy (project 1) and Pizza Party Planner (project 2).

New concepts: output, variables, input, strings, fstrings, math, types.
"""


def _code(s):
    return s.strip("\n") + "\n"


# Shared helpers prepended to checks that need them.
_H = r'''
import re, ast

def after_inputs(r, inputs):
    """Text printed after the program read all of `inputs` (skips prompts and echoed answers)."""
    out = r.output
    pos = 0
    for p, v in zip(r.prompts, inputs):
        chunk = p + str(v) + "\n"
        i = out.find(chunk, pos)
        if i >= 0:
            pos = i + len(chunk)
    return out[pos:]

def nums(text):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", text.replace(",", ""))]

def has_num(text, n, tol=0.011):
    return any(abs(x - n) < tol for x in nums(text))
'''


def _check(body):
    return _H + "\n" + body.strip("\n") + "\n"


# ---------------------------------------------------------------------------
# Project 1: Robot Buddy
# ---------------------------------------------------------------------------

_RB1 = _code(r'''
print("Beep boop! Hello, human!")
''')

_RB2 = _code(r'''
print("Beep boop! Hello, human!")
robot_name = "Bolt"
print("My name is", robot_name)
''')

_RB3 = _code(r'''
print("Beep boop! Hello, human!")
robot_name = "Bolt"
print("My name is", robot_name)
name = input("What's your name? ")
print("Nice to meet you,", name)
''')

_RB4 = _code(r'''
print("Beep boop! Hello, human!")
robot_name = "Bolt"
print("My name is", robot_name)
name = input("What's your name? ")
print("Nice to meet you,", name)
print("LET ME SAY IT LOUDER:", name.upper())
print("Your name has", len(name), "letters. I counted them with my laser eyes.")
''')

_RB5 = _code(r'''
print("Beep boop! Hello, human!")
robot_name = "Bolt"
print(f"My name is {robot_name}")
name = input("What's your name? ")
print(f"Nice to meet you, {name}!")
print(f"LET ME SAY IT LOUDER: {name.upper()}")
print(f"Your name has {len(name)} letters. I counted them with my laser eyes.")
food = input("What's your favorite food? ")
print(f"{food}?! {name}, I LOVE {food}! Well... I eat batteries. But still.")
''')

_RB_BOSS = _code(r'''
print("Beep boop! Hello, human!")
robot_name = "Bolt"
print(f"My name is {robot_name}")
name = input("What's your name? ")
print(f"Nice to meet you, {name}!")
print(f"LET ME SAY IT LOUDER: {name.upper()}")
print(f"Your name has {len(name)} letters. I counted them with my laser eyes.")
food = input("What's your favorite food? ")
print(f"{food}?! {name}, I LOVE {food}! Well... I eat batteries. But still.")
last = input("Top secret question... what's your last name? ")
code_name = (name[:3] + last[-3:]).upper()
print(f"Your secret agent code name is: {code_name}")
''')

ROBOT_BUDDY = {
    "id": "robot_buddy",
    "week": 1,
    "order": 1,
    "title": "Robot Buddy",
    "emoji": "🤖",
    "tagline": "Build a chatbot that greets you by name (and roasts your snacks)",
    "story": ("You found a dusty robot in the garage, next to a box of old pizza crusts. "
              "It blinks once, but it can't talk yet... because nobody ever programmed it. "
              "That's your job. By the end of this project your robot will know its name, "
              "learn YOUR name, yell it back at you, and have opinions about your favorite food."),
    "concepts": ["output", "variables", "input", "strings", "fstrings"],
    "expected_minutes": 90,
    "steps": [
        {
            "id": "s1",
            "title": "Wake up the robot",
            "learn": (
                "<p>Programs are just instructions that the computer follows, top to bottom, one line at a time. "
                "The very first instruction every coder learns is <code>print</code>. It makes the computer "
                "show something on the screen.</p>"
                "<pre>print(\"Hello, human!\")</pre>"
                "<p>Think of <code>print</code> as your robot's mouth. Whatever you put inside the "
                "<code>( )</code> brackets comes out. The words go inside <b>quotes</b> so Python knows "
                "they're words to say, not instructions to follow.</p>"
                "<p>Press <b>Run</b> to see what your program does. Press <b>Check</b> when you think it's done.</p>"
            ),
            "task": ("<p>Make your robot say its very first words! Use <code>print</code> to show a greeting, "
                     "like <code>Beep boop! Hello, human!</code> (you can pick your own words).</p>"),
            "starter": _code(r'''
# Your robot is asleep. Wake it up!
# TODO: use print() to make your robot say hello.
'''),
            "hints": [
                "The command that makes Python show words is called print.",
                "Words need quotes around them, and the whole thing goes inside round brackets.",
                "Try this line: print(\"Beep boop! Hello, human!\")",
            ],
            "solution": _RB1,
            "check": _check(r'''
expect(calls("print") >= 1, "I don't see a print(...) yet. Your robot needs print to talk!")
r = run()
expect(len(r.lines) >= 1, "Your program ran but didn't show anything. Put some words in quotes inside print( ).")
SUCCESS = "IT'S ALIVE! Your robot just said its first words. ⚡"
'''),
            "concepts": ["output"],
            "xp": 10,
        },
        {
            "id": "s2",
            "title": "Give it a name",
            "learn": (
                "<p>A <b>variable</b> is a labeled box where your program keeps something to use later. "
                "You make one with <code>=</code>:</p>"
                "<pre>robot_name = \"Bolt\"\nprint(\"My name is\", robot_name)</pre>"
                "<p>Output: <code>My name is Bolt</code></p>"
                "<p>Notice: <code>robot_name</code> has <b>no quotes</b> in the print. No quotes means "
                "\"go look in the box called robot_name\". With quotes it would literally print the word robot_name.</p>"
                "<p>The comma in <code>print(a, b)</code> glues things together with a space in between. "
                "Why bother with a variable? Because if you rename your robot later, you change ONE line and every "
                "print updates. Like changing your gamer tag once instead of on every post.</p>"
            ),
            "task": ("<p>Make a variable called <code>robot_name</code> and put your robot's name in it (any name you like). "
                     "Then add a <code>print</code> that uses <code>robot_name</code> so the robot introduces itself.</p>"),
            "starter": _code(r'''
print("Beep boop! Hello, human!")

# TODO: make a variable called robot_name and put your robot's name in it
# TODO: print a line that uses robot_name, like: My name is ...
'''),
            "hints": [
                "A variable is made with a name, an equals sign, and a value: box = \"stuff\".",
                "Make robot_name = \"...\" and then print it using the variable name WITHOUT quotes.",
                "robot_name = \"Bolt\"\nprint(\"My name is\", robot_name)",
            ],
            "solution": _RB2,
            "check": _check(r'''
r = run()
name = r.var("robot_name")
expect(isinstance(name, str) and name.strip() != "",
       "robot_name should hold some text in quotes, like robot_name = \"Bolt\".")
used = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "print":
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and sub.id == "robot_name":
                used = True
expect(used, "You made robot_name, but no print uses it yet. Try print(\"My name is\", robot_name) - no quotes around robot_name!")
expect(r.has(name), f"I expected your robot to say its name ({name}) but I didn't see it in the output.")
SUCCESS = f"{name} has entered the chat. 🤖"
'''),
            "concepts": ["variables", "output"],
            "xp": 15,
        },
        {
            "id": "s3",
            "title": "Ask for your name",
            "learn": (
                "<p>So far your robot only talks. Let's make it <b>listen</b>. <code>input</code> shows a question, "
                "waits for the user to type something and press Enter, and hands you back what they typed.</p>"
                "<pre>name = input(\"What's your name? \")\nprint(\"Nice to meet you,\", name)</pre>"
                "<p>If you type <code>Zara</code>, the robot says <code>Nice to meet you, Zara</code>. Type something "
                "else and it says something else. Your program just became <b>interactive</b>!</p>"
                "<p>It's like the robot holding out an empty box: you drop your answer in, and the label on the box is "
                "<code>name</code>. Leave a space at the end of the question so the answer doesn't squish against it.</p>"
            ),
            "task": ("<p>Make your robot ask <b>What's your name?</b> using <code>input</code>, save the answer in a "
                     "variable called <code>name</code>, and then greet the person using their name.</p>"),
            "starter": _code(r'''
print("Beep boop! Hello, human!")
robot_name = "Bolt"
print("My name is", robot_name)

# TODO: ask the human for their name with input() and store it in a variable called name
# TODO: greet them using their name
'''),
            "hints": [
                "input(\"question \") shows the question and gives back whatever was typed.",
                "Store it: name = input(\"What's your name? \"). Then print a greeting that includes name.",
                "name = input(\"What's your name? \")\nprint(\"Nice to meet you,\", name)",
            ],
            "solution": _RB3,
            "check": _check(r'''
for who in ["Zara", "Maximilian"]:
    r = run(inputs=[who])
    expect(len(r.prompts) >= 1, "Your robot never asks anything. Use input(\"What's your name? \") to ask.")
    after = after_inputs(r, [who])
    expect(who.lower() in after.lower(),
           f"When I typed {who}, your robot didn't say {who} back afterwards. Print a greeting that uses your name variable.")
SUCCESS = "Your robot knows your name now. It will never forget. (Until you close the tab.) 👋"
'''),
            "concepts": ["input", "variables", "output"],
            "xp": 20,
        },
        {
            "id": "s4",
            "title": "SHOUT IT!",
            "learn": (
                "<p>Text in Python is called a <b>string</b> (like letters on a string of beads). Strings come with "
                "built-in superpowers. Put a dot after a string and call one:</p>"
                "<pre>name = \"Zara\"\nprint(name.upper())   # ZARA\nprint(name.lower())   # zara\nprint(len(name))      # 4</pre>"
                "<p><code>.upper()</code> makes a LOUD copy of the string. <code>len(...)</code> counts how many "
                "characters are in it (spaces count too!).</p>"
                "<p>Think of <code>.upper()</code> as the robot turning its volume knob to 11. The original "
                "<code>name</code> doesn't change; you just get a shouty copy.</p>"
            ),
            "task": ("<p>After greeting the human, make your robot:</p><ul>"
                     "<li>shout their name in ALL CAPS using <code>.upper()</code></li>"
                     "<li>say how many letters their name has using <code>len()</code></li></ul>"),
            "starter": _code(r'''
print("Beep boop! Hello, human!")
robot_name = "Bolt"
print("My name is", robot_name)
name = input("What's your name? ")
print("Nice to meet you,", name)

# TODO: shout their name in capitals with name.upper()
# TODO: tell them how many letters their name has with len(name)
'''),
            "hints": [
                "name.upper() gives you a capital-letters copy of name. len(name) gives a number.",
                "You can put both inside print with commas: print(\"Your name has\", len(name), \"letters\")",
                "print(\"LET ME SAY IT LOUDER:\", name.upper())\nprint(\"Your name has\", len(name), \"letters\")",
            ],
            "solution": _RB4,
            "check": _check(r'''
for who in ["Zara", "Maximilian"]:
    r = run(inputs=[who])
    after = after_inputs(r, [who])
    expect(who.upper() in after,
           f"When I typed {who}, I expected to see {who.upper()} in capitals. Try name.upper().")
    expect(has_num(after, len(who)),
           f"{who} has {len(who)} letters, but I didn't see the number {len(who)}. Try len(name).")
SUCCESS = "LOUD AND PROUD! Your robot can count and shout. 📢"
'''),
            "concepts": ["strings", "output"],
            "xp": 20,
        },
        {
            "id": "s5",
            "title": "f-string glow-up",
            "learn": (
                "<p>Gluing words with commas works, but it gets messy. An <b>f-string</b> lets you drop variables "
                "right into a sentence. Put an <code>f</code> before the quotes and wrap variables in "
                "<code>{curly braces}</code>:</p>"
                "<pre>food = \"tacos\"\nprint(f\"{food}?! I LOVE {food}!\")\n# tacos?! I LOVE tacos!</pre>"
                "<p>It's like a Mad Lib: the sentence has blanks, and Python fills them in. You can even put code in "
                "the blanks, like <code>{name.upper()}</code> or <code>{len(name)}</code>.</p>"
            ),
            "task": ("<p>Make your robot ask <b>What's your favorite food?</b> (save it in <code>food</code>). "
                     "Then use an <b>f-string</b> to reply with a sentence that includes BOTH the person's name and "
                     "their food. Bonus: switch your other prints to f-strings too.</p>"),
            "starter": _code(r'''
print("Beep boop! Hello, human!")
robot_name = "Bolt"
print("My name is", robot_name)
name = input("What's your name? ")
print("Nice to meet you,", name)
print("LET ME SAY IT LOUDER:", name.upper())
print("Your name has", len(name), "letters. I counted them with my laser eyes.")

# TODO: ask for their favorite food and store it in food
# TODO: reply with an f-string that uses BOTH name and food
'''),
            "hints": [
                "An f-string looks like f\"Hi {name}!\" - the f goes right before the first quote.",
                "First: food = input(\"What's your favorite food? \"). Then print an f-string with {name} and {food} inside.",
                "food = input(\"What's your favorite food? \")\nprint(f\"{food}?! {name}, I LOVE {food}!\")",
            ],
            "solution": _RB5,
            "check": _check(r'''
expect(uses("fstrings"), "I don't see an f-string yet. It starts with f before the quotes, like f\"Hi {name}\".")
for who, food in [("Zara", "tacos"), ("Max", "spaghetti")]:
    r = run(inputs=[who, food])
    expect(r.inputs_used >= 2, "Your robot should ask two questions now: your name, then your favorite food.")
    after = after_inputs(r, [who, food]).lower()
    expect(who.lower() in after and food in after,
           f"When I said my name is {who} and I like {food}, I expected the robot's reply to mention both {who} and {food}.")
SUCCESS = "Smooth talker! f-strings make your robot sound like a pro. ✨"
'''),
            "concepts": ["fstrings", "input", "strings"],
            "xp": 25,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: Secret Agent Code Name",
        "learn": (
            "<p>You can grab <b>pieces</b> of a string with square brackets. This is called <b>slicing</b>:</p>"
            "<pre>word = \"Maximilian\"\nprint(word[:3])    # Max  (first 3 letters)\nprint(word[-3:])   # ian  (last 3 letters)</pre>"
            "<p><code>[:3]</code> means \"from the start up to letter 3\". <code>[-3:]</code> means \"start 3 from the "
            "end and go to the end\". Like cutting a sub sandwich: you choose where to slice.</p>"
            "<p>And you can glue strings with <code>+</code>: <code>\"Max\" + \"ian\"</code> gives <code>\"Maxian\"</code>.</p>"
        ),
        "task": ("<p>At the end of your program, ask for the person's <b>last name</b>. Build a secret code name: the "
                 "<b>first 3 letters</b> of their first name + the <b>last 3 letters</b> of their last name, in "
                 "<b>ALL CAPS</b>. Print it! Example: Zara Khan becomes <code>ZARHAN</code>.</p>"
                 "<p>Your program should ask 3 things in order: name, favorite food, last name.</p>"),
        "starter": _code(r'''
print("Beep boop! Hello, human!")
robot_name = "Bolt"
print(f"My name is {robot_name}")
name = input("What's your name? ")
print(f"Nice to meet you, {name}!")
print(f"LET ME SAY IT LOUDER: {name.upper()}")
print(f"Your name has {len(name)} letters. I counted them with my laser eyes.")
food = input("What's your favorite food? ")
print(f"{food}?! {name}, I LOVE {food}! Well... I eat batteries. But still.")

# TODO: ask for their last name
# TODO: code name = first 3 letters of name + last 3 letters of last name, in capitals
# TODO: print the code name
'''),
        "hints": [
            "name[:3] is the first 3 letters. last[-3:] is the last 3 letters.",
            "Glue them with + and then shout the result with .upper().",
            "last = input(\"What's your last name? \")\ncode_name = (name[:3] + last[-3:]).upper()\nprint(f\"Your code name is {code_name}\")",
        ],
        "solution": _RB_BOSS,
        "check": _check(r'''
for first, food, last in [("Zara", "tacos", "Khan"), ("Maximilian", "pizza", "Rodriguez")]:
    code = (first[:3] + last[-3:]).upper()
    ins = [first, food, last]
    r = run(inputs=ins)
    expect(r.inputs_used >= 3, "Your program should ask three things: name, favorite food, then last name.")
    after = after_inputs(r, ins)
    expect(code.lower() in after.lower(),
           f"For {first} {last} I expected the code name {code} (first 3 of {first} + last 3 of {last}).")
    expect(code in after, f"Almost! I see the code name, but it should be in ALL CAPS: {code}. Try .upper().")
SUCCESS = "Agent, your code name has been issued. This message will self-destruct. 🕶️"
'''),
        "concepts": ["strings", "input", "fstrings"],
        "xp": 70,
    },
    "remix": {
        "prompt": "Make it yours! Give your robot a personality: grumpy, dramatic, overly polite, pirate...",
        "ideas": [
            "Add ASCII art for your robot's face using a few print lines, like [o_o]",
            "Ask for their age and have the robot say how old it is compared to them",
            "Print their name backwards with name[::-1] and call it their 'robot name'",
            "Make the robot ask 5 questions and then print a full 'Human Profile' report with f-strings",
        ],
    },
}


# ---------------------------------------------------------------------------
# Project 2: Pizza Party Planner
# ---------------------------------------------------------------------------

_PZ1 = _code(r'''
print("🍕 PIZZA PARTY PLANNER 3000 🍕")
pizzas = 3
slices_per_pizza = 8
total_slices = pizzas * slices_per_pizza
print("Total slices:", total_slices)
''')

_PZ2 = _code(r'''
print("🍕 PIZZA PARTY PLANNER 3000 🍕")
pizzas = int(input("How many pizzas are we ordering? "))
slices_per_pizza = 8
total_slices = pizzas * slices_per_pizza
print("Total slices:", total_slices)
''')

_PZ3 = _code(r'''
print("🍕 PIZZA PARTY PLANNER 3000 🍕")
pizzas = int(input("How many pizzas are we ordering? "))
slices_per_pizza = 8
total_slices = pizzas * slices_per_pizza
print("Total slices:", total_slices)
people = int(input("How many people are coming (including you)? "))
slices_each = total_slices // people
leftovers = total_slices % people
print("Everyone gets", slices_each, "slices.")
print("Leftover slices:", leftovers, "(the chef gets those)")
''')

_PZ4 = _code(r'''
print("🍕 PIZZA PARTY PLANNER 3000 🍕")
pizzas = int(input("How many pizzas are we ordering? "))
slices_per_pizza = 8
total_slices = pizzas * slices_per_pizza
print("Total slices:", total_slices)
people = int(input("How many people are coming (including you)? "))
slices_each = total_slices // people
leftovers = total_slices % people
print("Everyone gets", slices_each, "slices.")
print("Leftover slices:", leftovers, "(the chef gets those)")
price = float(input("How much does one pizza cost? $"))
total_cost = pizzas * price
cost_each = round(total_cost / people, 2)
print("Each person pays: $", cost_each)
''')

_PZ5 = _code(r'''
print("🍕 PIZZA PARTY PLANNER 3000 🍕")
pizzas = int(input("How many pizzas are we ordering? "))
slices_per_pizza = 8
total_slices = pizzas * slices_per_pizza
people = int(input("How many people are coming (including you)? "))
slices_each = total_slices // people
leftovers = total_slices % people
price = float(input("How much does one pizza cost? $"))
total_cost = pizzas * price
cost_each = round(total_cost / people, 2)

print("=========== RECEIPT ===========")
print(f"Pizzas:          {pizzas}")
print(f"Total slices:    {total_slices}")
print(f"Slices each:     {slices_each}")
print(f"Leftovers:       {leftovers} (chef's snack)")
print(f"Total cost:      ${total_cost:.2f}")
print(f"Each person pays ${cost_each:.2f}")
print("===============================")
''')

_PZ_BOSS = _PZ5 + _code(r'''
hungry = int(input("How many slices can each person eat? "))
slices_needed = people * hungry
pizzas_needed = (slices_needed + slices_per_pizza - 1) // slices_per_pizza
print(f"For {people} hungry humans you actually need {pizzas_needed} pizzas!")
''')

PIZZA_PARTY = {
    "id": "pizza_party",
    "week": 1,
    "order": 2,
    "title": "Pizza Party Planner",
    "emoji": "🍕",
    "tagline": "A calculator that splits pizza (and the bill) fairly",
    "story": ("You're throwing a party and the #1 question is: how much pizza? Last time Uncle Dev ordered "
              "one pizza for twelve people and there was almost a riot. Never again. "
              "You'll build the Pizza Party Planner 3000: it counts slices, splits them fairly, "
              "figures out who gets leftovers, and tells everyone what they owe."),
    "concepts": ["math", "types", "variables", "input", "fstrings"],
    "expected_minutes": 100,
    "steps": [
        {
            "id": "s1",
            "title": "Pizza math",
            "learn": (
                "<p>Python is a super-fast calculator. The math symbols are:</p>"
                "<pre>3 + 2    # 5   add\n3 - 2    # 1   subtract\n3 * 2    # 6   multiply (star, not x)\n3 / 2    # 1.5 divide</pre>"
                "<p>You can do math with variables too. Python works out the right side first and puts the answer in the box on the left:</p>"
                "<pre>pizzas = 3\nslices_per_pizza = 8\ntotal_slices = pizzas * slices_per_pizza   # 24</pre>"
                "<p>Why not just type 24? Because next step the number of pizzas will change, and the math will "
                "keep working. Let the computer do the counting.</p>"
            ),
            "task": ("<p>Make three variables: <code>pizzas = 3</code>, <code>slices_per_pizza = 8</code>, and "
                     "<code>total_slices</code>, which is <b>calculated</b> by multiplying the first two. Print the total.</p>"),
            "starter": _code(r'''
print("🍕 PIZZA PARTY PLANNER 3000 🍕")

# TODO: make a variable pizzas = 3
# TODO: make a variable slices_per_pizza = 8
# TODO: make total_slices by MULTIPLYING them (use *), then print it
'''),
            "hints": [
                "Multiply in Python with the star: *",
                "total_slices = pizzas * slices_per_pizza",
                "pizzas = 3\nslices_per_pizza = 8\ntotal_slices = pizzas * slices_per_pizza\nprint(\"Total slices:\", total_slices)",
            ],
            "solution": _PZ1,
            "check": _check(r'''
r = run()
p = r.var("pizzas")
s = r.var("slices_per_pizza")
t = r.var("total_slices")
calc = False
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and any(getattr(tg, "id", None) == "total_slices" for tg in node.targets):
        if isinstance(node.value, ast.BinOp):
            calc = True
expect(calc, "total_slices should be CALCULATED, like total_slices = pizzas * slices_per_pizza, not typed in as a number.")
expect(t == p * s, f"total_slices is {t}, but {p} pizzas x {s} slices should be {p * s}.")
expect(has_num(r.output, t), f"Print total_slices so we can see it ({t}).")
SUCCESS = f"{t} slices. The math checks out, chef! 🧮"
'''),
            "concepts": ["math", "variables"],
            "xp": 15,
        },
        {
            "id": "s2",
            "title": "How many pizzas?",
            "learn": (
                "<p>Let's ask how many pizzas instead of typing 3. But careful! <code>input</code> always gives you "
                "<b>text</b>, even when someone types a number. And text math is weird:</p>"
                "<pre>\"3\" * 8        # \"33333333\"  (eight 3s glued together!)\nint(\"3\") * 8   # 24  (real math)</pre>"
                "<p><code>int(...)</code> turns text into a whole number (an <b>integer</b>). It's like translating "
                "from \"word language\" to \"number language\" so the calculator can understand it.</p>"
                "<pre>pizzas = int(input(\"How many pizzas? \"))</pre>"
            ),
            "task": ("<p>Change <code>pizzas = 3</code> so it <b>asks</b> how many pizzas are being ordered, using "
                     "<code>input</code> wrapped in <code>int()</code>. The total slices should update for any number.</p>"),
            "starter": _code(r'''
print("🍕 PIZZA PARTY PLANNER 3000 🍕")
pizzas = 3  # TODO: ask the user instead! use int(input(...))
slices_per_pizza = 8
total_slices = pizzas * slices_per_pizza
print("Total slices:", total_slices)
'''),
            "hints": [
                "Replace the 3 with an input(...) question.",
                "input gives text, so wrap it: int(input(\"...\")).",
                "pizzas = int(input(\"How many pizzas are we ordering? \"))",
            ],
            "solution": _PZ2,
            "check": _check(r'''
for n in ["3", "5"]:
    r = run(inputs=[n])
    expect(r.inputs_used >= 1, "Your program should ask how many pizzas with input(...).")
    expect(isinstance(r.var("pizzas"), int),
           "pizzas is still text! input gives text, so wrap it in int(...) to make it a number.")
    after = after_inputs(r, [n])
    expect(has_num(after, int(n) * 8), f"With {n} pizzas I expected {int(n) * 8} total slices, but didn't see that number.")
SUCCESS = "Your planner now works for ANY number of pizzas. Uncle Dev is saved. 🙌"
'''),
            "concepts": ["types", "input", "math"],
            "xp": 20,
        },
        {
            "id": "s3",
            "title": "Fair shares",
            "learn": (
                "<p>Say there are 24 slices and 5 people. <code>24 / 5</code> is <code>4.8</code>, but you can't hand "
                "someone 0.8 of a slice (well, you can, but it gets messy). Python has two special operators for this:</p>"
                "<pre>24 // 5   # 4  how many whole slices each (floor division)\n24 % 5    # 4  how many are LEFT OVER (remainder)</pre>"
                "<p><code>//</code> divides and throws away the decimal. <code>%</code> (called <b>modulo</b>) gives "
                "the remainder. It's exactly like dealing cards: everyone gets the same number, and the extras stay in your hand.</p>"
            ),
            "task": ("<p>Ask how many <b>people</b> are coming (as an <code>int</code>). Then make "
                     "<code>slices_each</code> using <code>//</code> and <code>leftovers</code> using <code>%</code>, "
                     "and print both.</p>"),
            "starter": _code(r'''
print("🍕 PIZZA PARTY PLANNER 3000 🍕")
pizzas = int(input("How many pizzas are we ordering? "))
slices_per_pizza = 8
total_slices = pizzas * slices_per_pizza
print("Total slices:", total_slices)

# TODO: ask how many people are coming (use int(input(...))), store it in people
# TODO: slices_each = total slices split evenly (use //)
# TODO: leftovers = the slices left over (use %)
# TODO: print slices_each and leftovers
'''),
            "hints": [
                "// gives whole slices each. % gives the remainder.",
                "people = int(input(\"How many people? \")) and then slices_each = total_slices // people",
                "slices_each = total_slices // people\nleftovers = total_slices % people\nprint(\"Everyone gets\", slices_each, \"slices. Leftovers:\", leftovers)",
            ],
            "solution": _PZ3,
            "check": _check(r'''
for p, ppl in [("4", "6"), ("2", "3")]:
    ins = [p, ppl]
    r = run(inputs=ins)
    expect(r.inputs_used >= 2, "Your program should ask two things: pizzas, then how many people.")
    total = int(p) * 8
    each, left = total // int(ppl), total % int(ppl)
    expect(r.var("slices_each") == each,
           f"With {total} slices and {ppl} people, slices_each should be {each} (use //), but it was {r.var('slices_each')}.")
    expect(r.var("leftovers") == left,
           f"With {total} slices and {ppl} people, leftovers should be {left} (use %), but it was {r.var('leftovers')}.")
    after = after_inputs(r, ins)
    expect(has_num(after, each) and has_num(after, left),
           f"Print both numbers! I expected to see {each} slices each and {left} leftovers.")
SUCCESS = "Perfectly fair. No riots today. ⚖️"
'''),
            "concepts": ["math", "types", "input"],
            "xp": 25,
        },
        {
            "id": "s4",
            "title": "Split the bill",
            "learn": (
                "<p>Prices have decimals, like <code>12.50</code>. <code>int()</code> can't handle a decimal point, so "
                "use <code>float()</code> instead. A <b>float</b> is a number with a decimal point.</p>"
                "<pre>price = float(\"12.50\")   # 12.5\nprint(26.97 / 4)          # 6.7425  ugh, too many digits\nprint(round(26.97 / 4, 2)) # 6.74    ahh, nice</pre>"
                "<p><code>round(number, 2)</code> keeps 2 digits after the decimal point, perfect for money. "
                "Types are like containers: <code>int</code> is an egg carton (whole eggs only), <code>float</code> "
                "is a measuring cup (any amount), and a string is a label maker.</p>"
            ),
            "task": ("<p>Ask how much <b>one pizza costs</b> (use <code>float</code>). Calculate <code>total_cost</code>, "
                     "then <code>cost_each</code> = total cost divided by people, rounded to 2 decimals with "
                     "<code>round</code>. Print how much each person pays.</p>"),
            "starter": _code(r'''
print("🍕 PIZZA PARTY PLANNER 3000 🍕")
pizzas = int(input("How many pizzas are we ordering? "))
slices_per_pizza = 8
total_slices = pizzas * slices_per_pizza
print("Total slices:", total_slices)
people = int(input("How many people are coming (including you)? "))
slices_each = total_slices // people
leftovers = total_slices % people
print("Everyone gets", slices_each, "slices.")
print("Leftover slices:", leftovers, "(the chef gets those)")

# TODO: ask the price of one pizza with float(input(...))
# TODO: total_cost = pizzas times price
# TODO: cost_each = total_cost divided by people, rounded to 2 decimals
# TODO: print cost_each
'''),
            "hints": [
                "float(input(...)) works just like int(input(...)) but allows decimals.",
                "total_cost = pizzas * price, then cost_each = round(total_cost / people, 2)",
                "price = float(input(\"How much does one pizza cost? $\"))\ntotal_cost = pizzas * price\ncost_each = round(total_cost / people, 2)\nprint(\"Each person pays: $\", cost_each)",
            ],
            "solution": _PZ4,
            "check": _check(r'''
expect(calls("float") >= 1, "Prices have decimals, so use float(input(...)) for the price.")
expect(calls("round") >= 1, "Use round(..., 2) so the money has just 2 decimal places.")
for p, ppl, price in [("3", "4", "8.99"), ("4", "6", "11.25")]:
    ins = [p, ppl, price]
    r = run(inputs=ins)
    expect(r.inputs_used >= 3, "Your program should ask three things: pizzas, people, then the price of one pizza.")
    want = round(int(p) * float(price) / int(ppl), 2)
    got = r.var("cost_each")
    expect(isinstance(got, (int, float)) and abs(got - want) < 0.011,
           f"{p} pizzas at ${price} split between {ppl} people should be {want} each, but cost_each was {got}.")
    expect(has_num(after_inputs(r, ins), want), f"Print cost_each! I expected to see {want}.")
SUCCESS = "Bill split to the penny. You'd make a great accountant. (Or a pizza mogul.) 💸"
'''),
            "concepts": ["types", "math", "input"],
            "xp": 25,
        },
        {
            "id": "s5",
            "title": "The official receipt",
            "learn": (
                "<p>f-strings can <b>format</b> numbers too. Add <code>:.2f</code> after the variable inside the braces "
                "to always show exactly 2 decimals:</p>"
                "<pre>cost = 7.5\nprint(f\"You owe ${cost}\")       # You owe $7.5   (looks weird)\nprint(f\"You owe ${cost:.2f}\")   # You owe $7.50  (looks like money!)</pre>"
                "<p><code>.2f</code> means \"2 digits after the point, as a float\". It's like a picture frame: the number "
                "is the same, it just looks nicer.</p>"
            ),
            "task": ("<p>Make your planner print a fancy <b>RECEIPT</b> using f-strings. It must show the "
                     "<b>total cost</b> and the <b>cost per person</b> with exactly 2 decimals (like <code>$7.50</code>), "
                     "plus the slices each and leftovers. Make it look official!</p>"),
            "starter": _code(r'''
print("🍕 PIZZA PARTY PLANNER 3000 🍕")
pizzas = int(input("How many pizzas are we ordering? "))
slices_per_pizza = 8
total_slices = pizzas * slices_per_pizza
print("Total slices:", total_slices)
people = int(input("How many people are coming (including you)? "))
slices_each = total_slices // people
leftovers = total_slices % people
print("Everyone gets", slices_each, "slices.")
print("Leftover slices:", leftovers, "(the chef gets those)")
price = float(input("How much does one pizza cost? $"))
total_cost = pizzas * price
cost_each = round(total_cost / people, 2)
print("Each person pays: $", cost_each)

# TODO: print a RECEIPT with f-strings.
# Show total_cost and cost_each with 2 decimals, like {cost_each:.2f}
'''),
            "hints": [
                "Inside an f-string, {total_cost:.2f} shows total_cost with 2 decimals.",
                "Try print(f\"Total cost: ${total_cost:.2f}\") and the same idea for cost_each.",
                "print(\"===== RECEIPT =====\")\nprint(f\"Slices each: {slices_each}  Leftovers: {leftovers}\")\nprint(f\"Total cost: ${total_cost:.2f}\")\nprint(f\"Each person pays ${cost_each:.2f}\")",
            ],
            "solution": _PZ5,
            "check": _check(r'''
expect(uses("fstrings"), "Use f-strings for the receipt, like print(f\"Total: ${total_cost:.2f}\").")
for p, ppl, price in [("4", "6", "11.25"), ("2", "3", "10")]:
    ins = [p, ppl, price]
    r = run(inputs=ins)
    after = after_inputs(r, ins)
    total = int(p) * float(price)
    each = round(total / int(ppl), 2)
    t_txt, e_txt = f"{total:.2f}", f"{each:.2f}"
    expect(t_txt in after, f"For {p} pizzas at ${price}, the receipt should show the total cost as {t_txt} (2 decimals, use :.2f).")
    expect(e_txt in after, f"The receipt should show the cost per person as {e_txt} (2 decimals, use :.2f).")
    total_slices = int(p) * 8
    expect(has_num(after, total_slices // int(ppl)) and has_num(after, total_slices % int(ppl)),
           "Don't forget to show slices each and leftovers on the receipt too!")
SUCCESS = "That receipt is so official it could be framed. 🧾"
'''),
            "concepts": ["fstrings", "math", "types"],
            "xp": 25,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: The Pizza Oracle",
        "learn": (
            "<p>Now flip the question around: if everyone eats 3 slices, how many pizzas do we <b>need</b>? "
            "15 slices needed / 8 per pizza = 1.875 pizzas. You can't order 0.875 of a pizza, so you must "
            "<b>round UP</b> to 2.</p>"
            "<p>But <code>//</code> rounds DOWN. Sneaky trick: add <code>slices_per_pizza - 1</code> first:</p>"
            "<pre>(15 + 7) // 8   # 2   good, rounded up\n(16 + 7) // 8   # 2   still 2 when it's exact</pre>"
            "<p>Figure out why this works and you've got a real programmer brain. (Or look up <code>math.ceil</code>.)</p>"
        ),
        "task": ("<p>At the end, ask <b>How many slices can each person eat?</b> (an <code>int</code>). Calculate "
                 "<code>pizzas_needed</code>: the number of whole pizzas to order so nobody goes hungry, rounded UP. "
                 "Print it. Your program should now ask 4 things: pizzas, people, price, slices per person.</p>"),
        "starter": _PZ5 + _code(r'''

# TODO: ask how many slices each person can eat (int)
# TODO: pizzas_needed = enough whole pizzas for everyone, rounded UP
# TODO: print pizzas_needed
'''),
        "hints": [
            "First work out slices_needed = people * hungry.",
            "Round up with the trick (slices_needed + 7) // 8, or with slices_per_pizza instead of 8.",
            "hungry = int(input(\"How many slices can each person eat? \"))\nslices_needed = people * hungry\npizzas_needed = (slices_needed + slices_per_pizza - 1) // slices_per_pizza\nprint(f\"You need {pizzas_needed} pizzas!\")",
        ],
        "solution": _PZ_BOSS,
        "check": _check(r'''
for ppl, hungry, want in [("5", "3", 2), ("6", "5", 4), ("4", "4", 2), ("1", "1", 1)]:
    ins = ["2", ppl, "10", hungry]
    r = run(inputs=ins)
    expect(r.inputs_used >= 4, "Your program should ask 4 things: pizzas, people, price, then slices per person.")
    got = r.var("pizzas_needed")
    expect(got == want,
           f"{ppl} people eating {hungry} slices each need {int(ppl) * int(hungry)} slices = {want} pizza(s), rounded up. pizzas_needed was {got}.")
    expect(has_num(after_inputs(r, ins), want), f"Print pizzas_needed! I expected to see {want}.")
SUCCESS = "The Pizza Oracle has spoken. No human shall go hungry. 🔮🍕"
'''),
        "concepts": ["math", "types"],
        "xp": 80,
    },
    "remix": {
        "prompt": "Make it yours! Turn the planner into the ultimate party calculator.",
        "ideas": [
            "Add a tip: ask for a tip percent and add it to the total cost",
            "Ask how many drinks each person wants and how much a bottle costs",
            "Print a pizza made of text characters at the top of the receipt",
            "Plan a party for your whole grade: how many pizzas for 300 people who each eat 3 slices?",
        ],
    },
}

PROJECTS = [ROBOT_BUDDY, PIZZA_PARTY]


# ---------------------------------------------------------------------------
# Practice
# ---------------------------------------------------------------------------

PRACTICE = [
    {
        "id": "p_output_1",
        "concept": "output",
        "title": "Robot Poem",
        "difficulty": 1,
        "task": "<p>Print a 3-line poem about a robot (or a cat, or pizza). Each line gets its own <code>print</code>.</p>",
        "starter": _code(r'''
# TODO: print 3 lines of poetry
'''),
        "hints": [
            "Each print(...) makes one line.",
            "Put each line of the poem in quotes inside its own print.",
            "print(\"Roses are red\")\nprint(\"Robots are metal\")\nprint(\"I left my charger by the kettle\")",
        ],
        "solution": _code(r'''
print("Roses are red")
print("Robots are metal")
print("I left my charger by the kettle")
'''),
        "check": _check(r'''
r = run()
expect(len(r.lines) >= 3, f"I counted {len(r.lines)} line(s). A 3-line poem needs at least 3 lines!")
SUCCESS = "Beautiful. The robots are weeping oil tears. 🤖📝"
'''),
        "xp": 10,
    },
    {
        "id": "p_variables_1",
        "concept": "variables",
        "title": "Swap-a-roo",
        "difficulty": 2,
        "task": ("<p>The variables <code>a</code> and <code>b</code> got mixed up! Swap them so <code>a</code> holds "
                 "\"dog\" and <code>b</code> holds \"cat\"... <b>without</b> typing \"dog\" or \"cat\" again. "
                 "Hint: you might need a third box.</p>"),
        "starter": _code(r'''
a = "cat"
b = "dog"
# TODO: swap them without typing "cat" or "dog" again
print("a is", a)
print("b is", b)
'''),
        "hints": [
            "If you do a = b first, the cat is gone forever! Save it somewhere first.",
            "Make a temporary variable: temp = a. Then you can overwrite a.",
            "temp = a\na = b\nb = temp",
        ],
        "solution": _code(r'''
a = "cat"
b = "dog"
temp = a
a = b
b = temp
print("a is", a)
print("b is", b)
'''),
        "check": _check(r'''
r = run()
expect(r.var("a") == "dog" and r.var("b") == "cat",
       f"After your swap, a is {r.var('a')!r} and b is {r.var('b')!r}. I wanted a = 'dog' and b = 'cat'.")
lits = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and n.value in ("cat", "dog")]
expect(len(lits) <= 2, "No cheating! Don't type \"cat\" or \"dog\" again. Move them between variables instead.")
SUCCESS = "Swapped like a magician. 🎩🐶🐱"
'''),
        "xp": 15,
    },
    {
        "id": "p_input_1",
        "concept": "input",
        "title": "Echo Chamber",
        "difficulty": 1,
        "task": "<p>Ask the user for a word, then print it back <b>3 times</b> (on 3 lines), like an echo in a cave.</p>",
        "starter": _code(r'''
# TODO: ask for a word with input()
# TODO: print it 3 times
'''),
        "hints": [
            "word = input(\"Say something: \") saves what they type.",
            "Then print(word) three times.",
            "word = input(\"Say something: \")\nprint(word)\nprint(word)\nprint(word)",
        ],
        "solution": _code(r'''
word = input("Shout into the cave: ")
print(word)
print(word)
print(word)
'''),
        "check": _check(r'''
for w in ["banana", "moon"]:
    r = run(inputs=[w])
    after = after_inputs(r, [w]).lower()
    expect(after.count(w) >= 3, f"When I typed {w}, I expected to hear it echo back 3 times but saw it {after.count(w)} time(s).")
SUCCESS = "Echo... echo... echo... 🦇"
'''),
        "xp": 10,
    },
    {
        "id": "p_strings_1",
        "concept": "strings",
        "title": "Whisper and Shout",
        "difficulty": 1,
        "task": ("<p>Ask for a sentence. Print it in ALL CAPS (shouting) using <code>.upper()</code>, then in all "
                 "lowercase (whispering) using <code>.lower()</code>.</p>"),
        "starter": _code(r'''
text = input("Say something: ")
# TODO: print text shouted, then whispered
'''),
        "hints": [
            "text.upper() makes a capital copy.",
            "text.lower() makes a lowercase copy.",
            "print(text.upper())\nprint(text.lower())",
        ],
        "solution": _code(r'''
text = input("Say something: ")
print(text.upper())
print(text.lower())
'''),
        "check": _check(r'''
for t in ["HeLLo ThErE", "Pizza Time"]:
    r = run(inputs=[t])
    after = after_inputs(r, [t])
    expect(t.upper() in after, f"When I typed {t}, I expected to see {t.upper()} (shouting).")
    expect(t.lower() in after, f"When I typed {t}, I expected to see {t.lower()} (whispering).")
SUCCESS = "LOUD... and quiet. Nice range! 🔊🔈"
'''),
        "xp": 10,
    },
    {
        "id": "p_strings_2",
        "concept": "strings",
        "title": "Underline Machine",
        "difficulty": 2,
        "task": ("<p>Ask for a word and print it. On the next line, print a row of <code>=</code> signs that is "
                 "<b>exactly</b> as long as the word. Trick: <code>\"=\" * 5</code> makes <code>=====</code>.</p>"),
        "starter": _code(r'''
word = input("Type a word: ")
print(word)
# TODO: print a line of = signs exactly as long as the word
'''),
        "hints": [
            "len(word) tells you how many letters there are.",
            "Multiplying a string repeats it: \"=\" * 3 is \"===\".",
            "print(\"=\" * len(word))",
        ],
        "solution": _code(r'''
word = input("Type a word: ")
print(word)
print("=" * len(word))
'''),
        "check": _check(r'''
for w in ["dragon", "Mississippi"]:
    r = run(inputs=[w])
    rows = [l.strip() for l in after_inputs(r, [w]).splitlines() if l.strip() and set(l.strip()) == {"="}]
    expect(rows, f"When I typed {w}, I didn't see a line made of = signs.")
    expect(len(rows[0]) == len(w), f"{w} has {len(w)} letters, but your underline has {len(rows[0])} = signs.")
SUCCESS = "Perfectly underlined. ✏️"
'''),
        "xp": 15,
    },
    {
        "id": "p_fstrings_1",
        "concept": "fstrings",
        "title": "Mad Lib Machine",
        "difficulty": 1,
        "task": ("<p>Ask for an <b>animal</b> and a <b>verb</b> (an action word). Use an f-string to print a silly "
                 "sentence with both, like <code>The llama likes to dance at midnight.</code></p>"),
        "starter": _code(r'''
animal = input("Give me an animal: ")
verb = input("Give me an action word: ")
# TODO: print a silly sentence with an f-string
'''),
        "hints": [
            "An f-string has an f before the quotes: f\"...\"",
            "Put variables in curly braces inside it: {animal}",
            "print(f\"The {animal} likes to {verb} at midnight.\")",
        ],
        "solution": _code(r'''
animal = input("Give me an animal: ")
verb = input("Give me an action word: ")
print(f"The {animal} likes to {verb} at midnight.")
'''),
        "check": _check(r'''
expect(uses("fstrings"), "Use an f-string: f\"The {animal} ...\".")
for a, v in [("llama", "dance"), ("shark", "juggle")]:
    r = run(inputs=[a, v])
    after = after_inputs(r, [a, v]).lower()
    expect(a in after and v in after, f"With {a} and {v}, I expected a sentence that uses both words.")
SUCCESS = "Award-winning nonsense. 🦙💃"
'''),
        "xp": 10,
    },
    {
        "id": "p_math_1",
        "concept": "math",
        "title": "Candy Split",
        "difficulty": 2,
        "task": ("<p>Ask how many <b>candies</b> and how many <b>kids</b> (both whole numbers). Print how many "
                 "candies each kid gets (use <code>//</code>) and how many are left over (use <code>%</code>).</p>"),
        "starter": _code(r'''
candies = int(input("How many candies? "))
kids = int(input("How many kids? "))
# TODO: print candies each (//) and leftovers (%)
'''),
        "hints": [
            "// is division that throws away the decimal.",
            "% gives the remainder: what's left after sharing.",
            "print(\"Each kid gets\", candies // kids)\nprint(\"Left over:\", candies % kids)",
        ],
        "solution": _code(r'''
candies = int(input("How many candies? "))
kids = int(input("How many kids? "))
print("Each kid gets", candies // kids)
print("Left over:", candies % kids)
'''),
        "check": _check(r'''
for c, k in [("23", "4"), ("50", "7")]:
    ins = [c, k]
    r = run(inputs=ins)
    after = after_inputs(r, ins)
    each, left = int(c) // int(k), int(c) % int(k)
    expect(has_num(after, each), f"{c} candies for {k} kids: each kid gets {each}. I didn't see {each}.")
    expect(has_num(after, left), f"{c} candies for {k} kids: {left} left over. I didn't see {left}.")
SUCCESS = "Fair and square. The leftover candy is yours, obviously. 🍬"
'''),
        "xp": 15,
    },
    {
        "id": "p_math_2",
        "concept": "math",
        "title": "Game Time Tracker",
        "difficulty": 2,
        "task": ("<p>Ask how many <b>hours</b> of video games you play per week. Print how many <b>minutes</b> "
                 "that is in a whole year (52 weeks). Hint: hours × 60 × 52.</p>"),
        "starter": _code(r'''
hours = int(input("Hours of games per week? "))
# TODO: work out minutes per year and print it
'''),
        "hints": [
            "There are 60 minutes in an hour and 52 weeks in a year.",
            "Multiply with *: hours * 60 * 52",
            "minutes = hours * 60 * 52\nprint(\"That's\", minutes, \"minutes a year!\")",
        ],
        "solution": _code(r'''
hours = int(input("Hours of games per week? "))
minutes = hours * 60 * 52
print("That's", minutes, "minutes of gaming a year!")
'''),
        "check": _check(r'''
for h in ["5", "12"]:
    r = run(inputs=[h])
    want = int(h) * 60 * 52
    expect(has_num(after_inputs(r, [h]), want), f"For {h} hours a week I expected {want} minutes a year.")
SUCCESS = "That's... a lot of minutes. GG. 🎮"
'''),
        "xp": 15,
    },
    {
        "id": "p_types_1",
        "concept": "types",
        "title": "Future You",
        "difficulty": 1,
        "task": ("<p>Ask for your age. Print how old you'll be in <b>10 years</b>. Remember: <code>input</code> "
                 "gives text, so turn it into a number with <code>int()</code> first.</p>"),
        "starter": _code(r'''
age = input("How old are you? ")
# TODO: turn age into a number, then print age + 10
'''),
        "hints": [
            "\"13\" + 10 crashes, because you can't add text and a number.",
            "age = int(input(...)) makes it a number.",
            "age = int(input(\"How old are you? \"))\nprint(\"In 10 years you'll be\", age + 10)",
        ],
        "solution": _code(r'''
age = int(input("How old are you? "))
print("In 10 years you'll be", age + 10)
'''),
        "check": _check(r'''
for a in ["13", "7"]:
    r = run(inputs=[a])
    expect(has_num(after_inputs(r, [a]), int(a) + 10), f"If you're {a} now, in 10 years you'll be {int(a) + 10}. I didn't see that.")
SUCCESS = "Future you says thanks. 🔮"
'''),
        "xp": 10,
    },
    {
        "id": "p_types_2",
        "concept": "types",
        "title": "Allowance Calculator",
        "difficulty": 2,
        "task": ("<p>Ask for your <b>weekly allowance</b> (it can have cents, like 5.50, so use <code>float</code>). "
                 "Print how much you'd get in a year (52 weeks), rounded to 2 decimals.</p>"),
        "starter": _code(r'''
# TODO: ask for the weekly allowance as a float
# TODO: print the yearly total, rounded to 2 decimals
'''),
        "hints": [
            "float(input(...)) allows decimals.",
            "Multiply by 52, then round(..., 2).",
            "weekly = float(input(\"Weekly allowance? $\"))\nprint(\"Per year: $\", round(weekly * 52, 2))",
        ],
        "solution": _code(r'''
weekly = float(input("Weekly allowance? $"))
print("Per year: $", round(weekly * 52, 2))
'''),
        "check": _check(r'''
for w in ["5.50", "2.25"]:
    r = run(inputs=[w])
    want = round(float(w) * 52, 2)
    expect(has_num(after_inputs(r, [w]), want), f"${w} a week is ${want} a year. I didn't see {want}.")
SUCCESS = "Cha-ching! Time to negotiate a raise. 💰"
'''),
        "xp": 15,
    },
]
