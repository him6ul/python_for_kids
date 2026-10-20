"""Daily progress emails: one summary per learner per active day, sent to a configurable list of parents.

Recipients, on/off and the send time are edited in Parent Zone → Settings (stored in the `settings` table).
SMTP credentials are secrets, so they only come from environment variables:

    PYQUEST_SMTP_HOST      e.g. smtp.gmail.com
    PYQUEST_SMTP_PORT      587 (STARTTLS, default) or 465 (SSL)
    PYQUEST_SMTP_USER      the account to log in as
    PYQUEST_SMTP_PASSWORD  for Gmail, an App Password (not your normal password)
    PYQUEST_SMTP_FROM      optional "From" address (defaults to PYQUEST_SMTP_USER)

Without them, reports are written to data/outbox/*.eml instead of being sent, so nothing is lost.
"""
import datetime as dt
import html
import json
import os
import re
import smtplib
import ssl
import threading
import time
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid

from . import analytics, db, gamification
from . import observability as obs
from .curriculum import BY_ID, PRACTICE_BY_ID, PROJECTS

DEFAULTS = {"enabled": True, "recipients": ["him6ul@gmail.com"], "send_time": "20:30"}
OUTBOX = os.path.join(os.path.dirname(db.DB_PATH), "outbox")
EMAIL_RE = re.compile(r"^[^@\s,;<>]+@[^@\s,;<>]+\.[^@\s,;<>]+$")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS email_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL, learner_id INTEGER, day TEXT, kind TEXT,
    recipients TEXT, subject TEXT, status TEXT, error TEXT, message_id TEXT
);
CREATE INDEX IF NOT EXISTS ix_email_ld ON email_log(learner_id, day);
"""


def init():
    with db.tx() as c:
        c.executescript(SCHEMA_SQL)
    if "email_log" not in db.TABLES:
        db.TABLES.append("email_log")


# ---------------------------------------------------------------------------
# settings
# ---------------------------------------------------------------------------
def settings():
    s = dict(DEFAULTS)
    s.update(db.get_setting("email", {}) or {})
    return s


def parse_recipients(value):
    """Accepts a list or a string separated by commas, semicolons, spaces or new lines."""
    items = value if isinstance(value, list) else re.split(r"[,;\s]+", str(value or ""))
    out, bad = [], []
    for raw in items:
        e = raw.strip()
        if not e:
            continue
        (out if EMAIL_RE.match(e) else bad).append(e)
    seen = set()
    out = [e for e in out if not (e.lower() in seen or seen.add(e.lower()))]
    return out, bad


def save_settings(new):
    s = settings()
    if "enabled" in new:
        s["enabled"] = bool(new["enabled"])
    if "recipients" in new:
        good, bad = parse_recipients(new["recipients"])
        if bad:
            raise ValueError("These don't look like email addresses: " + ", ".join(bad))
        s["recipients"] = good
    if "send_time" in new:
        t = str(new["send_time"])
        if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", t):
            raise ValueError("Send time must look like 20:30")
        s["send_time"] = t
    db.set_setting("email", s)
    return s


def smtp_config():
    host = os.environ.get("PYQUEST_SMTP_HOST", "").strip()
    user = os.environ.get("PYQUEST_SMTP_USER", "").strip()
    return {
        "host": host,
        "port": int(os.environ.get("PYQUEST_SMTP_PORT", "587") or 587),
        "user": user,
        "password": os.environ.get("PYQUEST_SMTP_PASSWORD", ""),
        "from": os.environ.get("PYQUEST_SMTP_FROM", "").strip() or user,
        "configured": bool(host and os.environ.get("PYQUEST_SMTP_FROM", user)),
    }


def status():
    s = settings()
    c = smtp_config()
    return {
        **s,
        "smtp": {"configured": c["configured"], "host": c["host"], "port": c["port"], "user": c["user"], "from": c["from"]},
        "outbox": OUTBOX,
        "recent": db.q("""SELECT e.id, e.ts, e.day, e.kind, e.recipients, e.subject, e.status, e.error, l.name
                          FROM email_log e LEFT JOIN learners l ON l.id = e.learner_id ORDER BY e.ts DESC LIMIT 15"""),
    }


# ---------------------------------------------------------------------------
# the daily summary
# ---------------------------------------------------------------------------
def _bounds(day):
    start = dt.datetime.combine(day, dt.time()).timestamp()
    return start, start + 86400


def _step_title(project_id, step_id):
    if project_id == "_practice":
        pr = PRACTICE_BY_ID.get(step_id)
        return ("Side quest", pr["title"] if pr else step_id)
    p = BY_ID.get(project_id)
    if not p:
        return (project_id, step_id)
    for s in p["steps"] + ([p["boss"]] if p.get("boss") else []):
        if s["id"] == step_id:
            title = re.sub(r"^boss:\s*", "", s["title"], flags=re.I)
            return (p["title"], ("Boss: " if step_id == "boss" else "") + title)
    return (p["title"], step_id)


def day_summary(learner_id, day):
    a, b = _bounds(day)
    L, R = (learner_id, a, b), (learner_id, day.isoformat())
    passed = db.q("""SELECT project_id, step_id, attempts, hints_used, first_try, xp FROM step_progress
                     WHERE learner_id=? AND status='done' AND completed_at>=? AND completed_at<? ORDER BY completed_at""", L)
    for r in passed:
        r["project"], r["title"] = _step_title(r["project_id"], r["step_id"])
    runs = db.q("SELECT ok, error_type FROM runs WHERE learner_id=? AND ts>=? AND ts<?", L)
    fixed = db.q("""SELECT DISTINCT r.error_type FROM runs r WHERE r.learner_id=? AND r.ts>=? AND r.ts<? AND r.ok=0
                    AND r.error_type IS NOT NULL AND EXISTS (SELECT 1 FROM runs r2 WHERE r2.learner_id=r.learner_id
                    AND r2.project_id=r.project_id AND r2.step_id=r.step_id AND r2.ts>r.ts AND r2.ok=1)""", L)
    ideas = db.q("SELECT text, score, analysis FROM ideas WHERE learner_id=? AND ts>=? AND ts<? ORDER BY ts", L)
    for i in ideas:
        i["level"] = (json.loads(i.pop("analysis") or "{}")).get("level_name", "")
    badges = db.q("SELECT badge_id FROM badges WHERE learner_id=? AND earned_at>=? AND earned_at<?", L)
    statuses = analytics.project_status(learner_id)
    total = sum(p["steps_total"] for p in statuses)
    done = sum(p["steps_done"] for p in statuses)
    sched = analytics.schedule(learner_id, statuses)
    pos = analytics.current_position(learner_id, statuses)
    try:
        notes = analytics.guide(learner_id)["parent"][:2]
    except Exception:  # noqa: BLE001 - a coaching-note hiccup must never block the email
        notes = []
    xp_total = gamification.total_xp(learner_id)
    return {
        "day": day.isoformat(),
        "minutes": round(db.scalar("SELECT SUM(seconds) FROM time_log WHERE learner_id=? AND day=?", R) / 60),
        "sessions": db.scalar("SELECT COUNT(*) FROM learning_sessions WHERE learner_id=? AND started_at>=? AND started_at<?", L),
        "missions": [r for r in passed if r["project_id"] != "_practice"],
        "side_quests": [r for r in passed if r["project_id"] == "_practice"],
        "runs": len(runs), "crashes": sum(1 for r in runs if not r["ok"]),
        "bugs_fixed": [r["error_type"] for r in fixed],
        "checks": db.scalar("SELECT COUNT(*) FROM checks WHERE learner_id=? AND ts>=? AND ts<?", L),
        "hints": db.scalar("SELECT COUNT(*) FROM hints WHERE learner_id=? AND ts>=? AND ts<?", L),
        "tutor_questions": db.scalar("""SELECT COUNT(*) FROM tutor_messages WHERE learner_id=? AND ts>=? AND ts<?
                                        AND role='kid'""", L) if "tutor_messages" in db.TABLES else 0,
        "ideas": ideas,
        "remixes": db.scalar("SELECT COUNT(*) FROM remixes WHERE learner_id=? AND ts>=? AND ts<?", L),
        "xp_today": db.scalar("SELECT SUM(amount) FROM xp_log WHERE learner_id=? AND ts>=? AND ts<?", L),
        "badges": [{"id": x["badge_id"], "emoji": gamification.BADGES.get(x["badge_id"], ("", x["badge_id"], ""))[0],
                    "name": gamification.BADGES.get(x["badge_id"], ("", x["badge_id"], ""))[1]} for x in badges],
        "badges_earned": db.scalar("SELECT COUNT(*) FROM badges WHERE learner_id=?", (learner_id,)),
        "badges_total": len(gamification.BADGES),
        "level": gamification.level_for(xp_total),
        "streak": gamification.streak(learner_id)["current"],
        "overall": {"steps_done": done, "steps_total": total, "pct": round(done / total * 100) if total else 0,
                    "projects_done": sum(1 for p in statuses if p["complete"])},
        "schedule": sched["status"], "next": pos, "notes": notes,
    }


def active_quick(learner_id, day):
    """Cheap check used by the scheduler before building a full report."""
    a, b = _bounds(day)
    return bool(db.scalar("SELECT SUM(seconds) FROM time_log WHERE learner_id=? AND day=?", (learner_id, day.isoformat())) >= 60
                or db.scalar("SELECT COUNT(*) FROM runs WHERE learner_id=? AND ts>=? AND ts<?", (learner_id, a, b))
                or db.scalar("SELECT COUNT(*) FROM step_progress WHERE learner_id=? AND completed_at>=? AND completed_at<?",
                             (learner_id, a, b))
                or db.scalar("SELECT COUNT(*) FROM ideas WHERE learner_id=? AND ts>=? AND ts<?", (learner_id, a, b)))


def was_active(s):
    return s["minutes"] >= 1 or s["runs"] > 0 or bool(s["missions"]) or bool(s["side_quests"]) or bool(s["ideas"])


# ---------------------------------------------------------------------------
# rendering (plain text + simple inline-styled HTML that renders in Gmail)
# ---------------------------------------------------------------------------
def badge_bar(earned, total, cells=5):
    """A tiny text progress bar for the subject line, e.g. "▰▰▱▱▱ 9/23 badges"."""
    if not total:
        return ""
    filled = cells if earned >= total else int(earned / total * cells)   # only full when every badge is earned
    if earned and not filled:
        filled = 1                      # any badge at all shows as one filled cell
    return "▰" * filled + "▱" * (cells - filled) + f" {earned}/{total} badges"


def render(learner, s, app_url="http://127.0.0.1:8765"):
    day = dt.date.fromisoformat(s["day"])
    nice_day = f"{day:%A, %B} {day.day}"          # no %-d: it isn't supported on Windows
    n_m = len(s["missions"])
    headline = f"{n_m} mission{'s' if n_m != 1 else ''} · {s['minutes']} min"
    if s["side_quests"]:
        headline += f" · {len(s['side_quests'])} side quest{'s' if len(s['side_quests']) != 1 else ''}"
    subject = f"PyQuest · {learner['name']} · {day:%a %b} {day.day} — {headline} · {badge_bar(s['badges_earned'], s['badges_total'])}"
    lvl = s["level"]
    nxt = f"{s['next']['project_title']} — {s['next']['step_title']}" if s["next"] else "Quest complete 🎓"
    sched = {"ahead": "ahead of the 6-week plan", "on track": "on track with the 6-week plan",
             "behind": "a little behind the 6-week plan"}.get(s["schedule"], s["schedule"])

    # ---- plain text
    t = [f"{learner['name']}'s PyQuest day — {nice_day}", "",
         f"Coding time: {s['minutes']} min in {s['sessions']} session(s)",
         f"XP earned: +{s['xp_today']}   Level {lvl['level']} · {lvl['title']}   Streak: {s['streak']} day(s)", ""]
    if s["missions"]:
        t.append("Missions passed:")
        t += [f"  • {m['project']} — {m['title']}" + ("  (first try)" if m["first_try"] else f"  ({m['attempts']} tries)")
              for m in s["missions"]]
        t.append("")
    if s["side_quests"]:
        t.append("Side quests cleared: " + ", ".join(m["title"] for m in s["side_quests"]))
    if s["ideas"]:
        t.append("Ideas saved: " + "; ".join(f"“{i['text'][:80]}” ({i['level']})" for i in s["ideas"]))
    t += ["", f"Programs run: {s['runs']} · crashes: {s['crashes']} · bugs fixed: {len(s['bugs_fixed'])}",
          f"Checks: {s['checks']} · hints opened: {s['hints']} · questions to Pixel: {s['tutor_questions']}", "",
          f"Overall: {s['overall']['steps_done']}/{s['overall']['steps_total']} missions ({s['overall']['pct']}%), "
          f"{s['overall']['projects_done']}/12 projects — {sched}.",
          f"Up next: {nxt}",
          f"Badges: {s['badges_earned']} of {s['badges_total']} earned"
          + (" · new today: " + ", ".join(f"{b['emoji']} {b['name']}" for b in s["badges"]) if s["badges"] else "")]
    if s["notes"]:
        t += ["", "Coaching notes:"] + [f"  • {n['title']}: {n['text']}" for n in s["notes"]]
    t += ["", f"Open PyQuest: {app_url}", "", "— Sent by PyQuest. Change recipients in Parent Zone → Settings."]
    text = "\n".join(t)

    # ---- HTML
    e = html.escape
    def stat(v, label):
        return (f'<td style="padding:10px 12px;background:#f1f0ec;border-radius:8px;width:25%">'
                f'<div style="font-size:18px;font-weight:600;color:#2b2d31">{v}</div>'
                f'<div style="font-size:12px;color:#8b8e95">{label}</div></td>')
    rows = "".join(
        f'<tr><td style="padding:6px 0;border-top:1px solid #e6e4dd"><b style="font-weight:600">{e(m["title"])}</b>'
        f'<div style="font-size:12px;color:#8b8e95">{e(m["project"])} · {"first try" if m["first_try"] else str(m["attempts"]) + " tries"}'
        f'{" · " + str(m["hints_used"]) + " hint(s)" if m["hints_used"] else ""}</div></td>'
        f'<td style="padding:6px 0;border-top:1px solid #e6e4dd;text-align:right;color:#5d6169;font-size:13px">+{m["xp"]} XP</td></tr>'
        for m in s["missions"] + s["side_quests"])
    extras = []
    if s["ideas"]:
        extras.append("<b>Ideas saved:</b> " + "; ".join(e(f"“{i['text'][:90]}” ({i['level']})") for i in s["ideas"]))
    if s["remixes"]:
        extras.append(f"<b>Remixes:</b> {s['remixes']}")
    notes = "".join(f'<div style="border-left:3px solid #4f6fa8;padding:6px 10px;margin:6px 0;background:#f7f6f2">'
                    f'<b style="font-weight:600">{e(n["title"])}</b><div style="color:#5d6169;font-size:13px">{e(n["text"])}</div></div>'
                    for n in s["notes"])
    pct = s["overall"]["pct"]
    b_pct = round(s["badges_earned"] / s["badges_total"] * 100) if s["badges_total"] else 0
    chips = "".join(f'<span style="display:inline-block;margin:6px 6px 0 0;padding:3px 9px;border-radius:99px;background:#efeee9;'
                    f'border:1px solid #dcdad3;font-size:12px;color:#2b2d31">{e(b["emoji"])} {e(b["name"])}</span>' for b in s["badges"])
    badges_html = (f'<h3 style="font-size:14px;margin:16px 0 6px;font-weight:600">Badges</h3>'
                   f'<div style="background:#e6e4dd;border-radius:99px;height:8px;overflow:hidden"><div style="width:{max(b_pct, 2)}%;height:8px;background:#6f9c80"></div></div>'
                   f'<div style="font-size:13px;color:#5d6169;margin-top:6px">{s["badges_earned"]} of {s["badges_total"]} badges earned ({b_pct}%)'
                   f'{" · new today:" if s["badges"] else " · no new badges today"}</div>{chips}')
    body = f"""<!doctype html><html><body style="margin:0;background:#f4f3ef;font-family:-apple-system,Segoe UI,Inter,Arial,sans-serif;color:#2b2d31">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f3ef;padding:24px 12px"><tr><td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#fbfaf8;border:1px solid #dcdad3;border-radius:12px;padding:22px">
<tr><td>
  <div style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#8b8e95;font-weight:600">PyQuest daily report · {e(nice_day)}</div>
  <h1 style="margin:4px 0 4px;font-size:22px;font-weight:650">{e(learner.get('avatar') or '')} {e(learner['name'])}'s day</h1>
  <div style="color:#5d6169;font-size:14px">{e(headline)} · {e(sched)}</div>
  <table role="presentation" width="100%" cellspacing="6" style="margin:14px -6px 6px"><tr>
    {stat(f"{s['minutes']} min", "coding time")}{stat(f"+{s['xp_today']}", "XP earned")}
    {stat(f"Lv {lvl['level']}", e(lvl['title']))}{stat(f"{s['streak']} d", "streak")}</tr></table>
  {f'<h3 style="font-size:14px;margin:16px 0 4px;font-weight:600">Completed today</h3><table role="presentation" width="100%" cellspacing="0">{rows}</table>' if rows else '<p style="color:#5d6169;font-size:14px">No missions passed today — time spent practising still counts.</p>'}
  {''.join(f'<p style="font-size:13px;margin:6px 0;color:#2b2d31">{x}</p>' for x in extras)}
  <p style="font-size:13px;color:#5d6169;margin:12px 0 4px">Programs run: <b>{s['runs']}</b> · crashes: <b>{s['crashes']}</b> · bugs fixed: <b>{len(s['bugs_fixed'])}</b> · checks: <b>{s['checks']}</b> · hints: <b>{s['hints']}</b> · questions to Pixel: <b>{s['tutor_questions']}</b></p>
  <h3 style="font-size:14px;margin:16px 0 6px;font-weight:600">Overall progress</h3>
  <div style="background:#e6e4dd;border-radius:99px;height:8px;overflow:hidden"><div style="width:{max(pct, 2)}%;height:8px;background:#4f6fa8"></div></div>
  <div style="font-size:13px;color:#5d6169;margin-top:6px">{s['overall']['steps_done']} of {s['overall']['steps_total']} missions ({pct}%) · {s['overall']['projects_done']} of 12 projects · up next: {e(nxt)}</div>
  {badges_html}
  {f'<h3 style="font-size:14px;margin:16px 0 4px;font-weight:600">Coaching notes</h3>{notes}' if notes else ''}
  <p style="margin:18px 0 0"><a href="{e(app_url)}" style="display:inline-block;background:#4f6fa8;color:#fff;text-decoration:none;padding:8px 14px;border-radius:8px;font-size:14px">Open PyQuest</a></p>
  <p style="font-size:11px;color:#8b8e95;margin:16px 0 0">Sent by PyQuest on your home computer. Change who gets this in Parent Zone → Settings.</p>
</td></tr></table></td></tr></table></body></html>"""
    return subject, text, body


# ---------------------------------------------------------------------------
# sending
# ---------------------------------------------------------------------------
def _deliver(recipients, subject, text, html_body):
    """Returns (status, error, message_id). status: sent | saved | failed."""
    cfg = smtp_config()
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["To"] = ", ".join(recipients)
    msg["From"] = formataddr(("PyQuest", cfg["from"] or "pyquest@localhost"))
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="pyquest.local")
    msg.set_content(text)
    msg.add_alternative(html_body, subtype="html")
    if not cfg["configured"]:
        os.makedirs(OUTBOX, exist_ok=True)
        name = f"{dt.datetime.now():%Y%m%d-%H%M%S}-{re.sub(r'[^A-Za-z0-9]+', '-', subject)[:60]}.eml"
        with open(os.path.join(OUTBOX, name), "wb") as f:
            f.write(bytes(msg))
        return "saved", f"SMTP not configured — saved to {os.path.join(OUTBOX, name)}", msg["Message-ID"]
    try:
        ctx = ssl.create_default_context()
        if cfg["port"] == 465:
            server = smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=ctx, timeout=30)
        else:
            server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=30)
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()
        with server:
            if cfg["user"] and cfg["password"]:
                server.login(cfg["user"], cfg["password"])
            server.send_message(msg)
        return "sent", None, msg["Message-ID"]
    except smtplib.SMTPAuthenticationError:
        return "failed", "The mail server rejected the login. For Gmail, use an App Password.", None
    except (smtplib.SMTPException, OSError) as e:
        return "failed", f"{type(e).__name__}: {e}", None


def _log(learner_id, day, kind, recipients, subject, status, error, mid):
    db.ex("""INSERT INTO email_log(ts, learner_id, day, kind, recipients, subject, status, error, message_id)
             VALUES(?,?,?,?,?,?,?,?,?)""", (time.time(), learner_id, day, kind, ", ".join(recipients), subject, status, error, mid))
    obs.record(f"email.{status}")
    obs.audit("system", f"email.{status}", "learner" if learner_id else None, learner_id,
              {"kind": kind, "day": day, "to": recipients, "error": error})


def already_sent(learner_id, day):
    return bool(db.scalar("""SELECT COUNT(*) FROM email_log WHERE learner_id=? AND day=? AND kind='daily'
                             AND status IN ('sent','saved')""", (learner_id, day)))


_send_lock = threading.Lock()


def send_daily(learner_id, day=None, force=False, recipients=None, kind="daily"):
    """Build and send one learner's report for one day. Skips if already sent unless force."""
    day = day or dt.date.today()
    learner = db.one("SELECT * FROM learners WHERE id=?", (learner_id,))
    if not learner:
        return {"status": "skipped", "error": "No such learner"}
    s = settings()
    to = recipients or s["recipients"]
    if not to:
        return {"status": "skipped", "error": "No recipients configured"}
    with _send_lock:
        if not force and already_sent(learner_id, day.isoformat()):
            return {"status": "skipped", "error": "Already sent for this day"}
        if not force and not active_quick(learner_id, day):
            return {"status": "skipped", "error": "No activity that day"}
        summary = day_summary(learner_id, day)
        if not force and not was_active(summary):
            return {"status": "skipped", "error": "No activity that day"}
        subject, text, body = render(learner, summary)
        status_, error, mid = _deliver(to, subject, text, body)
        _log(learner_id, day.isoformat(), kind, to, subject, status_, error, mid)
    return {"status": status_, "error": error, "subject": subject, "to": to}


def send_test(recipients=None):
    s = settings()
    to = recipients or s["recipients"]
    if not to:
        return {"status": "skipped", "error": "No recipients configured"}
    subject = "PyQuest · test email"
    text = "This is a test from PyQuest. Daily progress reports will arrive at this address."
    body = ('<div style="font-family:-apple-system,Segoe UI,Arial,sans-serif;color:#2b2d31">'
            "<p>This is a test from <b>PyQuest</b>.</p><p>Daily progress reports will arrive at this address.</p></div>")
    status_, error, mid = _deliver(to, subject, text, body)
    _log(None, dt.date.today().isoformat(), "test", to, subject, status_, error, mid)
    return {"status": status_, "error": error, "to": to}


# ---------------------------------------------------------------------------
# scheduler: once a minute, send any due reports (today's after send_time, and yesterday's if it was missed)
# ---------------------------------------------------------------------------
def tick(now=None):
    s = settings()
    if not s["enabled"] or not s["recipients"]:
        return []
    now = now or dt.datetime.now()
    hh, mm = map(int, s["send_time"].split(":"))
    due_days = [now.date() - dt.timedelta(days=1)]
    if (now.hour, now.minute) >= (hh, mm):
        due_days.append(now.date())
    results = []
    for learner in db.q("SELECT id FROM learners"):
        for day in due_days:
            if already_sent(learner["id"], day.isoformat()):
                continue
            r = send_daily(learner["id"], day)
            if r["status"] != "skipped":
                results.append((learner["id"], day.isoformat(), r["status"]))
    return results


_stop = threading.Event()


def start_scheduler():
    if os.environ.get("PYQUEST_NO_EMAIL_SCHEDULER"):
        return

    def loop():
        _stop.wait(15)          # let the server finish starting
        while not _stop.is_set():
            try:
                tick()
            except Exception as e:  # noqa: BLE001 - keep the scheduler alive, but record the problem
                obs.app_error("email.scheduler", e)
            _stop.wait(60)

    threading.Thread(target=loop, name="pyquest-email", daemon=True).start()


def stop_scheduler():
    _stop.set()
