"""Friendly error explanations, the Bug Bestiary, and idea-complexity analysis."""
import re

from .sandbox import kidast

# ---------------------------------------------------------------------------
# Bug Bestiary: every error type is a monster the learner "defeats" by fixing it
# ---------------------------------------------------------------------------
BESTIARY = {
    "SyntaxError": ("Syntax Slime", "🟢", "Oozes in when Python can't read a line — a missing bracket, quote or colon."),
    "IndentationError": ("Indent Imp", "😈", "Messes with your spaces. Code inside if/for/def must be pushed in the same amount."),
    "TabError": ("Indent Imp", "😈", "Mixed tabs and spaces. Pick one (the editor uses spaces)."),
    "NameError": ("Name Gremlin", "👺", "Appears when you use a name Python has never heard of — often a typo."),
    "TypeError": ("Type Troll", "🧌", "Gets angry when you mix types, like adding text and a number."),
    "ValueError": ("Value Vampire", "🧛", "Bites when a value has the right type but a weird value, like int('pizza')."),
    "IndexError": ("Index Ogre", "👹", "Stomps when you reach past the end of a list."),
    "KeyError": ("Key Kobold", "🗝️", "Hides dictionary keys that don't exist."),
    "ZeroDivisionError": ("Zero Dragon", "🐉", "Breathes fire when anything is divided by zero."),
    "AttributeError": ("Attribute Alien", "👽", "Asks for a .thing that the object doesn't have."),
    "UnboundLocalError": ("Scope Specter", "👻", "Haunts functions that use a variable before giving it a value."),
    "RecursionError": ("Echo Hydra", "🐍", "A function that calls itself forever."),
    "OutOfInputs": ("Loop Leech", "🌀", "A loop that keeps asking and never stops."),
    "EOFError": ("Loop Leech", "🌀", "The program wanted more input than it got."),
}
MYSTERY = ("Mystery Bug", "🐛", "A rarer bug. Read the message carefully — it's a clue!")


def monster(error_type):
    name, emoji, desc = BESTIARY.get(error_type, MYSTERY)
    return {"type": error_type, "name": name, "emoji": emoji, "desc": desc}


PATTERNS = [
    (r"can only concatenate str \(not \"(\w+)\"\) to str",
     "You tried to glue text and a non-text value (a {0}) together with +. Turn the number into text with str(...), or use an f-string like f\"Score: {{score}}\"."),
    (r"unsupported operand type\(s\) for ([^:]+): 'str' and 'int'",
     "You're doing math ({0}) with text and a number. If the text came from input(), wrap it in int(...) first."),
    (r"unsupported operand type\(s\) for ([^:]+): 'int' and 'str'",
     "You're doing math ({0}) with a number and text. If the text came from input(), wrap it in int(...) first."),
    (r"'(<|>|<=|>=)' not supported between instances of 'str' and 'int'",
     "You're comparing text with a number. input() always gives text — use int(input(...)) to get a number."),
    (r"invalid literal for int\(\) with base 10: '(.*)'",
     "int() can only turn digits into a number, but it got '{0}'. Did someone type letters where a number was expected?"),
    (r"could not convert string to float: '(.*)'",
     "float() couldn't turn '{0}' into a number."),
    (r"name '(\w+)' is not defined. Did you mean: '(\w+)'",
     "Python doesn't know '{0}'. Did you mean '{1}'? Check spelling and capital letters."),
    (r"name '(\w+)' is not defined",
     "Python doesn't know anything called '{0}'. Is it spelled right? Did you create it (with = ) before this line? If it's text, put it in quotes."),
    (r"list index out of range",
     "You asked for a list position that doesn't exist. Lists start at 0, so a list of 3 things has positions 0, 1 and 2."),
    (r"string index out of range",
     "You asked for a letter position past the end of the text. Positions start at 0."),
    (r"division by zero",
     "Something got divided by zero, which even computers can't do. Check the number on the right of / or %."),
    (r"(\w+)\(\) missing (\d+) required positional argument",
     "The function {0}() needs {1} more value(s) inside the brackets when you call it."),
    (r"(\w+)\(\) takes (\d+) positional arguments? but (\d+) (?:was|were) given",
     "{0}() expects {1} value(s) but you gave it {2}. (Inside a class, don't forget `self` as the first parameter!)"),
    (r"'(\w+)' object has no attribute '(\w+)'",
     "A {0} doesn't have anything called .{1}. Check the spelling, or whether you set self.{1} in __init__."),
    (r"'(\w+)' object is not callable",
     "You put () after a {0}, but only functions can be called. Maybe a variable has the same name as a function?"),
    (r"'(\w+)' object is not subscriptable",
     "You used [ ] on a {0}, but only lists, strings and dictionaries can do that."),
    (r"'str' object does not support item assignment",
     "Text can't be changed one letter at a time. Build a new string instead (or use a list of letters)."),
    (r"expected ':'",
     "Lines that start with if, elif, else, for, while, def and class need a colon : at the end."),
    (r"unterminated string literal",
     "A piece of text is missing its closing quote. Every \" needs a partner \"."),
    (r"'\(' was never closed",
     "An opening bracket ( is missing its closing ). Count your brackets!"),
    (r"unmatched '\)'",
     "There's an extra closing bracket )."),
    (r"expected an indented block",
     "After a line ending in :, the next line must be pushed in (press Tab or 4 spaces)."),
    (r"unexpected indent",
     "This line is pushed in, but it shouldn't be. Line it up with the code around it."),
    (r"unindent does not match any outer indentation level",
     "This line's spaces don't line up with anything above it. Make it match the block it belongs to."),
    (r"Perhaps you forgot a comma",
     "Python thinks a comma is missing between two things — maybe inside print(...) or a list."),
    (r"Missing parentheses in call to 'print'",
     "print needs brackets: print(\"hello\")."),
    (r"cannot assign to (?:literal|expression)",
     "The left side of = must be a variable name. To compare two things, use == instead."),
    (r"invalid syntax. Maybe you meant '==' or ':='",
     "To compare two things use == (two equal signs). A single = stores a value."),
    (r"KeyError",
     "That key isn't in the dictionary. Check spelling, or use .get(key) to be safe."),
]

GENERIC = {
    "SyntaxError": "Python couldn't read this line. Look for missing quotes, brackets, colons or commas.",
    "IndentationError": "The spaces at the start of the line are off. Blocks under if/for/def must line up.",
    "NameError": "Python doesn't recognise a name here. Check spelling and that it was created first.",
    "TypeError": "Two things of different types got mixed up (like text and numbers).",
    "ValueError": "A value had a strange form — like turning 'abc' into a number.",
    "IndexError": "You reached past the end of a list or string.",
    "KeyError": "That key doesn't exist in the dictionary.",
    "ZeroDivisionError": "Something was divided by zero.",
    "AttributeError": "That object doesn't have that .attribute or .method().",
    "EOFError": "The program wanted more input than it got.",
    "KeyboardInterrupt": "The program was stopped.",
    "RecursionError": "A function kept calling itself forever.",
    "UnboundLocalError": "Inside a function, a variable is used before it gets a value. Pass it in as a parameter, or return the new value.",
}


def explain(error_type, message, text=""):
    blob = f"{message}\n{text}"
    if error_type == "KeyError":
        return f"The dictionary has no key {message}. Check spelling, or use .get() to be safe."
    for pat, tmpl in PATTERNS:
        m = re.search(pat, blob)
        if m:
            return tmpl.format(*m.groups())
    return GENERIC.get(error_type, "Read the message carefully and look at the line number — it's a clue!")


# ---------------------------------------------------------------------------
# Idea analysis: how ambitious / complex is an idea the learner describes?
# ---------------------------------------------------------------------------
IDEA_SIGNALS = {
    "input": ["ask", "type", "answer", "enter", "user", "player types", "question", "chat", "talk", "reply"],
    "variables": ["score", "points", "lives", "health", "hp", "money", "coins", "name", "count", "level", "energy"],
    "math": ["calculate", "add", "total", "percent", "multiply", "divide", "average", "damage", "cost", "price", "speed"],
    "conditions": ["if", "when", "win", "lose", "correct", "wrong", "choose", "decide", "unless", "otherwise", "depends", "check"],
    "random": ["random", "surprise", "luck", "dice", "roll", "chance", "shuffle", "unpredictable", "spawn"],
    "while_loops": ["until", "keep", "again", "forever", "repeat", "game over", "rounds", "play again", "loop"],
    "for_loops": ["each", "every", "10 times", "times", "pattern", "grid", "rows"],
    "turtle": ["draw", "art", "color", "colour", "shape", "picture", "spiral", "star", "paint", "animation"],
    "lists": ["list", "inventory", "collect", "items", "deck", "cards", "queue", "leaderboard", "words", "team"],
    "dicts": ["stats", "profile", "map", "rooms", "database", "lookup", "shop", "catalog", "pokedex", "save"],
    "functions": ["menu", "options", "commands", "abilities", "moves", "tools", "modes"],
    "classes": ["character", "characters", "enemy", "enemies", "pet", "pets", "players", "monster", "monsters", "robot", "objects", "boss"],
    "strings": ["secret", "code", "letters", "word", "message", "encrypt", "reverse", "spell"],
}
LEVELS = [(0, "Spark", "⚡"), (25, "Builder", "🧱"), (45, "Inventor", "💡"), (65, "Architect", "🏗️"), (82, "Mastermind", "🧠")]


def analyze_idea(text, learned=None):
    """Score an idea description 0–100 and say which concepts it would need."""
    learned = set(learned or [])
    t = " " + re.sub(r"[^a-z0-9 ]", " ", text.lower()) + " "
    words = t.split()
    needed = {}
    for concept, keys in IDEA_SIGNALS.items():
        hits = [k for k in keys if f" {k} " in t]
        if hits:
            needed[concept] = hits
    parts = [p for p in re.split(r"[.!?\n,;]| and | then | also | plus ", text.lower()) if len(p.split()) >= 2]
    features = len(parts)
    breadth = len(needed)
    advanced = sum(1 for c in needed if c in ("classes", "dicts", "functions", "lists", "while_loops"))
    score = min(100, round(
        min(len(words), 80) / 80 * 20 + min(features, 6) / 6 * 30 + min(breadth, 8) / 8 * 35 + min(advanced, 4) / 4 * 15))
    level = 1
    for i, (threshold, _, _) in enumerate(LEVELS):
        if score >= threshold:
            level = i + 1
    _, level_name, level_emoji = LEVELS[level - 1]
    new_concepts = [c for c in needed if c not in learned]
    tips = []
    if features <= 1:
        tips.append("Idea booster: what happens when you win? When you lose? Add one twist!")
    if "random" not in needed:
        tips.append("Could something surprising happen? A random event makes games replayable.")
    if features >= 5:
        tips.append("Big idea! Build the smallest version first, then add one feature at a time.")
    if new_concepts:
        tips.append("This needs things you haven't learned yet: "
                    + ", ".join(kidast.CONCEPT_LABELS[c] for c in new_concepts)
                    + ". You can still start — or save it for later!")
    return {
        "score": score, "level": level, "level_name": level_name, "level_emoji": level_emoji,
        "features": features, "words": len(words),
        "concepts": {c: h for c, h in needed.items()},
        "new_concepts": new_concepts, "tips": tips[:3],
    }


def analyze_code(source):
    concepts = kidast.detect_concepts(source)
    return {
        "metrics": kidast.metrics(source),
        "complexity": kidast.complexity_score(source),
        "concepts": [c for c, n in concepts.items() if n],
    }
