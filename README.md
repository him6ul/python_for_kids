# 🐍 PyQuest — a 6-week, project-based Python adventure

PyQuest teaches Python to a middle schooler (built for an 8th grader) by having him **build 12 fun
projects**. Each concept is introduced right when a project needs it. Everything runs locally on your
computer (except the optional AI tutor, which calls the Claude API): a Python server plus a browser UI with a code editor, a live console, and a turtle-graphics
canvas. It also tracks progress, time and learning patterns, and gives a personalised guide for him and for you.

## Run it

```bash
./run.sh
```

Then open **http://127.0.0.1:8765**. On first run the script creates a `.venv` and installs FastAPI + Uvicorn.
All data is kept in `data/pyquest.db` (SQLite). Nothing leaves your machine except loading fonts and JS
libraries from public CDNs.

The Parent Zone is behind a PIN you choose the first time you open it (👪 icon, top right).

## The 6-week program

| Week | Projects (each 5–6 missions + a boss + a remix) | Concepts learned |
|---|---|---|
| 1 · Talking to computers | 🤖 **Robot Buddy**: a chatbot that greets and roasts you · 🍕 **Pizza Party Planner**: splits slices and the bill | print, variables, input, strings, f-strings, math, `//` `%`, int/float |
| 2 · Decisions & chance | 🎱 **Magic 8-Ball** · 🔢 **Guess My Number** | if/elif/else, comparisons, `random`, while loops, break |
| 3 · Loops & art | 🐢 **Turtle Art Studio**: polygons → spirographs · 🚀 **Math Quiz Blaster** | for loops, `range`, nested loops, turtle graphics, scoring |
| 4 · Lists & functions | 🎩 **Hangman** · 🕵️ **Secret Agent Code Machine**: Caesar cipher and password generator | lists, indexing, `in`, functions, parameters, return |
| 5 · Dictionaries & worlds | 👾 **Monster Collector**: stats and battles · 🏰 **Escape the Castle**: text adventure | dicts, dict-of-dicts, `.items()` `.get()`, game loops |
| 6 · Objects & your own game | 🐣 **Virtual Pet** · 🏆 **Capstone: Your Own Game**: he plans it and builds it | classes, methods, inheritance, planning, combining everything |

Every project follows the same loop:

1. **Missions.** Each has a short lesson with an analogy and an example, a task, and 3 hints of increasing detail. His code carries forward from one mission to the next, so he keeps growing *one* program.
2. **Automated checks** ("✔ Check my code"). They're lenient about wording (it's *his* robot) but strict about the idea. Programs that depend on input or randomness are tested with several inputs or seeds, so hard-coded answers don't pass.
3. **Boss challenge.** Harder and optional, for big XP.
4. **Remix Lab.** He writes an idea into the idea-o-meter, builds his own twist, and gets XP scaled by how much more complex it is than the original.
5. **Reflection.** He rates how fun and how hard the project was. This feeds the guide.

There are also **46 side quests**: small practice challenges per concept that the guide recommends when a
skill needs reinforcement. The **Playground** is a free-coding space where anything he writes counts as
"independent use" of a concept.

## What makes it fun

- 4 worlds (Space, Jungle, Ocean, Lava), 16 avatars, sound effects, and confetti.
- XP, 12 levels (Code Cadet → Grand Pythonista), 23 badges, and daily streaks.
- The **Bug Bestiary**: each error type is a monster (Syntax Slime 🟢, Name Gremlin 👺, Type Troll 🧌…). Crashes show a friendly, specific explanation, such as *"Python doesn't know 'nme'. Did you mean 'name'?"*, and highlight the line. Fixing one "defeats" the monster.
- Real `input()` right in the console, and turtle drawings animated on a canvas that he can save as PNG.
- An **idea journal** that rates ideas from ⚡ Spark to 🧠 Mastermind and points out concepts he'll need that he hasn't learned yet.

## 🤖 Pixel, the AI tutor (optional)

Pixel is an AI tutor built on the Claude API (`claude-opus-5-5`). It lives in a chat drawer in every mission, side quest, the Playground and the Remix Lab.

- **🤖 Ask Pixel.** Chat, plus one-tap questions: *I'm stuck*, *Why doesn't it work?*, *Explain the lesson*, *Make it cooler*. It replies with Socratic clues, never the solution. Replies use only concepts he has already learned, and Pixel can see the lesson, the task, his code with line numbers, his last output and error, and the last failed check.
- **🔍 Review.** A code review with 1–3 stars, a specific compliment, up to 4 tips tied to line numbers (highlighted in the editor), and a stretch challenge.
- **"Ask Pixel about this bug".** Appears on every crash card. "Ask Pixel why" appears after 2 failed checks.

Pixel has guardrails:
- It stays on topic.
- It never asks for personal information.
- It ignores "give me the answer" tricks hidden in code.
- If he writes about feeling unsafe, bullying or similar, it tells him to talk to a trusted adult and flags the message for you.

**Setup (parent):**

1. Get an API key at console.anthropic.com.
2. Start the app with the key:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-... ./run.sh
   ```
3. In **Parent Zone → AI Tutor**, turn it on, set a daily question limit (default 30), and press **Test connection**.

It is **off by default**. When on, his questions, code and program output are sent to Anthropic's API; his name is not sent.

**What you can see:**
- **AI Tutor tab.** Every conversation, tokens and estimated cost, reply times, question types, which concepts he asks about most, the mood read from his messages, and flagged messages.
- **Coaching guide.** Tutor usage feeds the learning analytics. Independence counts tutor questions, a concept he keeps asking about is marked as needing reinforcement, and coaching notes cover frustration, heavy tutor use, and flagged messages.
- **Monitoring and audit log.** Tutor latency, tokens, errors and declined requests, plus audit entries for every chat, review and settings change.

**Demo mode:** run `PYQUEST_TUTOR_FAKE=1 ./run.sh` to try the UI with canned replies (no key, no cost).

## What gets tracked & analysed

| Signal | How |
|---|---|
| **Time on each project / step** | Active time only: the tab is visible and he did something in the last 90s. Sent as heartbeats and grouped into sessions. Compared with each project's expected time. |
| **Progress & pace** | Missions done vs. the 6-week plan (measured from the start date). Shows ahead / on track / behind and a projected finish date. |
| **Concept mastery** (16 skills) | Missions completed, quality of each pass (attempts, hints, time), side quests, and *independent use* found by AST analysis of Playground and remix code. |
| **Learning style** | Precision (first-try passes), Independence (hints per step), Persistence (recovering after a failed check), Experimenting (runs per check), Creativity (remixes, ideas, going beyond the reference solution), Speed. These map to a persona: Tinkerer, Planner, Inventor, Determined Climber, or All-Rounder. |
| **Idea complexity** | Each idea gets a 0–100 score from its features, concept breadth and ambition. Remix code complexity is measured against the original project. Both are shown as trends. |
| **Code growth** | Every run and check keeps a snapshot with lines, cyclomatic complexity and concepts. Parents can scrub through every version of a mission next to the reference solution. |
| **Errors** | By type, per week, and recent; which ones he learned to fix; how long fixes take. |
| **Enjoyment** | Fun and difficulty ratings per project. Low fun triggers coaching suggestions. |

The **adaptive guide** turns all of this into next steps:

- **For him:** continue, a side quest for a weak skill, the boss when he's cruising, a remix, focus mode when behind schedule, a tip for a bug that keeps coming back, and idea boosters.
- **For you:** coaching notes, such as a concept that needs reinforcement, heavy hint use, a project he didn't enjoy, ideas running ahead of his skills, or inactivity. It also suggests conversation starters.

## Auditing, monitoring & data (Parent Zone)

- **Audit log.** An append-only record of every meaningful action (runs, checks, hints, answer peeks, ideas, remixes, reflections, sessions, parent logins including failed attempts, exports, deletions, server start/stop). Each entry has the actor, timestamp, IP and browser. It can be filtered and exported to CSV. There's also a per-learner **Activity timeline**.
- **Monitoring.**
  - Uptime and health (`/api/health`).
  - Request volume and per-endpoint latency (avg / p95 / max).
  - Program-runner and checker latency, and check pass rate.
  - Runaway programs stopped (time limit, output flood, check timeout).
  - Server exceptions with stack traces.
  - Database size, memory and disk.
  - Metrics are rolled up per minute into SQLite so there are history charts. The page auto-refreshes.
- **Data.** A catalog of every table (what it holds, row counts, first/last timestamps), plus:
  - a paginated table browser
  - CSV/JSON export per table
  - a full `.db` backup download
  - a data-collected-per-day chart and data-quality checks
  - a retention pruner for bulky telemetry
  - per-learner deletion, which is itself audited

## How it works

```
app/
  main.py            FastAPI: REST API, WebSocket runner, parent/admin endpoints, metrics middleware
  db.py              SQLite schema & helpers
  analytics.py       mastery, learning style, activity, errors, ideas, adaptive guide
  analysis.py        friendly error explanations, Bug Bestiary, idea-complexity scoring
  gamification.py    XP, levels, streaks, badges
  observability.py   audit log, metrics, error capture, monitoring & data catalog
  tutor.py           Pixel the AI tutor (Claude API): chat hints, code review, guardrails, usage analytics
  curriculum/        week1.py … week6.py  (projects, missions, checks, side quests) + CONTENT_SPEC.md
  sandbox/
    kidlive.py       runs a program in a subprocess, streams JSON (output, input requests, turtle events)
    kidcheck.py      automated-check harness (mocked input, seeded random, friendly failures)
    turtle.py        turtle stand-in that computes drawings for the browser canvas
    kidast.py        AST concept detection & complexity metrics
static/              index.html, css/style.css, js/ (app, kid, parent, workspace, turtle, core)
tools/validate_curriculum.py   proves every solution passes and every starter fails
```

Code runs as a separate local Python process with a timeout and an output cap. This is a family-computer
tool, not a hardened multi-user sandbox, so the server only listens on `127.0.0.1`.

### Editing the curriculum

Missions live in `app/curriculum/weekN.py` (format in `CONTENT_SPEC.md`). After editing, run:

```bash
.venv/bin/python tools/validate_curriculum.py
```

It currently checks all 121 missions and side quests: every reference solution passes and every starter fails.
