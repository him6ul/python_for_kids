"""Week 6: classes, then the capstone. Projects 11 (Virtual Pet) and 12 (Your Own Game)."""

# reply(r, inputs, k): the text printed right after the k-th answer (0-based), up to the next prompt.
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

# fresh(): a brand-new Pet("Testy") with all stats set to 5.
_FRESH = r'''
r = run(inputs=["Waffles", "q"], allow_error=True)
if r.error and r.error != "OutOfInputs":
    raise CheckFail(f"Your program crashed on line {r.error_line} with {r.error}: {r.error_msg}")
Pet = r.cls("Pet")

def fresh(h=5, hap=5, e=5):
    p, _ = capture(Pet, "Testy")
    p.hunger, p.happiness, p.energy = h, hap, e
    return p

def need_method(p, m):
    expect(callable(getattr(p, m, None)), f"Your Pet class needs a {m} method: def {m}(self):")
'''


def _next(prev, todo):
    """Starter for the next step: the previous solution plus a TODO comment."""
    return prev.rstrip() + "\n\n" + todo.strip() + "\n"


# ---------------------------------------------------------------------------
# Project 11: Virtual Pet
# ---------------------------------------------------------------------------

VP_START = r'''# Virtual Pet 🐣
# TODO: write class Pet with an __init__(self, name) that stores
#       self.name, self.hunger, self.happiness and self.energy (numbers from 0 to 10)

name = input("🥚 An egg is hatching! What will you name your pet? ")
# TODO: make pet = Pet(name) and print a hello message with pet.name
'''

VP_CLASS_HEAD = r'''# Virtual Pet 🐣
class Pet:
    def __init__(self, name):
        self.name = name
        self.hunger = 5
        self.happiness = 5
        self.energy = 5
'''

VP_MAIN_DEMO = r'''

name = input("🥚 An egg is hatching! What will you name your pet? ")
pet = Pet(name)
print(f"🐣 Say hi to {pet.name}! Hunger: {pet.hunger}, Happiness: {pet.happiness}, Energy: {pet.energy}")
'''

VP1 = VP_CLASS_HEAD + VP_MAIN_DEMO

VP_METHODS = r'''
    def feed(self):
        self.hunger = self.hunger - 3
        self.happiness = self.happiness + 1
        print(f"🍕 {self.name} gobbles the food. Nom nom nom!")

    def play(self):
        self.happiness = self.happiness + 2
        self.energy = self.energy - 2
        self.hunger = self.hunger + 1
        print(f"🎾 {self.name} zooms around the room like a tiny tornado!")

    def sleep(self):
        self.energy = self.energy + 4
        print(f"💤 {self.name} snores like a tiny chainsaw.")
'''

VP2 = VP_CLASS_HEAD + VP_METHODS + VP_MAIN_DEMO + r'''
pet.feed()
pet.play()
pet.sleep()
'''

VP_STATUS = r'''
    def status(self):
        print(f"----- {self.name} -----")
        print(f"🍔 Hunger:    {self.hunger}/10")
        print(f"😊 Happiness: {self.happiness}/10")
        print(f"⚡ Energy:    {self.energy}/10")
'''

VP3 = VP_CLASS_HEAD + VP_METHODS + VP_STATUS + VP_MAIN_DEMO + r'''
pet.feed()
pet.play()
pet.sleep()
pet.status()
'''

VP_METHODS_SAFE = r'''
    def fix_stats(self):
        self.hunger = max(0, min(10, self.hunger))
        self.happiness = max(0, min(10, self.happiness))
        self.energy = max(0, min(10, self.energy))

    def feed(self):
        self.hunger = self.hunger - 3
        self.happiness = self.happiness + 1
        self.fix_stats()
        print(f"🍕 {self.name} gobbles the food. Nom nom nom!")

    def play(self):
        self.happiness = self.happiness + 2
        self.energy = self.energy - 2
        self.hunger = self.hunger + 1
        self.fix_stats()
        print(f"🎾 {self.name} zooms around the room like a tiny tornado!")

    def sleep(self):
        self.energy = self.energy + 4
        self.fix_stats()
        print(f"💤 {self.name} snores like a tiny chainsaw.")

    def tick(self):
        self.hunger = self.hunger + 1
        self.happiness = self.happiness - 1
        self.energy = self.energy - 1
        self.fix_stats()
'''

VP_CLASS_FULL = VP_CLASS_HEAD + VP_METHODS_SAFE + VP_STATUS

VP4 = VP_CLASS_FULL + VP_MAIN_DEMO + r'''
pet.feed()
pet.play()
pet.tick()
pet.status()
'''

VP_LOOP = r'''
while True:
    pet.status()
    choice = input("1 = feed, 2 = play, 3 = sleep, q = quit: ")
    if choice == "1":
        pet.feed()
    elif choice == "2":
        pet.play()
    elif choice == "3":
        pet.sleep()
    elif choice == "q":
        print(f"Bye! {pet.name} will miss you. 👋")
        break
    else:
        print(f"{pet.name} tilts its head. Huh?")
    pet.tick()
    if pet.hunger >= 10 or pet.happiness <= 0:
        pet.status()
        print(f"😿 Oh no! {pet.name} packed a tiny suitcase and ran away. GAME OVER")
        break
'''

VP5 = VP_CLASS_FULL + r'''

name = input("🥚 An egg is hatching! What will you name your pet? ")
pet = Pet(name)
print(f"🐣 Say hi to {pet.name}!")
''' + VP_LOOP

VP_BOSS = VP_CLASS_FULL + r'''

class Dragon(Pet):
    def __init__(self, name):
        super().__init__(name)
        self.fire = 3

    def play(self):
        self.happiness = self.happiness + 3
        self.energy = self.energy - 3
        self.hunger = self.hunger + 2
        self.fix_stats()
        print(f"🔥 {self.name} plays by setting the curtains on fire. Whoops!")

    def breathe_fire(self):
        print(f"🐉 {self.name} roasts a marshmallow. Perfectly golden!")
        self.happiness = self.happiness + 1
        self.fix_stats()


pets = [Pet(input("🥚 Name your first pet: ")), Dragon(input("🐉 Name your baby dragon: "))]

while True:
    for p in pets:
        p.status()
    who = input("Which pet? 1 or 2 (q = quit): ")
    if who == "q":
        print("Bye! Your pets will miss you. 👋")
        break
    if who != "1" and who != "2":
        print("Pick 1 or 2!")
        continue
    pet = pets[int(who) - 1]
    choice = input("1 = feed, 2 = play, 3 = sleep, 4 = special trick: ")
    if choice == "1":
        pet.feed()
    elif choice == "2":
        pet.play()
    elif choice == "3":
        pet.sleep()
    elif choice == "4" and isinstance(pet, Dragon):
        pet.breathe_fire()
    else:
        print(f"{pet.name} tilts its head. Huh?")
    game_over = False
    for p in pets:
        p.tick()
        if p.hunger >= 10 or p.happiness <= 0:
            print(f"😿 {p.name} ran away! GAME OVER")
            game_over = True
    if game_over:
        break
'''

VP_CHECK1 = _REPLY + r'''
r = run(inputs=["Waffles"])
Pet = r.cls("Pet")
p, _ = capture(Pet, "Testy")
for a in ["name", "hunger", "happiness", "energy"]:
    expect(hasattr(p, a), f"A new Pet should have self.{a}. Set it inside __init__, like self.{a} = 5.")
expect(p.name == "Testy", f"Pet(\"Testy\").name should be \"Testy\", but it was {p.name!r}. Store the name you're given: self.name = name")
for a in ["hunger", "happiness", "energy"]:
    v = getattr(p, a)
    expect(isinstance(v, (int, float)) and 0 <= v <= 10, f"self.{a} should start as a number from 0 to 10. It's {v!r}.")
pet = r.var("pet")
expect(isinstance(pet, Pet), "Make your pet with pet = Pet(name).")
expect(pet.name == "Waffles", f"When I named my pet Waffles, pet.name was {pet.name!r}. Use the name from input().")
expect("waffles" in norm(reply(r, ["Waffles"], 0)), "Print a hello message that uses pet.name.")
r2 = run(inputs=["Sir Nibbles"])
expect(r2.var("pet").name == "Sir Nibbles", "When I named my pet Sir Nibbles, it didn't get that name.")
SUCCESS = "🐣 It's alive! Your first object just hatched."
'''

VP_CHECK2 = _FRESH + r'''
p = fresh()
for m in ["feed", "play", "sleep"]:
    need_method(p, m)
p = fresh()
_, out = capture(p.feed)
expect(p.hunger < 5, f"After feed(), hunger should go DOWN. It was 5, and now it's {p.hunger}.")
expect("testy" in norm(out), "feed() should print a message with the pet's name (use self.name).")
p = fresh()
_, out = capture(p.play)
expect(p.happiness > 5, f"After play(), happiness should go UP. It was 5, and now it's {p.happiness}.")
expect("testy" in norm(out), "play() should print a message with the pet's name (use self.name).")
p = fresh()
_, out = capture(p.sleep)
expect(p.energy > 5, f"After sleep(), energy should go UP. It was 5, and now it's {p.energy}.")
expect("testy" in norm(out), "sleep() should print a message with the pet's name (use self.name).")
SUCCESS = "Your pet can eat, play and snooze! 🍕🎾💤"
'''

VP_CHECK3 = _FRESH + r'''
p = fresh()
need_method(p, "status")
for h, hap, e in [(7, 2, 9), (3, 8, 6)]:
    p = fresh(h, hap, e)
    _, out = capture(p.status)
    expect("testy" in norm(out), "status() should print the pet's name.")
    for label, v in [("hunger", h), ("happiness", hap), ("energy", e)]:
        expect(str(v) in out, f"When {label} was {v}, I didn't see {v} in status(). Print all three stats with self.")
SUCCESS = "📊 Status report looking sharp!"
'''

VP_CHECK4 = _FRESH + r'''
p = fresh()
need_method(p, "tick")
_, out = capture(p.tick)
expect(p.hunger > 5, f"tick() means time passes, so hunger should go UP. It was 5, now {p.hunger}.")
expect(p.happiness < 5, f"tick() should make happiness go DOWN a little. It was 5, now {p.happiness}.")
expect(p.energy < 5, f"tick() should make energy go DOWN a little. It was 5, now {p.energy}.")
p = fresh(10, 0, 0)
capture(p.tick)
expect(p.hunger <= 10 and p.happiness >= 0 and p.energy >= 0,
       f"Stats must stay between 0 and 10! After tick() with hunger 10, happiness 0, energy 0, I got "
       f"hunger {p.hunger}, happiness {p.happiness}, energy {p.energy}.")
p = fresh(1, 5, 5)
capture(p.feed)
expect(p.hunger >= 0, f"Feeding a pet with hunger 1 made hunger {p.hunger}. Don't go below 0!")
p = fresh(5, 5, 1)
capture(p.play)
expect(p.energy >= 0, f"Playing with energy 1 made energy {p.energy}. Don't go below 0!")
p = fresh(5, 10, 9)
capture(p.sleep)
capture(p.play)
expect(p.energy <= 10 and p.happiness <= 10,
       f"Stats can't go above 10! I got energy {p.energy} and happiness {p.happiness}.")
SUCCESS = "⏰ Time flies, and your stats stay in bounds!"
'''

VP_CHECK5 = r'''
r = run(inputs=["Waffles", "q"])
Pet = r.cls("Pet")
expect(uses("while_loops"), "Put your menu inside a while True: loop.")
expect(calls("tick") >= 1, "Call pet.tick() inside your loop so time passes every turn.")
def state(inp):
    rr = run(inputs=inp)
    p = rr.var("pet")
    return (p.hunger, p.happiness, p.energy)
s0 = state(["Waffles", "q"])
s1 = state(["Waffles", "1", "q"])
s2 = state(["Waffles", "2", "q"])
s3 = state(["Waffles", "3", "q"])
expect(len({s1, s2, s3}) == 3,
       "Choices 1, 2 and 3 should do different things: 1 = feed, 2 = play, 3 = sleep. "
       f"After each one I got (hunger, happiness, energy) = {s1}, {s2}, {s3}.")
expect(s1 != s0, "After choosing 1 (feed), the pet's stats should change.")
r = run(inputs=["Waffles"] + ["3"] * 40, allow_error=True)
if r.error == "OutOfInputs":
    raise CheckFail("I only let Waffles sleep, 40 turns in a row, never feeding it. It should get too hungry or sad "
                    "and the game should end! After tick(), check: if pet.hunger >= 10 or pet.happiness <= 0: GAME OVER, break.")
expect(r.error is None, f"Your program crashed on line {r.error_line} with {r.error}: {r.error_msg}")
SUCCESS = "🎮 Your virtual pet is a real game now. Take good care of it!"
'''

VP_CHECK_BOSS = r'''
r = run(inputs=["Alpha", "Beta", "q", "q", "q", "q"], allow_error=True)
if r.error and r.error != "OutOfInputs":
    raise CheckFail(f"Your program crashed on line {r.error_line} with {r.error}: {r.error_msg}")
Pet = r.cls("Pet")
subs = [v for v in r.ns.values() if isinstance(v, type) and issubclass(v, Pet) and v is not Pet]
expect(subs, "Make a new kind of pet that inherits from Pet, like: class Dragon(Pet):")
S = subs[0]
own = [k for k, v in vars(S).items() if callable(v) and not k.startswith("__")]
expect(own, f"Your {S.__name__} class needs at least one method of its own: a new trick, or its own version of play/feed/sleep.")
d, _ = capture(S, "Sparky")
expect(getattr(d, "name", None) == "Sparky" and hasattr(d, "hunger") and hasattr(d, "tick"),
       f"A {S.__name__} should still work like a Pet (name, hunger, tick...). If it has its own __init__, call super().__init__(name) first.")
found = False
for v in r.ns.values():
    if isinstance(v, (list, dict)):
        items = list(v.values()) if isinstance(v, dict) else v
        pets_in = [x for x in items if isinstance(x, Pet)]
        if len(pets_in) >= 2 and any(type(x) is not Pet for x in pets_in):
            found = True
expect(found, f"Keep 2 or more pets together in a list, like pets = [Pet(...), {S.__name__}(...)], with at least one {S.__name__}.")
SUCCESS = "🐉 A whole pet family! You're a class master now."
'''

VIRTUAL_PET = {
    "id": "virtual_pet",
    "week": 6,
    "order": 11,
    "title": "Virtual Pet",
    "emoji": "🐣",
    "tagline": "Hatch a pet that gets hungry, bored and sleepy, and keep it happy",
    "story": ("An egg just rolled onto your desk. It's wobbling. 🥚 Something inside wants snacks, games "
              "and naps, and it will NOT stop complaining until it gets them. Build a virtual pet that "
              "has feelings, reacts to what you do, and runs away if you ignore it."),
    "concepts": ["classes", "functions", "while_loops", "conditions"],
    "expected_minutes": 110,
    "steps": [
        {
            "id": "s1",
            "title": "Hatch your pet",
            "learn": """<p>A <b>class</b> is a cookie cutter. 🍪 It describes the shape of something. Each
<b>object</b> you make from it is a cookie. Same shape, but each cookie can have its own sprinkles.</p>
<pre>class Pet:
    def __init__(self, name):
        self.name = name
        self.hunger = 5

rex = Pet("Rex")
mo = Pet("Mo")
print(rex.name, mo.name)   # Rex Mo</pre>
<p><code>__init__</code> runs automatically when a new pet is made. <code>self</code> means "this
particular pet", so <code>self.name = name</code> stores the name inside THAT pet. Values stored on
<code>self</code> are called <b>attributes</b>.</p>""",
            "task": """<p>Write <code>class Pet:</code> with an <code>__init__(self, name)</code> that stores
<code>self.name</code>, and starts <code>self.hunger</code>, <code>self.happiness</code> and
<code>self.energy</code> at a number from 0 to 10. Then ask the player to name the pet, make
<code>pet = Pet(name)</code>, and print a hello message using <code>pet.name</code>.</p>""",
            "starter": VP_START,
            "hints": [
                "The inside of the class is indented, and __init__ is indented again inside it. That's two underscores on each side!",
                "Inside __init__: self.name = name, then self.hunger = 5, and the same for happiness and energy.",
                "pet = Pet(name) and then print(f\"Say hi to {pet.name}!\")",
            ],
            "solution": VP1,
            "check": VP_CHECK1,
            "concepts": ["classes", "input", "fstrings"],
            "xp": 25,
        },
        {
            "id": "s2",
            "title": "Snacks, games and naps",
            "learn": """<p>A <b>method</b> is a function that lives inside a class. It always takes
<code>self</code> first, so it can read and change that pet's attributes:</p>
<pre>class Pet:
    ...
    def feed(self):
        self.hunger = self.hunger - 3
        print(self.name, "munches happily")

pet.feed()   # Python fills in self for you</pre>
<p>Think of methods as the buttons on a toy. 🧸 Every toy made from the same design has the same buttons,
but pressing one only affects the toy in your hand.</p>""",
            "task": """<p>Add three methods to your <code>Pet</code> class:</p>
<ul><li><code>feed(self)</code>: hunger goes <b>down</b> (and maybe happiness up a bit)</li>
<li><code>play(self)</code>: happiness goes <b>up</b>, energy goes down</li>
<li><code>sleep(self)</code>: energy goes <b>up</b></li></ul>
<p>Each one should print a funny message using <code>self.name</code>. Then try them out at the bottom:
<code>pet.feed()</code>, <code>pet.play()</code>, <code>pet.sleep()</code>.</p>""",
            "starter": _next(VP1, "# TODO: inside class Pet, add methods feed(self), play(self) and sleep(self)\n#       (put them in the class, indented like __init__!)\n# TODO: then call pet.feed(), pet.play() and pet.sleep() down here"),
            "hints": [
                "Methods go INSIDE the class, lined up with def __init__. They all start with def name(self):",
                "In feed: self.hunger = self.hunger - 3. In play: self.happiness = self.happiness + 2 and self.energy = self.energy - 2.",
                "print(f\"{self.name} gobbles the food!\") uses the pet's own name.",
            ],
            "solution": VP2,
            "check": VP_CHECK2,
            "concepts": ["classes", "functions", "math"],
            "xp": 30,
        },
        {
            "id": "s3",
            "title": "How are you feeling?",
            "learn": """<p>A <code>status</code> method prints a little report card for the pet. Because it uses
<code>self</code>, it always shows the stats of the pet you called it on:</p>
<pre>def status(self):
    print(f"--- {self.name} ---")
    print(f"Hunger: {self.hunger}/10")</pre>
<p>Want to get fancy? <code>"❤️" * self.happiness</code> makes a row of hearts. Keep the numbers too,
so you can see exactly what's going on.</p>""",
            "task": """<p>Add a <code>status(self)</code> method that prints the pet's name and all three stats
(hunger, happiness, energy) as numbers. Call <code>pet.status()</code> at the bottom.</p>""",
            "starter": _next(VP2, "# TODO: add a status(self) method to Pet that prints the name and all 3 stats\n# TODO: call pet.status()"),
            "hints": [
                "status goes inside the class, just like feed and play.",
                "Print each stat on its own line with an f-string.",
                "print(f\"Hunger: {self.hunger}/10\") and the same for happiness and energy.",
            ],
            "solution": VP3,
            "check": VP_CHECK3,
            "concepts": ["classes", "fstrings", "output"],
            "xp": 20,
        },
        {
            "id": "s4",
            "title": "Tick tock",
            "learn": """<p>Real pets don't wait for you. Time passes and they get hungry! A <code>tick</code> method
is one "moment" going by: hunger up, happiness and energy down.</p>
<p>But stats should stay between 0 and 10. Nobody has -4 hunger. A neat trick is
<code>max</code> and <code>min</code>:</p>
<pre>self.hunger = max(0, min(10, self.hunger))</pre>
<p>Read it inside-out: <code>min(10, ...)</code> chops anything above 10 down to 10, and
<code>max(0, ...)</code> lifts anything below 0 up to 0. Put that in a helper method like
<code>fix_stats(self)</code> and call it at the end of every method that changes stats.
Methods can call other methods with <code>self.fix_stats()</code>.</p>""",
            "task": """<p>Add a <code>tick(self)</code> method: hunger goes up by 1, happiness and energy go down by 1.
Then make sure <b>every</b> stat stays between 0 and 10 after feed, play, sleep and tick.</p>""",
            "starter": _next(VP3, "# TODO: add tick(self): hunger +1, happiness -1, energy -1\n# TODO: keep every stat between 0 and 10 (a fix_stats method helps!)"),
            "hints": [
                "def tick(self): self.hunger = self.hunger + 1 ... and so on.",
                "Write def fix_stats(self): with one max(0, min(10, ...)) line for each stat.",
                "Put self.fix_stats() at the end of feed, play, sleep and tick.",
            ],
            "solution": VP4,
            "check": VP_CHECK4,
            "concepts": ["classes", "math", "functions"],
            "xp": 30,
        },
        {
            "id": "s5",
            "title": "Pet game loop",
            "learn": """<p>Now put it all together with a game loop, just like the monster menu: show the status,
ask what to do, call the right method, then let time pass with <code>pet.tick()</code>.</p>
<pre>while True:
    pet.status()
    choice = input("1 = feed, 2 = play, 3 = sleep, q = quit: ")
    if choice == "1":
        pet.feed()
    ...
    pet.tick()</pre>
<p>And the scary part: if the pet gets too hungry or too sad, it runs away. 😿 Check after every tick
and <code>break</code> with a GAME OVER message.</p>""",
            "task": """<p>Replace the test calls at the bottom with a <code>while True:</code> game loop:
<code>1</code> = feed, <code>2</code> = play, <code>3</code> = sleep, <code>q</code> = quit. After each turn, call
<code>pet.tick()</code>. If <code>pet.hunger</code> reaches 10 or <code>pet.happiness</code> reaches 0,
print GAME OVER and break.</p>""",
            "starter": _next(VP4, "# TODO: replace the test calls above with a while True: game loop\n#   1 = feed, 2 = play, 3 = sleep, q = quit, then pet.tick() every turn\n# TODO: GAME OVER if hunger reaches 10 or happiness reaches 0"),
            "hints": [
                "Start with while True: and pet.status(), then choice = input(...).",
                "if choice == \"1\": pet.feed(), elif choice == \"2\": pet.play() ... elif choice == \"q\": break",
                "After the if/elif chain: pet.tick(), then if pet.hunger >= 10 or pet.happiness <= 0: print(\"GAME OVER\") and break",
            ],
            "solution": VP5,
            "check": VP_CHECK5,
            "concepts": ["while_loops", "conditions", "classes", "input"],
            "xp": 35,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: The Dragon Egg",
        "learn": """<p>A dragon is a pet... but spicier. 🐉 Instead of copying the whole Pet class, you can
make a class that <b>inherits</b> from it. It gets every Pet method for free, and you can add new ones or
replace old ones:</p>
<pre>class Dragon(Pet):
    def __init__(self, name):
        super().__init__(name)   # do the normal Pet setup first
        self.fire = 3

    def breathe_fire(self):
        print(self.name, "roasts a marshmallow!")</pre>
<p><code>super().__init__(name)</code> means "run the parent's __init__ too". If you write a
<code>play</code> method in Dragon, dragons use THAT one instead of Pet's. Same cookie cutter, extra spikes.</p>
<p>Then keep more than one pet in a list: <code>pets = [Pet("Mo"), Dragon("Blaze")]</code>.</p>""",
        "task": """<p>Make a new class that inherits from <code>Pet</code> (a Dragon, a Robot Cat, a Ghost Hamster...).
Give it at least one method of its own: a special trick, or its own version of play/feed/sleep.
Then keep <b>two pets</b> in a list (at least one of the new kind), and let the player pick which pet to
care for each turn. Tick every pet each turn!</p>""",
        "starter": _next(VP5, "# TODO (boss): class Dragon(Pet): with its own special method\n# TODO (boss): pets = [Pet(...), Dragon(...)] and let the player choose which pet to look after"),
        "hints": [
            "class Dragon(Pet): goes after the Pet class. If you give it an __init__, start it with super().__init__(name).",
            "pets = [Pet(input(\"First pet: \")), Dragon(input(\"Dragon: \"))] makes the list.",
            "who = input(\"Which pet? 1 or 2: \") then pet = pets[int(who) - 1]. At the end of the turn: for p in pets: p.tick()",
        ],
        "solution": VP_BOSS,
        "check": VP_CHECK_BOSS,
        "concepts": ["classes", "lists", "for_loops", "conditions"],
        "xp": 90,
    },
    "remix": {
        "prompt": "Make it yours! Give your pet a personality. 🐣",
        "ideas": [
            "Pick a mood emoji in status(): 😄 when happy, 😐 in the middle, 😭 when sad.",
            "Add a random event each tick: your pet finds a sock, sneezes, or sees a scary leaf.",
            "Add an age attribute. After 10 turns your pet grows up and gets a new name, like 'Big Waffles'.",
            "Add a shop: earn coins by playing, spend them on fancy snacks that fill hunger more.",
        ],
    },
}


# ---------------------------------------------------------------------------
# Project 12: Capstone
# ---------------------------------------------------------------------------

# Shared check pieces. Checks must be generic: the program is the kid's own idea.
_PLAN = r'''
plan = []
for line in source.splitlines():
    s = line.strip()
    if s.startswith("#"):
        text = s.lstrip("#").strip()
        if "todo" in text.lower() or len(text.split()) < 3:
            continue
        plan.append(text)
'''

_RUNS = r'''
code_lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
TRIES = [
    ["1"] * 40,
    ["yes", "2", "no", "3", "q", "quit", "exit", "n", "0", "done"] * 4,
    ["q", "quit", "exit", "no", "n", "0", "stop", "done"] * 5,
    ["hello", "abc", "1", "2", "3", "4", "yes", "no", "q"] * 4,
    ["0"] * 40,
    ["2", "3", "yes", "4", "5", "y", "1", "no"] * 5,
]

# Crashes that are bugs no matter what the player types. (ValueError, KeyError and IndexError
# can come from odd answers like "q" where a number was expected, so those are forgiven if
# some other set of answers works.)
ALWAYS_BUGS = ("NameError", "UnboundLocalError", "AttributeError", "TypeError", "ZeroDivisionError",
               "ImportError", "ModuleNotFoundError", "RecursionError")

def game_runs():
    first_crash = None
    good = None
    for inp in TRIES:
        rr = run(inputs=inp, allow_error=True)
        if rr.error in (None, "OutOfInputs"):
            good = good or rr
            continue
        if rr.error in ALWAYS_BUGS:
            first_crash = rr
            break
        if first_crash is None:
            first_crash = rr
    if good is not None and (first_crash is None or first_crash.error not in ALWAYS_BUGS):
        return good
    where = f" on line {first_crash.error_line}" if first_crash.error_line else ""
    raise CheckFail(f"I played your game with lots of different answers (numbers, yes/no, q...) and it crashed. "
                    f"The crash was{where}: {first_crash.error}: {first_crash.error_msg}. "
                    "Fix that and check again!")

def shows_something(rr):
    t = rr.turtle or {}
    return bool(rr.output.strip()) or bool(t.get("lines")) or bool(t.get("dots")) or bool(t.get("fills"))

BIG = ["input", "strings", "fstrings", "math", "types", "conditions", "random", "while_loops",
       "for_loops", "turtle", "lists", "functions", "dicts", "classes"]
found = [c for c in BIG if uses(c)]
'''

CAP_START = r'''# ===== MY GAME PLAN =====
# TODO: Replace these TODO lines with your plan, one idea per line (at least 5 lines!).
# TODO: What is my game called, and what is it about?
# TODO: How do you play it? What does the player type or do?
# TODO: How do you win? How do you lose?
# TODO: What will the very first, tiny version do?
print("My game is coming soon...")
'''

CAP_PLAN = r'''# ===== MY GAME PLAN =====
# Game name: Cosmic Quiz Show, a space trivia game
# Quizbot 3000, a robot host, asks you questions about space
# You get a point for every right answer and lose a life for a wrong one
# You start with 3 lives, and if you lose them all it is game over
# At the end it shows your score and a rank like Space Cadet or Galaxy Brain
# First version: say hi, ask one question, and tell the answer
'''

CAP1 = CAP_PLAN + r'''print("Cosmic Quiz Show is coming soon...")
'''

CAP2 = CAP_PLAN + r'''
print("🚀 WELCOME TO THE COSMIC QUIZ SHOW! 🚀")
print("I'm Quizbot 3000, your host. Beep boop.")
name = input("What's your name, contestant? ")
print(f"Great to have you, {name}!")
score = 0
lives = 3
print(f"You have {lives} lives. Let's go!")
answer = input("Question 1: What is the biggest planet? ")
print(f"You said {answer}. The answer is Jupiter!")
print(f"Thanks for playing, {name}. The full game is coming soon!")
'''

CAP3 = CAP_PLAN + r'''
print("🚀 WELCOME TO THE COSMIC QUIZ SHOW! 🚀")
print("I'm Quizbot 3000, your host. Beep boop.")
name = input("What's your name, contestant? ")
print(f"Great to have you, {name}!")
score = 0
lives = 3
print(f"You have {lives} lives. Let's go!")

questions = ["What is the biggest planet?", "What planet do we live on?", "What star is closest to Earth?"]
answers = ["jupiter", "earth", "sun"]
for i in range(len(questions)):
    guess = input(questions[i] + " ").lower().strip()
    if guess == answers[i]:
        score = score + 1
        print("✅ Correct! Quizbot does a happy beep.")
    else:
        lives = lives - 1
        print(f"❌ Nope! It was {answers[i]}. Lives left: {lives}")

print(f"Final score: {score}. Thanks for playing, {name}!")
'''

CAP4 = CAP_PLAN + r'''

def ask(question, answer):
    guess = input(question + " ").lower().strip()
    if guess == answer:
        print("✅ Correct! Quizbot does a happy beep.")
        return True
    print(f"❌ Nope! It was {answer}.")
    return False


def show_rank(score, total):
    print(f"You got {score} out of {total}!")
    if score == total:
        print("🌌 Rank: GALAXY BRAIN")
    else:
        print("🧑‍🚀 Rank: Space Cadet (keep training!)")


print("🚀 WELCOME TO THE COSMIC QUIZ SHOW! 🚀")
name = input("What's your name, contestant? ")
score = 0
questions = ["What is the biggest planet?", "What planet do we live on?", "What star is closest to Earth?"]
answers = ["jupiter", "earth", "sun"]
for i in range(len(questions)):
    if ask(questions[i], answers[i]):
        score = score + 1
show_rank(score, len(questions))
print(f"Thanks for playing, {name}!")
'''

CAP5 = CAP_PLAN + r'''
import random


def ask(question, answer):
    guess = input(question + " ").lower().strip()
    if guess == answer:
        print("✅ Correct! Quizbot does a happy beep.")
        return True
    print(f"❌ Nope! It was {answer}.")
    return False


def show_rank(score, total):
    print(f"You got {score} out of {total}!")
    if score == total:
        print("🌌 Rank: GALAXY BRAIN")
    elif score >= total // 2:
        print("🚀 Rank: Rocket Ranger")
    else:
        print("🧑‍🚀 Rank: Space Cadet (keep training!)")


def play_round():
    questions = ["What is the biggest planet?", "What planet do we live on?",
                 "What star is closest to Earth?", "What planet is called the Red Planet?",
                 "What planet has the famous rings?"]
    answers = ["jupiter", "earth", "sun", "mars", "saturn"]
    order = list(range(len(questions)))
    random.shuffle(order)
    score = 0
    lives = 3
    for i in order:
        if lives == 0:
            print("💥 Out of lives! Your rocket runs out of fuel.")
            break
        if ask(questions[i], answers[i]):
            score = score + 1
        else:
            lives = lives - 1
            print("Lives left: " + "❤️" * lives)
    show_rank(score, len(questions))
    return score


print("🚀 WELCOME TO THE COSMIC QUIZ SHOW! 🚀")
print("I'm Quizbot 3000, your host. Beep boop.")
name = input("What's your name, contestant? ")
best = 0
while True:
    score = play_round()
    if score > best:
        best = score
        print(f"🏆 New best score: {best}!")
    again = input("Play again? (yes/no) ").lower()
    if again != "yes":
        break
print(f"Thanks for playing, {name}! Your best score was {best}.")
'''

CAP_BOSS = CAP_PLAN + r'''
import random

QUIZ = {
    "What is the biggest planet?": "jupiter",
    "What planet do we live on?": "earth",
    "What star is closest to Earth?": "sun",
    "What planet is called the Red Planet?": "mars",
    "What planet has the famous rings?": "saturn",
    "What do astronauts wear in space?": "spacesuit",
}


def ask(question, answer):
    guess = input(question + " ").lower().strip()
    if guess == answer:
        print("✅ Correct! Quizbot does a happy beep.")
        return True
    print(f"❌ Nope! It was {answer}.")
    return False


def show_rank(score, total):
    print(f"You got {score} out of {total}!")
    if score == total:
        print("🌌 Rank: GALAXY BRAIN")
    elif score >= total // 2:
        print("🚀 Rank: Rocket Ranger")
    else:
        print("🧑‍🚀 Rank: Space Cadet (keep training!)")


def play_round():
    questions = list(QUIZ.keys())
    random.shuffle(questions)
    score = 0
    lives = 3
    for q in questions:
        if lives == 0:
            print("💥 Out of lives! Your rocket runs out of fuel.")
            break
        if ask(q, QUIZ[q]):
            score = score + 1
        else:
            lives = lives - 1
            print("Lives left: " + "❤️" * lives)
    show_rank(score, len(questions))
    return score


print("🚀 WELCOME TO THE COSMIC QUIZ SHOW! 🚀")
print("I'm Quizbot 3000, your host. Beep boop.")
name = input("What's your name, contestant? ")
best = 0
while True:
    score = play_round()
    if score > best:
        best = score
        print(f"🏆 New best score: {best}!")
    again = input("Play again? (yes/no) ").lower()
    if again != "yes":
        break
print(f"Thanks for playing, {name}! Your best score was {best}.")
'''

CAP_CHECK1 = _PLAN + r'''
expect(len(plan) >= 5,
       f"Write your plan as at least 5 comment lines (each starts with # and has a few words). "
       f"I found {len(plan)} so far. Try answering: What's it called? How do you play? How do you win or lose? "
       "What will it print? What's the first tiny thing to build? (Delete the TODO lines as you go.)")
SUCCESS = "📝 Great plan! Every real game starts on paper (or in comments)."
'''

CAP_CHECK2 = _RUNS + r'''
expect(len(code_lines) >= 8,
       f"Your first version needs at least 8 lines of real code (comments don't count). You have {len(code_lines)}. "
       "Build the smallest version of your game that actually does something!")
r = game_runs()
expect(shows_something(r), "When I ran your game, nothing showed up. Print something (or draw something) so the player knows what's happening!")
SUCCESS = "🎉 Version 1 runs! That's the hardest step. Everything from here is upgrades."
'''

CAP_CHECK3 = _RUNS + r'''
expect(uses("while_loops") or uses("for_loops"),
       "Add a loop! A while loop can keep the game going (rounds, turns, 'play again?'), "
       "or a for loop can repeat something (questions, enemies, shapes).")
expect(uses("conditions"),
       "Add a decision with if! Games are full of them: right or wrong answer? win or lose? which menu choice?")
r = game_runs()
expect(shows_something(r), "When I ran your game, nothing showed up. Print something so the player knows what's happening!")
SUCCESS = "🔁 Loops and decisions: your game has a brain now!"
'''

CAP_CHECK4 = _RUNS + r'''
import ast
funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
used = [f for f in funcs if f != "__init__" and calls(f) >= 1]
made = [c for c in classes if calls(c) >= 1]
expect(len(used) >= 2 or len(made) >= 1,
       f"Organize your game into at least 2 functions (or a class) and USE them. "
       f"I found functions {funcs or 'none'}, and these ones get called: {used or 'none'}. "
       "Good candidates: the part that asks one question, one turn, drawing one shape, showing the score.")
r = game_runs()
expect(shows_something(r), "When I ran your game, nothing showed up. Make sure you still call your functions!")
SUCCESS = "🧩 Nicely organized! Future-you says thanks."
'''

CAP_CHECK5 = _RUNS + r'''
expect(len(found) >= 4,
       f"Mix in at least 4 different Python ideas (printing and variables don't count, they're everywhere). "
       f"I found: {', '.join(found) or 'none'}. Ideas: random, f-strings, lists, a while loop, a for loop, functions, math.")
expect(len(code_lines) >= 35,
       f"Polish time! Grow your game to at least 35 lines of real code (not counting comments or blank lines). "
       f"You have {len(code_lines)}. Ideas: a 'play again?' loop, a high score, more levels, a title screen, random surprises.")
r = game_runs()
expect(shows_something(r), "When I ran your game, nothing showed up. Print something so the player knows what's happening!")
SUCCESS = f"✨ Polished! {len(code_lines)} lines using {len(found)} different ideas. That's a REAL game."
'''

CAP_CHECK_BOSS = _RUNS + r'''
expect(uses("dicts") or uses("classes"),
       "Level up your game's data with a dictionary (like questions -> answers, or item -> price) "
       "or a class (like a Player or Monster with its own stats and methods).")
expect(len(found) >= 6,
       f"Use at least 6 different Python ideas. I found {len(found)}: {', '.join(found)}. "
       "What else could your game use? random, lists, f-strings, for loops, while loops, functions, math...")
r = game_runs()
expect(shows_something(r), "When I ran your game, nothing showed up. Print something so the player knows what's happening!")
SUCCESS = f"🏆 BOSS DEFEATED! {len(found)} different ideas in one game you invented yourself. You're a programmer now. For real."
'''

CAPSTONE = {
    "id": "capstone",
    "week": 6,
    "order": 12,
    "title": "Capstone: Your Own Game",
    "emoji": "🏆",
    "tagline": "Invent, plan and build a game that's 100% yours",
    "story": ("No more instructions from us. 😎 For the last project, YOU are the game designer. Pick any "
              "idea you like, plan it, build a tiny version, then keep upgrading it until you'd happily "
              "show it to your friends. Everything you learned in six weeks is in your toolbox."),
    "concepts": ["functions", "conditions", "while_loops", "lists", "dicts", "classes"],
    "expected_minutes": 180,
    "steps": [
        {
            "id": "s1",
            "title": "Dream it, plan it",
            "learn": """<p>Real game makers plan before they code. A plan doesn't have to be fancy. Just a few
lines answering: what's it called, how do you play, how do you win or lose?</p>
<p>Need an idea? Here are some sparks: 🎯</p>
<ul><li><b>Trivia game</b> about your favorite show, sport or video game</li>
<li><b>Dungeon crawler</b>: fight random monsters room by room</li>
<li><b>Pet shop</b> or <b>lemonade stand</b>: buy, sell, try to get rich</li>
<li><b>Sports manager</b>: pick players, simulate matches with random</li>
<li><b>Turtle art generator</b>: random colorful patterns every time</li>
<li><b>Rock-paper-scissors tournament</b> against 3 robot opponents</li></ul>
<p>Write your plan as <b>comments</b> at the top of your file. Python ignores lines starting with
<code>#</code>, so they're notes for humans:</p>
<pre># Game name: Lava Floor Escape
# You jump across rocks by picking left or right
# One side is random lava. 3 lives.</pre>""",
            "task": """<p>Replace the TODO lines with your own plan: <b>at least 5 comment lines</b>, each a few words
long. Say what your game is called, how you play, how you win or lose, and what the very first tiny
version will do.</p>""",
            "starter": CAP_START,
            "hints": [
                "Pick something you'd actually want to play. Small is fine: you can always add more later!",
                "Each plan line starts with # and should be a real sentence, like # You start with 3 lives",
                "Try: # Game name: ..., # How to play: ..., # How to win: ..., # How to lose: ..., # First version: ...",
            ],
            "solution": CAP1,
            "check": CAP_CHECK1,
            "concepts": ["output"],
            "xp": 20,
        },
        {
            "id": "s2",
            "title": "Version 1: make it run",
            "learn": """<p>The secret of big programs: they start small. Build the tiniest version of your game that
actually <i>does</i> something. Say hi, ask one question, show one result. Don't worry about making it
awesome yet.</p>
<p>This is called a <b>prototype</b>. Game studios make ugly prototypes all the time to check the idea is
fun before they spend months on it.</p>
<pre>print("Welcome to Lava Floor Escape!")
name = input("Name, brave jumper? ")
side = input("Left or right? ")
print(f"{name} jumps {side}... and survives! (for now)")</pre>""",
            "task": """<p>Under your plan, write the first version of your game: <b>at least 8 lines of real code</b>
that run without crashing. It should print something (or draw something with turtle).</p>""",
            "starter": _next(CAP1, "# TODO: build version 1 of your game here: at least 8 lines of real code that run!"),
            "hints": [
                "Start with a title screen: a few print lines with your game's name.",
                "Ask the player something with input() and react to it with an f-string.",
                "Keep it simple! If something crashes, read the line number in the error and fix just that line.",
            ],
            "solution": CAP2,
            "check": CAP_CHECK2,
            "concepts": ["output", "input", "variables"],
            "xp": 30,
        },
        {
            "id": "s3",
            "title": "Loops and choices",
            "learn": """<p>Almost every game has two things:</p>
<ul><li>A <b>loop</b>: rounds, turns, questions, enemies, or "play again?" (<code>while</code> or <code>for</code>)</li>
<li><b>Decisions</b>: right or wrong? alive or not? which menu option? (<code>if/elif/else</code>)</li></ul>
<pre>lives = 3
while lives &gt; 0:
    side = input("Left or right? ")
    if side == random.choice(["left", "right"]):
        print("LAVA! 🔥")
        lives -= 1</pre>
<p>Tip: make sure your loop can end, so players aren't trapped forever! 😅</p>""",
            "task": """<p>Add at least <b>one loop</b> and <b>one if</b> to your game. The game should still run
without crashing.</p>""",
            "starter": _next(CAP2, "# TODO: add a loop (while or for) and a decision (if) to your game"),
            "hints": [
                "What in your game happens more than once? That's your loop.",
                "What can go two ways in your game? That's your if/else.",
                "A 'play again?' loop works for almost any game: while True: ... if input(\"Again? \") != \"yes\": break",
            ],
            "solution": CAP3,
            "check": CAP_CHECK3,
            "concepts": ["while_loops", "for_loops", "conditions"],
            "xp": 30,
        },
        {
            "id": "s4",
            "title": "Get organized",
            "learn": """<p>As games grow, the code gets messy. 🍝 <b>Functions</b> are like labelled boxes: each one
does one job, and has a name that says what it is.</p>
<pre>def jump(lives):
    ...
    return lives

def show_score(score):
    print(f"Score: {score}")</pre>
<p>Look through your code: which parts do one clear job? Asking one question, one fight, one turn,
drawing one shape, showing the score? Move each into its own function, and call it.
(Or, if your game has a "thing" with stats like a player or a monster, a <b>class</b> works too!)</p>""",
            "task": """<p>Organize your game with <b>at least 2 functions</b> that you actually call (or a class
that you create objects from). The game should still run.</p>""",
            "starter": _next(CAP3, "# TODO: move parts of your game into at least 2 functions (or a class), and call them"),
            "hints": [
                "Find a chunk of code that does one job, and put def some_name(): above it (then indent it).",
                "If the chunk needs a value, make it a parameter. If it figures something out, return it.",
                "Don't forget to CALL your functions, like show_score(score), or they'll never run!",
            ],
            "solution": CAP4,
            "check": CAP_CHECK4,
            "concepts": ["functions"],
            "xp": 35,
        },
        {
            "id": "s5",
            "title": "Polish it till it shines",
            "learn": """<p>Now make it the kind of game your friends ask to play again. ✨ Some polish ideas:</p>
<ul><li>A title screen and a goodbye message</li>
<li>A "play again?" loop and a best score</li>
<li><code>random</code> so every game is different</li>
<li>Levels that get harder, or lives shown as hearts: <code>"❤️" * lives</code></li>
<li>A list of questions, enemies, items or colors instead of just one</li></ul>
<p>Test it a bunch. Try weird answers. Try to break it! Then fix what breaks.</p>""",
            "task": """<p>Grow your game to <b>at least 35 lines of real code</b> (not counting comments and blank
lines) that use <b>at least 4 different Python ideas</b> (like input, if, loops, random, lists, functions,
f-strings, math). Printing and variables don't count, they're in everything!</p>""",
            "starter": _next(CAP4, "# TODO: polish! Get to 35+ lines of code using 4+ different ideas (random, lists, loops, f-strings...)"),
            "hints": [
                "Add a 'play again?' while loop around your whole game.",
                "Use random to shuffle, pick or roll something so each game is a surprise.",
                "Keep a best score or high score and show it at the end.",
            ],
            "solution": CAP5,
            "check": CAP_CHECK5,
            "concepts": ["functions", "random", "lists", "while_loops", "fstrings"],
            "xp": 40,
        },
    ],
    "boss": {
        "id": "boss",
        "title": "BOSS: Pro Game Designer",
        "learn": """<p>Pro games keep their data organized. Two tools you know:</p>
<ul><li>A <b>dictionary</b> for things that go in pairs: question → answer, item → price, enemy → hp</li>
<li>A <b>class</b> for things with stats and actions: a Player with <code>hp</code> and <code>attack()</code>,
a Shop with <code>buy()</code></li></ul>
<pre>shop = {"sword": 50, "potion": 10, "rubber chicken": 3}
for item, price in shop.items():
    print(f"{item}: {price} coins")</pre>
<p>Use one of them to make your game easier to grow. Then you can add 20 more items just by adding lines to the dictionary!</p>""",
        "task": """<p>Use a <b>dictionary or a class</b> in your game, and use <b>at least 6 different Python
ideas</b> in total. The game must still run!</p>""",
        "starter": _next(CAP5, "# TODO (boss): use a dictionary or a class, and 6+ different Python ideas"),
        "hints": [
            "What pairs does your game have? Questions and answers? Items and prices? That's a dictionary.",
            "Is there a 'thing' in your game with stats? A player, a monster, a car? That could be a class.",
            "Loop over a dictionary with for key, value in my_dict.items(): to use it.",
        ],
        "solution": CAP_BOSS,
        "check": CAP_CHECK_BOSS,
        "concepts": ["dicts", "classes", "functions"],
        "xp": 100,
    },
    "remix": {
        "prompt": "It's your game, so keep going! Here are some sparks for version 2 (or a whole new game): 🚀",
        "ideas": [
            "Trivia showdown: a question dictionary about your favorite show, with a timer-free 'lightning round'.",
            "Dungeon crawler: rooms from Escape the Castle + monster battles from Monster Collector. Mash them together!",
            "Pet shop tycoon: buy pets, sell pets, feed them, try to make 1000 coins before they all run away.",
            "Sports manager: a team dictionary of players with skill stats, random match results, and a league table.",
            "Turtle art generator: random shapes, colors and sizes, a new masterpiece every run.",
            "Rock-paper-scissors tournament: beat 3 robot opponents, each with its own sneaky strategy class.",
        ],
    },
}

PROJECTS = [VIRTUAL_PET, CAPSTONE]


# ---------------------------------------------------------------------------
# Practice
# ---------------------------------------------------------------------------

PRACTICE = [
    {
        "id": "p_classes_1",
        "concept": "classes",
        "title": "Robot Blueprint",
        "difficulty": 1,
        "task": """<p>Write <code>class Robot:</code> with an <code>__init__(self, name, color)</code> that stores
both. Add a method <code>beep(self)</code> that <b>returns</b> a string like <code>"Bolt the red robot says BEEP!"</code>.
Make one robot and print its beep.</p>""",
        "starter": r'''class Robot:
    # TODO: __init__(self, name, color) stores self.name and self.color
    # TODO: beep(self) returns a string with the name, the color and BEEP
    pass

bolt = Robot("Bolt", "red")
print(bolt.beep())
''',
        "hints": [
            "def __init__(self, name, color): then self.name = name and self.color = color",
            "def beep(self): return f\"...\" (return, not print!)",
            "return f\"{self.name} the {self.color} robot says BEEP!\"",
        ],
        "solution": r'''class Robot:
    def __init__(self, name, color):
        self.name = name
        self.color = color

    def beep(self):
        return f"{self.name} the {self.color} robot says BEEP!"

bolt = Robot("Bolt", "red")
print(bolt.beep())
''',
        "check": r'''
r = run(allow_error=True)
Robot = r.cls("Robot")
for n, c in [("Zappy", "green"), ("Clank", "purple")]:
    b, _ = capture(Robot, n, c)
    expect(getattr(b, "name", None) == n and getattr(b, "color", None) == c,
           f"Robot({n!r}, {c!r}) should store self.name and self.color.")
    expect(callable(getattr(b, "beep", None)), "Your Robot needs a beep(self) method.")
    v, _ = capture(b.beep)
    expect(isinstance(v, str) and n.lower() in v.lower() and c in v.lower(),
           f"beep() for Robot({n!r}, {c!r}) should RETURN a string with its name and color. It returned {v!r}.")
expect(r.error is None, f"Your program crashed on line {r.error_line} with {r.error}: {r.error_msg}")
SUCCESS = "🤖 BEEP BOOP! Robot factory online."
''',
        "xp": 15,
    },
    {
        "id": "p_classes_2",
        "concept": "classes",
        "title": "Piggy Bank",
        "difficulty": 2,
        "task": """<p>Write <code>class PiggyBank:</code>. It starts with <code>self.coins = 0</code>.
<code>add(self, amount)</code> adds coins. <code>spend(self, amount)</code> takes coins away and returns
<code>True</code>, but only if there are enough. If not, it changes nothing and returns <code>False</code>. 🐷</p>""",
        "starter": r'''class PiggyBank:
    def __init__(self):
        self.coins = 0

    # TODO: add(self, amount)
    # TODO: spend(self, amount) -> True if there were enough coins, otherwise False

bank = PiggyBank()
bank.add(10)
print(bank.spend(3), bank.coins)
''',
        "hints": [
            "def add(self, amount): self.coins = self.coins + amount",
            "In spend, check first: if amount > self.coins: return False",
            "Otherwise: self.coins = self.coins - amount and return True",
        ],
        "solution": r'''class PiggyBank:
    def __init__(self):
        self.coins = 0

    def add(self, amount):
        self.coins = self.coins + amount

    def spend(self, amount):
        if amount > self.coins:
            return False
        self.coins = self.coins - amount
        return True

bank = PiggyBank()
bank.add(10)
print(bank.spend(3), bank.coins)
''',
        "check": r'''
r = run(allow_error=True)
PB = r.cls("PiggyBank")
b, _ = capture(PB)
expect(getattr(b, "coins", None) == 0, "A new PiggyBank should start with self.coins = 0.")
expect(callable(getattr(b, "add", None)) and callable(getattr(b, "spend", None)), "Your PiggyBank needs add and spend methods.")
capture(b.add, 10)
capture(b.add, 5)
expect(b.coins == 15, f"After add(10) and add(5), coins should be 15, but it's {b.coins}.")
v, _ = capture(b.spend, 4)
expect(v is True and b.coins == 11, f"spend(4) with 15 coins should return True and leave 11. Got {v!r} and {b.coins}.")
v, _ = capture(b.spend, 50)
expect(v is False and b.coins == 11, f"spend(50) with only 11 coins should return False and keep 11. Got {v!r} and {b.coins}.")
SUCCESS = "🐷 Oink! Your money is safe."
''',
        "xp": 20,
    },
    {
        "id": "p_classes_3",
        "concept": "classes",
        "title": "Hero Health Bar",
        "difficulty": 2,
        "task": """<p>Write <code>class Hero:</code> with <code>__init__(self, name)</code> that sets
<code>self.hp = 100</code>. Add <code>take_damage(self, amount)</code> (hp goes down, but never below 0),
<code>heal(self, amount)</code> (hp goes up, but never above 100), and <code>is_alive(self)</code>
which returns <code>True</code> if hp is more than 0.</p>""",
        "starter": r'''class Hero:
    def __init__(self, name):
        self.name = name
        self.hp = 100

    # TODO: take_damage(self, amount), heal(self, amount), is_alive(self)

hero = Hero("Sir Snacks")
hero.take_damage(30)
print(hero.name, hero.hp, hero.is_alive())
''',
        "hints": [
            "self.hp = max(0, self.hp - amount) keeps it from going below 0.",
            "self.hp = min(100, self.hp + amount) keeps it from going above 100.",
            "def is_alive(self): return self.hp > 0",
        ],
        "solution": r'''class Hero:
    def __init__(self, name):
        self.name = name
        self.hp = 100

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount):
        self.hp = min(100, self.hp + amount)

    def is_alive(self):
        return self.hp > 0

hero = Hero("Sir Snacks")
hero.take_damage(30)
print(hero.name, hero.hp, hero.is_alive())
''',
        "check": r'''
r = run(allow_error=True)
Hero = r.cls("Hero")
h, _ = capture(Hero, "Testy")
for m in ["take_damage", "heal", "is_alive"]:
    expect(callable(getattr(h, m, None)), f"Your Hero needs a {m} method.")
capture(h.take_damage, 30)
expect(h.hp == 70, f"After take_damage(30), hp should be 70, but it's {h.hp}.")
capture(h.heal, 50)
expect(h.hp == 100, f"Healing 50 from 70 should stop at 100, but hp is {h.hp}.")
v, _ = capture(h.is_alive)
expect(v is True, "is_alive() should return True when hp is above 0.")
capture(h.take_damage, 999)
expect(h.hp == 0, f"After a huge hit, hp should stop at 0, but it's {h.hp}.")
v, _ = capture(h.is_alive)
expect(v is False, "is_alive() should return False when hp is 0.")
SUCCESS = "🛡️ Your hero is ready for adventure!"
''',
        "xp": 20,
    },
    {
        "id": "p_classes_4",
        "concept": "classes",
        "title": "Animal Family",
        "difficulty": 3,
        "task": """<p>Write <code>class Animal:</code> with <code>__init__(self, name)</code> and a method
<code>speak(self)</code> that returns <code>"..."</code>. Then write <code>class Dog(Animal):</code> and
<code>class Cat(Animal):</code> that inherit from it and each have their own <code>speak</code> returning
something like <code>"Woof!"</code> and <code>"Meow!"</code>. Dogs and cats should still have a name,
without writing their own <code>__init__</code>.</p>""",
        "starter": r'''class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

# TODO: class Dog(Animal): with its own speak()
# TODO: class Cat(Animal): with its own speak()
''',
        "hints": [
            "class Dog(Animal): means a Dog is a kind of Animal, so it gets __init__ for free.",
            "Inside Dog, write def speak(self): return \"Woof!\"",
            "Do the same for Cat with \"Meow!\". Try: print(Dog(\"Rex\").name, Dog(\"Rex\").speak())",
        ],
        "solution": r'''class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."


class Dog(Animal):
    def speak(self):
        return "Woof!"


class Cat(Animal):
    def speak(self):
        return "Meow!"


rex = Dog("Rex")
print(rex.name, "says", rex.speak())
''',
        "check": r'''
r = run(allow_error=True)
A = r.cls("Animal")
D = r.cls("Dog")
C = r.cls("Cat")
expect(issubclass(D, A) and issubclass(C, A), "Dog and Cat should inherit from Animal: class Dog(Animal):")
a, _ = capture(A, "Blob")
d, _ = capture(D, "Rex")
c, _ = capture(C, "Tom")
expect(getattr(d, "name", None) == "Rex" and getattr(c, "name", None) == "Tom", "Dog(\"Rex\").name should be \"Rex\" (it comes from Animal's __init__).")
sa, _ = capture(a.speak)
sd, _ = capture(d.speak)
sc, _ = capture(c.speak)
expect(isinstance(sd, str) and isinstance(sc, str), "speak() should RETURN a string.")
expect(len({sa, sd, sc}) == 3, f"Animal, Dog and Cat should each say something different. I got {sa!r}, {sd!r}, {sc!r}.")
SUCCESS = "🐶🐱 One family, many voices. That's inheritance!"
''',
        "xp": 25,
    },
    {
        "id": "p_dicts_w6_1",
        "concept": "dicts",
        "title": "Pet Shop Checkout",
        "difficulty": 2,
        "task": """<p>There's a <code>prices</code> dictionary. Write <code>def total(cart):</code> where
<code>cart</code> is a list of item names. Return the total cost. Items that aren't in the shop cost 0
(use <code>.get</code>).</p>""",
        "starter": r'''prices = {"kibble": 5, "chew toy": 3, "tiny hat": 12, "fish food": 2}

def total(cart):
    # TODO: add up prices for every item in the cart (unknown items cost 0)
    return 0

print(total(["kibble", "tiny hat"]))
''',
        "hints": [
            "Start with cost = 0, then loop: for item in cart:",
            "prices.get(item, 0) gives the price, or 0 if the shop doesn't sell it.",
            "cost = cost + prices.get(item, 0), and return cost at the end.",
        ],
        "solution": r'''prices = {"kibble": 5, "chew toy": 3, "tiny hat": 12, "fish food": 2}

def total(cart):
    cost = 0
    for item in cart:
        cost = cost + prices.get(item, 0)
    return cost

print(total(["kibble", "tiny hat"]))
''',
        "check": r'''
r = run()
f = r.fn("total")
prices = r.var("prices")
for cart in (["kibble", "tiny hat"], ["chew toy", "chew toy", "fish food"], [], ["unicorn"], ["kibble", "unicorn"]):
    want = sum(prices.get(i, 0) for i in cart)
    v, _ = capture(f, cart)
    expect(v == want, f"total({cart}) should be {want}, but it returned {v!r}.")
SUCCESS = "🛒 Ka-ching! Checkout works."
''',
        "xp": 20,
    },
    {
        "id": "p_lists_w6_1",
        "concept": "lists",
        "title": "Top Three",
        "difficulty": 2,
        "task": """<p>Write <code>def top_three(scores):</code> that returns a new list with the 3 highest scores,
biggest first. <code>top_three([5, 90, 12, 77, 40])</code> → <code>[90, 77, 40]</code>. If there are fewer
than 3 scores, return all of them, biggest first.</p>""",
        "starter": r'''def top_three(scores):
    # TODO: return the 3 biggest scores, biggest first
    return scores

print(top_three([5, 90, 12, 77, 40]))
''',
        "hints": [
            "sorted(scores) gives a sorted copy. sorted(scores, reverse=True) sorts biggest first.",
            "A slice like my_list[:3] gives the first 3 items.",
            "return sorted(scores, reverse=True)[:3]",
        ],
        "solution": r'''def top_three(scores):
    ordered = sorted(scores, reverse=True)
    return ordered[:3]

print(top_three([5, 90, 12, 77, 40]))
''',
        "check": r'''
r = run()
f = r.fn("top_three")
for s, want in [([5, 90, 12, 77, 40], [90, 77, 40]), ([1, 2], [2, 1]), ([8, 8, 3, 9], [9, 8, 8])]:
    v, _ = capture(f, list(s))
    expect(v == want, f"top_three({s}) should return {want}, but it returned {v!r}.")
SUCCESS = "🥇🥈🥉 Podium ready!"
''',
        "xp": 20,
    },
    {
        "id": "p_functions_w6_1",
        "concept": "functions",
        "title": "Stat Bar",
        "difficulty": 1,
        "task": """<p>Write <code>def bar(value, maximum):</code> that returns a bar made of <code>#</code> for the value
and <code>-</code> for the rest. <code>bar(3, 10)</code> → <code>"###-------"</code>. Great for pet stats!</p>""",
        "starter": r'''def bar(value, maximum):
    # TODO: return value '#' characters, then (maximum - value) '-' characters
    return ""

print(bar(3, 10))
''',
        "hints": [
            "\"#\" * 3 makes \"###\".",
            "The dashes are \"-\" * (maximum - value).",
            "return \"#\" * value + \"-\" * (maximum - value)",
        ],
        "solution": r'''def bar(value, maximum):
    return "#" * value + "-" * (maximum - value)

print(bar(3, 10))
''',
        "check": r'''
r = run()
f = r.fn("bar")
for v, m in [(3, 10), (0, 5), (5, 5), (7, 8)]:
    got, _ = capture(f, v, m)
    want = "#" * v + "-" * (m - v)
    expect(got == want, f"bar({v}, {m}) should return {want!r}, but it returned {got!r}.")
SUCCESS = "📊 ####------ Looking good!"
''',
        "xp": 15,
    },
]
