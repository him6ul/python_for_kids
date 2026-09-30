"""XP, levels, streaks and badges."""
import datetime as dt

from . import db

LEVEL_TITLES = ["Code Cadet", "Print Pilot", "Variable Voyager", "Loop Ranger", "Bug Squasher",
                "Function Forger", "List Wrangler", "Dictionary Druid", "Class Commander",
                "Python Knight", "Code Wizard", "Grand Pythonista"]


def level_for(xp):
    """Level n needs 50*n*(n+1) XP in total (100, 300, 600, 1000, ...)."""
    n = 0
    while xp >= 50 * (n + 1) * (n + 2):
        n += 1
    lo, hi = 50 * n * (n + 1), 50 * (n + 1) * (n + 2)
    return {"level": n + 1, "title": LEVEL_TITLES[min(n, len(LEVEL_TITLES) - 1)],
            "xp": xp, "into": xp - lo, "needed": hi - lo}


def total_xp(learner_id):
    return db.scalar("SELECT SUM(amount) FROM xp_log WHERE learner_id=?", (learner_id,))


def award_xp(learner_id, amount, reason):
    if amount:
        db.ex("INSERT INTO xp_log(learner_id, ts, amount, reason) VALUES(?,?,?,?)",
              (learner_id, db.now(), int(amount), reason))
    return amount


def active_days(learner_id):
    rows = db.q("SELECT day, SUM(seconds) s FROM time_log WHERE learner_id=? GROUP BY day HAVING s >= 60 ORDER BY day",
                (learner_id,))
    return [r["day"] for r in rows]


def streak(learner_id):
    days = set(active_days(learner_id))
    today = dt.date.today()
    d = today if today.isoformat() in days else today - dt.timedelta(days=1)
    n = 0
    while d.isoformat() in days:
        n += 1
        d -= dt.timedelta(days=1)
    best, cur, prev = 0, 0, None
    for day in sorted(days):
        x = dt.date.fromisoformat(day)
        cur = cur + 1 if prev and (x - prev).days == 1 else 1
        best = max(best, cur)
        prev = x
    return {"current": n, "best": best}


BADGES = {
    "first_run": ("🚀", "Liftoff", "Ran your very first program"),
    "first_step": ("👣", "First Steps", "Completed your first mission step"),
    "first_project": ("🏆", "Project Pro", "Finished a whole project"),
    "bug_hunter": ("🔍", "Bug Hunter", "Defeated 5 different kinds of bugs"),
    "bug_slayer": ("⚔️", "Bug Slayer", "Fixed 25 crashing programs"),
    "persistent": ("💪", "Never Give Up", "Passed a step after 5+ tries"),
    "no_hints": ("🧠", "Solo Genius", "Finished a project without any hints"),
    "speedy": ("⚡", "Speed Coder", "Finished a project faster than expected"),
    "artist": ("🎨", "Turtle Artist", "Drew 500+ lines with turtle in one run"),
    "remixer": ("🎛️", "Remix Master", "Remixed 3 projects your own way"),
    "big_thinker": ("💡", "Big Thinker", "Had an idea rated Architect or higher"),
    "explorer": ("🧭", "Explorer", "Ran 10 experiments in the Playground"),
    "practice_pro": ("🥋", "Practice Pro", "Cleared 10 practice side-quests"),
    "boss_1": ("👾", "Boss Beater", "Beat your first boss challenge"),
    "boss_5": ("🐲", "Boss Crusher", "Beat 5 boss challenges"),
    "streak_3": ("🔥", "On Fire", "Coded 3 days in a row"),
    "streak_7": ("🌋", "Unstoppable", "Coded 7 days in a row"),
    "week_1": ("1️⃣", "Week 1 Done", "Finished week 1"),
    "week_2": ("2️⃣", "Week 2 Done", "Finished week 2"),
    "week_3": ("3️⃣", "Week 3 Done", "Finished week 3"),
    "week_4": ("4️⃣", "Week 4 Done", "Finished week 4"),
    "week_5": ("5️⃣", "Week 5 Done", "Finished week 5"),
    "week_6": ("🎓", "Graduate", "Finished the whole 6-week quest!"),
}


def badge_list(learner_id):
    earned = {r["badge_id"]: r["earned_at"] for r in db.q("SELECT * FROM badges WHERE learner_id=?", (learner_id,))}
    return [{"id": k, "emoji": v[0], "name": v[1], "desc": v[2], "earned_at": earned.get(k)} for k, v in BADGES.items()]


def evaluate_badges(learner_id, projects, extra=None):
    """Grant any newly earned badges. Returns list of new badge dicts."""
    extra = extra or {}
    have = {r["badge_id"] for r in db.q("SELECT badge_id FROM badges WHERE learner_id=?", (learner_id,))}
    L = (learner_id,)
    done = {(r["project_id"], r["step_id"]): r for r in
            db.q("SELECT * FROM step_progress WHERE learner_id=? AND status='done'", L)}
    finished = []
    for p in projects:
        core = [s["id"] for s in p["steps"]]
        if all((p["id"], s) in done for s in core):
            finished.append(p)
    earned = set()
    if db.scalar("SELECT COUNT(*) FROM runs WHERE learner_id=?", L):
        earned.add("first_run")
    if any(k[0] != "_practice" for k in done):
        earned.add("first_step")
    if finished:
        earned.add("first_project")
    fixed_types = db.q("""SELECT DISTINCT r.error_type FROM runs r WHERE r.learner_id=? AND r.ok=0 AND r.error_type IS NOT NULL
                          AND EXISTS (SELECT 1 FROM runs r2 WHERE r2.learner_id=r.learner_id AND r2.project_id=r.project_id
                                      AND r2.step_id=r.step_id AND r2.ts>r.ts AND r2.ok=1)""", L)
    if len(fixed_types) >= 5:
        earned.add("bug_hunter")
    if db.scalar("SELECT COUNT(*) FROM runs WHERE learner_id=? AND ok=0", L) >= 25 and fixed_types:
        earned.add("bug_slayer")
    if any(r["attempts"] >= 5 for r in done.values()):
        earned.add("persistent")
    for p in finished:
        rows = [done[(p["id"], s["id"])] for s in p["steps"]]
        if sum(r["hints_used"] for r in rows) == 0:
            earned.add("no_hints")
        secs = sum(r["seconds"] for r in rows)
        if 0 < secs < p["expected_minutes"] * 60 * 0.8:
            earned.add("speedy")
    if extra.get("turtle_lines", 0) >= 500:
        earned.add("artist")
    if db.scalar("SELECT COUNT(DISTINCT project_id) FROM remixes WHERE learner_id=?", L) >= 3:
        earned.add("remixer")
    if db.scalar("SELECT MAX(level) FROM ideas WHERE learner_id=?", L) >= 4:
        earned.add("big_thinker")
    if db.scalar("SELECT COUNT(*) FROM runs WHERE learner_id=? AND mode='playground'", L) >= 10:
        earned.add("explorer")
    if db.scalar("SELECT COUNT(*) FROM step_progress WHERE learner_id=? AND project_id='_practice' AND status='done'", L) >= 10:
        earned.add("practice_pro")
    bosses = sum(1 for k in done if k[1] == "boss")
    if bosses >= 1:
        earned.add("boss_1")
    if bosses >= 5:
        earned.add("boss_5")
    st = streak(learner_id)["best"]
    if st >= 3:
        earned.add("streak_3")
    if st >= 7:
        earned.add("streak_7")
    finished_ids = {p["id"] for p in finished}
    for w in range(1, 7):
        wk = [p for p in projects if p["week"] == w]
        if wk and all(p["id"] in finished_ids for p in wk):
            earned.add(f"week_{w}")
    new = []
    for b in sorted(earned - have):
        db.ex("INSERT OR IGNORE INTO badges(learner_id, badge_id, earned_at) VALUES(?,?,?)", (learner_id, b, db.now()))
        e, n, d = BADGES[b]
        new.append({"id": b, "emoji": e, "name": n, "desc": d})
        award_xp(learner_id, 25, f"badge:{b}")
    return new
