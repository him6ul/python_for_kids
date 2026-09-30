"""PyQuest server: a project-based Python course for kids with tracking & analytics."""
import asyncio
import csv
import datetime as dt
import hashlib
import io
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time

from fastapi import Body, Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import analysis, analytics, db, gamification, tutor
from . import observability as obs
from .curriculum import BY_ID, PRACTICE, PRACTICE_BY_ID, PROJECTS
from .curriculum import step as find_step
from .sandbox import kidast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANDBOX = os.path.join(ROOT, "app", "sandbox")
STATIC = os.path.join(ROOT, "static")
PY = sys.executable
RUN_LIMIT_SEC = 600          # interactive programs may wait on input for a while
CHECK_TIMEOUT_SEC = 10

app = FastAPI(title="PyQuest")
db.init()
tutor.init()
obs.audit("system", "server.start", details={"python": sys.version.split()[0], "pid": os.getpid()})


# ---------------------------------------------------------------------------
# middleware: metrics + error capture
# ---------------------------------------------------------------------------
@app.middleware("http")
async def metrics_mw(request: Request, call_next):
    t0 = time.perf_counter()
    route = request.url.path
    try:
        response = await call_next(request)
    except Exception as e:  # noqa: BLE001
        obs.app_error(f"{request.method} {route}", e)
        obs.record("http.status_5xx")
        return JSONResponse({"detail": "Something went wrong on the server. It has been logged."}, status_code=500)
    ms = (time.perf_counter() - t0) * 1000
    if route.startswith("/static/"):
        # always revalidate so a new version of the app shows up without a hard refresh
        response.headers["Cache-Control"] = "no-cache"
    if route.startswith("/api/"):
        # collapse ids so metrics group by endpoint
        parts = ["{id}" if p.isdigit() else p for p in route.split("/")]
        key = f"http.{request.method} {'/'.join(parts[:6])}"
        obs.record(key, ms)
        obs.record("http.all", ms)
        if response.status_code >= 500:
            obs.record("http.status_5xx")
        elif response.status_code >= 400:
            obs.record("http.status_4xx")
    return response


# ---------------------------------------------------------------------------
# parent auth (simple local PIN)
# ---------------------------------------------------------------------------
_parent_tokens = {}


def _hash_pin(pin, salt):
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), bytes.fromhex(salt), 200_000).hex()


def parent_required(request: Request):
    tok = request.cookies.get("pq_parent")
    exp = _parent_tokens.get(tok)
    if not exp or exp < time.time():
        raise HTTPException(401, "Parent PIN required")
    return True


@app.get("/api/parent/status")
def parent_status(request: Request):
    tok = request.cookies.get("pq_parent")
    return {"pin_set": bool(db.get_setting("parent_pin")), "logged_in": bool(_parent_tokens.get(tok, 0) > time.time())}


@app.post("/api/parent/login")
def parent_login(request: Request, body: dict = Body(...)):
    pin = str(body.get("pin", ""))
    stored = db.get_setting("parent_pin")
    if not stored:
        if len(pin) < 4:
            raise HTTPException(400, "Choose a PIN of at least 4 digits")
        salt = secrets.token_hex(16)
        db.set_setting("parent_pin", {"salt": salt, "hash": _hash_pin(pin, salt)})
        obs.audit("parent", "parent.pin_set", request=request)
    elif _hash_pin(pin, stored["salt"]) != stored["hash"]:
        obs.audit("unknown", "parent.login_failed", request=request)
        raise HTTPException(403, "Wrong PIN")
    tok = secrets.token_urlsafe(24)
    _parent_tokens[tok] = time.time() + 12 * 3600
    obs.audit("parent", "parent.login", request=request)
    resp = JSONResponse({"ok": True})
    resp.set_cookie("pq_parent", tok, httponly=True, samesite="strict", max_age=12 * 3600)
    return resp


@app.post("/api/parent/logout")
def parent_logout(request: Request):
    _parent_tokens.pop(request.cookies.get("pq_parent"), None)
    obs.audit("parent", "parent.logout", request=request)
    resp = JSONResponse({"ok": True})
    resp.delete_cookie("pq_parent")
    return resp


@app.post("/api/parent/pin")
def parent_change_pin(request: Request, body: dict = Body(...), _=Depends(parent_required)):
    pin = str(body.get("pin", ""))
    if len(pin) < 4:
        raise HTTPException(400, "PIN must be at least 4 digits")
    salt = secrets.token_hex(16)
    db.set_setting("parent_pin", {"salt": salt, "hash": _hash_pin(pin, salt)})
    obs.audit("parent", "parent.pin_changed", request=request)
    return {"ok": True}


# ---------------------------------------------------------------------------
# curriculum & learners
# ---------------------------------------------------------------------------
def _public_step(s):
    return {k: v for k, v in s.items() if k not in ("solution", "check", "hints")} | {"hint_count": len(s.get("hints", []))}


@app.get("/api/curriculum")
def curriculum():
    projects = []
    for p in PROJECTS:
        q = {k: v for k, v in p.items() if k not in ("steps", "boss")}
        q["steps"] = [_public_step(s) for s in p["steps"]]
        q["boss"] = _public_step(p["boss"]) if p.get("boss") else None
        projects.append(q)
    practice = [_public_step(pr) for pr in PRACTICE]
    return {"projects": projects, "practice": practice, "concepts": kidast.CONCEPT_LABELS,
            "bestiary": {k: analysis.monster(k) for k in analysis.BESTIARY}, "badges": gamification.BADGES}


def _learner(learner_id):
    row = db.one("SELECT * FROM learners WHERE id=?", (learner_id,))
    if not row:
        raise HTTPException(404, "No such learner")
    return row


@app.get("/api/learners")
def list_learners():
    rows = db.q("SELECT * FROM learners ORDER BY id")
    for r in rows:
        r["level"] = gamification.level_for(gamification.total_xp(r["id"]))
    return rows


@app.post("/api/learners")
def create_learner(request: Request, body: dict = Body(...)):
    name = str(body.get("name", "")).strip()[:40]
    if not name:
        raise HTTPException(400, "Name required")
    start = body.get("start_date") or dt.date.today().isoformat()
    lid = db.ex("INSERT INTO learners(name, avatar, theme, start_date, created_at) VALUES(?,?,?,?,?)",
                (name, body.get("avatar", "🦊"), body.get("theme", "space"), start, db.now()))
    obs.audit(f"learner:{lid}", "learner.create", "learner", lid, {"name": name, "start_date": start}, request)
    return _learner(lid)


@app.patch("/api/learners/{lid}")
def update_learner(lid: int, request: Request, body: dict = Body(...)):
    _learner(lid)
    allowed = {k: body[k] for k in ("name", "avatar", "theme", "sound", "start_date") if k in body}
    for k, v in allowed.items():
        db.ex(f"UPDATE learners SET {k}=? WHERE id=?", (v, lid))
    obs.audit(f"learner:{lid}", "learner.update", "learner", lid, allowed, request)
    return _learner(lid)


@app.get("/api/learners/{lid}/state")
def learner_state(lid: int):
    learner = _learner(lid)
    xp = gamification.total_xp(lid)
    prog = db.q("SELECT project_id, step_id, status, attempts, hints_used, seconds, xp FROM step_progress WHERE learner_id=?", (lid,))
    g = analytics.guide(lid)
    return {
        "learner": learner,
        "level": gamification.level_for(xp),
        "streak": gamification.streak(lid),
        "progress": prog,
        "projects": analytics.project_status(lid),
        "badges": gamification.badge_list(lid),
        "guide": {"kid": g["kid"], "path": g["path"], "position": g["position"], "schedule": g["schedule"]},
        "today_minutes": round(db.scalar("SELECT SUM(seconds) FROM time_log WHERE learner_id=? AND day=?",
                                         (lid, dt.date.today().isoformat())) / 60),
    }


@app.get("/api/learners/{lid}/journey")
def journey(lid: int):
    """Kid-friendly slice of the analytics."""
    _learner(lid)
    return {
        "mastery": analytics.concept_mastery(lid),
        "style": analytics.learning_style(lid),
        "activity": analytics.activity(lid, 28),
        "errors": analytics.errors(lid),
        "ideas": analytics.ideas(lid),
        "code_growth": analytics.code_growth(lid),
    }


# ---------------------------------------------------------------------------
# code: load / autosave
# ---------------------------------------------------------------------------
def _item(project_id, step_id):
    if project_id == "_practice":
        return PRACTICE_BY_ID.get(step_id)
    if project_id in BY_ID:
        if step_id == "remix":
            return None
        try:
            return find_step(project_id, step_id)
        except KeyError:
            return None
    return None


@app.get("/api/learners/{lid}/code")
def get_code(lid: int, project: str, step: str):
    require_unlocked(lid, project, step)
    row = db.one("SELECT code FROM code_saves WHERE learner_id=? AND project_id=? AND step_id=?", (lid, project, step))
    if row:
        return {"code": row["code"], "source": "saved"}
    if project in BY_ID:
        p = BY_ID[project]
        ids = [s["id"] for s in p["steps"]]
        if step == "remix" or step == "boss":
            prev = ids[-1]
        elif step in ids and ids.index(step) > 0:
            prev = ids[ids.index(step) - 1]
        else:
            prev = None
        if prev:
            r = db.one("""SELECT c.code FROM code_saves c JOIN step_progress s ON s.learner_id=c.learner_id
                          AND s.project_id=c.project_id AND s.step_id=c.step_id
                          WHERE c.learner_id=? AND c.project_id=? AND c.step_id=? AND s.status='done'""", (lid, project, prev))
            if r:
                title = "Remix it your way!" if step == "remix" else find_step(project, step)["title"]
                return {"code": r["code"].rstrip() + f"\n\n# 👉 New mission: {title} (see the mission card)\n",
                        "source": "carried"}
        if step == "remix":
            return {"code": find_step(project, ids[-1])["solution"], "source": "starter"}
    if project == "_playground":
        return {"code": "# 🧪 Playground — try anything here!\nprint(\"Hello from the playground!\")\n", "source": "starter"}
    it = _item(project, step)
    return {"code": it["starter"] if it else "", "source": "starter"}


@app.put("/api/learners/{lid}/code")
def save_code(lid: int, body: dict = Body(...)):
    code = str(body.get("code", ""))[:100_000]
    db.ex("""INSERT INTO code_saves(learner_id, project_id, step_id, code, updated_at) VALUES(?,?,?,?,?)
             ON CONFLICT(learner_id, project_id, step_id) DO UPDATE SET code=excluded.code, updated_at=excluded.updated_at""",
          (lid, body["project"], body["step"], code, db.now()))
    return {"ok": True}


@app.post("/api/learners/{lid}/code/reset")
def reset_code(lid: int, request: Request, body: dict = Body(...)):
    db.ex("DELETE FROM code_saves WHERE learner_id=? AND project_id=? AND step_id=?", (lid, body["project"], body["step"]))
    obs.audit(f"learner:{lid}", "code.reset", "step", f"{body['project']}/{body['step']}", request=request)
    it = _item(body["project"], body["step"])
    return {"code": it["starter"] if it else ""}


# ---------------------------------------------------------------------------
# progression: work unlocks strictly in order
# ---------------------------------------------------------------------------
def _concept_week():
    weeks = {}
    for p in PROJECTS:
        for c in p["concepts"]:
            weeks[c] = min(weeks.get(c, 99), p["week"])
    return weeks


CONCEPT_WEEK = _concept_week()


def locked_reason(lid, project, step):
    """None if the learner may open this step now, otherwise a friendly reason.

    Rules: projects unlock one after another (so weeks unlock in order); inside a project each
    mission needs all earlier missions done; the boss and the remix need every mission done;
    a side quest unlocks once the week that teaches its concept is reachable.
    """
    if project == "_playground":
        return None
    statuses = analytics.project_status(lid)
    if project == "_practice":
        pr = PRACTICE_BY_ID.get(step)
        if not pr:
            return "Unknown side quest."
        reachable = max([ps["week"] for ps in statuses if ps["unlocked"]], default=1)
        week = CONCEPT_WEEK.get(pr["concept"], 1)
        return None if week <= reachable else f"This side quest unlocks in week {week}."
    if project not in BY_ID:
        return "Unknown project."
    ps = next(x for x in statuses if x["id"] == project)
    if not ps["unlocked"]:
        return "This project is still locked. Finish the previous project first. 🔒"
    ids = [s["id"] for s in BY_ID[project]["steps"]]
    done = {r["step_id"] for r in db.q("""SELECT step_id FROM step_progress WHERE learner_id=? AND project_id=?
                                          AND status='done'""", (lid, project))}
    if step in ("boss", "remix"):
        missing = [i for i in ids if i not in done]
        return f"Finish all {len(ids)} missions first ({len(missing)} to go)." if missing else None
    if step in ids:
        for n, earlier in enumerate(ids[:ids.index(step)]):
            if earlier not in done:
                return f"Finish mission {n + 1} first. Missions unlock one at a time."
        return None
    return "Unknown mission."


def require_unlocked(lid, project, step):
    reason = locked_reason(lid, project, step)
    if reason:
        raise HTTPException(403, reason)


@app.get("/api/learners/{lid}/access")
def access(lid: int, project: str, step: str):
    reason = locked_reason(lid, project, step)
    return {"allowed": reason is None, "reason": reason}


def _ensure_progress(lid, project, step):
    db.ex("""INSERT OR IGNORE INTO step_progress(learner_id, project_id, step_id, status, started_at)
             VALUES(?,?,?,'started',?)""", (lid, project, step, db.now()))


def _snapshot(lid, project, step, kind, code):
    info = analysis.analyze_code(code)
    db.ex("""INSERT INTO snapshots(learner_id, project_id, step_id, ts, kind, code, lines, complexity, concepts)
             VALUES(?,?,?,?,?,?,?,?,?)""",
          (lid, project, step, db.now(), kind, code, info["metrics"]["lines"], info["complexity"], json.dumps(info["concepts"])))
    return info


# ---------------------------------------------------------------------------
# live runner over websocket
# ---------------------------------------------------------------------------
_active_runs = 0


@app.websocket("/ws/run")
async def ws_run(ws: WebSocket):
    global _active_runs
    await ws.accept()
    proc = None
    tmp = None
    try:
        msg = await ws.receive_json()
        if msg.get("type") != "run":
            await ws.close()
            return
        lid = int(msg["learner"])
        project, step, mode = msg.get("project", "_playground"), msg.get("step", "main"), msg.get("mode", "step")
        code = str(msg.get("code", ""))[:100_000]
        reason = locked_reason(lid, project, step if step != "main" else "main")
        if reason:
            await ws.send_json({"t": "err", "d": f"🔒 {reason}\n"})
            await ws.send_json({"t": "end", "ok": False, "reason": "locked"})
            obs.audit(f"learner:{lid}", "access.denied", "step", f"{project}/{step}", {"via": "run", "reason": reason})
            return
        tmp = tempfile.mkdtemp(prefix="pyquest_")
        with open(os.path.join(tmp, "main.py"), "w", encoding="utf-8") as f:
            f.write(code)
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": SANDBOX, "PYTHONIOENCODING": "utf-8",
               "PYTHONUNBUFFERED": "1", "HOME": tmp, "PYTHONDONTWRITEBYTECODE": "1"}
        t0 = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            PY, "-u", os.path.join(SANDBOX, "kidlive.py"), os.path.join(tmp, "main.py"),
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            cwd=tmp, env=env, limit=4 * 1024 * 1024)
        _active_runs += 1
        obs.gauge("runner.active", _active_runs)
        stats = {"out": 0, "inputs": 0, "turtle": 0, "error": None, "end": None, "turtle_lines": 0}

        async def pump_out():
            async for raw in proc.stdout:
                try:
                    m = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                t = m.get("t")
                if t == "out":
                    stats["out"] += len(m["d"])
                elif t == "input":
                    stats["inputs"] += 1
                elif t == "turtle":
                    stats["turtle"] += len(m["e"])
                    stats["turtle_lines"] += sum(1 for e in m["e"] if e.get("op") == "line")
                elif t == "error":
                    m["friendly"] = analysis.explain(m["type"], m.get("msg", ""), m.get("text", ""))
                    m["monster"] = analysis.monster(m["type"])
                    stats["error"] = m
                elif t == "end":
                    stats["end"] = m
                await ws.send_json(m)

        async def pump_err():
            async for raw in proc.stderr:
                await ws.send_json({"t": "err", "d": raw.decode("utf-8", "replace")})

        async def pump_in():
            while True:
                m = await ws.receive_json()
                if m.get("type") == "stdin" and proc.stdin:
                    proc.stdin.write((str(m.get("data", "")).replace("\n", " ") + "\n").encode())
                    await proc.stdin.drain()
                elif m.get("type") == "stop":
                    stats["stopped"] = True
                    proc.kill()
                    return

        out_task = asyncio.create_task(pump_out())
        err_task = asyncio.create_task(pump_err())
        in_task = asyncio.create_task(pump_in())
        try:
            await asyncio.wait_for(asyncio.gather(out_task, err_task, proc.wait()), timeout=RUN_LIMIT_SEC)
        except asyncio.TimeoutError:
            proc.kill()
            stats["killed"] = True
            obs.record("runner.killed")
            await ws.send_json({"t": "err", "d": "\n[Stopped after 10 minutes]\n"})
        in_task.cancel()
        dur = (time.perf_counter() - t0) * 1000
        obs.record("runner.duration_ms", dur)
        end = stats["end"] or {}
        reason = "stopped" if stats.get("stopped") else "timeout" if stats.get("killed") else end.get("reason", "done")
        if reason == "output_limit":
            obs.record("runner.output_limit")
        err = stats["error"]
        ok = bool(end.get("ok")) and not err
        if err:
            obs.record("runner.kid_error")
        if not stats["end"] and not stats.get("stopped"):
            await ws.send_json({"t": "end", "ok": False, "reason": reason})
        # --- tracking ---
        db.ex("""INSERT INTO runs(learner_id, project_id, step_id, mode, ts, duration_ms, ok, error_type, error_line, error_msg,
                 output_chars, inputs, turtle_events, end_reason) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (lid, project, step, mode, db.now(), int(dur), int(ok), err["type"] if err else None,
               err.get("line") if err else None, (err.get("msg") or "")[:300] if err else None,
               stats["out"], stats["inputs"], stats["turtle"], reason))
        if project not in ("_playground",):
            _ensure_progress(lid, project, step)
            db.ex("UPDATE step_progress SET runs=runs+1, errors=errors+? WHERE learner_id=? AND project_id=? AND step_id=?",
                  (1 if err else 0, lid, project, step))
        _snapshot(lid, project, step, mode if mode in ("playground", "remix") else "run", code)
        obs.audit(f"learner:{lid}", "code.run", "step", f"{project}/{step}",
                  {"mode": mode, "ok": ok, "error": err["type"] if err else None, "ms": int(dur), "reason": reason})
        new_badges = gamification.evaluate_badges(lid, PROJECTS, {"turtle_lines": stats["turtle_lines"]})
        if new_badges:
            await ws.send_json({"t": "badges", "badges": new_badges})
    except WebSocketDisconnect:
        if proc and proc.returncode is None:
            proc.kill()
    except Exception as e:  # noqa: BLE001
        obs.app_error("ws_run", e)
        if proc and proc.returncode is None:
            proc.kill()
    finally:
        if proc is not None:
            _active_runs = max(0, _active_runs - 1)
            obs.gauge("runner.active", _active_runs)
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
        try:
            await ws.close()
        except Exception:  # noqa: BLE001
            pass


# ---------------------------------------------------------------------------
# checks, hints
# ---------------------------------------------------------------------------
def run_check(source, check):
    t0 = time.perf_counter()
    try:
        p = subprocess.run([PY, os.path.join(SANDBOX, "kidcheck.py")],
                           input=json.dumps({"source": source, "check": check}), capture_output=True, text=True,
                           timeout=CHECK_TIMEOUT_SEC, cwd=tempfile.gettempdir(),
                           env={"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"})
        res = json.loads(p.stdout)
    except subprocess.TimeoutExpired:
        obs.record("checker.timeout")
        res = {"passed": False, "message": "Your program took too long — maybe a loop that never ends? "
                                           "Make sure every while loop has a way to stop."}
    except json.JSONDecodeError:
        obs.record("checker.internal_error")
        res = {"passed": False, "message": "The checker got confused. Try running your program first.", "checker_error": True}
    ms = (time.perf_counter() - t0) * 1000
    obs.record("checker.duration_ms", ms)
    if res.get("passed"):
        obs.record("checker.passed")
    if res.get("checker_error"):
        obs.record("checker.internal_error")
    res["duration_ms"] = int(ms)
    return res


@app.post("/api/learners/{lid}/check")
async def check(lid: int, request: Request, body: dict = Body(...)):
    _learner(lid)
    project, step, code = body["project"], body["step"], str(body.get("code", ""))
    item = _item(project, step)
    if not item:
        raise HTTPException(404, "Unknown step")
    reason = locked_reason(lid, project, step)
    if reason:
        obs.audit(f"learner:{lid}", "access.denied", "step", f"{project}/{step}", {"via": "check", "reason": reason}, request)
        raise HTTPException(403, reason)
    res = await asyncio.to_thread(run_check, code, item["check"])
    _ensure_progress(lid, project, step)
    prog = db.one("SELECT * FROM step_progress WHERE learner_id=? AND project_id=? AND step_id=?", (lid, project, step))
    was_done = prog["status"] == "done"
    attempts = prog["attempts"] + 1
    db.ex("UPDATE step_progress SET attempts=? WHERE learner_id=? AND project_id=? AND step_id=?", (attempts, lid, project, step))
    db.ex("INSERT INTO checks(learner_id, project_id, step_id, ts, passed, message, duration_ms) VALUES(?,?,?,?,?,?,?)",
          (lid, project, step, db.now(), int(res["passed"]), res.get("message", "")[:500], res["duration_ms"]))
    code_info = _snapshot(lid, project, step, "check", code)
    level_before = gamification.level_for(gamification.total_xp(lid))["level"]
    rewards = {"xp": 0, "bonuses": [], "badges": [], "level_up": None}
    if res["passed"] and not was_done:
        base = item.get("xp", 20)
        xp = base
        first_try = attempts == 1
        if first_try:
            xp += 5
            rewards["bonuses"].append("First try! +5")
        if prog["hints_used"] == 0:
            xp += 5
            rewards["bonuses"].append("No hints! +5")
        if prog["hints_used"] >= 4:   # peeked at the answer
            xp = max(5, base // 3)
            rewards["bonuses"] = ["Peeked at the answer — partial XP"]
        gamification.award_xp(lid, xp, f"step:{project}/{step}")
        db.ex("""UPDATE step_progress SET status='done', completed_at=?, first_try=?, xp=?
                 WHERE learner_id=? AND project_id=? AND step_id=?""", (db.now(), int(first_try), xp, lid, project, step))
        rewards["xp"] = xp
        rewards["badges"] = gamification.evaluate_badges(lid, PROJECTS)
        lvl = gamification.level_for(gamification.total_xp(lid))
        if lvl["level"] > level_before:
            rewards["level_up"] = lvl
    nxt = None
    project_complete = False
    if res["passed"] and project in BY_ID:
        p = BY_ID[project]
        ids = [s["id"] for s in p["steps"]]
        if step in ids and ids.index(step) + 1 < len(ids):
            nxt = {"project": project, "step": ids[ids.index(step) + 1]}
        done = {r["step_id"] for r in db.q("SELECT step_id FROM step_progress WHERE learner_id=? AND project_id=? AND status='done'",
                                           (lid, project))}
        project_complete = all(i in done for i in ids) and step in ids
    obs.audit(f"learner:{lid}", "check.pass" if res["passed"] else "check.fail", "step", f"{project}/{step}",
              {"attempt": attempts, "xp": rewards["xp"], "ms": res["duration_ms"], "complexity": code_info["complexity"],
               "message": res.get("message", "")[:120]}, request)
    return {**res, "attempts": attempts, "rewards": rewards, "next": nxt, "project_complete": project_complete,
            "code": code_info, "level": gamification.level_for(gamification.total_xp(lid))}


@app.post("/api/learners/{lid}/hint")
def hint(lid: int, request: Request, body: dict = Body(...)):
    project, step, level = body["project"], body["step"], int(body.get("level", 1))
    item = _item(project, step)
    if not item:
        raise HTTPException(404, "Unknown step")
    require_unlocked(lid, project, step)
    _ensure_progress(lid, project, step)
    prog = db.one("SELECT * FROM step_progress WHERE learner_id=? AND project_id=? AND step_id=?", (lid, project, step))
    hints = item.get("hints", [])
    if level == 4:
        if prog["hints_used"] < 3 or prog["attempts"] < 3:
            raise HTTPException(400, "Try all 3 hints and at least 3 checks first — you've got this!")
        text = item["solution"]
    elif 1 <= level <= len(hints):
        text = hints[level - 1]
    else:
        raise HTTPException(400, "No such hint")
    if level > prog["hints_used"]:
        db.ex("UPDATE step_progress SET hints_used=? WHERE learner_id=? AND project_id=? AND step_id=?", (level, lid, project, step))
        db.ex("INSERT INTO hints(learner_id, project_id, step_id, ts, level) VALUES(?,?,?,?,?)", (lid, project, step, db.now(), level))
        obs.audit(f"learner:{lid}", "hint.open" if level < 4 else "solution.peek", "step", f"{project}/{step}", {"level": level}, request)
    return {"level": level, "text": text, "is_solution": level == 4}


@app.get("/api/learners/{lid}/hints")
def hints_opened(lid: int, project: str, step: str):
    prog = db.one("SELECT hints_used, attempts FROM step_progress WHERE learner_id=? AND project_id=? AND step_id=?", (lid, project, step))
    item = _item(project, step)
    n = prog["hints_used"] if prog else 0
    hints = item.get("hints", []) if item else []
    return {"opened": [hints[i] for i in range(min(n, 3, len(hints)))], "used": n,
            "attempts": prog["attempts"] if prog else 0,
            "solution": item["solution"] if item and n >= 4 else None}


# ---------------------------------------------------------------------------
# time tracking
# ---------------------------------------------------------------------------
@app.post("/api/learners/{lid}/heartbeat")
def heartbeat(lid: int, body: dict = Body(...)):
    secs = max(0, min(int(body.get("seconds", 0)), 30))
    project, step = str(body.get("project") or "_home"), str(body.get("step") or "-")
    now = db.now()
    last = db.one("SELECT * FROM learning_sessions WHERE learner_id=? ORDER BY last_seen DESC LIMIT 1", (lid,))
    if last and now - last["last_seen"] < 300:
        db.ex("UPDATE learning_sessions SET last_seen=?, active_seconds=active_seconds+? WHERE id=?", (now, secs, last["id"]))
    else:
        sid = db.ex("INSERT INTO learning_sessions(learner_id, started_at, last_seen, active_seconds) VALUES(?,?,?,?)",
                    (lid, now, now, secs))
        obs.audit(f"learner:{lid}", "session.start", "session", sid)
    if secs:
        db.ex("""INSERT INTO time_log(learner_id, project_id, step_id, day, seconds) VALUES(?,?,?,?,?)
                 ON CONFLICT(learner_id, project_id, step_id, day) DO UPDATE SET seconds=seconds+excluded.seconds""",
              (lid, project, step, dt.date.today().isoformat(), secs))
        if project in BY_ID or project == "_practice":
            _ensure_progress(lid, project, step)
            db.ex("UPDATE step_progress SET seconds=seconds+? WHERE learner_id=? AND project_id=? AND step_id=?",
                  (secs, lid, project, step))
    obs.record("heartbeat")
    return {"ok": True}


# ---------------------------------------------------------------------------
# ideas, remixes, reflections
# ---------------------------------------------------------------------------
def _learned(lid):
    return [m["concept"] for m in analytics.concept_mastery(lid) if m["started"]]


@app.post("/api/learners/{lid}/ideas/analyze")
def idea_preview(lid: int, body: dict = Body(...)):
    return analysis.analyze_idea(str(body.get("text", "")), _learned(lid))


@app.post("/api/learners/{lid}/ideas")
def add_idea(lid: int, request: Request, body: dict = Body(...)):
    text = str(body.get("text", "")).strip()[:2000]
    if len(text) < 5:
        raise HTTPException(400, "Tell me a bit more about your idea!")
    a = analysis.analyze_idea(text, _learned(lid))
    iid = db.ex("INSERT INTO ideas(learner_id, project_id, ts, text, score, level, analysis) VALUES(?,?,?,?,?,?,?)",
                (lid, body.get("project"), db.now(), text, a["score"], a["level"], json.dumps(a)))
    xp = gamification.award_xp(lid, 5 + a["level"] * 3, f"idea:{iid}")
    obs.audit(f"learner:{lid}", "idea.add", "idea", iid, {"score": a["score"], "level": a["level"], "project": body.get("project")}, request)
    badges = gamification.evaluate_badges(lid, PROJECTS)
    return {"id": iid, "analysis": a, "xp": xp, "badges": badges}


@app.get("/api/learners/{lid}/ideas")
def list_ideas(lid: int):
    return analytics.ideas(lid)


@app.post("/api/learners/{lid}/remix")
async def submit_remix(lid: int, request: Request, body: dict = Body(...)):
    project, code = body["project"], str(body.get("code", ""))
    if project not in BY_ID:
        raise HTTPException(404, "Unknown project")
    require_unlocked(lid, project, "remix")
    p = BY_ID[project]
    base = p["steps"][-1]["solution"]
    # must at least run cleanly with a handful of generic inputs
    res = await asyncio.to_thread(run_check, code, """
r = run(["1", "yes", "2", "a", "q", "quit", "n", "no", "3", "x"] * 3, allow_error=True)
expect(r.error in (None, "OutOfInputs"), f"Your remix crashed with {r.error}: {r.error_msg} — fix it and submit again!")
""")
    info = _snapshot(lid, project, "remix", "remix", code)
    base_c = kidast.complexity_score(base)
    changed = code.strip() != base.strip()
    if not res["passed"]:
        return {"accepted": False, "message": res["message"], "code": info}
    if not changed or info["complexity"] < 5:
        return {"accepted": False, "message": "Add your own twist first — change or add something!", "code": info}
    growth = info["complexity"] - base_c
    xp = max(15, min(80, 20 + growth * 2 + len(info["concepts"]) * 2))
    prev = db.one("SELECT MAX(xp) m FROM remixes WHERE learner_id=? AND project_id=?", (lid, project))
    award = max(0, xp - (prev["m"] or 0))
    rid = db.ex("""INSERT INTO remixes(learner_id, project_id, idea_id, ts, code, complexity, base_complexity, concepts, xp)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (lid, project, body.get("idea_id"), db.now(), code, info["complexity"], base_c, json.dumps(info["concepts"]), award))
    if body.get("idea_id"):
        db.ex("UPDATE ideas SET status='built', built_complexity=? WHERE id=? AND learner_id=?", (info["complexity"], body["idea_id"], lid))
    gamification.award_xp(lid, award, f"remix:{project}")
    obs.audit(f"learner:{lid}", "remix.submit", "project", project, {"complexity": info["complexity"], "base": base_c, "xp": award}, request)
    badges = gamification.evaluate_badges(lid, PROJECTS)
    return {"accepted": True, "id": rid, "xp": award, "complexity": info["complexity"], "base_complexity": base_c,
            "concepts": info["concepts"], "badges": badges,
            "message": "Remix saved! " + ("It's more complex than the original — nice!" if growth > 0 else "Nice twist!")}


@app.post("/api/learners/{lid}/reflection")
def reflection(lid: int, request: Request, body: dict = Body(...)):
    fun, diff = int(body.get("fun", 3)), int(body.get("difficulty", 3))
    db.ex("INSERT INTO reflections(learner_id, project_id, ts, fun, difficulty, note) VALUES(?,?,?,?,?,?)",
          (lid, body.get("project"), db.now(), max(1, min(5, fun)), max(1, min(5, diff)), str(body.get("note", ""))[:500]))
    xp = 0
    if not db.scalar("SELECT COUNT(*) FROM xp_log WHERE learner_id=? AND reason=?", (lid, f"reflect:{body.get('project')}")):
        xp = gamification.award_xp(lid, 10, f"reflect:{body.get('project')}")
    obs.audit(f"learner:{lid}", "reflection.add", "project", body.get("project"), {"fun": fun, "difficulty": diff}, request)
    return {"ok": True, "xp": xp}


# ---------------------------------------------------------------------------
# parent: analytics, audit, monitoring, data
# ---------------------------------------------------------------------------
@app.get("/api/parent/report/{lid}")
def parent_report(lid: int, request: Request, _=Depends(parent_required)):
    _learner(lid)
    obs.audit("parent", "report.view", "learner", lid, request=request)
    return analytics.full_report(lid)


@app.get("/api/parent/timeline/{lid}")
def parent_timeline(lid: int, limit: int = 200, _=Depends(parent_required)):
    return obs.audit_query(actor=f"learner:{lid}", limit=limit)


@app.get("/api/parent/code/{lid}")
def parent_code_history(lid: int, project: str, step: str, _=Depends(parent_required)):
    rows = db.q("""SELECT id, ts, kind, lines, complexity, concepts, code FROM snapshots
                   WHERE learner_id=? AND project_id=? AND step_id=? ORDER BY ts""", (lid, project, step))
    item = _item(project, step)
    return {"snapshots": rows, "reference": item["solution"] if item else None}


@app.get("/api/parent/solution/{project}/{step}")
def parent_solution(project: str, step: str, _=Depends(parent_required)):
    item = _item(project, step)
    if not item:
        raise HTTPException(404)
    return {"solution": item["solution"], "hints": item.get("hints", [])}


@app.get("/api/parent/audit")
def parent_audit(request: Request, actor: str = None, action: str = None, entity: str = None, since: float = None,
                 until: float = None, text: str = None, limit: int = 200, offset: int = 0, _=Depends(parent_required)):
    return obs.audit_query(actor, action, entity, since, until, text, min(limit, 1000), offset)


@app.get("/api/parent/monitoring")
def parent_monitoring(hours: int = 24, _=Depends(parent_required)):
    return obs.snapshot(max(1, min(hours, 24 * 30)))


@app.get("/api/parent/errors/{eid}")
def parent_error_detail(eid: int, _=Depends(parent_required)):
    return db.one("SELECT * FROM app_errors WHERE id=?", (eid,))


@app.get("/api/parent/data")
def parent_data(_=Depends(parent_required)):
    return obs.data_overview()


@app.get("/api/parent/data/{table}")
def parent_table(table: str, request: Request, limit: int = 50, offset: int = 0, learner: int = None, _=Depends(parent_required)):
    if table not in db.TABLES:
        raise HTTPException(404)
    cols = [r["name"] for r in db.q(f"PRAGMA table_info({table})")]
    where, args = "", []
    if learner is not None and "learner_id" in cols:
        where, args = "WHERE learner_id=?", [learner]
    order = "ts DESC" if "ts" in cols else "rowid DESC"
    rows = db.q(f"SELECT * FROM {table} {where} ORDER BY {order} LIMIT ? OFFSET ?", (*args, min(limit, 500), offset))
    if table == "settings":
        rows = [{"key": r["key"], "value": "•••" if r["key"] == "parent_pin" else r["value"]} for r in rows]
    return {"columns": cols, "rows": rows, "total": db.scalar(f"SELECT COUNT(*) FROM {table} {where}", args)}


@app.get("/api/parent/export/{table}.{fmt}")
def parent_export(table: str, fmt: str, request: Request, _=Depends(parent_required)):
    if table not in db.TABLES or table == "settings" or fmt not in ("csv", "json"):
        raise HTTPException(404)
    rows = db.q(f"SELECT * FROM {table}")
    obs.audit("parent", "data.export", "table", table, {"format": fmt, "rows": len(rows)}, request)
    if fmt == "json":
        return Response(json.dumps(rows, default=str, indent=1), media_type="application/json",
                        headers={"Content-Disposition": f"attachment; filename={table}.json"})
    buf = io.StringIO()
    if rows:
        w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return Response(buf.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={table}.csv"})


@app.get("/api/parent/backup")
def parent_backup(request: Request, _=Depends(parent_required)):
    path = os.path.join(tempfile.gettempdir(), f"pyquest-backup-{int(time.time())}.db")
    src = db.conn()
    import sqlite3
    dst = sqlite3.connect(path)
    src.backup(dst)
    dst.close()
    obs.audit("parent", "data.backup", details={"bytes": os.path.getsize(path)}, request=request)
    return FileResponse(path, filename=f"pyquest-backup-{dt.date.today()}.db", media_type="application/octet-stream")


@app.delete("/api/parent/learners/{lid}")
def parent_delete_learner(lid: int, request: Request, _=Depends(parent_required)):
    learner = _learner(lid)
    with db.tx() as c:
        for t in ("step_progress", "code_saves", "snapshots", "runs", "checks", "hints", "time_log",
                  "learning_sessions", "ideas", "remixes", "reflections", "xp_log", "badges", "tutor_messages"):
            c.execute(f"DELETE FROM {t} WHERE learner_id=?", (lid,))
        c.execute("DELETE FROM learners WHERE id=?", (lid,))
    obs.audit("parent", "learner.delete", "learner", lid, {"name": learner["name"]}, request)
    return {"ok": True}


@app.post("/api/parent/retention")
def parent_retention(request: Request, body: dict = Body(...), _=Depends(parent_required)):
    """Prune bulky telemetry older than N days (code snapshots, metrics). Learning records are kept."""
    days = max(7, int(body.get("days", 90)))
    cutoff = time.time() - days * 86400
    with db.tx() as c:
        s = c.execute("DELETE FROM snapshots WHERE ts < ? AND kind IN ('run','playground')", (cutoff,)).rowcount
        m = c.execute("DELETE FROM metrics_minute WHERE minute < ?", (int(cutoff // 60),)).rowcount
    obs.audit("parent", "data.retention", details={"days": days, "snapshots_deleted": s, "metrics_deleted": m}, request=request)
    return {"snapshots_deleted": s, "metrics_deleted": m}


# ---------------------------------------------------------------------------
# AI tutor (Pixel)
# ---------------------------------------------------------------------------
def _tutor_target(project, step):
    item = _item(project, step)
    title = BY_ID[project]["title"] if project in BY_ID else {"_practice": "Side quest", "_playground": "Playground"}.get(project, project)
    return item, title


def _tutor_reply(fn):
    try:
        return {"ok": True, **fn()}
    except tutor.TutorError as e:
        return {"ok": False, "error": str(e), "status": e.status}


@app.get("/api/tutor/status")
def tutor_status(learner: int = None):
    return tutor.status(learner)


@app.get("/api/learners/{lid}/tutor/history")
def tutor_history(lid: int, project: str, step: str):
    return tutor.history(lid, project, step)


@app.post("/api/learners/{lid}/tutor/chat")
async def tutor_chat(lid: int, body: dict = Body(...)):
    _learner(lid)
    project, step = body["project"], body["step"]
    require_unlocked(lid, project, step)
    item, title = _tutor_target(project, step)
    kind = "error" if body.get("kind") == "error" else "chat"
    return await asyncio.to_thread(_tutor_reply, lambda: tutor.chat(
        lid, project, step, body.get("question", ""), str(body.get("code", ""))[:20000], body.get("run"), item, title, kind))


@app.post("/api/learners/{lid}/tutor/review")
async def tutor_review(lid: int, body: dict = Body(...)):
    _learner(lid)
    project, step = body["project"], body["step"]
    require_unlocked(lid, project, step)
    item, title = _tutor_target(project, step)
    return await asyncio.to_thread(_tutor_reply, lambda: tutor.review(
        lid, project, step, str(body.get("code", ""))[:20000], body.get("run"), item, title))


@app.get("/api/parent/tutor/{lid}")
def parent_tutor(lid: int, _=Depends(parent_required)):
    return {"status": tutor.status(lid), "stats": tutor.stats(lid), "transcripts": tutor.transcripts(lid)}


@app.post("/api/parent/tutor/settings")
def parent_tutor_settings(request: Request, body: dict = Body(...), _=Depends(parent_required)):
    before = tutor.settings()
    after = tutor.save_settings(body)
    obs.audit("parent", "tutor.settings", details={"before": before, "after": after}, request=request)
    return tutor.status()


@app.post("/api/parent/tutor/test")
async def parent_tutor_test(request: Request, _=Depends(parent_required)):
    if not tutor.status()["configured"]:
        return {"ok": False, "error": "No Anthropic credentials found. Set ANTHROPIC_API_KEY before starting PyQuest."}
    res = await asyncio.to_thread(_tutor_reply, tutor.test_connection)
    obs.audit("parent", "tutor.test", details={"ok": res.get("ok"), "error": res.get("error")}, request=request)
    return res


@app.get("/api/health")
def health():
    try:
        db.scalar("SELECT 1")
        ok = True
    except Exception:  # noqa: BLE001
        ok = False
    return {"status": "ok" if ok else "degraded", "uptime_sec": round(time.time() - obs.STARTED),
            "projects": len(PROJECTS), "practice": len(PRACTICE), "active_runs": _active_runs}


@app.on_event("shutdown")
def _shutdown():
    obs.flush()
    obs.audit("system", "server.stop")


# ---------------------------------------------------------------------------
# static front-end
# ---------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC, "index.html"), headers={"Cache-Control": "no-cache"})
