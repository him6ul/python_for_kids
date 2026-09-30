"""Week 2: Magic 8-Ball (project 3) and Guess My Number (project 4).

New concepts: conditions, random, while_loops.
"""
from .week1 import _H, _code


_H2 = _H + r'''

def digitless(text):
    return norm(re.sub(r"\d+", "#", text))

def secret_for(seed, inputs=()):
    r0 = run(inputs=list(inputs), seed=seed, allow_error=True)
    s = r0.ns.get("secret")
    if not isinstance(s, int):
        raise CheckFail("I couldn't find a whole-number variable called secret. Pick it with secret = random.randint(1, 100) BEFORE asking for a guess.")
    return s
'''


def _check(body):
    return _H2 + "\n" + body.strip("\n") + "\n"


# ---------------------------------------------------------------------------
# Project 3: Magic 8-Ball
# ---------------------------------------------------------------------------

_M1 = _code(r'''
import random

print("🎱 Madame Byte's Magic 8-Ball 🎱")
answers = ["It is certain.", "Ask again later.", "My sources say NO.",
           "Absolutely, 100%.", "The spirits are on a snack break.", "Outlook not so good."]
question = input("Ask the Magic 8-Ball a yes/no question: ")
print("The ball is thinking... 🌀")
print(random.choice(answers))
''')

_M2 = _code(r'''
import random

print("🎱 Madame Byte's Magic 8-Ball 🎱")
answers = ["It is certain.", "Ask again later.", "My sources say NO.",
           "Absolutely, 100%.", "The spirits are on a snack break.", "Outlook not so good."]
question = input("Ask the Magic 8-Ball a yes/no question: ")
if question == "":
    print("You didn't ask anything! The ball is not a mind reader. (Okay, it is. But still.)")
else:
    print("The ball is thinking... 🌀")
    print(random.choice(answers))
''')

_M3 = _code(r'''
import random

print("🎱 Madame Byte's Magic 8-Ball 🎱")
answers = ["It is certain.", "Ask again later.", "My sources say NO.",
           "Absolutely, 100%.", "The spirits are on a snack break.", "Outlook not so good."]
question = input("Ask the Magic 8-Ball a yes/no question: ")
if question == "":
    print("You didn't ask anything! The ball is not a mind reader. (Okay, it is. But still.)")
elif "homework" in question.lower():
    print("The ball refuses to answer homework questions. Nice try. 📚")
else:
    print("The ball is thinking... 🌀")
    print(random.choice(answers))
''')

_M4 = _M3 + _code(r'''
luck = int(input("How lucky do you feel today, 1 to 10? "))
if luck >= 8:
    print("🍀 The stars are on your side. Buy a lottery ticket. (Kidding.)")
elif luck >= 4:
    print("😐 A perfectly average day. Could be worse. Could be pizza.")
else:
    print("🌧️ Uh oh. Maybe stay in bed and avoid ladders.")
''')

_M5 = _code(r'''
import random

print("🎱 Madame Byte's Magic 8-Ball 🎱")
vip = "Zed"
name = input("Who dares approach the ball? ")
if name.lower() == vip.lower():
    print("👑 The ball bows before you, Supreme Leader. Ask anything.")
else:
    print("Hmm, a mere mortal. Very well.")
answers = ["It is certain.", "Ask again later.", "My sources say NO.",
           "Absolutely, 100%.", "The spirits are on a snack break.", "Outlook not so good."]
question = input("Ask the Magic 8-Ball a yes/no question: ")
if question == "":
    print("You didn't ask anything! The ball is not a mind reader. (Okay, it is. But still.)")
elif "homework" in question.lower():
    print("The ball refuses to answer homework questions. Nice try. 📚")
else:
    print("The ball is thinking... 🌀")
    print(random.choice(answers))
luck = int(input("How lucky do you feel today, 1 to 10? "))
if luck >= 8:
    print("🍀 The stars are on your side. Buy a lottery ticket. (Kidding.)")
elif luck >= 4:
    print("😐 A perfectly average day. Could be worse. Could be pizza.")
else:
    print("🌧️ Uh oh. Maybe stay in bed and avoid ladders.")
''')

_M_BOSS = _M5 + _code(r'''
move = input("The ball challenges you! rock, paper, or scissors? ").lower()
ball_move = random.choice(["rock", "paper", "scissors"])
print(f"The ball chooses {ball_move}!")
if move == ball_move:
    print("It's a tie! Great minds think alike.")
elif (move == "rock" and ball_move == "scissors") or (move == "paper" and ball_move == "rock") or (move == "scissors" and ball_move == "paper"):
    print("You win! The ball is... cracked. Emotionally.")
else:
    print("You lose! The ball saw that coming. It sees everything.")
''')

MAGIC_8_BALL = {
    "id": "magic_8_ball",
    "week": 2,
    "order": 3,
    "title": "Magic 8-Ball",
    "emoji": "🎱",
    "tagline": "A fortune teller that answers your questions (and dodges homework)",
    "story": ("Madame Byte, the world's most dramatic fortune teller, has retired to a beach in Florida. "
              "She left you her crystal ball... but it's empty inside. You need to program it! "
              "Your ball will give random mysterious answers, notice when you're being sneaky, "
              "read your luck, and bow down to exactly one person: you."),
    "concepts": ["random", "conditions", "input", "strings"],
    "expected_minutes": 100,
    "steps": [
        {
            "id": "s1",
            "title": "Shake the ball",
            "learn": (
                "<p>To make the ball unpredictable we need <b>randomness</b>. Python keeps its random tools in a "
                "toolbox called <code>random</code>. You open the toolbox with <code>import random</code> at the top.</p>"
                "<p>Next, a <b>list</b>: a bunch of values inside square brackets, separated by commas. "
                "<code>random.choice</code> picks one at random, like pulling a name out of a hat:</p>"
                "<pre>import random\nsnacks = [\"chips\", \"cookies\", \"a single grape\"]\nprint(random.choice(snacks))</pre>"
                "<p>Run it a few times. Different snack each time (sometimes the sad grape).</p>"
            ),
            "task": ("<p>The ball always says the same boring thing. Fix it: add <code>import random</code> at the top, "
                     "make a list called <code>answers</code> with <b>at least 4</b> mysterious answers, and print "
                     "<code>random.choice(answers)</code> instead of the boring line.</p>"),
            "starter": _code(r'''
# TODO: import random here

print("🎱 Madame Byte's Magic 8-Ball 🎱")
question = input("Ask the Magic 8-Ball a yes/no question: ")
print("The ball is thinking... 🌀")
print("Ask again later.")  # boring! it ALWAYS says this

# TODO: make a list called answers with at least 4 answers,
# then print random.choice(answers) instead of the boring line above
'''),
            "hints": [
                "Start with import random on the very first line.",
                "A list looks like: answers = [\"Yes!\", \"No way.\", \"Maybe...\", \"Ask your cat.\"]",
                "answers = [\"It is certain.\", \"No way.\", \"Maybe...\", \"Ask your cat.\"]\nprint(random.choice(answers))",
            ],
            "solution": _M1,
            "check": _check(r'''
expect(imports("random"), "Add import random at the top so you can use the random toolbox.")
expect(calls("choice") >= 1, "Use random.choice(answers) to pick a random answer.")
q = "Will I be famous?"
r = run(inputs=[q])
answers = r.var("answers")
expect(isinstance(answers, list) and len(answers) >= 4, "answers should be a list with at least 4 answers inside [ ].")
seen = set()
for seed in range(1, 13):
    r = run(inputs=[q], seed=seed)
    after = norm(after_inputs(r, [q]))
    expect(any(norm(a) in after for a in answers), "After the question, the ball should print one of your answers.")
    seen.add(after)
expect(len(seen) >= 2, "I shook the ball 12 times and always got the same answer. Print random.choice(answers)!")
SUCCESS = "The ball glows... it has spoken! 🔮"
'''),
            "concepts": ["random", "output"],
            "xp": 20,
        },
        {
            "id": "s2",
            "title": "No question, no answer",
            "learn": (
                "<p>Programs can make <b>decisions</b> with <code>if</code>. If something is true, do one thing; "
                "<code>else</code>, do another:</p>"
                "<pre>if question == \"\":\n    print(\"You forgot to ask!\")\nelse:\n    print(\"Hmm, let me think...\")</pre>"
                "<p><code>==</code> means \"is equal to?\" (two equals signs to ASK, one equals sign to STORE). "
                "<code>\"\"</code> is an empty string: nothing typed at all.</p>"
                "<p>The lines under <code>if</code> and <code>else</code> are <b>indented</b> (4 spaces). That's how Python "
                "knows which lines belong to which choice. Like a fork in the road: you only walk down one path.</p>"
            ),
            "task": ("<p>If the user just presses Enter without typing a question, the ball should scold them "
                     "instead of answering. Otherwise (<code>else</code>), it thinks and gives a random answer like before.</p>"),
            "starter": _M1.replace("print(\"The ball is thinking... 🌀\")\nprint(random.choice(answers))\n",
                                   "# TODO: if question is empty (\"\"), scold the user\n"
                                   "# else: think and give a random answer (indent these lines!)\n"
                                   "print(\"The ball is thinking... 🌀\")\nprint(random.choice(answers))\n"),
            "hints": [
                "Check for an empty question with: if question == \"\":",
                "Indent the random answer lines under an else: so they only run when there IS a question.",
                "if question == \"\":\n    print(\"You didn't ask anything!\")\nelse:\n    print(\"The ball is thinking...\")\n    print(random.choice(answers))",
            ],
            "solution": _M2,
            "check": _check(r'''
empty = set()
for seed in range(1, 9):
    r = run(inputs=[""], seed=seed)
    empty.add(digitless(after_inputs(r, [""])))
expect("" not in empty, "When I pressed Enter without a question, the ball said nothing. Print a message telling me to ask something!")
expect(len(empty) == 1, "When I asked NOTHING, the ball still gave me a random answer. Use if question == \"\": to catch the empty question.")
q = "Will it snow on my birthday?"
seen = set()
for seed in range(1, 13):
    r = run(inputs=[q], seed=seed)
    seen.add(norm(after_inputs(r, [q])))
expect(len(seen) >= 2, "When I asked a real question, the ball should still give random answers (in the else part).")
expect(empty.isdisjoint(seen), "A real question and an empty question got the same reply. They should be different!")
SUCCESS = "The ball won't be fooled by silence. 🤫"
'''),
            "concepts": ["conditions"],
            "xp": 20,
        },
        {
            "id": "s3",
            "title": "The homework detector",
            "learn": (
                "<p>Need more than two paths? Add <code>elif</code> (short for \"else if\") in the middle. Python checks "
                "each one from top to bottom and runs the FIRST one that's true.</p>"
                "<p>The word <code>in</code> checks if one string is hiding inside another:</p>"
                "<pre>\"cat\" in \"concatenate\"         # True\n\"homework\" in \"do my homework\"  # True\n\"homework\" in \"HOMEWORK help\"   # False! capitals are different</pre>"
                "<p>So use <code>question.lower()</code> first to make everything lowercase. It's like a metal detector "
                "at the airport: beep if the forbidden word is anywhere in the bag.</p>"
                "<pre>if a:\n    ...\nelif b:\n    ...\nelse:\n    ...</pre>"
            ),
            "task": ("<p>Madame Byte had one rule: <b>no homework questions</b>. If the question contains the word "
                     "\"homework\" (in any capitals: Homework, HOMEWORK...), the ball refuses with a special message "
                     "instead of a random answer. Add an <code>elif</code> between your <code>if</code> and "
                     "<code>else</code>.</p>"),
            "starter": _M2.replace("else:\n", "# TODO: add an elif that catches questions with \"homework\" in them (any capitals!)\nelse:\n"),
            "hints": [
                "\"homework\" in question checks if the word is in the question.",
                "Use question.lower() so HOMEWORK and Homework are caught too.",
                "elif \"homework\" in question.lower():\n    print(\"The ball refuses to answer homework questions!\")",
            ],
            "solution": _M3,
            "check": _check(r'''
def replies(q, seeds=range(1, 9)):
    out = set()
    for seed in seeds:
        r = run(inputs=[q], seed=seed)
        out.add(digitless(after_inputs(r, [q])))
    return out
empty = replies("", [1])
for q in ["Will my homework do itself?", "Can my HOMEWORK wait until tomorrow?", "Is Homework bad?"]:
    hw = replies(q)
    expect(len(hw) == 1, f"I asked \"{q}\" and the ball gave a random answer. It should refuse homework questions (any capitals - try question.lower()).")
    expect("" not in hw, f"I asked \"{q}\" and the ball said nothing. Print a special refusal message!")
    expect(hw != empty, "The homework message should be different from the empty-question message.")
seen = replies("Will I win the talent show?", range(1, 13))
expect(len(seen) >= 2, "Normal questions should still get random answers.")
SUCCESS = "Homework detected and denied. Madame Byte would be proud. 📚🚫"
'''),
            "concepts": ["conditions", "strings"],
            "xp": 25,
        },
        {
            "id": "s4",
            "title": "Luck-o-meter",
            "learn": (
                "<p>Besides <code>==</code>, you can compare numbers with:</p>"
                "<pre>&gt;    greater than        luck &gt; 7\n&lt;    less than           luck &lt; 4\n&gt;=   greater or equal    luck &gt;= 8\n&lt;=   less or equal       luck &lt;= 3\n!=   not equal           luck != 5</pre>"
                "<p>With <code>if/elif/else</code>, order matters. Check the biggest range first:</p>"
                "<pre>if score &gt;= 90:\n    print(\"A\")\nelif score &gt;= 80:\n    print(\"B\")\nelse:\n    print(\"Keep going!\")</pre>"
                "<p>A score of 95 is also &gt;= 80, but Python stops at the first true one, so it prints A. "
                "Like sorting laundry: first pull out the socks, then the shirts, everything else goes in the last pile.</p>"
            ),
            "task": ("<p>At the very end of the program (not indented), ask <b>How lucky do you feel, 1 to 10?</b> "
                     "(use <code>int</code>). Then print one of three fortunes:</p><ul>"
                     "<li><b>8 or more</b>: super lucky</li><li><b>4 to 7</b>: an average day</li>"
                     "<li><b>3 or less</b>: uh oh</li></ul>"),
            "starter": _M3 + _code(r'''

# TODO: ask how lucky they feel (1 to 10) with int(input(...))
# TODO: 8 or more -> super lucky, 4 to 7 -> average, 3 or less -> uh oh
'''),
            "hints": [
                "luck = int(input(\"How lucky do you feel, 1 to 10? \"))",
                "Start with if luck >= 8: then elif luck >= 4: then else:",
                "if luck >= 8:\n    print(\"Super lucky!\")\nelif luck >= 4:\n    print(\"Average day.\")\nelse:\n    print(\"Uh oh.\")",
            ],
            "solution": _M4,
            "check": _check(r'''
q = "Will I find a dragon?"
def fortune(n):
    r = run(inputs=[q, str(n)], seed=7)
    expect(r.inputs_used >= 2, "After the answer, ask how lucky they feel (1 to 10). Make sure it's not indented under if/else.")
    return digitless(after_inputs(r, [q, str(n)]))
f = {n: fortune(n) for n in [10, 8, 7, 4, 3, 1]}
expect(f[10] != "", "After I told you my luck, the ball said nothing. Print a fortune!")
expect(f[10] == f[8], "Luck 10 and luck 8 should get the same (super lucky) fortune. Check your >= 8.")
expect(f[7] == f[4], "Luck 7 and luck 4 should get the same (average) fortune.")
expect(f[3] == f[1], "Luck 3 and luck 1 should get the same (uh oh) fortune.")
expect(f[8] != f[7], "Luck 8 and luck 7 got the same fortune, but 8 is super lucky and 7 is average.")
expect(f[4] != f[3], "Luck 4 and luck 3 got the same fortune, but 4 is average and 3 is uh-oh.")
expect(f[10] != f[1], "Super lucky and unlucky got the same fortune. They should be different!")
SUCCESS = "The Luck-o-meter is calibrated. 🍀"
'''),
            "concepts": ["conditions", "types"],
            "xp": 25,
        },
        {
            "id": "s5",
            "title": "The chosen one",
            "learn": (
                "<p>You can compare strings too. But <code>\"Zed\" == \"zed\"</code> is <b>False</b>, because capital "
                "letters count. The fix is to lowercase both sides before comparing:</p>"
                "<pre>vip = \"Zed\"\nname = input(\"Name? \")\nif name.lower() == vip.lower():\n    print(\"Welcome, boss!\")</pre>"
                "<p>Now ZED, zed, and Zed all work. It's like a bouncer who recognizes your face whether "
                "you're wearing a hat or not.</p>"
            ),
            "task": ("<p>At the very <b>start</b> of the program, make a variable <code>vip</code> with your name, and ask "
                     "<b>Who dares approach the ball?</b> (save it in <code>name</code>). If the name matches "
                     "<code>vip</code> (any capitals), the ball gives a royal welcome. Otherwise, a normal greeting. "
                     "Your program now asks: name, question, luck.</p>"),
            "starter": _code(r'''
import random

print("🎱 Madame Byte's Magic 8-Ball 🎱")
# TODO: make vip = "your name", ask for their name,
# and give the VIP a royal welcome (any capitals should work!)
''') + _M4.split("print(\"🎱 Madame Byte's Magic 8-Ball 🎱\")\n", 1)[1],
            "hints": [
                "vip = \"YourName\" and name = input(\"Who dares approach the ball? \")",
                "Compare with name.lower() == vip.lower() so capitals don't matter.",
                "if name.lower() == vip.lower():\n    print(\"The ball bows before you!\")\nelse:\n    print(\"Hmm, a mere mortal.\")",
            ],
            "solution": _M5,
            "check": _check(r'''
q = "Will I be rich?"
r = run(inputs=["Somebody", q, "5"])
vip = r.var("vip")
expect(isinstance(vip, str) and vip.strip() != "", "vip should hold your name in quotes, like vip = \"Zed\".")
def talk(who):
    r = run(inputs=[who, q, "5"], seed=3)
    expect(r.inputs_used >= 3, "Your program should ask three things in this order: name, question, luck.")
    return norm(r.output).replace(norm(who), "@")
stranger = "Random Stranger" if norm(vip) != "random stranger" else "Someone Else"
v1, v2, v3, s = talk(vip), talk(vip.upper()), talk(vip.lower()), talk(stranger)
expect(v1 != s, f"When {vip} (the VIP) visited, the ball acted exactly like it does for a stranger. Give the VIP a special welcome!")
expect(v1 == v2 == v3, f"The VIP welcome should work with any capitals: {vip.upper()} and {vip.lower()} too. Try name.lower() == vip.lower().")
SUCCESS = "The ball recognizes its true master. 👑"
'''),
            "concepts": ["conditions", "strings", "input"],
            "xp": 25,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: Rock, Paper, Crystal Ball",
        "learn": (
            "<p>Sometimes one condition isn't enough. Combine them with <code>and</code> / <code>or</code>:</p>"
            "<pre>if move == \"rock\" and ball_move == \"scissors\":\n    print(\"Rock smashes scissors!\")</pre>"
            "<p><code>and</code> means BOTH must be true. <code>or</code> means at least one must be true. "
            "Wrap groups in brackets to keep things clear:</p>"
            "<pre>(a and b) or (c and d)</pre>"
            "<p>Tip: check for a tie first (<code>move == ball_move</code>), then check the 3 ways to win. "
            "Anything else is a loss.</p>"
        ),
        "task": ("<p>At the end, the ball challenges you to Rock, Paper, Scissors! Ask for your move (any capitals). "
                 "The ball picks with <code>ball_move = random.choice([\"rock\", \"paper\", \"scissors\"])</code> and "
                 "says what it picked. Then print a message containing <b>You win</b>, <b>You lose</b>, or <b>tie</b>.</p>"
                 "<p>Your program now asks: name, question, luck, move.</p>"),
        "starter": _M5 + _code(r'''

# TODO: ask for rock, paper, or scissors (lowercase it!)
# TODO: ball_move = random.choice(["rock", "paper", "scissors"]) and print it
# TODO: print "tie", "You win", or "You lose"
'''),
        "hints": [
            "Rock beats scissors, scissors beats paper, paper beats rock.",
            "Check tie first: if move == ball_move: ... then elif for the 3 winning combos, then else: you lose.",
            "elif (move == \"rock\" and ball_move == \"scissors\") or (move == \"paper\" and ball_move == \"rock\") or (move == \"scissors\" and ball_move == \"paper\"):\n    print(\"You win!\")",
        ],
        "solution": _M_BOSS,
        "check": _check(r'''
beats = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
seen = {"win": 0, "lose": 0, "tie": 0}
for seed in range(1, 7):
    for move in ["rock", "Paper", "SCISSORS"]:
        ins = ["Stranger", "Will I win?", "5", move]
        r = run(inputs=ins, seed=seed)
        expect(r.inputs_used >= 4, "Your program should ask 4 things in order: name, question, luck, then rock/paper/scissors.")
        ball = r.var("ball_move")
        m = move.lower()
        want = "tie" if m == ball else ("win" if beats[m] == ball else "lose")
        seen[want] += 1
        after = norm(after_inputs(r, ins))
        expect(ball in after, "Tell the player what the ball picked!")
        has = {"win": "you win" in after, "lose": "you lose" in after, "tie": re.search(r"\btie\b", after) is not None}
        expect(has[want] and sum(has.values()) == 1,
               f"I played {move} and the ball played {ball}. That's a {want.upper()}, so the message should say "
               + {"win": "\"You win\"", "lose": "\"You lose\"", "tie": "\"tie\""}[want] + " (and only that).")
expect(all(seen.values()), "Use random.choice for ball_move so the ball's move changes.")
SUCCESS = "Rock, paper, CRYSTAL BALL! You beat the boss. 🪨📄✂️🔮"
'''),
        "concepts": ["conditions", "random", "strings"],
        "xp": 80,
    },
    "remix": {
        "prompt": "Make it yours! Give your fortune teller a wild personality.",
        "ideas": [
            "Add 10 more answers, including some really weird ones",
            "Add more secret words: 'pizza', 'crush', 'test' each get their own response",
            "Give a random lucky number with random.randint(1, 99) and a lucky color with random.choice",
            "Make the VIP always get a good answer, from a separate good_answers list",
        ],
    },
}


# ---------------------------------------------------------------------------
# Project 4: Guess My Number
# ---------------------------------------------------------------------------

_G1 = _code(r'''
import random

print("🔢 I'm thinking of a number between 1 and 100...")
secret = random.randint(1, 100)
guess = int(input("Your guess: "))
if guess == secret:
    print("WHAT?! You got it! Are you reading my circuits?")
else:
    print("Nope! My number was", secret)
''')

_G2 = _code(r'''
import random

print("🔢 I'm thinking of a number between 1 and 100...")
secret = random.randint(1, 100)
guess = int(input("Your guess: "))
if guess > secret:
    print("Too high! ⬆️")
elif guess < secret:
    print("Too low! ⬇️")
else:
    print("WHAT?! You got it! Are you reading my circuits?")
''')

_G3 = _code(r'''
import random

print("🔢 I'm thinking of a number between 1 and 100...")
secret = random.randint(1, 100)
guess = 0
while guess != secret:
    guess = int(input("Your guess: "))
    if guess > secret:
        print("Too high! ⬆️")
    elif guess < secret:
        print("Too low! ⬇️")
    else:
        print("WHAT?! You got it! Are you reading my circuits?")
''')

_G4 = _code(r'''
import random

print("🔢 I'm thinking of a number between 1 and 100...")
secret = random.randint(1, 100)
guess = 0
tries = 0
while guess != secret:
    guess = int(input("Your guess: "))
    tries += 1
    if guess > secret:
        print("Too high! ⬆️")
    elif guess < secret:
        print("Too low! ⬇️")
    else:
        print("WHAT?! You got it! Are you reading my circuits?")
print(f"You got it in {tries} tries!")
''')

_G5 = _code(r'''
import random

while True:
    print("🔢 I'm thinking of a number between 1 and 100...")
    secret = random.randint(1, 100)
    guess = 0
    tries = 0
    while guess != secret:
        guess = int(input("Your guess: "))
        tries += 1
        if guess > secret:
            print("Too high! ⬆️")
        elif guess < secret:
            print("Too low! ⬇️")
        else:
            print("WHAT?! You got it! Are you reading my circuits?")
    print(f"You got it in {tries} tries!")
    again = input("Play again? (yes/no) ")
    if again.lower() != "yes":
        break
print("Thanks for playing! My circuits need a nap. 😴")
''')

_G_BOSS = _code(r'''
import random

while True:
    print("🔢 I'm thinking of a number between 1 and 100... you get 7 guesses!")
    secret = random.randint(1, 100)
    guess = 0
    tries = 0
    while guess != secret and tries < 7:
        guess = int(input("Your guess: "))
        tries += 1
        if guess > secret:
            print("Too high! ⬆️")
        elif guess < secret:
            print("Too low! ⬇️")
    if guess == secret:
        print(f"WHAT?! You got it in {tries} tries!")
    else:
        print(f"💀 Out of guesses! My number was {secret}.")
    again = input("Play again? (yes/no) ")
    if again.lower() != "yes":
        break
print("Thanks for playing! My circuits need a nap. 😴")
''')

GUESS_NUMBER = {
    "id": "guess_my_number",
    "week": 2,
    "order": 4,
    "title": "Guess My Number",
    "emoji": "🔢",
    "tagline": "The computer picks a secret number. Can you crack it?",
    "story": ("Your robot has a new hobby: keeping secrets. It's thinking of a number between 1 and 100 "
              "and it is VERY smug about it. You'll build the game: the computer picks a number, you guess, "
              "it says too high or too low, and it keeps going until you crack the code. "
              "Then it counts how many tries you needed, so you can brag."),
    "concepts": ["random", "while_loops", "conditions", "variables"],
    "expected_minutes": 100,
    "steps": [
        {
            "id": "s1",
            "title": "Pick a secret",
            "learn": (
                "<p><code>random.randint(a, b)</code> picks a random whole number from a to b (both included). "
                "It's like rolling a giant 100-sided die:</p>"
                "<pre>import random\nsecret = random.randint(1, 100)\nguess = int(input(\"Guess: \"))\nif guess == secret:\n    print(\"You got it!\")\nelse:\n    print(\"Nope! It was\", secret)</pre>"
                "<p>Remember <code>int()</code>: <code>input</code> gives text, and the text <code>\"7\"</code> is "
                "never equal to the number <code>7</code>. Apples and oranges!</p>"
            ),
            "task": ("<p>Make the computer pick <code>secret = random.randint(1, 100)</code>. Ask for ONE guess "
                     "(as an <code>int</code>). If it's right, celebrate. If not, say what the secret number was.</p>"),
            "starter": _code(r'''
import random

print("🔢 I'm thinking of a number between 1 and 100...")
# TODO: make secret = random.randint(1, 100)
# TODO: ask for a guess (use int()!), then say if it's right or wrong
'''),
            "hints": [
                "secret = random.randint(1, 100) picks the number.",
                "guess = int(input(\"Your guess: \")) and then if guess == secret: ... else: ...",
                "secret = random.randint(1, 100)\nguess = int(input(\"Your guess: \"))\nif guess == secret:\n    print(\"You got it!\")\nelse:\n    print(\"Nope! It was\", secret)",
            ],
            "solution": _G1,
            "check": _check(r'''
expect(calls("randint") >= 1, "Pick the secret with random.randint(1, 100).")
secrets = [secret_for(seed) for seed in range(1, 8)]
expect(all(1 <= s <= 100 for s in secrets), "The secret should be between 1 and 100.")
expect(len(set(secrets)) >= 3, "The secret number is always the same! Use random.randint(1, 100).")
for seed in [1, 2]:
    s = secret_for(seed)
    right = run(inputs=[str(s)], seed=seed)
    wrong_guess = s + 1 if s < 100 else s - 1
    wrong = run(inputs=[str(wrong_guess)], seed=seed)
    expect(isinstance(right.var("guess"), int), "guess should be a number. Wrap your input in int(...).")
    a, b = after_inputs(right, [str(s)]), after_inputs(wrong, [str(wrong_guess)])
    expect(a.strip() != "" and b.strip() != "", "After the guess, tell the player if they were right or wrong!")
    expect(digitless(a) != digitless(b), "A right guess and a wrong guess got the same message. Use if guess == secret: ... else: ...")
    expect(has_num(b, s), f"When the guess is wrong, tell the player what the secret was (it was {s}).")
SUCCESS = "The robot has a secret. And now it's smug. 😏"
'''),
            "concepts": ["random", "conditions", "types"],
            "xp": 20,
        },
        {
            "id": "s2",
            "title": "Hotter or colder",
            "learn": (
                "<p>\"Nope\" isn't very helpful. Let's give clues! Use <code>&gt;</code> and <code>&lt;</code>:</p>"
                "<pre>if guess &gt; secret:\n    print(\"Too high!\")\nelif guess &lt; secret:\n    print(\"Too low!\")\nelse:\n    print(\"You got it!\")</pre>"
                "<p>If it's not bigger and not smaller... it must be equal! That's why the last one can just be "
                "<code>else</code>. It's like a thermometer: too hot, too cold, or just right.</p>"
            ),
            "task": ("<p>Change the game so a wrong guess says <b>Too high</b> or <b>Too low</b> instead of revealing the "
                     "number. A right guess still celebrates.</p>"),
            "starter": _G1.replace("if guess == secret:", "# TODO: say \"Too high\" or \"Too low\" instead of revealing the number\nif guess == secret:"),
            "hints": [
                "guess > secret means the guess is too high.",
                "Use if / elif / else with three different messages.",
                "if guess > secret:\n    print(\"Too high!\")\nelif guess < secret:\n    print(\"Too low!\")\nelse:\n    print(\"You got it!\")",
            ],
            "solution": _G2,
            "check": _check(r'''
for seed in [1, 2, 5]:
    s = secret_for(seed)
    hi = run(inputs=[str(s + 7)], seed=seed)
    lo = run(inputs=[str(s - 7)], seed=seed)
    ok = run(inputs=[str(s)], seed=seed)
    h = norm(after_inputs(hi, [str(s + 7)]))
    l = norm(after_inputs(lo, [str(s - 7)]))
    k = norm(after_inputs(ok, [str(s)]))
    expect("high" in h, f"The secret was {s} and I guessed {s + 7}. I expected your game to say Too high.")
    expect("low" in l, f"The secret was {s} and I guessed {s - 7}. I expected your game to say Too low.")
    expect(digitless(h) != digitless(l), "Too high and too low should be different messages!")
    expect("too high" not in k and "too low" not in k, f"I guessed {s}, the right answer, but the game said too high/too low.")
    expect(digitless(k) not in (digitless(h), digitless(l)), "A right guess should get a celebration, not a clue!")
SUCCESS = "Clues unlocked. Now it's a real game! 🌡️"
'''),
            "concepts": ["conditions"],
            "xp": 20,
        },
        {
            "id": "s3",
            "title": "Keep guessing!",
            "learn": (
                "<p>One guess is not fair. Let's keep asking until they get it. A <code>while</code> loop repeats its "
                "indented lines <b>as long as</b> its condition is true:</p>"
                "<pre>guess = 0\nwhile guess != secret:\n    guess = int(input(\"Guess: \"))\n    ...clues here...</pre>"
                "<p><code>!=</code> means \"is not equal\". So: \"while the guess is wrong, keep going\". "
                "Why <code>guess = 0</code> first? The loop checks <code>guess</code> before the first question, so the box "
                "needs something in it (0 is never the secret).</p>"
                "<p>It's like a toddler asking \"are we there yet?\" over and over, until the answer is yes.</p>"
            ),
            "task": ("<p>Put the guessing and the clues inside a <code>while</code> loop so the player keeps guessing "
                     "until they get the number right.</p>"),
            "starter": _G2.replace("guess = int(input", "# TODO: start with guess = 0, then loop: while guess != secret:\n# (indent the guess and the clues inside the loop)\nguess = int(input"),
            "hints": [
                "Put guess = 0 before the loop, then while guess != secret:",
                "Everything that should repeat (asking + clues) goes indented under the while.",
                "guess = 0\nwhile guess != secret:\n    guess = int(input(\"Your guess: \"))\n    if guess > secret:\n        print(\"Too high!\")\n    ...",
            ],
            "solution": _G3,
            "check": _check(r'''
expect(uses("while_loops"), "Use a while loop so the player can keep guessing: while guess != secret:")
for seed in [3, 7]:
    s = secret_for(seed)
    ins = [str(s + 5), str(s - 5), str(s)]
    r = run(inputs=ins, seed=seed, allow_error=True)
    expect(r.inputs_used == 3 and not r.error,
           f"The secret was {s}. I guessed {s + 5}, then {s - 5}, then {s}. The game should keep asking until I'm right, then stop.")
    between = after_inputs(r, ins[:1])
    expect("high" in norm(between), "Keep the too high / too low clues inside the loop!")
    one = run(inputs=[str(s)], seed=seed, allow_error=True)
    expect(one.inputs_used == 1 and not one.error, "If I guess right the first time, the loop should stop right away.")
SUCCESS = "The loop lives! Guess forever (or until you win). 🔁"
'''),
            "concepts": ["while_loops", "conditions"],
            "xp": 30,
        },
        {
            "id": "s4",
            "title": "Count the tries",
            "learn": (
                "<p>A <b>counter</b> is a variable that goes up by one each time something happens. Start it at 0, "
                "and add 1 inside the loop:</p>"
                "<pre>tries = 0\nwhile ...:\n    tries += 1     # same as: tries = tries + 1</pre>"
                "<p>It's like the clicker a bouncer uses to count people coming in. Put <code>tries = 0</code> "
                "BEFORE the loop (or it resets every time!), and the print AFTER the loop (not indented), so it only "
                "happens once at the end.</p>"
            ),
            "task": ("<p>Count how many guesses the player takes in a variable called <code>tries</code>. After they win, "
                     "print something like <code>You got it in 4 tries!</code> using an f-string.</p>"),
            "starter": _G3.replace("guess = 0\n", "guess = 0\n# TODO: tries = 0 here, add 1 inside the loop,\n# and print the number of tries after the loop\n"),
            "hints": [
                "tries = 0 before the loop, tries += 1 inside the loop.",
                "After the loop (no indent): print(f\"You got it in {tries} tries!\")",
                "tries = 0\nwhile guess != secret:\n    guess = int(input(\"Your guess: \"))\n    tries += 1\n    ...\nprint(f\"You got it in {tries} tries!\")",
            ],
            "solution": _G4,
            "check": _check(r'''
for seed in [3, 8]:
    s = secret_for(seed)
    ins = [str(s + 5), str(s - 5), str(s + 1), str(s)]
    r = run(inputs=ins, seed=seed)
    expect(r.var("tries") == 4, f"I needed 4 guesses, but tries was {r.var('tries')}. Start at 0 BEFORE the loop and add 1 inside it.")
    expect(has_num(after_inputs(r, ins), 4), "I needed 4 guesses. After the loop, print the number of tries!")
    one = run(inputs=[str(s)], seed=seed)
    expect(one.var("tries") == 1 and has_num(after_inputs(one, [str(s)]), 1),
           "When I guessed right the first time, it should say 1 try.")
SUCCESS = "Counting like a champ. Now go get a new high score! 🏆"
'''),
            "concepts": ["while_loops", "variables", "fstrings"],
            "xp": 25,
        },
        {
            "id": "s5",
            "title": "Play again?",
            "learn": (
                "<p>Want another round? Wrap the WHOLE game in a loop that runs forever... and escape with <code>break</code>:</p>"
                "<pre>while True:\n    ...play one round...\n    again = input(\"Play again? \")\n    if again.lower() != \"yes\":\n        break\nprint(\"Bye!\")</pre>"
                "<p><code>while True</code> never stops on its own. <code>break</code> is the emergency exit: it jumps "
                "out of the loop immediately. That's a <b>loop inside a loop</b>: the outer one is \"rounds\", the "
                "inner one is \"guesses\".</p>"
                "<p>Tip: select all your game lines and press <b>Tab</b> to indent them all at once.</p>"
            ),
            "task": ("<p>After each round ask <b>Play again?</b>. If they answer <code>yes</code> (any capitals), start a new "
                     "round with a NEW secret number and tries back at 0. Otherwise, <code>break</code> out and say goodbye.</p>"),
            "starter": _code(r'''
import random

# TODO: wrap the whole game in  while True:  (indent everything below)
# TODO: at the end of each round ask "Play again?" and break if the answer isn't yes
''') + _G4.split("import random\n\n", 1)[1],
            "hints": [
                "Put while True: above the game and indent all the game lines under it.",
                "The secret, guess = 0 and tries = 0 must be INSIDE while True, so each round starts fresh.",
                "    again = input(\"Play again? (yes/no) \")\n    if again.lower() != \"yes\":\n        break\nprint(\"Thanks for playing!\")",
            ],
            "solution": _G5,
            "check": _check(r'''
new_secret = False
for seed in [4, 9]:
    a = secret_for(seed)
    b = secret_for(seed, [str(a), "yes"])
    if a != b:
        new_secret = True
    ins = [str(a + 3), str(a), "Yes", str(b), "no"]
    r = run(inputs=ins, seed=seed, allow_error=True)
    expect(not r.error and r.inputs_used == 5,
           "I played a round, said Yes to play again, played another round, then said no. The game should stop after the no. "
           "(Check: does it ask Play again? after each round, and does yes work with any capitals?)")
    expect(r.var("tries") == 1, "In round 2 I guessed right first try, but tries didn't say 1. Reset tries = 0 at the start of each round.")
    expect(after_inputs(r, ins).strip() != "", "Say goodbye after they stop playing!")
    r2 = run(inputs=[str(a), "no"], seed=seed, allow_error=True)
    expect(not r2.error and r2.inputs_used == 2, "When I said no, the game should stop (use break).")
expect(new_secret, "Round 2 used the same secret as round 1. Pick a new secret inside the while True loop.")
SUCCESS = "Infinite replay unlocked. Warning: may cause 'one more round' syndrome. 🔄"
'''),
            "concepts": ["while_loops", "conditions"],
            "xp": 30,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: Seven Lives",
        "learn": (
            "<p>Games are more exciting when you can LOSE. A loop can check two things at once with <code>and</code>:</p>"
            "<pre>while guess != secret and tries &lt; 7:\n    ...</pre>"
            "<p>This keeps going only while the guess is wrong AND you still have guesses left. When the loop ends, "
            "you don't know WHY it ended, so check afterwards:</p>"
            "<pre>if guess == secret:\n    print(\"You win!\")\nelse:\n    print(\"Out of guesses!\")</pre>"
            "<p>Fun fact: with smart guessing (always pick the middle), 7 guesses is enough for ANY number from 1 to 100.</p>"
        ),
        "task": ("<p>Give the player only <b>7 guesses</b> per round. If they run out, print that they're out of guesses "
                 "and <b>reveal the secret number</b>. Then ask Play again? like before.</p>"),
        "starter": _G5.replace("    while guess != secret:", "    # TODO: only allow 7 guesses! (and reveal the secret if they run out)\n    while guess != secret:"),
        "hints": [
            "Add a second condition to the inner loop: and tries < 7",
            "After the inner loop, use if guess == secret: to decide if they won or ran out.",
            "    while guess != secret and tries < 7:\n        ...\n    if guess == secret:\n        print(f\"You got it in {tries} tries!\")\n    else:\n        print(f\"Out of guesses! It was {secret}.\")",
        ],
        "solution": _G_BOSS,
        "check": _check(r'''
for seed in [2, 6]:
    a = secret_for(seed)
    wrong = str(a + 1)
    ins = [wrong] * 7 + ["no"]
    r = run(inputs=ins, seed=seed, allow_error=True)
    expect(not r.error and r.inputs_used == 8,
           "I guessed wrong 7 times. After the 7th guess the round should end and ask Play again? (I said no).")
    expect(has_num(after_inputs(r, ins[:7]), a), f"When I ran out of guesses, reveal the secret number (it was {a}).")
    ins = [wrong] * 6 + [str(a), "no"]
    r = run(inputs=ins, seed=seed, allow_error=True)
    expect(not r.error and r.inputs_used == 8, "I got it right on my 7th guess, so that should still count as a win!")
    expect(r.var("tries") == 7, "I won on my 7th guess, so tries should be 7.")
    lose = digitless(after_inputs(run(inputs=[wrong] * 7 + ["no"], seed=seed), [wrong] * 7))
    win = digitless(after_inputs(r, ins[:7]))
    expect(lose != win, "Winning on the last guess and running out of guesses should print different messages.")
    ins = [str(a - 1), str(a), "no"]
    r = run(inputs=ins, seed=seed, allow_error=True)
    expect(not r.error and r.inputs_used == 3, "Guessing right early should still end the round right away.")
SUCCESS = "Seven lives, zero mercy. You built a real game! 💀🎮"
'''),
        "concepts": ["while_loops", "conditions"],
        "xp": 90,
    },
    "remix": {
        "prompt": "Make it yours! Turn Guess My Number into your own game.",
        "ideas": [
            "Add 'warm' and 'hot' clues when the guess is within 10 or within 3 of the secret",
            "Let the player pick a difficulty: easy (1-10), medium (1-100), hard (1-1000)",
            "Keep a best score across rounds and announce a NEW RECORD when they beat it",
            "Flip it around: YOU pick the number and the computer guesses, with you saying higher/lower",
        ],
    },
}

PROJECTS = [MAGIC_8_BALL, GUESS_NUMBER]


# ---------------------------------------------------------------------------
# Practice
# ---------------------------------------------------------------------------

PRACTICE = [
    {
        "id": "p_conditions_1",
        "concept": "conditions",
        "title": "Hot or Cold?",
        "difficulty": 1,
        "task": ("<p>Ask for the temperature (a whole number). If it's <b>80 or more</b>, print that it's hot. If it's "
                 "<b>50 or less</b>, print that it's cold. Anything in between: print that it's nice.</p>"),
        "starter": _code(r'''
temp = int(input("What's the temperature? "))
# TODO: hot (80 or more), cold (50 or less), or nice
'''),
        "hints": [
            "Use if temp >= 80: for hot.",
            "Then elif temp <= 50: for cold, and else: for nice.",
            "if temp >= 80:\n    print(\"Hot!\")\nelif temp <= 50:\n    print(\"Cold!\")\nelse:\n    print(\"Nice!\")",
        ],
        "solution": _code(r'''
temp = int(input("What's the temperature? "))
if temp >= 80:
    print("🔥 Hot! Ice cream time.")
elif temp <= 50:
    print("🥶 Cold! Hoodie time.")
else:
    print("😎 Nice weather!")
'''),
        "check": _check(r'''
def say(t):
    r = run(inputs=[str(t)])
    return digitless(after_inputs(r, [str(t)]))
m = {t: say(t) for t in [95, 80, 79, 51, 50, 20]}
expect(m[95] != "", "Print something after you get the temperature!")
expect(m[95] == m[80], "80 counts as hot (80 or more).")
expect(m[79] == m[51], "79 and 51 should both be 'nice'.")
expect(m[50] == m[20], "50 counts as cold (50 or less).")
expect(len({m[95], m[79], m[20]}) == 3, "Hot, nice and cold should be three different messages.")
SUCCESS = "Weather report: you nailed it. ☀️"
'''),
        "xp": 10,
    },
    {
        "id": "p_conditions_2",
        "concept": "conditions",
        "title": "The Password Door",
        "difficulty": 2,
        "task": ("<p>A secret door opens only for the password stored in <code>password</code>. Ask for the password. "
                 "If it matches (any capitals!), print that the door opens. Otherwise, print that access is denied.</p>"),
        "starter": _code(r'''
password = "open sesame"
attempt = input("Say the password: ")
# TODO: open the door if attempt matches password (capitals shouldn't matter)
'''),
        "hints": [
            "Compare with == (two equals signs).",
            "attempt.lower() makes the attempt lowercase so OPEN SESAME works too.",
            "if attempt.lower() == password:\n    print(\"The door creaks open...\")\nelse:\n    print(\"ACCESS DENIED\")",
        ],
        "solution": _code(r'''
password = "open sesame"
attempt = input("Say the password: ")
if attempt.lower() == password:
    print("🚪 The door creaks open...")
else:
    print("⛔ ACCESS DENIED. The door laughs at you.")
'''),
        "check": _check(r'''
def say(t):
    r = run(inputs=[t])
    return norm(after_inputs(r, [t]))
ok, caps, bad, bad2 = say("open sesame"), say("OPEN Sesame"), say("please?"), say("open sesam")
expect(ok != "" and bad != "", "Print a message for both the right and the wrong password.")
expect(ok != bad, "The right password and a wrong password got the same message!")
expect(ok == caps, "OPEN Sesame should work too. Try attempt.lower().")
expect(bad == bad2, "Only the exact password should open the door.")
SUCCESS = "The door recognizes you. 🗝️"
'''),
        "xp": 15,
    },
    {
        "id": "p_conditions_3",
        "concept": "conditions",
        "title": "Vowel Detector",
        "difficulty": 2,
        "task": ("<p>Ask for a single letter. Print whether it's a <b>vowel</b> (a, e, i, o, u) or a <b>consonant</b>. "
                 "Capital letters should work too. Trick: <code>letter in \"aeiou\"</code>.</p>"),
        "starter": _code(r'''
letter = input("Give me a letter: ")
# TODO: vowel or consonant?
'''),
        "hints": [
            "\"e\" in \"aeiou\" is True. \"b\" in \"aeiou\" is False.",
            "Lowercase it first so \"E\" works: letter.lower()",
            "if letter.lower() in \"aeiou\":\n    print(\"Vowel!\")\nelse:\n    print(\"Consonant!\")",
        ],
        "solution": _code(r'''
letter = input("Give me a letter: ")
if letter.lower() in "aeiou":
    print("That's a vowel! 🅰️")
else:
    print("That's a consonant!")
'''),
        "check": _check(r'''
def say(t):
    r = run(inputs=[t])
    return norm(after_inputs(r, [t]))
for x in ["a", "E", "u", "O"]:
    t = say(x)
    expect("vowel" in t and "consonant" not in t and "not a vowel" not in t,
           f"{x} is a vowel (capitals count too!), so your message should say vowel.")
for x in ["b", "Z", "t"]:
    t = say(x)
    expect("consonant" in t or "not a vowel" in t, f"{x} is not a vowel, so your message should say consonant.")
SUCCESS = "Vowel detection: 100% accurate. 🔍"
'''),
        "xp": 15,
    },
    {
        "id": "p_random_1",
        "concept": "random",
        "title": "Coin Flip",
        "difficulty": 1,
        "task": "<p>Flip a coin! Use <code>random.choice</code> to print either <b>Heads</b> or <b>Tails</b>.</p>",
        "starter": _code(r'''
import random
# TODO: print Heads or Tails at random
print("Heads")
'''),
        "hints": [
            "random.choice picks one thing from a list.",
            "The list is [\"Heads\", \"Tails\"].",
            "print(random.choice([\"Heads\", \"Tails\"]))",
        ],
        "solution": _code(r'''
import random
print("Flipping... 🪙")
print(random.choice(["Heads", "Tails"]))
'''),
        "check": _check(r'''
expect(imports("random"), "Start with import random.")
got = set()
for seed in range(1, 15):
    out = norm(run(seed=seed).output)
    expect("heads" in out or "tails" in out, "Print Heads or Tails!")
    got.add("heads" in out)
expect(len(got) == 2, "I flipped 14 times and always got the same side. Use random.choice([\"Heads\", \"Tails\"]).")
SUCCESS = "Heads, you're awesome. Tails, you're also awesome. 🪙"
'''),
        "xp": 10,
    },
    {
        "id": "p_random_2",
        "concept": "random",
        "title": "Dice Roller",
        "difficulty": 2,
        "task": ("<p>Roll two dice! Make <code>die1</code> and <code>die2</code> with <code>random.randint(1, 6)</code>, "
                 "print both, and print their total.</p>"),
        "starter": _code(r'''
import random
# TODO: die1 and die2 = random numbers from 1 to 6
# TODO: print both dice and the total
'''),
        "hints": [
            "random.randint(1, 6) gives 1, 2, 3, 4, 5 or 6.",
            "The total is die1 + die2.",
            "die1 = random.randint(1, 6)\ndie2 = random.randint(1, 6)\nprint(die1, die2, \"Total:\", die1 + die2)",
        ],
        "solution": _code(r'''
import random
die1 = random.randint(1, 6)
die2 = random.randint(1, 6)
print(f"🎲 {die1} and 🎲 {die2}")
print(f"Total: {die1 + die2}")
'''),
        "check": _check(r'''
totals = set()
for seed in range(1, 10):
    r = run(seed=seed)
    d1, d2 = r.var("die1"), r.var("die2")
    expect(d1 in range(1, 7) and d2 in range(1, 7), f"Dice go from 1 to 6, but I got {d1} and {d2}.")
    expect(has_num(r.output, d1) and has_num(r.output, d2), "Print both dice!")
    expect(has_num(r.output, d1 + d2), f"The dice were {d1} and {d2}, so print the total {d1 + d2}.")
    totals.add((d1, d2))
expect(len(totals) >= 3, "The dice always land the same way! Use random.randint(1, 6).")
SUCCESS = "Snake eyes? Boxcars? Either way, nice roll. 🎲🎲"
'''),
        "xp": 15,
    },
    {
        "id": "p_while_1",
        "concept": "while_loops",
        "title": "Rocket Countdown",
        "difficulty": 1,
        "task": ("<p>Use a <code>while</code> loop to count down from <b>10 to 1</b> (one number per line), then print "
                 "<b>Liftoff!</b>. No typing 10 separate prints!</p>"),
        "starter": _code(r'''
count = 10
# TODO: while count is bigger than 0, print it and take 1 away
print("Liftoff! 🚀")
'''),
        "hints": [
            "while count > 0: keeps going until count hits 0.",
            "Inside the loop: print(count) and then count -= 1",
            "while count > 0:\n    print(count)\n    count -= 1",
        ],
        "solution": _code(r'''
count = 10
while count > 0:
    print(count)
    count -= 1
print("Liftoff! 🚀")
'''),
        "check": _check(r'''
expect(uses("while_loops"), "Use a while loop for the countdown.")
r = run()
seq = [int(x) for x in nums(r.output)]
expect(seq[:10] == list(range(10, 0, -1)), f"I expected 10, 9, 8 ... 1 but saw {seq[:10]}.")
expect(r.has("liftoff"), "Don't forget Liftoff! at the end.")
SUCCESS = "3... 2... 1... you're in orbit! 🚀"
'''),
        "xp": 10,
    },
    {
        "id": "p_while_2",
        "concept": "while_loops",
        "title": "Are We There Yet?",
        "difficulty": 2,
        "task": ("<p>Keep asking <b>Are we there yet?</b> until the answer is <code>yes</code> (any capitals). Then print "
                 "something like <b>FINALLY!</b></p>"),
        "starter": _code(r'''
answer = input("Are we there yet? ")
# TODO: keep asking while the answer isn't yes
print("FINALLY! 🎉")
'''),
        "hints": [
            "while answer.lower() != \"yes\": keeps looping until they say yes.",
            "Inside the loop, ask again and store the new answer in the same variable.",
            "while answer.lower() != \"yes\":\n    answer = input(\"Are we there yet? \")",
        ],
        "solution": _code(r'''
answer = input("Are we there yet? ")
while answer.lower() != "yes":
    answer = input("Are we there yet? ")
print("FINALLY! 🎉")
'''),
        "check": _check(r'''
r = run(inputs=["no", "nope", "almost", "Yes"], allow_error=True)
expect(not r.error and r.inputs_used == 4, "I answered no, nope, almost, then Yes. It should keep asking until Yes, then stop.")
r = run(inputs=["yes"], allow_error=True)
expect(not r.error and r.inputs_used == 1, "If the first answer is yes, it should stop right away.")
expect(after_inputs(r, ["yes"]).strip() != "", "Celebrate when you finally arrive!")
SUCCESS = "You have arrived. Your parents are relieved. 🚗"
'''),
        "xp": 15,
    },
    {
        "id": "p_while_3",
        "concept": "while_loops",
        "title": "Piggy Bank Goal",
        "difficulty": 3,
        "task": ("<p>You're saving up $100 for a game. Keep asking <b>How much are you adding?</b> (whole dollars) until "
                 "the total reaches <b>100 or more</b>. Then print the total AND how many deposits it took.</p>"),
        "starter": _code(r'''
total = 0
deposits = 0
# TODO: while total is less than 100, ask for money, add it, count the deposit
# TODO: print the total and the number of deposits
'''),
        "hints": [
            "while total < 100: keeps asking until you reach the goal.",
            "Inside: total += int(input(...)) and deposits += 1",
            "while total < 100:\n    total += int(input(\"How much are you adding? \"))\n    deposits += 1\nprint(f\"You saved ${total} in {deposits} deposits!\")",
        ],
        "solution": _code(r'''
total = 0
deposits = 0
while total < 100:
    total += int(input("How much are you adding? $"))
    deposits += 1
print(f"🐷 Goal reached! You saved ${total} in {deposits} deposits.")
'''),
        "check": _check(r'''
for ins, t, d in [(["30", "50", "25"], 105, 3), (["100"], 100, 1), (["10", "10", "10", "10", "60"], 100, 5)]:
    r = run(inputs=ins, allow_error=True)
    expect(not r.error and r.inputs_used == len(ins),
           f"I added {', '.join(ins)}. That reaches {t}, so it should stop after {len(ins)} deposit(s).")
    after = after_inputs(r, ins)
    expect(has_num(after, t), f"Print the total! It should be {t}.")
    expect(has_num(after, d), f"Print how many deposits it took ({d}).")
SUCCESS = "Goal smashed. Go buy that game! 🐷💰"
'''),
        "xp": 20,
    },
]
