# Curriculum content spec

The learner is an 8th grader (~13 years old) who has never programmed. The program is
6 weeks, 2 projects per week, each project a small fun thing he *builds*. Concepts are
learned *because the project needs them*. Tone: warm, playful, a bit goofy, never
condescending, short sentences. Emoji welcome but not in every line. Assume he does
~45–60 minutes per session, 3–4 sessions per week.

Each week lives in `app/curriculum/weekN.py` and defines two module-level lists:
`PROJECTS` and `PRACTICE`.

## Project

```python
{
    "id": "robot_buddy",            # snake_case, globally unique
    "week": 1,
    "order": 1,                     # 1..12 across the whole program
    "title": "Robot Buddy",
    "emoji": "🤖",
    "tagline": "Build a chatbot that greets you by name",   # one line
    "story": "…2–4 sentences that set up the mission…",
    "concepts": ["output", "variables", "input"],           # concepts this project TEACHES
    "expected_minutes": 90,         # realistic total for core steps
    "steps": [ STEP, ... ],         # 4–6 core steps, each building the SAME program further
    "boss": STEP,                   # one harder optional stretch challenge (bigger xp)
    "remix": {
        "prompt": "Make it yours! …",                        # open-ended invitation
        "ideas": ["idea 1", "idea 2", "idea 3", "idea 4"],   # sparks, easy → ambitious
    },
}
```

## Step (also used for `boss`)

```python
{
    "id": "s1",                     # unique within the project ("boss" for the boss)
    "title": "Say hello",
    "learn": "HTML string. The mini-lesson: 2–5 short paragraphs, may use <p>, <code>, <pre>, <b>, <ul><li>. "
             "Show a tiny example in <pre>. Explain WHY, with an analogy.",
    "task": "HTML string. Exactly what to do in this step. Concrete, e.g. 'Make your robot print …'",
    "starter": "python code the editor starts with for this step (carry forward the previous step's program "
               "plus a TODO comment for the new part). Must NOT already pass the check.",
    "hints": ["gentle nudge", "more specific", "nearly the answer (a code line)"],   # exactly 3
    "solution": "a complete, working program that passes the check (kept for validation, shown to parents)",
    "check": "python snippet, see below",
    "concepts": ["output"],         # concepts exercised in this step (subset of the 16 ids)
    "xp": 20,                        # 10–40 for steps, 60–100 for boss
}
```

The learner's code carries forward: when he passes step N, step N+1's editor opens with HIS
code (the `starter` is only used if he has no code yet), so each step's task must make
sense as "add/modify something in the program you already have". Keep starters consistent
with the previous step's solution.

## Concept ids (use only these)

`output, variables, input, strings, fstrings, math, types, conditions, random,
while_loops, for_loops, turtle, lists, functions, dicts, classes`

Suggested arc (each project may reuse earlier concepts):

| Week | Projects | New concepts |
|---|---|---|
| 1 | 1 Robot Buddy (chatbot greeter) · 2 Pizza Party Planner (calculator) | output, variables, input, strings, fstrings, math, types |
| 2 | 3 Magic 8-Ball / Fortune Teller · 4 Guess My Number | conditions, random, while_loops |
| 3 | 5 Turtle Art Studio · 6 Math Quiz Blaster | for_loops, turtle (+ loops+conditions+score) |
| 4 | 7 Hangman · 8 Secret Agent Code Machine (Caesar cipher / password gen) | lists, functions |
| 5 | 9 Monster Collector (Pokédex-like) · 10 Escape the Castle (text adventure) | dicts (+ functions, game loop) |
| 6 | 11 Virtual Pet · 12 Capstone: Your Own Game | classes, planning, putting it all together |

## Check snippets

A check is Python code executed in a sandbox after the learner's code is available. It
passes if it finishes without raising. Fail with `expect(cond, "friendly message")`. The
FIRST failing message is shown to the kid, so write it as a helpful coach: say what you
expected and what you saw, never just "wrong". Optionally set `SUCCESS = "…"` to a
celebration line.

Available names:

- `source` – learner code (str); `tree` – its `ast` tree
- `run(inputs=None, seed=None, allow_error=False)` → `Result`. Runs the whole program
  fresh. `inputs` is a list fed to `input()` in order (running out raises a friendly
  failure, so loops that never end are caught). `random` is seeded (default 12345) so
  runs are repeatable; pass different seeds to try several. `time.sleep` is a no-op.
  If the program crashes, `run` fails the check with a friendly message unless
  `allow_error=True`.
- `Result`: `.output` (everything printed, including input prompts and echoed answers),
  `.lines` (non-blank output lines), `.has(text)` (case/whitespace-insensitive contains),
  `.ns` (the program's globals), `.var(name)`, `.fn(name)`, `.cls(name)` (fail kindly if
  missing), `.prompts` (input prompts), `.inputs_used`, `.error`, `.turtle` — a dict:
  `{"lines", "fills", "dots", "writes", "colors", "distance", "turtles", "bg", "events"}`.
- `expect(cond, msg)`, `raise CheckFail(msg)`
- `uses(concept)` – static detection (e.g. `uses("for_loops")`, `uses("fstrings")`)
- `calls(name)` – number of calls to a function/method name in the code (e.g. `calls("print")`)
- `defines(name)`, `imports(module)`
- `capture(fn, *args, inputs=None)` → `(return_value, printed_text)` — call one of the
  learner's functions safely, e.g. `v, out = capture(r.fn("shift"), "abc", 1)`
- `norm(text)` lower-case & collapse spaces

Rules for good checks:

- Be **lenient about wording/format**, strict about the idea. Prefer `r.has(name)` over exact
  string equality. Kids customize text — that's the point.
- Test with 2+ different inputs when behavior depends on input so hard-coding doesn't pass.
- For random programs, run with several seeds, or check structure (`imports("random")`,
  `calls("choice")`) plus behavior that must hold for every seed.
- The starter must FAIL the check and the solution must PASS it.
- Never require things the task didn't ask for.
- Turtle: the canvas is ~800×600 centered at (0,0). `turtle` is a shim — drawing only;
  `onkey`/`onclick` games are not supported, don't use them. `turtle.done()` is fine.
- No file I/O, no network, no third-party packages. Standard library only.

## PRACTICE (per week, ~2 per new concept, 6–10 items per week)

Small standalone warm-up challenges used by the adaptive guide when a concept is weak.

```python
{
    "id": "p_conditions_1",          # globally unique, prefix p_
    "concept": "conditions",
    "title": "Hot or Cold?",
    "difficulty": 1,                 # 1 easy, 2 medium, 3 tricky
    "task": "HTML: what to build (self-contained, 3–10 lines of code expected)",
    "starter": "python",
    "hints": ["…", "…", "…"],
    "solution": "python",
    "check": "python (same API)",
    "xp": 15,
}
```

## Validate

`python tools/validate_curriculum.py` runs every solution (must pass) and every starter
(must fail) through the real checker. Keep going until it reports zero problems.
