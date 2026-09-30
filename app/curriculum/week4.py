"""Week 4: lists (Hangman) and functions (Secret Agent Code Machine)."""

# ---------------------------------------------------------------------------
# Shared check helpers
# ---------------------------------------------------------------------------

HANG_HELP = r'''
ALPHA = "etaoinshrdlucmfwypvbgkqjxz"

def secret(seed):
    """Find out which word the program picked for this seed."""
    r0 = run(inputs=list(ALPHA) * 2, seed=seed, allow_error=True)
    w = r0.var("word")
    expect(isinstance(w, str) and w.isalpha(), "Keep the secret word in a variable called <code>word</code>, made of lowercase letters only.")
    return w

def uniq(word):
    out = []
    for c in word:
        if c not in out:
            out.append(c)
    return out

def wrong_letters(word, n=12):
    return [c for c in "zqxjkvwyfbgmpuhcdlrsnoaiet" if c not in word][:n]

def after_last_prompt(r):
    if not r.prompts:
        return []
    i = r.output.rfind(r.prompts[-1])
    return r.output[i:].splitlines()[1:]
'''

AGENT_HELP = r'''
def ref_encode(msg, key):
    a = "abcdefghijklmnopqrstuvwxyz"
    return "".join(a[(a.index(c) + key) % 26] if c in a else c for c in msg.lower())

def same(v, want):
    return isinstance(v, str) and v.lower() == want.lower()
'''

# ---------------------------------------------------------------------------
# Project 7: Hangman
# ---------------------------------------------------------------------------

H1_SOL = """import random

words = ["pizza", "dragon", "banana", "wizard", "rocket", "penguin", "zombie", "ninja"]
print("🎩 Welcome to HANGMAN! 🎩")
print("I know", len(words), "words. The first one is", words[0])

word = random.choice(words)
print("I'm thinking of a word with", len(word), "letters...")
"""

H2_SOL = H1_SOL + """
guessed = []

display = ""
for letter in word:
    if letter in guessed:
        display = display + letter + " "
    else:
        display = display + "_ "
print(display)
"""

H3_SOL = H2_SOL + """
guess = input("Guess a letter: ").lower()
guessed.append(guess)
if guess in word:
    print("Yes! There's a", guess, "in there! 🎉")
else:
    print("Nope, no", guess, "in this word. 😬")

# build the display again (copy-paste... for now!)
display = ""
for letter in word:
    if letter in guessed:
        display = display + letter + " "
    else:
        display = display + "_ "
print(display)
"""

H4_SOL = H1_SOL + """
guessed = []
lives = 6

while lives > 0:
    display = ""
    for letter in word:
        if letter in guessed:
            display = display + letter + " "
        else:
            display = display + "_ "
    print(display)

    if "_" not in display:
        print("YOU WIN! You saved the stick figure! 🏆")
        break

    guess = input("Guess a letter: ").lower()
    guessed.append(guess)
    if guess in word:
        print("Yes! There's a", guess, "in there! 🎉")
    else:
        lives = lives - 1
        print("Nope! Lives left:", lives)

if lives == 0:
    print("GAME OVER! 💀 The word was", word)
"""

H5_SOL = H1_SOL + """
guessed = []
lives = 6

while lives > 0:
    display = ""
    for letter in word:
        if letter in guessed:
            display = display + letter + " "
        else:
            display = display + "_ "
    print(display)
    print("Guessed so far:", guessed)

    if "_" not in display:
        print("YOU WIN! You saved the stick figure! 🏆")
        break

    guess = input("Guess a letter: ").lower()
    if guess in guessed:
        print("You already guessed", guess, "— no penalty, try again!")
    else:
        guessed.append(guess)
        if guess in word:
            print("Yes! There's a", guess, "in there! 🎉")
        else:
            lives = lives - 1
            print("Nope! Lives left:", lives)

if lives == 0:
    print("GAME OVER! 💀 The word was", word)
"""

HBOSS_SOL = H1_SOL + r"""
stages = [
'''
  +---+
  |   |
      |
      |
      |
=======''',
'''
  +---+
  |   |
  O   |
      |
      |
=======''',
'''
  +---+
  |   |
  O   |
  |   |
      |
=======''',
'''
  +---+
  |   |
  O   |
 /|   |
      |
=======''',
'''
  +---+
  |   |
  O   |
 /|\\  |
      |
=======''',
'''
  +---+
  |   |
  O   |
 /|\\  |
 /    |
=======''',
'''
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
=======''',
]

guessed = []
lives = 6

while lives > 0:
    print(stages[6 - lives])
    display = ""
    for letter in word:
        if letter in guessed:
            display = display + letter + " "
        else:
            display = display + "_ "
    print(display)
    print("Guessed so far:", guessed)

    if "_" not in display:
        print("YOU WIN! You saved the stick figure! 🏆")
        break

    guess = input("Guess a letter: ").lower()
    if guess in guessed:
        print("You already guessed", guess, "— no penalty, try again!")
    else:
        guessed.append(guess)
        if guess in word:
            print("Yes! There's a", guess, "in there! 🎉")
        else:
            lives = lives - 1
            print("Nope! Lives left:", lives)

if lives == 0:
    print(stages[6])
    print("GAME OVER! 💀 The word was", word)
"""

HANGMAN_PROJECT = {
    "id": "hangman",
    "week": 4,
    "order": 7,
    "title": "Hangman",
    "emoji": "🎩",
    "tagline": "The classic guess-the-word game, with a secret word list only you know",
    "story": (
        "A tiny stick figure named Gary has been captured by the Evil Spelling Wizard. 🧙 The only way to free him: "
        "guess the wizard's secret word one letter at a time. Every wrong guess, Gary gets a little more worried. "
        "You're going to build the whole game — which means YOU get to pick the words. Mwahaha."
    ),
    "concepts": ["lists", "for_loops", "while_loops", "conditions", "random"],
    "expected_minutes": 120,
    "steps": [
        {
            "id": "s1",
            "title": "The secret word list",
            "learn": (
                "<p>A <b>list</b> holds many things in one variable, in order, inside square brackets:</p>"
                "<pre>snacks = [\"chips\", \"cookies\", \"grapes\"]\nprint(snacks[0])     # chips  (first one!)\nprint(snacks[2])     # grapes\nprint(len(snacks))   # 3</pre>"
                "<p>The number in <code>[ ]</code> is the <b>index</b> — the item's seat number. Like floors in some "
                "buildings, it starts at <b>0</b>, not 1. 🛗</p>"
                "<p>And <code>random.choice(snacks)</code> picks one item at random, like pulling a name out of a hat.</p>"
            ),
            "task": (
                "<p>Make a list called <code>words</code> with <b>at least 5 lowercase words</b>. Print how many words "
                "you have and the first one (<code>words[0]</code>). Then pick one at random into a variable called "
                "<code>word</code>, and print how many letters it has with <code>len(word)</code> (but don't reveal it!).</p>"
            ),
            "starter": "import random\n\nprint(\"🎩 Welcome to HANGMAN! 🎩\")\n\n# TODO: make a list called words with at least 5 lowercase words\n# print len(words) and words[0]\n# pick word = random.choice(words) and print len(word)\n",
            "hints": [
                "A list looks like this: <code>words = [\"pizza\", \"dragon\", \"banana\", \"wizard\", \"rocket\"]</code>",
                "<code>print(\"I know\", len(words), \"words. The first one is\", words[0])</code>",
                "<code>word = random.choice(words)</code> then <code>print(\"The word has\", len(word), \"letters\")</code>",
            ],
            "solution": H1_SOL,
            "check": r'''
import re
seen = set()
for seed in range(1, 9):
    r = run(seed=seed)
    words = r.var("words")
    expect(isinstance(words, list), "<code>words</code> should be a list, with square brackets: <code>[\"pizza\", \"dragon\", ...]</code>")
    expect(len(words) >= 5, f"Your list has {len(words)} word(s). Add at least 5 so the game isn't too easy!")
    expect(all(isinstance(w, str) and w.isalpha() and w == w.lower() for w in words),
           "Every word should be lowercase letters only (no spaces or capitals), like <code>\"pizza\"</code>.")
    word = r.var("word")
    expect(word in words, "<code>word</code> should be picked from your list with <code>random.choice(words)</code>.")
    expect(r.has(words[0]), "Print the first word in your list using <code>words[0]</code>.")
    nums = re.findall(r"\d+", r.output)
    expect(str(len(word)) in nums, f"The word has {len(word)} letters, but I didn't see that number. Print <code>len(word)</code>.")
    seen.add(word)
expect(len(seen) >= 2, "The same word comes up every time! Use <code>random.choice(words)</code>.")
SUCCESS = "The wizard's word list is ready. Gary gulps. 😰"
''',
            "concepts": ["lists", "random"],
            "xp": 20,
        },
        {
            "id": "s2",
            "title": "_ _ _ _ _",
            "learn": (
                "<p>Players need to see blanks like <code>_ _ _ _ _</code>. We'll build that with a for loop that walks "
                "through the word letter by letter.</p>"
                "<p>We also need a list of letters the player has guessed. It starts <b>empty</b>: <code>guessed = []</code>.</p>"
                "<p>The <code>in</code> word asks “is this inside?” — it works on lists AND strings:</p>"
                "<pre>\"a\" in [\"a\", \"b\"]    # True\n\"z\" in \"pizza\"        # True</pre>"
                "<pre>display = \"\"\nfor letter in word:\n    if letter in guessed:\n        display = display + letter + \" \"\n    else:\n        display = display + \"_ \"</pre>"
                "<p>It's like a scratch-off card: guessed letters are scratched, the rest stay covered.</p>"
            ),
            "task": (
                "<p>Make an empty list <code>guessed = []</code>. Then build a <code>display</code> string with a for loop: "
                "a letter if it's been guessed, otherwise <code>_ </code>. Print it. (Right now nothing is guessed, "
                "so it's all blanks!)</p>"
            ),
            "starter": H1_SOL + "\n# TODO: guessed = []\n# build a display string: letter if guessed, else \"_ \"\n",
            "hints": [
                "Start with <code>guessed = []</code> and <code>display = \"\"</code>.",
                "Loop <code>for letter in word:</code> and inside use <code>if letter in guessed:</code>",
                "Add a letter with <code>display = display + letter + \" \"</code>, or a blank with <code>display = display + \"_ \"</code>. Then <code>print(display)</code>.",
            ],
            "solution": H2_SOL,
            "check": r'''
expect(uses("for_loops"), "Use <code>for letter in word:</code> to build the blanks.")
lengths = set()
for seed in range(1, 7):
    r = run(seed=seed)
    word = r.var("word")
    g = r.var("guessed")
    expect(isinstance(g, list), "<code>guessed</code> should be a list — start it empty: <code>guessed = []</code>")
    expect(any(line.count("_") == len(word) for line in r.lines),
           f"The word has {len(word)} letters, so I expected a line with {len(word)} blanks like <code>_ _ _</code>.")
    lengths.add(len(word))
SUCCESS = "Mysterious blanks! 🕵️ Now let's let the player guess."
''',
            "concepts": ["lists", "for_loops", "conditions", "strings"],
            "xp": 20,
        },
        {
            "id": "s3",
            "title": "Take a guess",
            "learn": (
                "<p>Lists can grow! <code>.append()</code> adds an item to the end:</p>"
                "<pre>guessed = []\nguessed.append(\"e\")\nguessed.append(\"z\")\nprint(guessed)    # ['e', 'z']</pre>"
                "<p>It's like adding a sticker to the end of a sticker row. Now <code>\"e\" in guessed</code> is <code>True</code>, "
                "so the next time you build the display, every <b>e</b> shows up!</p>"
            ),
            "task": (
                "<p>After printing the blanks, ask the player for a letter, <code>.append()</code> it to <code>guessed</code>, "
                "and say whether it's in the word. Then build and print the display <b>again</b> so the letter shows up. "
                "(Yes, you'll copy the display loop — we'll fix that next step.)</p>"
            ),
            "starter": H2_SOL + "\n# TODO: ask for a letter, append it to guessed,\n# say if it's in the word, then build + print the display again\n",
            "hints": [
                "<code>guess = input(\"Guess a letter: \").lower()</code> then <code>guessed.append(guess)</code>",
                "<code>if guess in word:</code> print a happy message, <code>else:</code> a sad one.",
                "Copy your <code>display = \"\"</code> + for loop + <code>print(display)</code> lines and paste them at the bottom.",
            ],
            "solution": H3_SOL,
            "check": HANG_HELP + r'''
for seed in (1, 2):
    word = secret(seed)
    good = word[0]
    r = run(inputs=[good], seed=seed)
    expect(r.inputs_used == 1, "Ask the player for a letter with <code>input()</code>.")
    g = r.var("guessed")
    expect(isinstance(g, list) and good in g, "Add the guess to the list with <code>guessed.append(guess)</code>.")
    after = after_last_prompt(r)
    want = len(word) - word.count(good)
    expect(any(good in line and line.count("_") == want for line in after),
           f"The word was \"{word}\" and I guessed \"{good}\" — after my guess I expected the display to show it with {want} blank(s) left.")
    bad = wrong_letters(word)[0]
    rb = run(inputs=[bad], seed=seed)
    after_bad = after_last_prompt(rb)
    expect(any(line.count("_") == len(word) for line in after_bad), "After a wrong guess, the display should still be all blanks.")
    nice = [l.replace(good, "") for l in after if "_" not in l]
    sad = [l.replace(bad, "") for l in after_bad if "_" not in l]
    expect(norm(" ".join(nice)) != norm(" ".join(sad)), "Right and wrong guesses should get different messages. Use <code>if guess in word:</code>")
SUCCESS = "Letters are appearing! Gary feels a tiny bit of hope. 🙏"
''',
            "concepts": ["lists", "input", "conditions", "for_loops"],
            "xp": 25,
        },
        {
            "id": "s4",
            "title": "Lives & the game loop",
            "learn": (
                "<p>One guess is not a game. We need to keep guessing until the player <b>wins</b> or runs out of <b>lives</b>. "
                "That's a <code>while</code> loop's job!</p>"
                "<pre>lives = 6\nwhile lives > 0:\n    # build + print display\n    if \"_\" not in display:\n        print(\"You win!\")\n        break          # escape the loop!\n    # ask for a guess...\n    # wrong? lives = lives - 1</pre>"
                "<p><code>break</code> is the emergency exit — it jumps out of the loop right away. "
                "No blanks left means every letter is found = victory!</p>"
                "<p>Bonus: since the display loop is now inside the while loop, you only need it <b>once</b>. Bye-bye copy-paste!</p>"
            ),
            "task": (
                "<p>Rebuild the game as a loop: start with <code>lives = 6</code>. While lives are left: build and print the "
                "display, <b>win</b> (and <code>break</code>) if there are no blanks, otherwise ask for a guess. A wrong guess "
                "loses a life. After the loop, if lives hit 0, print <code>GAME OVER</code> and <b>reveal the word</b>.</p>"
            ),
            "starter": H3_SOL.replace(
                "guess = input(",
                "# TODO: turn this into a while loop with lives = 6:\n"
                "# build display, win + break if no \"_\" left, ask for a guess,\n"
                "# lose a life if it's wrong. After the loop, reveal the word if lives == 0\n"
                "guess = input(",
            ),
            "hints": [
                "Put <code>lives = 6</code> before the loop and <code>while lives > 0:</code> around the display + guess code (keep ONE display loop).",
                "Inside the loop, right after printing display: <code>if \"_\" not in display:</code> → print a win message and <code>break</code>. In the wrong-guess branch: <code>lives = lives - 1</code>.",
                "After the loop (no indent): <code>if lives == 0:</code> <code>print(\"GAME OVER! The word was\", word)</code>",
            ],
            "solution": H4_SOL,
            "check": HANG_HELP + r'''
expect(uses("while_loops"), "Use a <code>while lives > 0:</code> loop so the player can keep guessing.")
for seed in (1, 2):
    word = secret(seed)
    letters = uniq(word)
    rw = run(inputs=letters, seed=seed)
    expect(rw.inputs_used == len(letters), f"The word was \"{word}\". I guessed all its letters ({', '.join(letters)}), "
                                            "but the game didn't end with a win. Check for no blanks with <code>if \"_\" not in display:</code> and <code>break</code>.")
    rl = run(inputs=wrong_letters(word), seed=seed)
    expect(3 <= rl.inputs_used <= 10, f"I kept guessing wrong and the game ended after {rl.inputs_used} guess(es). "
                                      "Give the player about 6 lives and subtract 1 for each wrong guess.")
    expect(rl.has(word), f"When I lost, you didn't reveal the word (\"{word}\"). Print it after GAME OVER!")
    expect(norm(rw.lines[-1]) != norm(rl.lines[-1]), "Winning and losing should end with different messages!")
SUCCESS = "It's a real game now! Play a round — can you save Gary? 🎮"
''',
            "concepts": ["while_loops", "lists", "conditions", "for_loops"],
            "xp": 35,
        },
        {
            "id": "s5",
            "title": "No double-dipping",
            "learn": (
                "<p>Bug alert! 🐛 If you guess <b>z</b> twice, you lose TWO lives for the same mistake. Unfair!</p>"
                "<p>Our <code>guessed</code> list remembers every letter, so before doing anything, check it:</p>"
                "<pre>if guess in guessed:\n    print(\"You already guessed that!\")\nelse:\n    guessed.append(guess)\n    # ...the normal right/wrong code</pre>"
                "<p>It's like a teacher saying “you already asked that” instead of marking you down. You can even show the list: "
                "<code>print(\"Guessed:\", guessed)</code>.</p>"
            ),
            "task": (
                "<p>If the player types a letter they <b>already guessed</b>, print a message with the word "
                "<b>already</b> in it and <b>don't</b> take a life. Bonus: print the letters guessed so far each turn.</p>"
            ),
            "starter": H4_SOL.replace(
                "    guessed.append(guess)\n",
                "    # TODO: if guess is already in guessed, say so (no life lost!)\n    guessed.append(guess)\n",
            ),
            "hints": [
                "Right after the <code>input()</code> line: <code>if guess in guessed:</code>",
                "Print something like <code>\"You already guessed that!\"</code> in that branch.",
                "Put the old <code>guessed.append(guess)</code> and right/wrong code inside an <code>else:</code> (indent it one more level).",
            ],
            "solution": H5_SOL,
            "check": HANG_HELP + r'''
for seed in (3, 4):
    word = secret(seed)
    wl = wrong_letters(word)
    ra = run(inputs=wl, seed=seed)
    rb = run(inputs=[wl[0], wl[0], wl[0]] + wl[1:], seed=seed)
    expect(rb.has("already"), f"I guessed \"{wl[0]}\" three times, but didn't see a message with the word <b>already</b>.")
    expect(rb.inputs_used == ra.inputs_used + 2, f"I guessed \"{wl[0]}\" three times in a row and lost extra lives for it. "
                                                  "Repeat guesses shouldn't cost a life — check <code>if guess in guessed:</code> first.")
    letters = uniq(word)
    rw = run(inputs=[letters[0]] + letters, seed=seed)
    expect(rw.inputs_used == len(letters) + 1, "Guessing a correct letter twice shouldn't break winning.")
SUCCESS = "No more double-dipping. Your game is fair AND fun. ⚖️"
''',
            "concepts": ["lists", "conditions"],
            "xp": 25,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: Draw Gary",
        "learn": (
            "<p>Real hangman has a picture that gets scarier with each miss. A list is perfect for that — store each "
            "picture as one item, and pick it by index!</p>"
            "<p>Triple quotes <code>'''</code> let a string span many lines, so you can draw ASCII art:</p>"
            "<pre>stages = [\n'''\n  +---+\n      |\n''',\n'''\n  +---+\n  O   |\n''',\n]\nprint(stages[6 - lives])</pre>"
            "<p>With 6 lives, <code>6 - lives</code> is 0 at the start and 6 when you're out — so you need 7 pictures. "
            "Tip: a backslash is special in Python, so type <code>\\\\</code> to draw one <code>\\</code> arm.</p>"
        ),
        "task": (
            "<p>Make a list called <code>stages</code> with at least 5 ASCII-art pictures (7 is perfect for 6 lives). "
            "Each turn, print the picture that matches how many lives are lost: <code>stages[6 - lives]</code>.</p>"
        ),
        "starter": H5_SOL.replace(
            "guessed = []\nlives = 6\n",
            "# TODO BOSS: make a list called stages with ASCII-art pictures,\n"
            "# then print stages[6 - lives] at the start of each turn\nguessed = []\nlives = 6\n",
        ),
        "hints": [
            "Each picture is a triple-quoted string, separated by commas inside <code>stages = [ ... ]</code>.",
            "Start with an empty gallows, then add the head <code>O</code>, body <code>|</code>, arms <code>/|\\\\</code>, legs <code>/ \\\\</code>.",
            "First line inside the while loop: <code>print(stages[6 - lives])</code>",
        ],
        "solution": HBOSS_SOL,
        "check": HANG_HELP + r'''
r0 = run(inputs=list(ALPHA) * 2, seed=5, allow_error=True)
stages = r0.var("stages")
expect(isinstance(stages, list) and len(stages) >= 5 and all(isinstance(s, str) for s in stages),
       "Make a list called <code>stages</code> with at least 5 picture strings.")
expect(len({norm(s) for s in stages}) >= 5, "Your pictures should all be different — add one body part per stage!")
for seed in (5, 6):
    word = secret(seed)
    rl = run(inputs=wrong_letters(word), seed=seed)
    shown = sum(1 for s in {norm(s) for s in stages} if s and s in norm(rl.output))
    expect(shown >= 4, f"While I lost a game, I only saw {shown} different picture(s). Print <code>stages[6 - lives]</code> every turn.")
    letters = uniq(word)
    rw = run(inputs=letters, seed=seed)
    expect(rw.inputs_used == len(letters), "Winning should still work after adding the pictures!")
SUCCESS = "Gary has a face now! And a body. And, uh, a lot of stress. 😅 BOSS DEFEATED!"
''',
        "concepts": ["lists", "strings"],
        "xp": 80,
    },
    "remix": {
        "prompt": "Make it yours! It's your wizard, your words, your rules.",
        "ideas": [
            "Swap the words for a theme: video games, Pokémon, your friends' names (lowercase!).",
            "Add a hint: if the player types <code>hint</code>, reveal one letter but take a life.",
            "Let the player pick a category (animals / food / space) — each is its own list.",
            "Play again? Wrap the whole game in another loop and keep a win counter.",
        ],
    },
}

# ---------------------------------------------------------------------------
# Project 8: Secret Agent Code Machine
# ---------------------------------------------------------------------------

A1_SOL = """def codename(name):
    return "Agent " + name[::-1].title()

agent = input("What's your name, recruit? ")
print("Welcome to HQ,", codename(agent), "🕶️")
"""

A2_SOL = """alphabet = "abcdefghijklmnopqrstuvwxyz"

def codename(name):
    return "Agent " + name[::-1].title()

def shift_letter(letter, key):
    if letter not in alphabet:
        return letter
    position = alphabet.find(letter)
    new_position = (position + key) % 26
    return alphabet[new_position]

agent = input("What's your name, recruit? ")
print("Welcome to HQ,", codename(agent), "🕶️")
print("Test: a shifted by 1 is", shift_letter("a", 1))
"""

A3_SOL = """alphabet = "abcdefghijklmnopqrstuvwxyz"

def codename(name):
    return "Agent " + name[::-1].title()

def shift_letter(letter, key):
    if letter not in alphabet:
        return letter
    position = alphabet.find(letter)
    new_position = (position + key) % 26
    return alphabet[new_position]

def encode(message, key):
    result = ""
    for letter in message.lower():
        result = result + shift_letter(letter, key)
    return result

agent = input("What's your name, recruit? ")
print("Welcome to HQ,", codename(agent), "🕶️")

message = input("Secret message: ")
key = int(input("Secret key number (1-25): "))
secret = encode(message, key)
print("Encoded:", secret)
"""

A4_SOL = A3_SOL.replace(
    """    return result

agent""",
    """    return result

def decode(message, key):
    return encode(message, -key)

agent""",
) + """print("Decoded again:", decode(secret, key))
"""

A5_SOL = "import random\n\n" + A4_SOL.replace(
    """def decode(message, key):
    return encode(message, -key)
""",
    """def decode(message, key):
    return encode(message, -key)

def make_password(length):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*?"
    password = ""
    for i in range(length):
        password = password + random.choice(chars)
    return password
""",
) + """
size = int(input("How long should your password be? "))
print("Your new password:", make_password(size))
"""

A_FUNCS = A5_SOL.split("agent = input(")[0]

A6_SOL = A_FUNCS + """agent = input("What's your name, recruit? ")
print("Welcome to HQ,", codename(agent), "🕶️")

while True:
    print()
    print("===== 🕵️ CODE MACHINE 🕵️ =====")
    print("1) Encode a message")
    print("2) Decode a message")
    print("3) Make a password")
    print("4) Quit")
    choice = input("Pick 1-4: ")
    if choice == "1":
        message = input("Message to encode: ")
        key = int(input("Key: "))
        print("Encoded:", encode(message, key))
    elif choice == "2":
        message = input("Message to decode: ")
        key = int(input("Key: "))
        print("Decoded:", decode(message, key))
    elif choice == "3":
        size = int(input("Password length: "))
        print("Password:", make_password(size))
    elif choice == "4":
        print("This message will self-destruct... just kidding. Bye, agent! 💣")
        break
    else:
        print("That's not on the menu, agent!")
"""

ABOSS_SOL = A_FUNCS + """def crack(secret):
    for key in range(1, 26):
        print(key, decode(secret, key))

agent = input("What's your name, recruit? ")
print("Welcome to HQ,", codename(agent), "🕶️")

while True:
    print()
    print("===== 🕵️ CODE MACHINE 🕵️ =====")
    print("1) Encode a message")
    print("2) Decode a message")
    print("3) Make a password")
    print("4) Quit")
    print("5) CRACK an enemy code")
    choice = input("Pick 1-5: ")
    if choice == "1":
        message = input("Message to encode: ")
        key = int(input("Key: "))
        print("Encoded:", encode(message, key))
    elif choice == "2":
        message = input("Message to decode: ")
        key = int(input("Key: "))
        print("Decoded:", decode(message, key))
    elif choice == "3":
        size = int(input("Password length: "))
        print("Password:", make_password(size))
    elif choice == "4":
        print("This message will self-destruct... just kidding. Bye, agent! 💣")
        break
    elif choice == "5":
        crack(input("Enemy message: "))
    else:
        print("That's not on the menu, agent!")
"""

AGENT_PROJECT = {
    "id": "secret_agent",
    "week": 4,
    "order": 8,
    "title": "Secret Agent Code Machine",
    "emoji": "🕵️",
    "tagline": "Encode secret messages, crack codes, and make unbreakable passwords",
    "story": (
        "HQ calling. 📡 Enemy spies are reading our messages! You've been recruited to build the agency's new "
        "Code Machine: it scrambles messages with a secret key (the same trick Julius Caesar used 2,000 years ago), "
        "unscrambles them, and invents passwords nobody can guess. To build it, you'll learn to make your own "
        "commands called <b>functions</b>. This message will self-destruct in… just kidding."
    ),
    "concepts": ["functions", "strings", "for_loops", "random", "while_loops"],
    "expected_minutes": 130,
    "steps": [
        {
            "id": "s1",
            "title": "Your codename",
            "learn": (
                "<p>A <b>function</b> is your own custom command. You teach Python a recipe once with <code>def</code>, "
                "then use it whenever you want:</p>"
                "<pre>def double(n):\n    return n * 2\n\nprint(double(5))    # 10\nprint(double(21))   # 42</pre>"
                "<p><code>n</code> is a <b>parameter</b> — the ingredient you hand in. <code>return</code> hands the "
                "result back out. It's like a vending machine: coins in (parameters), snack out (return value). 🥤</p>"
                "<p>Spy trick: <code>name[::-1]</code> flips a string backwards. <code>\"sam\"[::-1]</code> is <code>\"mas\"</code>.</p>"
            ),
            "task": (
                "<p>Write a function <code>codename(name)</code> that <b>returns</b> <code>\"Agent \"</code> plus the "
                "name backwards (so <code>codename(\"Sam\")</code> gives <code>Agent Mas</code>). Then ask the user's name "
                "and print their codename.</p>"
            ),
            "starter": "# TODO: def codename(name): that RETURNS \"Agent \" + the name backwards\n\nagent = input(\"What's your name, recruit? \")\n# TODO: print their codename\n",
            "hints": [
                "Start with <code>def codename(name):</code> and indent the next line.",
                "Return it, don't print it: <code>return \"Agent \" + name[::-1]</code> (add <code>.title()</code> for a capital letter).",
                "At the bottom: <code>print(\"Welcome to HQ,\", codename(agent))</code>",
            ],
            "solution": A1_SOL,
            "check": r'''
expect(defines("codename"), "Create the function with <code>def codename(name):</code>")
r = run(inputs=["Sam"])
f = r.fn("codename")
for name in ("sam", "Maria", "Zoe"):
    v, out = capture(f, name)
    expect(v is not None, f"<code>codename(\"{name}\")</code> gave back nothing. Use <code>return</code>, not print, inside the function.")
    expect(isinstance(v, str) and name[::-1].lower() in v.lower(),
           f"<code>codename(\"{name}\")</code> returned <code>{v!r}</code>. I expected the name backwards: \"{name[::-1]}\".")
expect(r.has("mas"), "Print the codename for the name the user typed: <code>print(codename(agent))</code>")
SUCCESS = "Welcome to the agency, Agent Uoy. 🕶️"
''',
            "concepts": ["functions", "strings", "input"],
            "xp": 20,
        },
        {
            "id": "s2",
            "title": "Shift one letter",
            "learn": (
                "<p>The <b>Caesar cipher</b>: move every letter forward in the alphabet by a secret <b>key</b>. "
                "With key 3: a→d, b→e, h→k. So <i>hi</i> becomes <i>kl</i>. 🔐</p>"
                "<p>Functions can take <b>two</b> parameters. Our plan: find the letter's position, add the key, look up the new letter.</p>"
                "<pre>alphabet = \"abcdefghijklmnopqrstuvwxyz\"\nalphabet.find(\"c\")     # 2  (positions start at 0!)\nalphabet[5]             # \"f\"</pre>"
                "<p>What about <b>z</b> + 1? There's no position 26! The <code>%</code> (remainder) sign wraps it around: "
                "<code>26 % 26</code> is 0 → back to <b>a</b>. Like a clock going from 12 back to 1. 🕛</p>"
            ),
            "task": (
                "<p>Write <code>shift_letter(letter, key)</code> that returns the letter moved <code>key</code> places "
                "(wrapping from z back to a). If it's not a lowercase letter (a space, <code>!</code>…), return it unchanged.</p>"
            ),
            "starter": "alphabet = \"abcdefghijklmnopqrstuvwxyz\"\n\n" + A1_SOL.replace(
                "agent = input(",
                "# TODO: def shift_letter(letter, key):\n#   if letter not in alphabet, return it unchanged\n"
                "#   otherwise find its position, add key, % 26, return the new letter\n\nagent = input(",
            ),
            "hints": [
                "First: <code>if letter not in alphabet:</code> <code>return letter</code>",
                "<code>position = alphabet.find(letter)</code> then <code>new_position = (position + key) % 26</code>",
                "<code>return alphabet[new_position]</code>",
            ],
            "solution": A2_SOL,
            "check": r'''
r = run(inputs=["Sam"])
f = r.fn("shift_letter")
cases = [("a", 1, "b"), ("h", 3, "k"), ("m", 13, "z"), ("y", 3, "b"), ("z", 1, "a"), (" ", 4, " "), ("!", 2, "!")]
for letter, key, want in cases:
    v, out = capture(f, letter, key)
    expect(v is not None, "<code>shift_letter</code> gave back nothing. Use <code>return</code> to hand back the new letter.")
    expect(v == want, f"<code>shift_letter({letter!r}, {key})</code> returned {v!r}, but I expected {want!r}."
                      + (" Use <code>% 26</code> to wrap around!" if letter in "yz" else "")
                      + (" Things that aren't letters should come back unchanged." if not letter.isalpha() else ""))
SUCCESS = "One letter shifted. Julius Caesar nods approvingly. 🏛️"
''',
            "concepts": ["functions", "strings", "math", "conditions"],
            "xp": 25,
        },
        {
            "id": "s3",
            "title": "Encode a whole message",
            "learn": (
                "<p>Functions can <b>use other functions</b>. That's their superpower: build small pieces, then snap them "
                "together like LEGO. 🧱</p>"
                "<pre>def encode(message, key):\n    result = \"\"\n    for letter in message:\n        result = result + shift_letter(letter, key)\n    return result</pre>"
                "<p>We start with an empty string and add one shifted letter at a time — like threading beads onto a necklace. "
                "Use <code>message.lower()</code> so capitals work too.</p>"
            ),
            "task": (
                "<p>Write <code>encode(message, key)</code> that returns the whole message shifted (use your "
                "<code>shift_letter</code>!). Then ask the user for a message and a key number, and print the encoded message.</p>"
            ),
            "starter": A2_SOL.replace('print("Test: a shifted by 1 is", shift_letter("a", 1))\n', "").replace(
                "agent = input(",
                "# TODO: def encode(message, key): loop over message.lower(),\n"
                "#   add shift_letter(letter, key) to a result string, return it\n\nagent = input(",
            ) + "\n# TODO: ask for a message and a key (int!), print the encoded message\n",
            "hints": [
                "Inside <code>encode</code>: start with <code>result = \"\"</code>, then <code>for letter in message.lower():</code>",
                "In the loop: <code>result = result + shift_letter(letter, key)</code>. After the loop: <code>return result</code>.",
                "At the bottom: <code>message = input(\"Secret message: \")</code>, <code>key = int(input(\"Key: \"))</code>, <code>print(\"Encoded:\", encode(message, key))</code>",
            ],
            "solution": A3_SOL,
            "check": AGENT_HELP + r'''
r = run(inputs=["Sam", "hello", "3"])
expect(r.has("khoor"), "I typed <code>hello</code> with key 3 and expected to see <code>khoor</code>. Ask for a message and key, then print <code>encode(message, key)</code>.")
r2 = run(inputs=["Sam", "spy", "1"])
expect(r2.has("tqz"), "I typed <code>spy</code> with key 1 and expected <code>tqz</code>. Remember <code>int()</code> around the key input!")
f = r.fn("encode")
for msg, key in (("hello", 3), ("attack at dawn", 1), ("xyz", 2), ("Pizza Party!", 10)):
    v, out = capture(f, msg, key)
    want = ref_encode(msg, key)
    expect(v is not None, "<code>encode</code> should <code>return result</code> at the end (not just print it).")
    expect(same(v, want), f"<code>encode({msg!r}, {key})</code> returned {v!r} — I expected {want!r}.")
SUCCESS = "khoor, djhqw! (That's \"hello, agent!\" in code.) 🔐"
''',
            "concepts": ["functions", "for_loops", "strings", "input", "types"],
            "xp": 30,
        },
        {
            "id": "s4",
            "title": "Decode it back",
            "learn": (
                "<p>To unscramble, shift <b>backwards</b> by the same key. And guess what? We already have a function that shifts! "
                "Shifting by <code>-3</code> undoes shifting by <code>3</code>:</p>"
                "<pre>def decode(message, key):\n    return encode(message, -key)</pre>"
                "<p>One line. That's the joy of functions: you wrote the hard part once, now you reuse it. "
                "It's like a remote with a rewind button. ⏪</p>"
            ),
            "task": (
                "<p>Write <code>decode(message, key)</code> that returns the original message. Then, at the bottom, "
                "decode the secret you just made and print it, to prove it works.</p>"
            ),
            "starter": A3_SOL.replace(
                "agent = input(",
                "# TODO: def decode(message, key): (hint: encode with the key backwards!)\n\nagent = input(",
            ) + "# TODO: print decode(secret, key) to prove it works\n",
            "hints": [
                "Decoding with key 3 is the same as encoding with key -3.",
                "<code>def decode(message, key):</code> then <code>return encode(message, -key)</code>",
                "At the bottom: <code>print(\"Decoded again:\", decode(secret, key))</code>",
            ],
            "solution": A4_SOL,
            "check": AGENT_HELP + r'''
r = run(inputs=["Sam", "hello", "3"])
f = r.fn("decode")
for plain, key in (("hello", 3), ("attack at dawn", 1), ("zebra", 4), ("meet me at noon!", 11)):
    v, out = capture(f, ref_encode(plain, key), key)
    expect(v is not None, "<code>decode</code> should <code>return</code> the decoded message.")
    expect(same(v, plain), f"<code>decode({ref_encode(plain, key)!r}, {key})</code> returned {v!r} — I expected {plain!r}.")
expect(calls("decode") >= 1, "Call your decode function at the bottom to prove it works.")
SUCCESS = "Encode ➡️ decode ➡️ same message. The enemy is SO confused. 😵‍💫"
''',
            "concepts": ["functions"],
            "xp": 20,
        },
        {
            "id": "s5",
            "title": "Password generator",
            "learn": (
                "<p>Good agents need strong passwords. Not <code>password123</code>. 🙄</p>"
                "<p><code>random.choice()</code> works on strings too — it picks one random character:</p>"
                "<pre>random.choice(\"abc123!\")   # maybe \"3\", maybe \"b\"...</pre>"
                "<p>Loop <code>length</code> times, adding one random character each time. The <code>length</code> parameter "
                "means the SAME function can make a short password or a giant one — you just hand in a different number.</p>"
            ),
            "task": (
                "<p>Write <code>make_password(length)</code> that returns a random password of exactly that many characters, "
                "mixing letters, numbers and symbols. Ask the user how long they want it and print one. "
                "(Don't forget <code>import random</code> at the top!)</p>"
            ),
            "starter": A4_SOL.replace(
                "agent = input(",
                "# TODO: import random (at the very top), then\n# def make_password(length): pick length random characters, return them\n\nagent = input(",
            ) + "# TODO: ask how long, print make_password(size)\n",
            "hints": [
                "Make a string with all allowed characters: <code>chars = \"abc...XYZ0123456789!@#$\"</code>",
                "<code>password = \"\"</code>, then <code>for i in range(length):</code> <code>password = password + random.choice(chars)</code>",
                "Don't forget <code>return password</code> — and <code>import random</code> at the top of the file.",
            ],
            "solution": A5_SOL,
            "check": r'''
r = run(inputs=["Sam", "hello", "3", "10"])
f = r.fn("make_password")
pws = []
for n in (8, 12, 20, 20, 20):
    v, out = capture(f, n)
    expect(isinstance(v, str), "<code>make_password</code> should <code>return</code> the password string.")
    expect(len(v) == n, f"<code>make_password({n})</code> gave a password with {len(v)} characters. It should have exactly {n}.")
    pws.append(v)
expect(pws[2] != pws[3] or pws[3] != pws[4], "Every password is the same! Use <code>random.choice</code> to pick each character.")
allc = "".join(pws)
expect(any(c.isalpha() for c in allc) and any(c.isdigit() for c in allc) and any(not c.isalnum() for c in allc),
       "Mix it up: your passwords should use letters, numbers AND symbols like <code>!@#</code>.")
SUCCESS = "Password: aZ7!q#9x. Good luck guessing THAT, enemy spies. 🔑"
''',
            "concepts": ["functions", "random", "for_loops"],
            "xp": 25,
        },
        {
            "id": "s6",
            "title": "The Code Machine menu",
            "learn": (
                "<p>Time to put it all together in a <b>menu loop</b> — like the main screen of a game. It repeats forever "
                "until the player picks Quit:</p>"
                "<pre>while True:\n    print(\"1) Encode  2) Decode  3) Password  4) Quit\")\n    choice = input(\"Pick: \")\n    if choice == \"1\":\n        ...\n    elif choice == \"4\":\n        break</pre>"
                "<p>Notice how short each option is — because your <b>functions</b> do the hard work. The menu is just the "
                "boss handing out jobs to its agents. 🕴️</p>"
            ),
            "task": (
                "<p>Replace the code at the bottom (keep the name + codename greeting) with a <code>while True</code> menu: "
                "<b>1</b> encode (ask message + key), <b>2</b> decode (ask message + key), <b>3</b> password (ask length), "
                "<b>4</b> quit with <code>break</code>. Anything else: print a funny “not on the menu” message.</p>"
            ),
            "starter": A5_SOL.replace(
                'message = input("Secret message: ")',
                "# TODO: replace everything below with a while True menu:\n"
                "# 1 encode, 2 decode, 3 password, 4 quit (break)\n"
                'message = input("Secret message: ")',
            ),
            "hints": [
                "Start with <code>while True:</code>, print the 4 options, then <code>choice = input(\"Pick 1-4: \")</code>.",
                "For option 1: <code>message = input(...)</code>, <code>key = int(input(...))</code>, <code>print(encode(message, key))</code>. Option 2 is the same with decode.",
                "<pre>    elif choice == \"4\":\n        print(\"Bye, agent!\")\n        break\n    else:\n        print(\"Not on the menu!\")</pre>",
            ],
            "solution": A6_SOL,
            "check": r'''
expect(uses("while_loops"), "Use a <code>while True:</code> loop for the menu.")
ra = run(inputs=["Sam", "2", "ifmmp", "1", "4"])
expect(ra.has("hello"), "I picked 2 (decode) with <code>ifmmp</code> and key 1, and expected to see <code>hello</code>.")
rb = run(inputs=["Sam", "1", "hello", "3", "1", "abc", "2", "4"])
expect(rb.has("khoor") and rb.has("cde"), "I picked 1 (encode) twice — <code>hello</code> key 3 and <code>abc</code> key 2 — and expected <code>khoor</code> and <code>cde</code>. Does the menu loop back after each job?")
rc1 = run(inputs=["Sam", "9", "3", "12", "4"], seed=1)
rc2 = run(inputs=["Sam", "9", "3", "12", "4"], seed=2)
expect(rc1.output != rc2.output, "I picked 3 (password), but the output looks the same every time. Print <code>make_password(size)</code>.")
SUCCESS = "The Code Machine is ONLINE. HQ is promoting you to Senior Agent. 🕵️🎖️"
''',
            "concepts": ["functions", "while_loops", "conditions", "input"],
            "xp": 35,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: Crack the enemy code",
        "learn": (
            "<p>You intercepted an enemy message, but you don't know the key! 😱 Good news: there are only 25 possible keys. "
            "A computer can try them ALL in a blink — that's called a <b>brute-force attack</b>.</p>"
            "<pre>for key in range(1, 26):\n    print(key, decode(secret, key))</pre>"
            "<p>Scan the list — only one line will be real words. That's the key! "
            "(This is why real spies use much stronger codes than Caesar's. 😉)</p>"
        ),
        "task": (
            "<p>Write <code>crack(secret)</code> that prints the message decoded with <b>every key from 1 to 25</b>, "
            "showing the key next to each try. Bonus: add it to your menu as option 5.</p>"
        ),
        "starter": A6_SOL.replace(
            'agent = input("What\'s your name, recruit? ")',
            "# TODO BOSS: def crack(secret): print decode(secret, key) for every key 1 to 25\n\n"
            'agent = input("What\'s your name, recruit? ")',
        ),
        "hints": [
            "<code>def crack(secret):</code> then a for loop over <code>range(1, 26)</code>.",
            "Inside the loop, print the key AND <code>decode(secret, key)</code>.",
            "<pre>def crack(secret):\n    for key in range(1, 26):\n        print(key, decode(secret, key))</pre>",
        ],
        "solution": ABOSS_SOL,
        "check": AGENT_HELP + r'''
r = run(inputs=["Sam", "4"])
f = r.fn("crack")
for plain, key in (("meet me at the park", 7), ("the pizza is a lie", 19)):
    v, out = capture(f, ref_encode(plain, key))
    text = out + " " + str(v)
    expect(plain in text.lower(), f"I gave <code>crack</code> an enemy message (secretly \"{plain}\"), but none of the tries showed it. "
                                  "Decode with every key from 1 to 25!")
    expect(len([l for l in out.splitlines() if l.strip()]) >= 25 or (isinstance(v, list) and len(v) >= 25),
           "Show ALL 25 tries (keys 1 to 25), one per line.")
SUCCESS = "Enemy code CRACKED. You are officially the agency's top codebreaker. 🏆🕵️"
''',
        "concepts": ["functions", "for_loops"],
        "xp": 90,
    },
    "remix": {
        "prompt": "Make it yours! Every agent customizes their gear.",
        "ideas": [
            "Make capital letters stay capital (hint: check <code>letter.isupper()</code> and use an uppercase alphabet).",
            "Add a \"password strength\" function that returns weak / okay / strong based on length.",
            "Add a secret agent login: the menu only opens if the user types the right passphrase.",
            "Invent your own cipher: reverse the message, THEN Caesar shift it. Double trouble!",
        ],
    },
}

PROJECTS = [HANGMAN_PROJECT, AGENT_PROJECT]

# ---------------------------------------------------------------------------
# PRACTICE
# ---------------------------------------------------------------------------

PRACTICE = [
    {
        "id": "p_lists_1",
        "concept": "lists",
        "title": "Snack Stack",
        "difficulty": 1,
        "task": (
            "<p>Make a list called <code>snacks</code> with 3 of your favorite snacks. Then <code>.append()</code> "
            "a 4th one, print the whole list, and print the first snack using <code>snacks[0]</code>.</p>"
        ),
        "starter": "# TODO: snacks = [...] with 3 snacks\n# append a 4th, print the list, print snacks[0]\n",
        "hints": [
            "<code>snacks = [\"chips\", \"cookies\", \"grapes\"]</code>",
            "<code>snacks.append(\"popcorn\")</code>",
            "<code>print(snacks)</code> and <code>print(\"First up:\", snacks[0])</code>",
        ],
        "solution": "snacks = [\"chips\", \"cookies\", \"grapes\"]\nsnacks.append(\"popcorn\")\nprint(snacks)\nprint(\"First up:\", snacks[0])\n",
        "check": r'''
r = run()
s = r.var("snacks")
expect(isinstance(s, list), "<code>snacks</code> should be a list with square brackets.")
expect(len(s) >= 4, f"Your list has {len(s)} snack(s). Start with 3 and <code>.append()</code> one more.")
expect(calls("append") >= 1, "Use <code>snacks.append(...)</code> to add the 4th snack.")
expect(all(r.has(str(x)) for x in s), "Print the whole list with <code>print(snacks)</code>.")
SUCCESS = "Snack stack secured. 🍿"
''',
        "xp": 15,
    },
    {
        "id": "p_lists_2",
        "concept": "lists",
        "title": "High Score Board",
        "difficulty": 2,
        "task": (
            "<p>Use a for loop to ask for <b>5 scores</b> (as numbers) and <code>.append()</code> each to a list called "
            "<code>scores</code>. Then print the <b>highest</b> and <b>lowest</b> score. "
            "(<code>max(scores)</code> and <code>min(scores)</code> are allowed!)</p>"
        ),
        "starter": "scores = []\n\n# TODO: ask for 5 scores with a for loop and append each one (use int!)\n\n# TODO: print the highest and lowest\n",
        "hints": [
            "<code>for i in range(5):</code> then <code>score = int(input(\"Score: \"))</code>",
            "<code>scores.append(score)</code> inside the loop.",
            "After the loop: <code>print(\"Highest:\", max(scores))</code> and <code>print(\"Lowest:\", min(scores))</code>",
        ],
        "solution": "scores = []\n\nfor i in range(5):\n    score = int(input(\"Score: \"))\n    scores.append(score)\n\nprint(\"Highest:\", max(scores))\nprint(\"Lowest:\", min(scores))\n",
        "check": HANG_HELP + r'''
import re
for vals in ([3, 9, 2, 7, 5], [40, 15, 88, 62, 71]):
    r = run(inputs=[str(v) for v in vals])
    s = r.var("scores")
    expect(isinstance(s, list) and [int(x) for x in s] == vals, f"I typed {vals}, but <code>scores</code> is {s!r}. Append each score to the list.")
    nums = [int(x) for x in re.findall(r"\d+", " ".join(after_last_prompt(r)))]
    expect(max(vals) in nums and min(vals) in nums, f"For {vals} I expected to see the highest ({max(vals)}) and lowest ({min(vals)}) at the end.")
SUCCESS = "Leaderboard updated! 🏅"
''',
        "xp": 20,
    },
    {
        "id": "p_lists_3",
        "concept": "lists",
        "title": "Backwards Parade",
        "difficulty": 3,
        "task": (
            "<p>Keep asking for words until the user types <code>done</code>. Store them in a list, then print them in "
            "<b>reverse</b> order — the last word first. (Try <code>words.reverse()</code> or a loop over "
            "<code>range(len(words) - 1, -1, -1)</code>.)</p>"
        ),
        "starter": "words = []\n\n# TODO: keep asking for words until \"done\", append each (but not \"done\")\n\n# TODO: print them in reverse order\n",
        "hints": [
            "<code>while True:</code> → <code>w = input(\"Word: \")</code> → <code>if w == \"done\": break</code> → <code>words.append(w)</code>",
            "<code>words.reverse()</code> flips the list in place.",
            "Then <code>for w in words:</code> <code>print(w)</code>",
        ],
        "solution": "words = []\n\nwhile True:\n    w = input(\"Word (or done): \")\n    if w == \"done\":\n        break\n    words.append(w)\n\nwords.reverse()\nfor w in words:\n    print(w)\n",
        "check": HANG_HELP + r'''
for vals in (["cat", "dog", "emu"], ["red", "blue", "green", "pink"]):
    r = run(inputs=vals + ["done"])
    t = "\n".join(after_last_prompt(r))
    pos = [t.find(v) for v in vals]
    expect(all(p >= 0 for p in pos), f"After typing done, I expected to see all the words {vals} printed.")
    expect(pos == sorted(pos, reverse=True), f"I typed {vals}, but they didn't come out backwards (last one first).")
SUCCESS = "!edarap sdrawkcab A 🎉"
''',
        "xp": 25,
    },
    {
        "id": "p_functions_1",
        "concept": "functions",
        "title": "Double Trouble",
        "difficulty": 1,
        "task": "<p>Write a function <code>double(n)</code> that <b>returns</b> the number times 2.</p>",
        "starter": "def double(n):\n    # TODO: return n times 2\n    pass\n\nprint(double(21))\n",
        "hints": [
            "Replace <code>pass</code> with a <code>return</code> line.",
            "Multiply with <code>*</code>.",
            "<code>return n * 2</code>",
        ],
        "solution": "def double(n):\n    return n * 2\n\nprint(double(21))\n",
        "check": r'''
r = run()
f = r.fn("double")
for n in (3, 10, -4, 0):
    v, out = capture(f, n)
    expect(v is not None, "Your function gave back nothing — use <code>return</code>, not <code>print</code>.")
    expect(v == n * 2, f"<code>double({n})</code> returned {v!r}, but I expected {n * 2}.")
SUCCESS = "Double the fun! ✌️"
''',
        "xp": 15,
    },
    {
        "id": "p_functions_2",
        "concept": "functions",
        "title": "Even Steven",
        "difficulty": 2,
        "task": (
            "<p>Write <code>is_even(n)</code> that returns <code>True</code> if the number is even and <code>False</code> if it's odd. "
            "Tip: <code>n % 2</code> is the remainder after dividing by 2.</p>"
        ),
        "starter": "def is_even(n):\n    # TODO: return True if n is even, False if odd\n    pass\n\nprint(is_even(4), is_even(7))\n",
        "hints": [
            "An even number has remainder 0 when divided by 2.",
            "<code>if n % 2 == 0:</code> <code>return True</code>, otherwise <code>return False</code>.",
            "Shortcut: <code>return n % 2 == 0</code>",
        ],
        "solution": "def is_even(n):\n    return n % 2 == 0\n\nprint(is_even(4), is_even(7))\n",
        "check": r'''
r = run()
f = r.fn("is_even")
for n, want in ((4, True), (7, False), (0, True), (-3, False), (100, True)):
    v, out = capture(f, n)
    expect(v in (True, False), f"<code>is_even({n})</code> returned {v!r}. It should return True or False.")
    expect(bool(v) == want, f"<code>is_even({n})</code> returned {v!r}, but I expected {want}.")
SUCCESS = "Even Steven approves. ⚖️"
''',
        "xp": 20,
    },
    {
        "id": "p_functions_3",
        "concept": "functions",
        "title": "Shout Machine",
        "difficulty": 2,
        "task": (
            "<p>Write <code>shout(word, times)</code> that returns the word in CAPITALS with an <code>!</code>, repeated "
            "<code>times</code> times. <code>shout(\"hey\", 3)</code> → <code>HEY!HEY!HEY!</code></p>"
        ),
        "starter": "def shout(word, times):\n    # TODO: return word.upper() + \"!\" repeated times times\n    pass\n\nprint(shout(\"hey\", 3))\n",
        "hints": [
            "<code>word.upper()</code> makes capitals.",
            "Strings can be multiplied: <code>\"ha\" * 3</code> is <code>\"hahaha\"</code>.",
            "<code>return (word.upper() + \"!\") * times</code>",
        ],
        "solution": "def shout(word, times):\n    return (word.upper() + \"!\") * times\n\nprint(shout(\"hey\", 3))\n",
        "check": r'''
r = run()
f = r.fn("shout")
for w, n in (("hey", 3), ("go", 1), ("pizza", 4)):
    v, out = capture(f, w, n)
    want = (w.upper() + "!") * n
    expect(isinstance(v, str), f"<code>shout({w!r}, {n})</code> should <code>return</code> a string.")
    expect(v.replace(" ", "") == want, f"<code>shout({w!r}, {n})</code> returned {v!r}, but I expected {want!r}.")
SUCCESS = "WOW!WOW!WOW! 📣"
''',
        "xp": 20,
    },
    {
        "id": "p_functions_4",
        "concept": "functions",
        "title": "Longest Word Finder",
        "difficulty": 3,
        "task": (
            "<p>Write <code>longest(words)</code> that takes a <b>list</b> of words and returns the longest one. "
            "Use a loop and keep track of the best so far (like a “king of the hill” game 👑).</p>"
        ),
        "starter": "def longest(words):\n    # TODO: loop over words, remember the longest so far, return it\n    pass\n\nprint(longest([\"cat\", \"giraffe\", \"dog\"]))\n",
        "hints": [
            "Start with <code>best = words[0]</code>.",
            "<code>for w in words:</code> → <code>if len(w) > len(best):</code> → <code>best = w</code>",
            "After the loop: <code>return best</code>",
        ],
        "solution": "def longest(words):\n    best = words[0]\n    for w in words:\n        if len(w) > len(best):\n            best = w\n    return best\n\nprint(longest([\"cat\", \"giraffe\", \"dog\"]))\n",
        "check": r'''
r = run()
f = r.fn("longest")
for ws, want in ((["cat", "giraffe", "dog"], "giraffe"), (["a", "bb", "ccc", "dd"], "ccc"), (["supercalifragilistic", "hi"], "supercalifragilistic"), (["solo"], "solo")):
    v, out = capture(f, list(ws))
    expect(v == want, f"<code>longest({ws})</code> returned {v!r}, but I expected {want!r}.")
SUCCESS = "King of the hill: crowned! 👑"
''',
        "xp": 25,
    },
]
