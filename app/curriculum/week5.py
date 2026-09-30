"""Week 5: dictionaries. Projects 9 (Monster Collector) and 10 (Escape the Castle)."""

# Shared helpers pasted in front of checks that need them.
# reply(r, inputs, k): the text the program printed right after the k-th answer (0-based),
# up to the next input prompt.
_REPLY = r'''
def reply(r, inputs, k):
    out, pos = r.output, 0
    for j in range(k + 1):
        if j >= len(r.prompts):
            return out[pos:]
        piece = r.prompts[j] + str(inputs[j]) + "\n"
        i = out.find(piece, pos)
        if i < 0:
            return out[pos:]
        pos = i + len(piece)
    end = len(out)
    if k + 1 < len(r.prompts) and r.prompts[k + 1].strip():
        e = out.find(r.prompts[k + 1], pos)
        if e >= 0:
            end = e
    return out[pos:end]
'''

# path_to(rooms, start, goal, blocked): breadth-first search through the castle.
# Returns (room, [directions]) or (None, None).
_PATH = r'''
def path_to(rooms, start, goal, blocked=()):
    seen = {start}
    queue = [(start, [])]
    while queue:
        room, p = queue.pop(0)
        if goal(room):
            return room, p
        exits = rooms.get(room, {}).get("exits", {}) if isinstance(rooms.get(room), dict) else {}
        for d, t in exits.items():
            if t in rooms and t not in seen and t not in blocked:
                seen.add(t)
                queue.append((t, p + [d]))
    return None, None
'''


def _next(prev, todo):
    """Starter for the next step: the previous solution plus a TODO comment."""
    return prev.rstrip() + "\n\n" + todo.strip() + "\n"


# ---------------------------------------------------------------------------
# Project 9: Monster Collector
# ---------------------------------------------------------------------------

MC_START = r'''# Monster Collector 👾
print("Welcome to Monster Collector!")

# TODO: make a dictionary called monster with the keys "name", "type", "hp" and "attack"
# TODO: print the monster's name and its hp
'''

MC1 = r'''# Monster Collector 👾
print("Welcome to Monster Collector!")

monster = {"name": "Blobzilla", "type": "slime", "hp": 30, "attack": 7}
print("You found a wild", monster["name"] + "!")
print(f"It has {monster['hp']} HP and {monster['attack']} attack.")
'''

MC2 = MC1 + r'''
# Give it a level
monster["level"] = 1
print(monster["name"], "is level", monster["level"])

# LEVEL UP!
monster["level"] = monster["level"] + 1
monster["hp"] += 5
print(f"⭐ LEVEL UP! {monster['name']} is now level {monster['level']} with {monster['hp']} HP!")
'''

MC3 = MC2 + r'''
# My whole collection: monster name -> stats dictionary
collection = {
    "Blobzilla": monster,
    "Sir Fluffington": {"name": "Sir Fluffington", "type": "fluff", "hp": 25, "attack": 9},
    "Toastgeist": {"name": "Toastgeist", "type": "ghost", "hp": 40, "attack": 5},
    "Captain Noodle": {"name": "Captain Noodle", "type": "pasta", "hp": 35, "attack": 6},
}

print("📖 MY COLLECTION")
for name, stats in collection.items():
    print(f"{name}: {stats['hp']} HP, {stats['attack']} attack")
'''

MC4 = MC3 + r'''
# Look up one monster
pick = input("Which monster do you want to look at? ")
stats = collection.get(pick)
if stats == None:
    print(f"Hmm, there's no {pick} in your collection. 🤔")
else:
    print(f"{pick}: {stats['hp']} HP, {stats['attack']} attack, type: {stats.get('type', 'mystery')}")
'''

MC5 = MC4 + r'''
import random

def battle(name1, name2):
    hp1 = collection[name1]["hp"]
    hp2 = collection[name2]["hp"]
    print(f"⚔️  {name1} VS {name2}! FIGHT!")
    turn = 1
    while hp1 > 0 and hp2 > 0:
        if turn == 1:
            hit = random.randint(1, collection[name1]["attack"])
            hp2 = hp2 - hit
            print(f"{name1} bonks {name2} for {hit}! ({name2} has {max(hp2, 0)} HP left)")
            turn = 2
        else:
            hit = random.randint(1, collection[name2]["attack"])
            hp1 = hp1 - hit
            print(f"{name2} whacks {name1} for {hit}! ({name1} has {max(hp1, 0)} HP left)")
            turn = 1
    if hp1 > 0:
        return name1
    return name2

winner = battle("Blobzilla", "Toastgeist")
print(f"🏆 {winner} wins the battle!")
'''

MC_MENU_HEAD = r'''# Monster Collector 👾
import random

print("Welcome to Monster Collector!")

monster = {"name": "Blobzilla", "type": "slime", "hp": 30, "attack": 7}
monster["level"] = 2
monster["hp"] += 5

collection = {
    "Blobzilla": monster,
    "Sir Fluffington": {"name": "Sir Fluffington", "type": "fluff", "hp": 25, "attack": 9},
    "Toastgeist": {"name": "Toastgeist", "type": "ghost", "hp": 40, "attack": 5},
    "Captain Noodle": {"name": "Captain Noodle", "type": "pasta", "hp": 35, "attack": 6},
}


def show_collection():
    print("📖 MY COLLECTION")
    for name, stats in collection.items():
        print(f"{name}: {stats['hp']} HP, {stats['attack']} attack")


def battle(name1, name2):
    hp1 = collection[name1]["hp"]
    hp2 = collection[name2]["hp"]
    print(f"⚔️  {name1} VS {name2}! FIGHT!")
    turn = 1
    while hp1 > 0 and hp2 > 0:
        if turn == 1:
            hit = random.randint(1, collection[name1]["attack"])
            hp2 = hp2 - hit
            print(f"{name1} bonks {name2} for {hit}! ({name2} has {max(hp2, 0)} HP left)")
            turn = 2
        else:
            hit = random.randint(1, collection[name2]["attack"])
            hp1 = hp1 - hit
            print(f"{name2} whacks {name1} for {hit}! ({name1} has {max(hp1, 0)} HP left)")
            turn = 1
    if hp1 > 0:
        return name1
    return name2


while True:
    print()
    print("1 = show collection, 2 = look up, 3 = battle, 4 = catch a monster, q = quit")
    choice = input("What now? ")
    if choice == "1":
        show_collection()
    elif choice == "2":
        pick = input("Which monster? ")
        stats = collection.get(pick)
        if stats == None:
            print(f"Hmm, there's no {pick} in your collection. 🤔")
        else:
            print(f"{pick}: {stats['hp']} HP, {stats['attack']} attack")
    elif choice == "3":
        first = input("First fighter: ")
        second = input("Second fighter: ")
        if first in collection and second in collection:
            winner = battle(first, second)
'''

MC6 = MC_MENU_HEAD + r'''            print(f"🏆 {winner} wins!")
        else:
            print("Both fighters have to be in your collection!")
    elif choice == "4":
        new_name = input("A wild monster appears! What will you name it? ")
        collection[new_name] = {"name": new_name, "type": "wild",
                                "hp": random.randint(15, 45), "attack": random.randint(3, 10)}
        print(f"🎉 Gotcha! You caught {new_name}!")
    elif choice == "q":
        print("Bye, monster master! 👋")
        break
    else:
        print("Huh? Pick 1, 2, 3, 4 or q.")
'''

MC_BOSS = MC_MENU_HEAD + r'''            collection[winner]["wins"] = collection[winner].get("wins", 0) + 1
            collection[winner]["attack"] += 1
            print(f"🏆 {winner} wins! That's win #{collection[winner]['wins']}. Attack +1!")
        else:
            print("Both fighters have to be in your collection!")
    elif choice == "4":
        new_name = input("A wild monster appears! What will you name it? ")
        collection[new_name] = {"name": new_name, "type": "wild",
                                "hp": random.randint(15, 45), "attack": random.randint(3, 10)}
        print(f"🎉 Gotcha! You caught {new_name}!")
    elif choice == "5":
        print("🏅 LEADERBOARD")
        for name, stats in collection.items():
            print(f"{name}: {stats.get('wins', 0)} wins")
    elif choice == "q":
        print("Bye, monster master! 👋")
        break
    else:
        print("Huh? Pick 1, 2, 3, 4, 5 or q.")
'''

MC_CHECK1 = r'''
r = run()
m = r.var("monster")
expect(isinstance(m, dict), "`monster` should be a dictionary - made with curly braces, like {\"name\": \"Blobzilla\", ...}.")
for k in ["name", "hp", "attack"]:
    have = ", ".join(str(x) for x in m.keys()) or "nothing yet"
    expect(k in m, f"Your monster dictionary needs a \"{k}\" key. Right now it has: {have}.")
expect(isinstance(m["hp"], int) and isinstance(m["attack"], int),
       "Make \"hp\" and \"attack\" whole numbers (like 30, with no quotes) so we can do math with them later.")
expect(r.has(str(m["name"])), f"Print your monster's name! I expected to see {m['name']} in the output.")
expect(r.has(str(m["hp"])), f"Print your monster's hp too - I didn't see {m['hp']} in the output.")
expect("monster[" in source, "Read values OUT of the dictionary with square brackets, like monster[\"name\"].")
SUCCESS = f"{m['name']} has joined your team! 👾"
'''

MC_CHECK2 = r'''
import ast
r = run()
m = r.var("monster")
stores = 0
for n in ast.walk(tree):
    targets = n.targets if isinstance(n, ast.Assign) else ([n.target] if isinstance(n, ast.AugAssign) else [])
    if any(isinstance(t, ast.Subscript) for t in targets):
        stores += 1
expect(isinstance(m, dict) and "level" in m,
       "Add a \"level\" key to your monster AFTER you make it, with a line like: monster[\"level\"] = 1")
expect(stores >= 2, "Change the dictionary with square brackets: first monster[\"level\"] = 1, then level up with something like monster[\"level\"] += 1 and monster[\"hp\"] += 5.")
expect(isinstance(m["level"], int) and m["level"] >= 2,
       f"After leveling up, your monster should be at least level 2. It's level {m['level']}.")
expect(r.has(str(m["level"])), f"Print the new level! I didn't see {m['level']} in the output.")
expect(r.has(str(m["hp"])), f"Print the new hp after the level up! I didn't see {m['hp']} in the output.")
SUCCESS = "DING! ⭐ Your monster leveled up!"
'''

MC_CHECK3 = r'''
r = run()
col = r.var("collection")
expect(isinstance(col, dict) and len(col) >= 3,
       "Make a dictionary called `collection` with at least 3 monsters in it.")
for name, stats in col.items():
    expect(isinstance(stats, dict), f"Each monster in the collection should be a stats dictionary. collection[{name!r}] isn't one.")
    expect("hp" in stats and "attack" in stats,
           f"{name} needs \"hp\" and \"attack\" in its stats dictionary.")
expect(uses("for_loops") and calls("items") >= 1,
       "Show the collection with a loop: for name, stats in collection.items():")
for name, stats in col.items():
    expect(r.has(str(name)), f"I didn't see {name} in your collection list. Print every monster inside your loop!")
    expect(r.has(str(stats["hp"])), f"Print each monster's hp in the list - I didn't see {name}'s {stats['hp']}.")
SUCCESS = f"{len(col)} monsters in your Monster-dex! 📖"
'''

MC_CHECK4 = _REPLY + r'''
r0 = run(inputs=["zzz"])
col = r0.var("collection")
names = list(col.keys())
expect(len(r0.prompts) >= 1, "Ask the player which monster they want to see, using input().")
expect(calls("get") >= 1, "Look the monster up with collection.get(pick) - it gives back None instead of crashing if the monster isn't there.")
for nm in [names[0], names[-1]]:
    r = run(inputs=[nm])
    said = reply(r, [nm], 0)
    hp = col[nm]["hp"]
    expect(str(hp) in said, f"When I typed {nm}, I expected to see its HP ({hp}) printed after my answer. I saw: {said.strip()[:120]!r}")
r = run(inputs=["Definitely Not A Monster"])
said = reply(r, ["Definitely Not A Monster"], 0)
expect(said.strip(), "When I typed a monster that isn't in your collection, nothing got printed. Tell the player it's not there!")
SUCCESS = "Your Monster-dex can look things up! 🔍"
'''

MC_CHECK5 = r'''
r = run(inputs=["zzz"])
battle = r.fn("battle")
col = r.var("collection")
expect(imports("random"), "Battles need a little luck! import random and use random.randint(1, attack) for each hit.")

def fresh():
    col["Twin A"] = {"name": "Twin A", "type": "test", "hp": 20, "attack": 6}
    col["Twin B"] = {"name": "Twin B", "type": "test", "hp": 20, "attack": 6}
    col["Test Titan"] = {"name": "Test Titan", "type": "test", "hp": 100, "attack": 50}
    col["Tiny Tim"] = {"name": "Tiny Tim", "type": "test", "hp": 1, "attack": 1}

fresh()
w, out = capture(battle, "Twin A", "Twin B")
expect(w in ("Twin A", "Twin B"),
       f"battle(name1, name2) should RETURN the winner's name. When Twin A fought Twin B it returned {w!r}.")
expect("twin a" in norm(out) and "twin b" in norm(out),
       "Print the play-by-play! I want to see both monsters' names while they fight.")
expect(len([l for l in out.splitlines() if l.strip()]) >= 3,
       "Print a line for every hit so we can watch the fight, not just the result.")
winners = set()
for i in range(20):
    fresh()
    w, out = capture(battle, "Twin A", "Twin B")
    winners.add(w)
expect(len(winners) == 2,
       "When two identical monsters fight 20 times, each should win sometimes. Use random.randint for the damage!")
for a, b in [("Tiny Tim", "Test Titan"), ("Test Titan", "Tiny Tim")] * 5:
    fresh()
    w, out = capture(battle, a, b)
    expect(w == "Test Titan",
           "A monster with 100 hp and 50 attack should always beat one with 1 hp and 1 attack. "
           "Make sure the fight uses each monster's own \"hp\" and \"attack\" from the collection.")
SUCCESS = "⚔️ What a fight! Your battle engine works!"
'''

MC_CHECK6 = _REPLY + r'''
r = run(inputs=["q"])
col = r.var("collection")
names = list(col.keys())
expect(uses("while_loops"), "Put your menu inside a while True: loop so the player can keep choosing.")
inp = ["4", "Zappy McZapface", "1", "q"]
r = run(inputs=inp)
col2 = r.var("collection")
expect("Zappy McZapface" in col2,
       "When I chose 4 and named my monster Zappy McZapface, it didn't show up in collection. "
       "Add it with collection[new_name] = {...}")
z = col2["Zappy McZapface"]
expect(isinstance(z, dict) and isinstance(z.get("hp"), int) and isinstance(z.get("attack"), int),
       "New monsters need a stats dictionary with \"hp\" and \"attack\" numbers too (random.randint is fun here!).")
listing = reply(r, inp, 2)
expect("zappy mczapface" in norm(listing) and norm(names[0]) in norm(listing),
       "After catching Zappy McZapface, choice 1 should show the whole collection, including the new monster.")
inp = ["2", names[0], "q"]
r = run(inputs=inp)
hp = col[names[0]]["hp"]
expect(str(hp) in reply(r, inp, 1), f"Choice 2 should look up a monster. When I looked up {names[0]}, I didn't see its hp ({hp}).")
inp = ["3", names[0], names[1], "q"]
r = run(inputs=inp)
fight = reply(r, inp, 2)
expect(norm(names[0]) in norm(fight) and norm(names[1]) in norm(fight),
       f"Choice 3 should ask for two fighters and run battle(). When I picked {names[0]} and {names[1]}, I didn't see a fight.")
SUCCESS = "Your Monster Collector is a real game now! 🎮"
'''

MC_CHECK_BOSS = _REPLY + r'''
r = run(inputs=["q"])
col = r.var("collection")
names = list(col.keys())
a, b = names[0], names[1]
inp = ["3", a, b, "3", a, b, "3", b, a, "5", "q"]
r = run(inputs=inp)
col = r.var("collection")
total = sum(s.get("wins", 0) for s in col.values() if isinstance(s, dict))
expect(total == 3,
       f"I ran 3 battles, so your monsters should have 3 wins in total - I found {total}. "
       "After each battle do: collection[winner][\"wins\"] = collection[winner].get(\"wins\", 0) + 1")
expect(calls("get") >= 2, "Use .get(\"wins\", 0) so monsters that never won count as 0 instead of crashing.")
board = reply(r, inp, 9)
for n in (a, b):
    expect(norm(n) in norm(board), f"Choice 5 should show a leaderboard with every monster. I didn't see {n}.")
    line = [l for l in board.splitlines() if norm(n) in norm(l)]
    w = col[n].get("wins", 0)
    expect(any(str(w) in l for l in line), f"On the leaderboard, {n} should show {w} wins.")
SUCCESS = "🏅 Champion stuff! Your monsters remember every victory."
'''

MONSTER_COLLECTOR = {
    "id": "monster_collector",
    "week": 5,
    "order": 9,
    "title": "Monster Collector",
    "emoji": "👾",
    "tagline": "Catch goofy monsters, track their stats, and make them battle",
    "story": ("Professor Pickles has lost his Monster-dex! 😱 Wild monsters like Blobzilla and "
              "Sir Fluffington are running loose. Your mission: build a program that stores every "
              "monster's stats, shows off your collection, and lets two monsters BATTLE."),
    "concepts": ["dicts", "functions", "random", "while_loops", "for_loops"],
    "expected_minutes": 120,
    "steps": [
        {
            "id": "s1",
            "title": "Your first monster",
            "learn": """<p>A <b>dictionary</b> stores things by <i>name</i> instead of by position. It's like
the contacts app on your phone: you look up <code>"Mom"</code> and get her number. You don't need to
remember she's contact #37.</p>
<p>Each entry is a <b>key</b> and a <b>value</b>, joined with a colon. Curly braces go around the whole thing:</p>
<pre>pizza = {"topping": "pepperoni", "slices": 8}
print(pizza["topping"])   # pepperoni
print(pizza["slices"])    # 8</pre>
<p>A list would make you remember "slices is item #1". A dictionary lets you just say
<code>pizza["slices"]</code>. Perfect for a monster's stats!</p>""",
            "task": """<p>Make a dictionary called <code>monster</code> with these keys: <code>"name"</code>,
<code>"type"</code>, <code>"hp"</code> (hit points, a number) and <code>"attack"</code> (a number).
Invent your own goofy monster! Then print its name and its hp using square brackets, like
<code>monster["name"]</code>.</p>""",
            "starter": MC_START,
            "hints": [
                "A dictionary looks like {\"key\": value, \"key2\": value2}. Keys are strings in quotes.",
                "Numbers like hp don't need quotes: \"hp\": 30",
                "monster = {\"name\": \"Blobzilla\", \"type\": \"slime\", \"hp\": 30, \"attack\": 7} and then print(monster[\"name\"], monster[\"hp\"])",
            ],
            "solution": MC1,
            "check": MC_CHECK1,
            "concepts": ["dicts", "output", "fstrings"],
            "xp": 20,
        },
        {
            "id": "s2",
            "title": "LEVEL UP!",
            "learn": """<p>Dictionaries can change after you make them. Use the same square brackets, but put them
on the <b>left</b> of the <code>=</code>:</p>
<pre>pizza["slices"] = 6          # change a value
pizza["slices"] -= 1         # somebody ate one
pizza["extra_cheese"] = True # brand new key!</pre>
<p>If the key already exists, its value gets replaced. If it doesn't exist yet, Python adds it.
It's like editing a contact: change the number, or add a birthday that wasn't there before.</p>""",
            "task": """<p>Give your monster a new key <code>"level"</code> set to <code>1</code>. Then
<b>level it up</b>: add 1 to its level and add some hp (like <code>monster["hp"] += 5</code>).
Print a big LEVEL UP message showing the new level and the new hp.</p>""",
            "starter": _next(MC1, "# TODO: add a \"level\" key, then level up: +1 level and more hp. Print the new stats!"),
            "hints": [
                "Adding a key looks just like changing one: monster[\"level\"] = 1",
                "To add to a value, use += just like with a normal variable: monster[\"level\"] += 1",
                "monster[\"level\"] = 1, then monster[\"level\"] += 1 and monster[\"hp\"] += 5, then print(f\"LEVEL UP! Level {monster['level']}, HP {monster['hp']}\")",
            ],
            "solution": MC2,
            "check": MC_CHECK2,
            "concepts": ["dicts", "math", "fstrings"],
            "xp": 20,
        },
        {
            "id": "s3",
            "title": "Gotta store 'em all",
            "learn": """<p>One monster is lonely. Let's build a whole <b>collection</b>: a dictionary where each key
is a monster's name and each value is <i>that monster's stats dictionary</i>. A dictionary inside a
dictionary! Like a folder full of folders. 📁</p>
<pre>team = {
    "Blobzilla": {"hp": 30, "attack": 7},
    "Toastgeist": {"hp": 40, "attack": 5},
}
print(team["Toastgeist"]["hp"])   # 40</pre>
<p>To go through every entry, use <code>.items()</code>. It hands you the key AND the value each time around the loop:</p>
<pre>for name, stats in team.items():
    print(name, "has", stats["hp"], "HP")</pre>""",
            "task": """<p>Make a dictionary called <code>collection</code> with <b>at least 3 monsters</b>. Each
key is a monster name, and each value is a stats dictionary with at least <code>"hp"</code> and
<code>"attack"</code>. (You can put your first monster in too: <code>"Blobzilla": monster</code>.)
Then loop over <code>collection.items()</code> and print each monster's name, hp and attack.</p>""",
            "starter": _next(MC2, "# TODO: make a collection dictionary of 3+ monsters (name -> stats dictionary)\n# TODO: loop over collection.items() and print each one"),
            "hints": [
                "Each value in the collection is a whole dictionary, like \"Toastgeist\": {\"hp\": 40, \"attack\": 5}. Don't forget the commas between monsters!",
                "for name, stats in collection.items(): gives you each monster's name and stats",
                "Inside the loop: print(f\"{name}: {stats['hp']} HP, {stats['attack']} attack\")",
            ],
            "solution": MC3,
            "check": MC_CHECK3,
            "concepts": ["dicts", "for_loops", "fstrings"],
            "xp": 30,
        },
        {
            "id": "s4",
            "title": "Search the Monster-dex",
            "learn": """<p>If you ask a dictionary for a key that isn't there, like <code>collection["Bob"]</code>,
Python crashes with a <code>KeyError</code>. 💥 Not great when the player typed a name wrong!</p>
<p>The safe way is <code>.get()</code>. If the key is missing, it gives back <code>None</code>
(Python's word for "nothing") or a backup value you choose:</p>
<pre>ages = {"Ava": 13, "Ben": 12}
print(ages.get("Ava"))        # 13
print(ages.get("Zed"))        # None
print(ages.get("Zed", 0))     # 0  (your backup value)</pre>
<p>It's like asking a friend "do you have Zed's number?" instead of your phone exploding.</p>""",
            "task": """<p>Ask the player which monster they want to look at. Use <code>collection.get(pick)</code>
to find it. If the answer is <code>None</code>, print a friendly "no monster by that name" message.
Otherwise print that monster's hp and attack.</p>""",
            "starter": _next(MC3, "# TODO: ask which monster to look at, look it up with collection.get(...)\n# TODO: if it's None, say it's not there. Otherwise print its stats"),
            "hints": [
                "pick = input(\"Which monster? \") gets the name. The player has to type it exactly like your key.",
                "stats = collection.get(pick) and then check: if stats == None:",
                "if stats == None: print(\"No monster called that!\")  else: print(f\"{pick}: {stats['hp']} HP, {stats['attack']} attack\")",
            ],
            "solution": MC4,
            "check": MC_CHECK4,
            "concepts": ["dicts", "input", "conditions"],
            "xp": 25,
        },
        {
            "id": "s5",
            "title": "BATTLE TIME ⚔️",
            "learn": """<p>Time for the good stuff. A battle is a <b>function</b> that takes two monster names,
looks up their stats, and lets them take turns bonking each other until someone runs out of hp.</p>
<p>Copy the hp into normal variables first, so the fight doesn't permanently hurt your monsters:</p>
<pre>hp1 = collection[name1]["hp"]
hit = random.randint(1, collection[name1]["attack"])
hp2 = hp2 - hit</pre>
<p>A <code>while</code> loop keeps the fight going <code>while hp1 &gt; 0 and hp2 &gt; 0</code>. A
<code>turn</code> variable can flip between 1 and 2 so they take turns. When the loop ends, whoever
still has hp is the winner. <code>return</code> their name!</p>""",
            "task": """<p>Write <code>def battle(name1, name2):</code>. It should look up both monsters in
<code>collection</code>, make them take turns hitting each other for
<code>random.randint(1, attack)</code> damage, print every hit, and <b>return the winner's name</b>.
Then call it with two of your monsters and print who won.</p>""",
            "starter": _next(MC4, "import random\n\n# TODO: def battle(name1, name2): take turns hitting until someone's hp runs out\n# TODO: return the winner's name, then call battle() and print the winner"),
            "hints": [
                "Start with hp1 = collection[name1][\"hp\"] and hp2 = collection[name2][\"hp\"], then while hp1 > 0 and hp2 > 0:",
                "Use a turn variable: if turn == 1, monster 1 hits (hp2 = hp2 - hit) and turn = 2; else monster 2 hits and turn = 1.",
                "After the loop: if hp1 > 0: return name1, otherwise return name2. Then: winner = battle(\"Blobzilla\", \"Toastgeist\")",
            ],
            "solution": MC5,
            "check": MC_CHECK5,
            "concepts": ["functions", "dicts", "random", "while_loops", "conditions"],
            "xp": 40,
        },
        {
            "id": "s6",
            "title": "The Monster Menu",
            "learn": """<p>Real games have a menu. The trick is a <code>while True:</code> loop that shows the choices,
asks what to do, and uses <code>if/elif</code> to do it. <code>break</code> leaves the loop when the player quits.</p>
<pre>while True:
    choice = input("1 = show, q = quit: ")
    if choice == "1":
        show_collection()
    elif choice == "q":
        break</pre>
<p>Catching a new monster is just adding a key: <code>collection[new_name] = {"hp": 30, "attack": 5}</code>.
Use <code>random.randint</code> so every wild monster is a surprise!</p>""",
            "task": """<p>Turn your program into a menu game. Move the look-up and the battle <b>into</b> the menu
(delete the old ones that ran at the start). Inside a <code>while True:</code> loop, ask
<code>What now?</code> and handle:</p>
<ul><li><code>1</code> = show the collection</li>
<li><code>2</code> = look up a monster (ask for its name)</li>
<li><code>3</code> = battle (ask for two fighter names, then call <code>battle</code>)</li>
<li><code>4</code> = catch a monster (ask ONLY for its name, give it random hp and attack)</li>
<li><code>q</code> = quit</li></ul>""",
            "starter": _next(MC5, "# TODO: build a menu inside while True:\n#   1 = show collection, 2 = look up, 3 = battle, 4 = catch, q = quit\n# (move your look-up and battle code into the menu)"),
            "hints": [
                "Put your 'show the collection' loop into a function def show_collection(): so choice 1 can just call it.",
                "For choice 4: new_name = input(\"Name it: \") then collection[new_name] = {\"hp\": random.randint(15, 45), \"attack\": random.randint(3, 10)}",
                "For choice 3: first = input(\"First fighter: \"), second = input(\"Second fighter: \"), winner = battle(first, second), print(winner, \"wins!\")",
            ],
            "solution": MC6,
            "check": MC_CHECK6,
            "concepts": ["dicts", "while_loops", "conditions", "functions", "input"],
            "xp": 40,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: The Hall of Champions",
        "learn": """<p>Champions deserve to be remembered! Let's store how many battles each monster has won,
right inside its stats dictionary.</p>
<p>The problem: a brand new monster has no <code>"wins"</code> key yet. <code>.get</code> to the rescue:</p>
<pre>stats["wins"] = stats.get("wins", 0) + 1</pre>
<p>That says "take the wins (or 0 if there aren't any yet) and add 1." One line, no crash. 🏆</p>""",
        "task": """<p>After every battle in choice 3, add 1 to the winner's <code>"wins"</code> using
<code>.get("wins", 0)</code>. Then add menu choice <code>5</code> = leaderboard, which prints every
monster with its number of wins. Bonus: give the winner +1 attack so champions get stronger!</p>""",
        "starter": _next(MC6, "# TODO (boss): after a battle, add 1 to collection[winner][\"wins\"] using .get(\"wins\", 0)\n# TODO (boss): add choice 5 = leaderboard showing every monster's wins"),
        "hints": [
            "The winner's stats are collection[winner]. That's the dictionary to add \"wins\" to.",
            "collection[winner][\"wins\"] = collection[winner].get(\"wins\", 0) + 1",
            "For choice 5: for name, stats in collection.items(): print(f\"{name}: {stats.get('wins', 0)} wins\")",
        ],
        "solution": MC_BOSS,
        "check": MC_CHECK_BOSS,
        "concepts": ["dicts", "for_loops", "conditions"],
        "xp": 80,
    },
    "remix": {
        "prompt": "Make it yours! Your Monster-dex, your rules. 👾",
        "ideas": [
            "Invent 5 new monsters with ridiculous names (Grandma Kraken? Sir Loin of Beef?).",
            "Give each monster a special move that it shouts during battle, stored as a \"move\" key.",
            "Add types with weaknesses: fire does double damage to grass, water beats fire.",
            "Monsters level up after 3 wins and evolve: rename them to \"Mega \" + their name!",
        ],
    },
}


# ---------------------------------------------------------------------------
# Project 10: Escape the Castle
# ---------------------------------------------------------------------------

EC_START = r'''# Escape the Castle 🏰
print("🏰 You wake up in a spooky castle. Can you escape?")

# TODO: make a rooms dictionary. Each room is a dictionary with a "description" and "exits"
# TODO: make current = the room you start in, and print its description
'''

EC_ROOMS = r'''# Escape the Castle 🏰
print("🏰 You wake up in a spooky castle. Can you escape?")

rooms = {
    "dungeon": {
        "description": "A damp dungeon. Something drips. You hope it's water.",
        "exits": {"north": "hall"},
    },
    "hall": {
        "description": "A grand hall. The suits of armor are DEFINITELY watching you.",
        "exits": {"south": "dungeon", "east": "kitchen", "north": "tower"},
    },
    "kitchen": {
        "description": "A skeleton chef stirs a pot. 'Soup-er to see you!' he rattles.",
        "exits": {"west": "hall"},
    },
    "tower": {
        "description": "A windy tower. A bat hangs upside down and judges your outfit.",
        "exits": {"south": "hall"},
    },
}

current = "dungeon"
'''

EC1 = EC_ROOMS + r'''print(rooms[current]["description"])
'''

EC_DESCRIBE = r'''

def describe(room_name):
    room = rooms[room_name]
    print()
    print(f"📍 {room_name.upper()}")
    print(room["description"])
    exits = ", ".join(room["exits"].keys())
    print(f"Exits: {exits}")
'''

EC2 = EC_ROOMS + EC_DESCRIBE + r'''

describe(current)
'''

EC_MOVE = r'''

def move(room_name, direction):
    exits = rooms[room_name]["exits"]
    if direction in exits:
        return exits[direction]
    print("🧱 You bonk into a wall. You can't go that way!")
    return room_name
'''

EC3 = EC_ROOMS + EC_DESCRIBE + EC_MOVE + r'''

while True:
    describe(current)
    command = input("> ").lower().strip()
    if command.startswith("go "):
        direction = command[3:]
        current = move(current, direction)
    elif command == "quit":
        print("You curl up and nap in the castle forever. The end?")
        break
    else:
        print("I don't understand. Try 'go north' or 'quit'.")
'''

EC_ROOMS_ITEM = EC_ROOMS.replace(
    '''        "exits": {"west": "hall"},
    },''',
    '''        "exits": {"west": "hall"},
        "item": "rusty key",
    },''')

EC_DESCRIBE_ITEM = EC_DESCRIBE + r'''    if "item" in room:
        print(f"✨ You see a {room['item']} here.")
'''

EC_TAKE = r'''    elif command == "take":
        room = rooms[current]
        if "item" in room:
            item = room.pop("item")
            inventory.append(item)
            print(f"✋ You grab the {item}!")
        else:
            print("There's nothing here to take. Just dust. So much dust.")
    elif command == "inventory":
        if len(inventory) == 0:
            print("🎒 Your bag is empty.")
        else:
            print("🎒 You are carrying:", ", ".join(inventory))
    elif command == "quit":
        print("You curl up and nap in the castle forever. The end?")
        break
    else:
        print("I don't understand. Try 'go north', 'take', 'inventory' or 'quit'.")
'''

EC4 = EC_ROOMS_ITEM + EC_DESCRIBE_ITEM + EC_MOVE + r'''

inventory = []

while True:
    describe(current)
    command = input("> ").lower().strip()
    if command.startswith("go "):
        direction = command[3:]
        current = move(current, direction)
''' + EC_TAKE

EC_ROOMS_WIN = EC_ROOMS_ITEM.replace(
    '''        "exits": {"south": "hall"},
    },
}''',
    '''        "exits": {"south": "hall", "north": "drawbridge"},
    },
    "drawbridge": {
        "description": "The drawbridge! Sunshine! Birds! A duck quacks at you proudly.",
        "exits": {},
    },
}''').replace('current = "dungeon"\n', 'current = "dungeon"\nwin_room = "drawbridge"\n')

EC_LOOP_TOP = r'''

inventory = []

while True:
    describe(current)
    if current == win_room:
        print("🎉 YOU ESCAPED THE CASTLE! The duck gives you a round of applause.")
        break
    command = input("> ").lower().strip()
'''

EC5 = EC_ROOMS_WIN + EC_DESCRIBE_ITEM + EC_MOVE + EC_LOOP_TOP + r'''    if command.startswith("go "):
        direction = command[3:]
        current = move(current, direction)
''' + EC_TAKE

EC_ROOMS_LOCK = EC_ROOMS_WIN.replace('win_room = "drawbridge"\n',
                                     'win_room = "drawbridge"\nneeded_item = "rusty key"\n')

EC6 = EC_ROOMS_LOCK + EC_DESCRIBE_ITEM + EC_MOVE + EC_LOOP_TOP + r'''    if command.startswith("go "):
        direction = command[3:]
        next_room = move(current, direction)
        if next_room == win_room and needed_item not in inventory:
            print(f"🔒 The drawbridge gate is locked. You'll need a {needed_item}...")
        else:
            current = next_room
''' + EC_TAKE

EC_BOSS = EC_ROOMS_LOCK.replace('needed_item = "rusty key"\n',
                                'needed_item = "rusty key"\nmoves = 0\nmax_moves = 15\n') \
    + EC_DESCRIBE_ITEM + EC_MOVE + r'''

inventory = []

while True:
    describe(current)
    if current == win_room:
        print(f"🎉 YOU ESCAPED THE CASTLE in {moves} moves! The duck is impressed.")
        break
    if moves > max_moves:
        print("💂 Too slow! The castle guards catch you and make you polish armor forever. GAME OVER")
        break
    print(f"👣 Moves: {moves}/{max_moves}")
    command = input("> ").lower().strip()
    if command.startswith("go "):
        direction = command[3:]
        next_room = move(current, direction)
        if next_room == win_room and needed_item not in inventory:
            print(f"🔒 The drawbridge gate is locked. You'll need a {needed_item}...")
        elif next_room != current:
            current = next_room
            moves += 1
''' + EC_TAKE

EC_CHECK1 = r'''
r = run()
rooms = r.var("rooms")
expect(isinstance(rooms, dict) and len(rooms) >= 3, "Make a dictionary called `rooms` with at least 3 rooms in it.")
for name, room in rooms.items():
    expect(isinstance(room, dict), f"Each room should be its own dictionary. rooms[{name!r}] isn't a dictionary.")
    expect("description" in room, f"Room {name!r} needs a \"description\" key.")
    expect(isinstance(room.get("exits"), dict),
           f"Room {name!r} needs an \"exits\" dictionary, like \"exits\": {{\"north\": \"hall\"}}.")
    for d, target in room["exits"].items():
        expect(target in rooms,
               f"The {d} exit of {name!r} leads to {target!r}, but there's no room called that. Check the spelling!")
cur = r.var("current")
expect(cur in rooms, f"`current` should be the name of a room (a key in rooms). It's {cur!r}.")
expect(r.has(str(rooms[cur]["description"])),
       "Print the description of the room the player starts in: print(rooms[current][\"description\"])")
SUCCESS = "The castle exists! Spooky. 🏰"
'''

EC_CHECK2 = r'''
r = run()
rooms = r.var("rooms")
describe = r.fn("describe")
for name, room in rooms.items():
    v, out = capture(describe, name)
    expect(norm(room["description"]) in norm(out),
           f"describe({name!r}) should print that room's description.")
    for d in room["exits"]:
        expect(norm(d) in norm(out), f"describe({name!r}) should list the exits. I didn't see {d!r}.")
SUCCESS = "Every room describes itself. Very dramatic. 🎭"
'''

EC_CHECK3 = r'''
r = run(inputs=["quit"])
rooms = r.var("rooms")
start = r.var("current")
move = r.fn("move")
exits = rooms[start]["exits"]
expect(len(exits) > 0, "Your starting room has no exits. Give it at least one!")
d, t = next(iter(exits.items()))
v, out = capture(move, start, d)
expect(v == t, f"move({start!r}, {d!r}) should return {t!r} (the room that way), but it returned {v!r}.")
v, out = capture(move, start, "sideways")
expect(v == start, f"move({start!r}, 'sideways') should return {start!r} - you can't go that way, so you stay put. It returned {v!r}.")
expect(out.strip(), "When the player can't go that way, move should print a message like 'You bonk into a wall!'")
expect(uses("while_loops"), "Put your game in a while True: loop so the player can keep typing commands.")
r = run(inputs=["go " + d, "quit"])
expect(r.var("current") == t,
       f"I typed 'go {d}' then 'quit', so I expected to end up in {t!r}, but current was {r.var('current')!r}. "
       "Remember: current = move(current, direction)")
expect(r.has(str(rooms[t]["description"])), f"After I walked to {t!r}, I didn't see its description. Call describe(current) at the top of the loop.")
r = run(inputs=["go sideways", "quit"])
expect(r.var("current") == start, "Going a direction that doesn't exist should keep you in the same room.")
SUCCESS = "You can walk around the castle! 🚶"
'''

EC_CHECK4 = _REPLY + _PATH + r'''
r = run(inputs=["quit"])
rooms = r.var("rooms")
start = r.var("current")
expect(isinstance(r.var("inventory"), list), "Make an empty list called inventory before your game loop: inventory = []")
item_room, p = path_to(rooms, start, lambda n: "item" in rooms[n])
expect(item_room is not None, "Put an item in a room the player can reach, like \"item\": \"rusty key\".")
item = rooms[item_room]["item"]
expect(isinstance(item, str), "Make the item a string, like \"item\": \"rusty key\".")
inp = ["go " + d for d in p] + ["take", "take", "inventory", "quit"]
r = run(inputs=inp)
inv = r.var("inventory")
walk = ", ".join(inp[:-3])
expect(item in inv, f"I walked to {item_room!r} ({walk or 'no moves needed'}), typed 'take', but the {item} wasn't in inventory.")
expect(inv.count(item) == 1, "I typed 'take' twice and got two of the same item! Remove it from the room: room.pop(\"item\")")
said = reply(r, inp, len(inp) - 2)
expect(norm(item) in norm(said), f"When I typed 'inventory', I expected to see {item!r} printed.")
SUCCESS = "Yoink! ✋ You can pick things up."
'''

EC_CHECK5 = _PATH + r'''
r = run(inputs=["quit"])
rooms = r.var("rooms")
start = r.var("current")
win = r.var("win_room")
expect(win in rooms, f"win_room should be the name of a room in rooms. It's {win!r}.")
expect(win != start, "Don't start the player in the win room - that's too easy! 😄")
_, p = path_to(rooms, start, lambda n: n == win)
expect(p is not None, f"There's no way to walk from {start!r} to {win!r}. Connect it with an exit!")
inp = ["go " + d for d in p]
r = run(inputs=inp, allow_error=True)
walk = ", ".join(inp)
if r.error == "OutOfInputs":
    raise CheckFail(f"I walked to {win!r} ({walk}), but the game kept asking for commands. "
                    "When current == win_room, print a victory message and break!")
expect(r.error is None, f"Your program crashed on line {r.error_line} with {r.error}: {r.error_msg}")
expect(r.var("current") == win, f"I walked {walk} but didn't reach {win!r}.")
SUCCESS = "FREEDOM! 🎉 Your castle can be escaped!"
'''

EC_CHECK6 = _PATH + r'''
r = run(inputs=["quit"])
rooms = r.var("rooms")
start = r.var("current")
win = r.var("win_room")
need = r.var("needed_item")
item_room, p1 = path_to(rooms, start, lambda n: rooms[n].get("item") == need, blocked=(win,))
expect(item_room is not None, f"Put the {need!r} in a room the player can reach (with \"item\": {need!r}), not in the win room.")
_, p_win = path_to(rooms, start, lambda n: n == win)
expect(p_win is not None, f"There's no way to walk from {start!r} to {win!r}.")
inp = ["go " + d for d in p_win] + ["quit"]
r = run(inputs=inp, allow_error=True)
expect(r.var("current") != win,
       f"I walked straight to {win!r} WITHOUT the {need} and got in! Lock it: "
       "if next_room == win_room and needed_item not in inventory: print a 'locked' message.")
_, p2 = path_to(rooms, item_room, lambda n: n == win)
expect(p2 is not None, f"There's no way from {item_room!r} to {win!r}.")
inp = ["go " + d for d in p1] + ["take"] + ["go " + d for d in p2]
r = run(inputs=inp, allow_error=True)
walk = ", ".join(inp)
if r.error == "OutOfInputs":
    raise CheckFail(f"I typed {walk} - I had the {need} and walked to {win!r}, but the game didn't end with a win.")
expect(r.error is None, f"Your program crashed on line {r.error_line} with {r.error}: {r.error_msg}")
expect(r.var("current") == win, f"With the {need} in my bag I should get into {win!r}.")
SUCCESS = "🔓 Locked door, secret key, epic escape. You made a real adventure game!"
'''

EC_CHECK_BOSS = _PATH + r'''
r = run(inputs=["quit"])
rooms = r.var("rooms")
start = r.var("current")
win = r.var("win_room")
need = r.var("needed_item")
r.var("moves")
limit = r.var("max_moves")
expect(isinstance(limit, int), "max_moves should be a number, like max_moves = 15")
item_room, p1 = path_to(rooms, start, lambda n: rooms[n].get("item") == need, blocked=(win,))
_, p2 = path_to(rooms, item_room, lambda n: n == win) if item_room else (None, None)
expect(p1 is not None and p2 is not None, "I couldn't find a way to the item and then to the win room.")
inp = ["go " + d for d in p1] + ["go sideways", "take"] + ["go " + d for d in p2]
r = run(inputs=inp, allow_error=True)
walk = ", ".join(inp)
expect(r.error in (None, "OutOfInputs"), f"Your program crashed on line {r.error_line} with {r.error}: {r.error_msg}")
expect(r.var("current") == win, f"I typed {walk} and expected to escape. Is max_moves big enough for your castle?")
steps = len(p1) + len(p2)
expect(r.var("moves") == steps,
       f"I made {steps} real moves (plus one 'go sideways' into a wall, which shouldn't count), "
       f"but moves is {r.var('moves')}. Only add 1 when you actually change rooms.")
expect(str(steps) in r.output[-300:], f"When the player escapes, tell them how many moves it took ({steps}).")
pair = None
seen_start, p0 = start, []
for a in rooms:
    if a == win:
        continue
    for d1, b in rooms[a]["exits"].items():
        if b == win or b not in rooms:
            continue
        for d2, back in rooms[b]["exits"].items():
            if back == a:
                _, pa = path_to(rooms, start, lambda n: n == a, blocked=(win,))
                if pa is not None and pair is None:
                    pair = (pa, d1, d2)
if pair:
    pa, d1, d2 = pair
    inp = ["go " + d for d in pa] + ["go " + d1, "go " + d2] * (limit + 10)
    r = run(inputs=inp, allow_error=True)
    if r.error == "OutOfInputs":
        raise CheckFail(f"I walked back and forth ({d1}, {d2}, {d1}, {d2}...) more than {limit} times, "
                        "but the guards never caught me. When moves > max_moves, print GAME OVER and break!")
    expect(r.error is None, f"Your program crashed on line {r.error_line} with {r.error}: {r.error_msg}")
SUCCESS = "🏃 Speedrun mode unlocked! Can YOU beat your own record?"
'''

ESCAPE_CASTLE = {
    "id": "escape_castle",
    "week": 5,
    "order": 10,
    "title": "Escape the Castle",
    "emoji": "🏰",
    "tagline": "Build a text adventure with rooms, items and a locked door",
    "story": ("You wake up in a castle dungeon with no memory and a strong smell of old socks. 🧦 "
              "Somewhere there's a key, and somewhere there's a way out. Build the adventure game "
              "that lets a player explore room by room, grab items, and ESCAPE."),
    "concepts": ["dicts", "functions", "while_loops", "lists", "conditions"],
    "expected_minutes": 130,
    "steps": [
        {
            "id": "s1",
            "title": "Build the castle",
            "learn": """<p>A text adventure is a bunch of rooms connected by exits. Each room has a description and
a list of where you can go. That's a job for a <b>dictionary of dictionaries</b>:</p>
<pre>rooms = {
    "dungeon": {
        "description": "It's dark. Something squeaks.",
        "exits": {"north": "hall"},
    },
    "hall": {
        "description": "A big fancy hall.",
        "exits": {"south": "dungeon"},
    },
}</pre>
<p>See how <code>"exits"</code> is ALSO a dictionary? It maps a direction to a room name. Like a map where
each door has a sign on it. 🚪 Then one variable, <code>current</code>, remembers which room the player is in.</p>""",
            "task": """<p>Make a dictionary called <code>rooms</code> with <b>at least 3 rooms</b>. Each room needs a
<code>"description"</code> and an <code>"exits"</code> dictionary (direction → room name). Every exit must
lead to a room that exists! Then set <code>current</code> to your starting room and print
<code>rooms[current]["description"]</code>.</p>""",
            "starter": EC_START,
            "hints": [
                "Each room looks like \"hall\": {\"description\": \"...\", \"exits\": {\"south\": \"dungeon\"}}. Watch out for commas between rooms!",
                "If the dungeon has \"north\": \"hall\", the hall should have \"south\": \"dungeon\" so you can walk back.",
                "current = \"dungeon\" and then print(rooms[current][\"description\"])",
            ],
            "solution": EC1,
            "check": EC_CHECK1,
            "concepts": ["dicts", "variables"],
            "xp": 25,
        },
        {
            "id": "s2",
            "title": "Look around",
            "learn": """<p>Every time the player enters a room, we want to show the same stuff: the name, the
description, and the exits. Doing the same thing over and over? That's a <b>function</b>.</p>
<p>To get just the keys of a dictionary (the directions!), use <code>.keys()</code>. Then
<code>", ".join(...)</code> glues them together with commas:</p>
<pre>exits = {"north": "hall", "east": "kitchen"}
print("Exits:", ", ".join(exits.keys()))
# Exits: north, east</pre>""",
            "task": """<p>Write <code>def describe(room_name):</code> that prints the room's name, its description,
and its exits. Then call <code>describe(current)</code>.</p>""",
            "starter": _next(EC1, "# TODO: def describe(room_name): print the name, description and exits\n# TODO: call describe(current)"),
            "hints": [
                "Inside the function, grab the room first: room = rooms[room_name]",
                "print(room[\"description\"]) prints the description. The exits are room[\"exits\"].keys()",
                "print(\"Exits:\", \", \".join(room[\"exits\"].keys()))",
            ],
            "solution": EC2,
            "check": EC_CHECK2,
            "concepts": ["functions", "dicts", "strings"],
            "xp": 25,
        },
        {
            "id": "s3",
            "title": "Start walking",
            "learn": """<p>Time for the <b>game loop</b>: describe the room, ask for a command, do it, repeat forever
(until the player quits). Commands look like <code>go north</code>. <code>command[3:]</code> chops
off the first 3 letters (<code>"go "</code>) and leaves just the direction.</p>
<p>A <code>move</code> function keeps things tidy. It <b>returns</b> the new room, or the same room if
there's a wall:</p>
<pre>def move(room_name, direction):
    exits = rooms[room_name]["exits"]
    if direction in exits:
        return exits[direction]
    print("Bonk! A wall.")
    return room_name

current = move(current, "north")</pre>
<p><code>in</code> checks if a key is in a dictionary. It's like checking if a door exists before walking into it. 😅</p>""",
            "task": """<p>Write <code>def move(room_name, direction):</code> that returns the room in that direction,
or prints a "can't go that way" message and returns the same room. Then make a
<code>while True:</code> game loop: <code>describe(current)</code>, ask for a command with
<code>input("&gt; ")</code>, and handle <code>go &lt;direction&gt;</code> (using
<code>current = move(current, direction)</code>) and <code>quit</code> (break). You can delete the lonely
<code>describe(current)</code> at the bottom now, since the loop does it.</p>""",
            "starter": _next(EC2, "# TODO: def move(room_name, direction): return the new room, or the same room if you can't go that way\n# TODO: game loop: describe, ask for a command, handle 'go ...' and 'quit'"),
            "hints": [
                "In the loop: command = input(\"> \").lower().strip() makes 'GO North ' into 'go north'.",
                "if command.startswith(\"go \"): direction = command[3:] then current = move(current, direction)",
                "elif command == \"quit\": break",
            ],
            "solution": EC3,
            "check": EC_CHECK3,
            "concepts": ["functions", "while_loops", "conditions", "dicts", "strings"],
            "xp": 35,
        },
        {
            "id": "s4",
            "title": "Grab stuff",
            "learn": """<p>Adventurers pick up EVERYTHING. 🎒 Put an item in a room by adding a key:
<code>"item": "rusty key"</code>. The player's bag is a <b>list</b> called <code>inventory</code>.</p>
<p>When the player types <code>take</code>, move the item from the room into the list.
<code>.pop("item")</code> takes a key out of a dictionary AND gives you its value, so it's gone from the room:</p>
<pre>room = rooms[current]
if "item" in room:
    item = room.pop("item")
    inventory.append(item)</pre>""",
            "task": """<p>Add an <code>"item"</code> to at least one room. Make <code>inventory = []</code> before your
loop. Add two commands: <code>take</code> (picks up the item in this room, if there is one) and
<code>inventory</code> (prints what you're carrying). Taking twice should NOT give you two!</p>""",
            "starter": _next(EC3, "# TODO: add an \"item\" to a room, and make inventory = [] before the loop\n# TODO: add 'take' and 'inventory' commands to your loop"),
            "hints": [
                "Put the item right in the room's dictionary: \"item\": \"rusty key\". And add inventory = [] just before while True.",
                "elif command == \"take\": room = rooms[current], then if \"item\" in room: ... else: print(\"Nothing here!\")",
                "item = room.pop(\"item\") and inventory.append(item). For inventory: print(\"You have:\", \", \".join(inventory))",
            ],
            "solution": EC4,
            "check": EC_CHECK4,
            "concepts": ["dicts", "lists", "conditions"],
            "xp": 30,
        },
        {
            "id": "s5",
            "title": "The way out",
            "learn": """<p>Every game needs a way to <b>win</b>. Add one more room, the exit, and a variable that
remembers which room it is. Then, every time around the loop, check:</p>
<pre>if current == win_room:
    print("You escaped!")
    break</pre>
<p><code>break</code> jumps out of the loop, so the game ends. Put this check right after
<code>describe(current)</code> so the player sees the room they escaped into. 🌞</p>""",
            "task": """<p>Add a winning room (a drawbridge, a secret tunnel, a portal to the snack bar...) connected by an
exit. Make a variable <code>win_room</code> with its name. When <code>current == win_room</code>, print a
victory message and <code>break</code>.</p>""",
            "starter": _next(EC4, "# TODO: add a win room to rooms (connect it with an exit!) and make win_room = \"...\"\n# TODO: in the loop, if current == win_room: print a victory message and break"),
            "hints": [
                "Add the room to your rooms dictionary, and add an exit to it from another room, like \"north\": \"drawbridge\".",
                "win_room = \"drawbridge\" goes near current = ... at the top.",
                "Right after describe(current) in the loop: if current == win_room: print(\"YOU ESCAPED!\") then break",
            ],
            "solution": EC5,
            "check": EC_CHECK5,
            "concepts": ["conditions", "dicts", "while_loops"],
            "xp": 25,
        },
        {
            "id": "s6",
            "title": "Locked!",
            "learn": """<p>Right now escaping is too easy. Let's lock the door! 🔒 The player needs a certain item
first. <code>not in</code> checks if something is missing from a list:</p>
<pre>if "rusty key" not in inventory:
    print("It's locked!")</pre>
<p>Change your <code>go</code> command: work out where the player <i>would</i> go with
<code>next_room = move(current, direction)</code>. If that's the win room and they don't have the item,
print a locked message and don't move. Otherwise, <code>current = next_room</code>.</p>""",
            "task": """<p>Make a variable <code>needed_item</code> (it should be the item you hid in a room). The player
can only enter <code>win_room</code> if <code>needed_item</code> is in their inventory. Otherwise print
a "locked" message and keep them where they are.</p>""",
            "starter": _next(EC5, "# TODO: make needed_item = \"...\" (the item that opens the way out)\n# TODO: in 'go', if the next room is win_room and needed_item not in inventory, say it's locked and don't move"),
            "hints": [
                "needed_item = \"rusty key\" goes near win_room at the top. It must match the \"item\" in your room exactly.",
                "In the go part: next_room = move(current, direction)",
                "if next_room == win_room and needed_item not in inventory: print(\"Locked!\")  else: current = next_room",
            ],
            "solution": EC6,
            "check": EC_CHECK6,
            "concepts": ["conditions", "lists", "dicts"],
            "xp": 30,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: Speedrun or Get Caught",
        "learn": """<p>The castle guards are waking up! 💂 Let's add a move counter and a time limit.</p>
<pre>moves = 0
max_moves = 15
...
if moves &gt; max_moves:
    print("The guards got you!")
    break</pre>
<p>Only count a move when the player actually changes rooms. Walking into a wall doesn't count
(it just hurts). Tip: <code>if next_room != current:</code> tells you they really moved.</p>""",
        "task": """<p>Make <code>moves = 0</code> and <code>max_moves</code> (a number). Add 1 to <code>moves</code>
every time the player really changes rooms. If <code>moves &gt; max_moves</code>, the guards catch them:
print GAME OVER and break. When they escape, tell them how many moves it took!</p>""",
        "starter": _next(EC6, "# TODO (boss): moves = 0 and max_moves = 15. Count real moves.\n# TODO (boss): too many moves = GAME OVER. Show the move count when they escape"),
        "hints": [
            "Put moves = 0 and max_moves = 15 at the top, next to win_room.",
            "In the go part, where you do current = next_room, also do moves += 1, but only if next_room != current.",
            "At the top of the loop: if moves > max_moves: print(\"Caught!\") and break. In the win message: print(f\"Escaped in {moves} moves!\")",
        ],
        "solution": EC_BOSS,
        "check": EC_CHECK_BOSS,
        "concepts": ["conditions", "math", "while_loops"],
        "xp": 90,
    },
    "remix": {
        "prompt": "Make it yours! It's your castle. Fill it with weirdness. 🏰",
        "ideas": [
            "Add 5 more rooms: a library of whispering books, a moat full of rubber ducks, a throne room...",
            "Add a 'help' command that lists every command the player can type.",
            "Put a riddle on a door: the player must type the right answer to pass.",
            "Add a sleepy dragon room: if you enter without the cookie, the dragon eats you. GAME OVER.",
        ],
    },
}

PROJECTS = [MONSTER_COLLECTOR, ESCAPE_CASTLE]


# ---------------------------------------------------------------------------
# Practice
# ---------------------------------------------------------------------------

PRACTICE = [
    {
        "id": "p_dicts_1",
        "concept": "dicts",
        "title": "Emoji Translator",
        "difficulty": 1,
        "task": """<p>Make a dictionary called <code>emoji</code> with at least 4 words and their emoji
(like <code>"pizza": "🍕"</code>). Ask the player for a word and print its emoji. If the word isn't in
the dictionary, print <code>🤷</code> instead. Use <code>.get(word, "🤷")</code>!</p>""",
        "starter": r'''emoji = {
    "pizza": "🍕",
    # TODO: add at least 3 more words and their emoji
}
word = input("Type a word: ").lower()
# TODO: use emoji.get(word, "🤷") and print the result
''',
        "hints": [
            "Add more pairs inside the braces, like \"cat\": \"🐱\", with a comma after each one.",
            "emoji.get(word, \"🤷\") gives the emoji, or the shrug if the word is missing.",
            "print(emoji.get(word, \"🤷\"))",
        ],
        "solution": r'''emoji = {
    "pizza": "🍕",
    "cat": "🐱",
    "rocket": "🚀",
    "ghost": "👻",
    "taco": "🌮",
}
word = input("Type a word: ").lower()
print(emoji.get(word, "🤷"))
''',
        "check": _REPLY + r'''
r = run(inputs=["pizza"])
e = r.var("emoji")
expect(isinstance(e, dict) and len(e) >= 4,
       f"Put at least 4 words in your emoji dictionary (you have {len(e) if isinstance(e, dict) else 0}).")
expect(calls("get") >= 1, "Use emoji.get(word, \"🤷\") so missing words don't crash.")
keys = list(e.keys())
for k in [keys[0], keys[-1]]:
    r = run(inputs=[k])
    expect(str(e[k]) in reply(r, [k], 0), f"When I typed {k!r}, I expected to see {e[k]}.")
r = run(inputs=["xylophonezzz"])
expect(reply(r, ["xylophonezzz"], 0).strip(),
       "When I typed a word that's not in the dictionary, nothing printed. Show a 🤷!")
SUCCESS = "🍕 ➡️ 😎 Translation complete!"
''',
        "xp": 15,
    },
    {
        "id": "p_dicts_2",
        "concept": "dicts",
        "title": "Point Keeper",
        "difficulty": 2,
        "task": """<p>Make an empty dictionary <code>scores = {}</code>. In a loop, ask "Who scored?" until the
player types <code>done</code>. Each time, add 1 point to that person. New names start at 0, so use
<code>scores.get(name, 0) + 1</code>. At the end, print everyone's score with
<code>.items()</code>.</p>""",
        "starter": r'''scores = {}
while True:
    name = input("Who scored? (done to stop) ")
    if name == "done":
        break
    # TODO: add 1 point to scores[name] (use .get so new names start at 0)

# TODO: loop over scores.items() and print each name and score
''',
        "hints": [
            "scores.get(name, 0) gives their current points, or 0 if they're new.",
            "scores[name] = scores.get(name, 0) + 1",
            "for name, points in scores.items(): print(name, points)",
        ],
        "solution": r'''scores = {}
while True:
    name = input("Who scored? (done to stop) ")
    if name == "done":
        break
    scores[name] = scores.get(name, 0) + 1

for name, points in scores.items():
    print(f"{name}: {points} points")
''',
        "check": r'''
r = run(inputs=["Zed", "Ava", "Zed", "Zed", "done"])
s = r.var("scores")
expect(isinstance(s, dict) and s.get("Zed") == 3 and s.get("Ava") == 1,
       f"I typed Zed, Ava, Zed, Zed, done. scores should be {{'Zed': 3, 'Ava': 1}}, but it was {s!r}.")
r2 = run(inputs=["Momo", "done"])
expect(r2.var("scores") == {"Momo": 1}, "With just Momo, scores should be {'Momo': 1}.")
expect(calls("items") >= 1, "Print the scores with a loop over scores.items().")
out = r.output.split("done")[-1]
expect("zed" in norm(out) and "3" in out and "ava" in norm(out),
       "At the end, print every name and score (like Zed: 3).")
SUCCESS = "Scoreboard ready! 🏆"
''',
        "xp": 20,
    },
    {
        "id": "p_dicts_3",
        "concept": "dicts",
        "title": "Letter Counter",
        "difficulty": 3,
        "task": """<p>Write <code>def count_letters(word):</code> that returns a dictionary saying how many
times each letter appears. <code>count_letters("banana")</code> should return
<code>{"b": 1, "a": 3, "n": 2}</code>.</p>""",
        "starter": r'''def count_letters(word):
    counts = {}
    # TODO: loop over each letter and add 1 to counts[letter]
    return counts

print(count_letters("banana"))
''',
        "hints": [
            "for letter in word: goes through the letters one at a time.",
            "counts.get(letter, 0) is how many you've seen so far.",
            "counts[letter] = counts.get(letter, 0) + 1",
        ],
        "solution": r'''def count_letters(word):
    counts = {}
    for letter in word:
        counts[letter] = counts.get(letter, 0) + 1
    return counts

print(count_letters("banana"))
''',
        "check": r'''
r = run()
f = r.fn("count_letters")
for w, want in [("banana", {"b": 1, "a": 3, "n": 2}), ("hello", {"h": 1, "e": 1, "l": 2, "o": 1}), ("zz", {"z": 2})]:
    v, _ = capture(f, w)
    expect(v == want, f"count_letters({w!r}) should return {want}, but it returned {v!r}.")
SUCCESS = "🔤 You counted every letter!"
''',
        "xp": 25,
    },
    {
        "id": "p_functions_w5_1",
        "concept": "functions",
        "title": "Damage Calculator",
        "difficulty": 1,
        "task": """<p>Write <code>def damage(attack, defense):</code> that returns <code>attack - defense</code>,
but never less than 1 (every hit hurts a little!). <code>damage(10, 3)</code> → 7,
<code>damage(2, 9)</code> → 1.</p>""",
        "starter": r'''def damage(attack, defense):
    # TODO: return attack - defense, but at least 1
    pass

print(damage(10, 3))
''',
        "hints": [
            "Work out hit = attack - defense first.",
            "if hit < 1: hit = 1",
            "return max(attack - defense, 1) also works!",
        ],
        "solution": r'''def damage(attack, defense):
    hit = attack - defense
    if hit < 1:
        hit = 1
    return hit

print(damage(10, 3))
''',
        "check": r'''
r = run()
f = r.fn("damage")
for a, d, want in [(10, 3, 7), (2, 9, 1), (5, 5, 1), (20, 1, 19)]:
    v, _ = capture(f, a, d)
    expect(v == want, f"damage({a}, {d}) should return {want}, but it returned {v!r}.")
SUCCESS = "💥 Ouch! Perfect math."
''',
        "xp": 15,
    },
    {
        "id": "p_lists_w5_1",
        "concept": "lists",
        "title": "Monster Roster",
        "difficulty": 2,
        "task": """<p>Make an empty list <code>roster</code>. Keep asking for monster names until the player types
<code>done</code>, adding each one to the list. Then print how many monsters you have, and print each
one with a number: <code>1. Blobzilla</code>, <code>2. Toastgeist</code>...</p>""",
        "starter": r'''roster = []
while True:
    name = input("Monster name (done to stop): ")
    if name == "done":
        break
    # TODO: add name to roster

# TODO: print how many monsters there are, then each one numbered 1., 2., 3....
''',
        "hints": [
            "roster.append(name) adds to the list. len(roster) counts them.",
            "Keep a counter: number = 1 before the loop, and number += 1 inside.",
            "for monster in roster: print(f\"{number}. {monster}\") and then number += 1",
        ],
        "solution": r'''roster = []
while True:
    name = input("Monster name (done to stop): ")
    if name == "done":
        break
    roster.append(name)

print(f"You have {len(roster)} monsters!")
number = 1
for monster in roster:
    print(f"{number}. {monster}")
    number += 1
''',
        "check": r'''
for names in (["Blobzilla", "Toastgeist", "Mr Snuggles"], ["Gloop"]):
    r = run(inputs=names + ["done"])
    ro = r.var("roster")
    expect(ro == names, f"I typed {', '.join(names)}, then done. roster should be {names}, but it was {ro!r}.")
    out = r.output.split("done")[-1]
    expect(str(len(names)) in out, f"Print how many monsters there are ({len(names)}).")
    for i, n in enumerate(names):
        expect(f"{i + 1}. {norm(n)}" in norm(out) or f"{i + 1}) {norm(n)}" in norm(out) or f"{i + 1} {norm(n)}" in norm(out),
               f"I expected to see '{i + 1}. {n}' in the numbered list.")
SUCCESS = "📋 Roster complete!"
''',
        "xp": 20,
    },
    {
        "id": "p_functions_w5_2",
        "concept": "functions",
        "title": "Find the Strongest",
        "difficulty": 3,
        "task": """<p>Write <code>def biggest(numbers):</code> that returns the largest number in a list, using
a loop (no <code>max()</code> allowed, that's cheating 😄). <code>biggest([3, 9, 2])</code> → 9. Make sure
it works for negative numbers too!</p>""",
        "starter": r'''def biggest(numbers):
    best = numbers[0]
    # TODO: loop through numbers and keep the biggest one in best
    return best

print(biggest([3, 9, 2]))
''',
        "hints": [
            "Start with best = numbers[0], the first number.",
            "for n in numbers: then compare n with best.",
            "if n > best: best = n",
        ],
        "solution": r'''def biggest(numbers):
    best = numbers[0]
    for n in numbers:
        if n > best:
            best = n
    return best

print(biggest([3, 9, 2]))
''',
        "check": r'''
r = run()
f = r.fn("biggest")
expect(calls("max") == 0, "No max() allowed for this one! Use a loop and an if.")
for nums, want in [([3, 9, 2], 9), ([1, 2, 3, 50], 50), ([-5, -2, -9], -2), ([7], 7)]:
    v, _ = capture(f, nums)
    expect(v == want, f"biggest({nums}) should return {want}, but it returned {v!r}.")
SUCCESS = "💪 Found the champion!"
''',
        "xp": 25,
    },
    {
        "id": "p_dicts_4",
        "concept": "dicts",
        "title": "Report Card",
        "difficulty": 2,
        "task": """<p>Make a dictionary <code>grades</code> where each key is a student's name and each value is a
<b>list</b> of test scores. Loop over <code>grades.items()</code> and print each student's name and
their average (<code>sum(scores) / len(scores)</code>).</p>""",
        "starter": r'''grades = {
    "Ava": [90, 85, 100],
    "Ben": [70, 80, 75],
    "Cleo": [88, 92, 95],
}
# TODO: loop over grades.items() and print each name with their average
''',
        "hints": [
            "for name, scores in grades.items(): gives you each student and their list.",
            "average = sum(scores) / len(scores)",
            "print(f\"{name}: {round(average, 1)}\")",
        ],
        "solution": r'''grades = {
    "Ava": [90, 85, 100],
    "Ben": [70, 80, 75],
    "Cleo": [88, 92, 95],
}
for name, scores in grades.items():
    average = sum(scores) / len(scores)
    print(f"{name}: {round(average, 1)}")
''',
        "check": r'''
r = run()
g = r.var("grades")
expect(isinstance(g, dict) and len(g) >= 2, "Keep at least 2 students in grades.")
expect(calls("items") >= 1 and uses("for_loops"), "Loop over grades.items() to go through every student.")
for name, scores in g.items():
    avg = sum(scores) / len(scores)
    options = {str(avg), str(round(avg, 1)), str(round(avg, 2)), f"{avg:.1f}", f"{avg:.2f}", str(round(avg))}
    line = [l for l in r.lines if norm(name) in norm(l)]
    expect(line, f"I didn't see {name} in the output.")
    expect(any(o in line[0] for o in options), f"{name}'s average should be about {round(avg, 1)}.")
SUCCESS = "📝 Report cards printed! (Nobody got detention.)"
''',
        "xp": 20,
    },
]
