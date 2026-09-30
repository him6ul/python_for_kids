// Parent Zone: learning analytics, coaching guide, audit log, monitoring and data management.
import { fmt } from "./tutor.js";
import { api, chartDefaults, esc, fmtMin, fmtTime, makeChart, seriesColors, setContext, state, toast } from "./core.js";

const TABS = [["overview", "Overview"], ["learning", "Learning"], ["projects", "Projects & time"], ["guide", "Coaching"], ["tutor", "AI tutor"],
  ["timeline", "Timeline"], ["audit", "Audit log"], ["monitoring", "Monitoring"], ["data", "Data"], ["settings", "Settings"]];

let learners = [];
let sel = null;

export async function viewParent(app, tab = "overview", arg) {
  setContext("_parent", tab);
  document.body.classList.add("parent-mode");
  const st = await api("/api/parent/status");
  if (!st.logged_in) return pinGate(app, st.pin_set, tab);
  learners = await api("/api/learners");
  if (!sel || !learners.find((l) => l.id === sel)) sel = state.learner?.id || learners[0]?.id;
  app.innerHTML = `<div class="parent">
    <header class="p-head">
      <div><div class="eyebrow">Parent Zone</div><h1>${esc(TABS.find(([k]) => k === tab)?.[1] || "Overview")}</h1></div>
      <span class="spacer"></span>
      ${learners.length ? `<label class="p-learner"><span class="faint">Learner</span><select id="lsel">${learners.map((l) => `<option value="${l.id}" ${l.id === sel ? "selected" : ""}>${l.avatar} ${esc(l.name)}</option>`).join("")}</select></label>` : ""}
      <a class="btn small" href="#/home">Back to PyQuest</a><button class="btn small" id="logout">Lock</button>
    </header>
    <nav class="ptabs">${TABS.map(([k, n]) => `<a href="#/parent/${k}" class="${k === tab ? "active" : ""}">${n}</a>`).join("")}</nav>
    <div id="pbody"><p class="muted">Loading…</p></div></div>`;
  app.querySelector("#lsel")?.addEventListener("change", (e) => { sel = +e.target.value; viewParent(app, tab); });
  app.querySelector("#logout").onclick = async () => { await api("/api/parent/logout", { method: "POST" }); location.hash = "#/home"; };
  const body = app.querySelector("#pbody");
  const needsLearner = ["overview", "learning", "projects", "guide", "timeline", "tutor"];
  if (needsLearner.includes(tab) && !sel) { body.innerHTML = `<p class="muted">No learners yet.</p>`; return; }
  try {
    await ({ overview, learning, projects, guide, tutor, timeline, audit, monitoring, data, settings }[tab] || overview)(body, arg);
  } catch (e) {
    body.innerHTML = `<div class="note"><b>Couldn't load this view</b>${esc(e.message)}</div>`;
  }
}

function pinGate(app, pinSet, tab) {
  const field = (id, label, auto) => `<label class="pin-field"><span>${label}</span>
    <input id="${id}" type="password" inputmode="numeric" pattern="[0-9]*" autocomplete="${auto}" maxlength="12" placeholder="••••"></label>`;
  app.innerHTML = `<div class="parent pin-page"><section class="card pinbox">
    <div class="pin-icon" aria-hidden="true">🔒</div>
    <div class="eyebrow">Parent Zone</div>
    <h1>${pinSet ? "Enter your PIN" : "Create a parent PIN"}</h1>
    <p class="muted">${pinSet ? "Unlock progress, coaching notes, the audit log and data tools."
                              : "Choose a PIN of 4 or more digits. It protects the dashboard, audit log and data tools on this computer."}</p>
    <form id="pinform" novalidate>
      ${field("pin", pinSet ? "PIN" : "New PIN", pinSet ? "current-password" : "new-password")}
      ${pinSet ? "" : field("pin2", "Confirm PIN", "new-password")}
      <p class="pin-error" role="alert" aria-live="polite"></p>
      <button class="btn primary block" type="submit">${pinSet ? "Unlock" : "Set PIN and continue"}</button>
    </form>
    <div class="pin-foot"><a href="#/home">← Back to PyQuest</a><span class="faint">Stored only as a secure hash</span></div>
  </section></div>`;
  const $ = (q) => app.querySelector(q);
  const err = (m) => { $(".pin-error").textContent = m; if (m) { $("#pin").select(); $(".pinbox").classList.remove("shake"); void $(".pinbox").offsetWidth; $(".pinbox").classList.add("shake"); } };
  app.querySelectorAll(".pin-field input").forEach((i) => i.addEventListener("input", () => { i.value = i.value.replace(/\D/g, ""); err(""); }));
  $("#pinform").onsubmit = async (e) => {
    e.preventDefault();
    const pin = $("#pin").value;
    if (pin.length < 4) return err("Use at least 4 digits.");
    if (!pinSet && pin !== $("#pin2").value) return err("The two PINs don't match.");
    const btn = $("#pinform button"); btn.disabled = true;
    try { await api("/api/parent/login", { method: "POST", body: { pin } }); viewParent(app, tab); }
    catch (ex) { err(ex.status === 403 ? "That PIN isn't right. Try again." : ex.message); $("#pin").value = ""; if ($("#pin2")) $("#pin2").value = ""; }
    finally { btn.disabled = false; }
  };
  $("#pin").focus();
}

// Audit details are JSON; show them as "key value · key value" so they're readable at a glance.
function fmtDetails(raw) {
  if (!raw) return "";
  let d;
  try { d = JSON.parse(raw); } catch (e) { return esc(raw); }
  if (typeof d !== "object" || d === null) return esc(String(d));
  return Object.entries(d).filter(([, v]) => v !== null && v !== "" && v !== undefined)
    .map(([k, v]) => `<span class="kv"><span class="k">${esc(k.replace(/_/g, " "))}</span> ${esc(typeof v === "object" ? JSON.stringify(v) : String(v))}</span>`).join("");
}

const pct = (v) => (v === null || v === undefined ? "—" : `${Math.round(v * 100)}%`);
const kpi = (v, l, s = "") => `<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div>${s ? `<div class="s">${s}</div>` : ""}</div>`;
let reportCache = {};
async function report() {
  const r = await api(`/api/parent/report/${sel}`);
  reportCache[sel] = r;
  return r;
}
function P() { return document.querySelector(".parent"); }
function chartSetup() {
  const root = P();
  const { grid } = chartDefaults(root, "--p-text2", "--p-line");
  return { col: seriesColors(root), grid };
}
const baseOpts = (grid, extra = {}) => ({
  maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
  plugins: { legend: { position: "bottom", labels: { boxWidth: 10, boxHeight: 10 } } },
  scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: grid } } }, ...extra,
});

// ---------------------------------------------------------------- overview
async function overview(body) {
  const r = await report();
  const s = r.schedule, a = r.activity, st = r.style;
  const done = r.projects.filter((p) => p.complete).length;
  const steps = r.projects.reduce((x, p) => x + p.steps_done, 0), total = r.projects.reduce((x, p) => x + p.steps_total, 0);
  const statusPill = { ahead: "good", "on track": "good", behind: "warn" }[s.status];
  body.innerHTML = `
    <div class="kpis four">
      ${kpi(`${done}/12`, "Projects complete", `${steps}/${total} missions`)}
      ${kpi(`<span class="pill ${statusPill}" style="font-size:1rem">${esc(s.status)}</span>`, "Schedule", `Day ${s.days_in + 1} of 42 · week ${s.calendar_week}`)}
      ${kpi(fmtMin(a.total_minutes * 60), "Active coding time", `${a.sessions} sessions · avg ${a.avg_session_minutes} min`)}
      ${kpi(`${a.streak.current} <small>days</small>`, "Day streak", `best ${a.streak.best}`)}
      ${kpi(`Lv ${r.level.level}`, esc(r.level.title), `${r.level.xp} XP`)}
      ${kpi(pct(st.raw.first_try_rate), "First-try pass rate", `${st.raw.hints_per_step} hints / step`)}
      ${kpi(r.errors.total, "Program crashes", `${pct(r.errors.crash_rate)} of ${r.errors.runs} runs`)}
      ${kpi(r.enjoyment.avg_fun ? `${r.enjoyment.avg_fun}/5` : "—", "Average fun rating", r.enjoyment.avg_difficulty ? `difficulty ${r.enjoyment.avg_difficulty}/5` : "no ratings yet")}
    </div>
    <div class="grid g2">
      <div class="card"><h3>Progress vs 6-week plan</h3>
        <p class="muted" style="margin-top:0">${s.actual_pct}% of missions done; the plan expects ${s.expected_pct}% by today. Planned finish ${s.planned_finish}${s.projected_finish ? ` · projected finish at current pace <b>${s.projected_finish}</b>` : ""}.</p>
        <div class="row"><span class="faint" style="width:70px">Actual</span><div class="progress" style="flex:1"><i style="width:${s.actual_pct}%"></i></div></div>
        <div class="row" style="margin-top:6px"><span class="faint" style="width:70px">Plan</span><div class="progress" style="flex:1"><i style="width:${s.expected_pct}%;background:var(--p-muted)"></i></div></div>
        <h3 style="margin-top:18px">Learner profile: ${st.persona.emoji} ${esc(st.persona.name)}</h3><p class="muted">${esc(st.persona.desc)}</p></div>
      <div class="card"><h3>Top coaching notes</h3>${r.guide.parent.slice(0, 4).map(note).join("") || `<p class="muted">Nothing needs your attention right now. 👍</p>`}
        <p><a href="#/parent/guide">All notes →</a></p></div>
    </div>
    <div class="card" style="margin-top:16px"><h3>Daily active minutes (last 6 weeks)</h3><div class="chart-box"><canvas id="p-daily"></canvas></div></div>`;
  const { col, grid } = chartSetup();
  makeChart(body.querySelector("#p-daily"), {
    type: "bar",
    data: { labels: a.daily.map((d) => d.day.slice(5)), datasets: [{ label: "Active minutes", data: a.daily.map((d) => d.minutes), backgroundColor: col[0], borderRadius: 4, maxBarThickness: 18 }] },
    options: baseOpts(grid, { plugins: { legend: { display: false } } }),
  });
}

function note(n) {
  return `<div class="note"><b>${esc(n.title)}</b><span class="muted">${esc(n.text)}</span></div>`;
}

// ---------------------------------------------------------------- learning analytics
async function learning(body) {
  const r = reportCache[sel] || await report();
  const st = r.style, m = r.mastery, e = r.errors;
  body.innerHTML = `
    <div class="grid g2">
      <div class="card"><h3>Concept mastery</h3><p class="muted" style="margin-top:0">Combines missions completed, quality (attempts, hints, time), practice side quests and independent use in the Playground/remixes.</p>
        <div class="chart-box tall"><canvas id="p-mastery"></canvas></div></div>
      <div class="card"><h3>Learning style</h3><p class="muted" style="margin-top:0">${st.persona.emoji} <b>${esc(st.persona.name)}</b> — ${esc(st.persona.desc)}</p>
        <div class="chart-box tall"><canvas id="p-style"></canvas></div></div>
    </div>
    <div class="card" style="margin-top:16px"><h3>How he learns — raw signals</h3><div class="kpis five" style="margin:0">
      ${kpi(pct(st.raw.first_try_rate), "First-try passes", "Precision")}
      ${kpi(st.raw.hints_per_step, "Hints per step", "Independence")}
      ${kpi(st.raw.runs_per_check, "Runs per check", "Experimenting — how often he tests ideas")}
      ${kpi(pct(st.raw.persistence), "Recovered after a failed check", "Persistence")}
      ${kpi(st.raw.avg_error_recovery_sec ? `${st.raw.avg_error_recovery_sec}s` : "—", "Avg time to fix a crash", "Debugging speed")}
      ${kpi(st.raw.pace_ratio ?? "—", "Time vs expected", "1.0 = on estimate, <1 faster")}
      ${kpi(st.raw.beyond_reference_ratio ?? "—", "His code vs reference complexity", ">1 means he goes beyond what's asked")}
      ${kpi(`${st.raw.remixes} / ${st.raw.ideas} / ${st.raw.playground_runs}`, "Remixes / ideas / playground runs", "Creativity signals")}
      ${kpi(st.raw.tutor_questions ?? 0, "Questions to AI tutor", `${st.raw.tutor_per_step ?? 0} per mission`)}
    </div></div>
    <div class="grid g2" style="margin-top:16px">
      <div class="card"><h3>Idea complexity over time</h3><p class="muted" style="margin-top:0">Each idea in his journal is scored 0–100 on features, concept breadth and ambition (Spark → Mastermind). Remix code complexity is shown against the original project.</p>
        ${r.ideas.ideas.length || r.ideas.remixes.length ? `<div class="chart-box"><canvas id="p-ideas"></canvas></div>` : `<p class="faint">No ideas or remixes yet.</p>`}
        ${r.ideas.ideas.slice(-4).reverse().map((i) => `<div class="note"><b>${i.analysis.level_emoji} ${esc(i.analysis.level_name)} · ${i.score}/100 ${i.status === "built" ? "· built ✅" : ""}</b><span class="muted">"${esc(i.text)}"</span></div>`).join("")}</div>
      <div class="card"><h3>Code growth</h3><p class="muted" style="margin-top:0">Complexity (0–100) and lines of the code he passed each mission with.</p>
        <div class="chart-box"><canvas id="p-growth"></canvas></div></div>
    </div>
    <div class="grid g2" style="margin-top:16px">
      <div class="card"><h3>Errors by type</h3><div class="tscroll" style="max-height:300px"><table class="t"><thead><tr><th>Bug</th><th class="num">Total</th><th class="num">Last 7 days</th><th>Fixed?</th></tr></thead>
        <tbody>${e.by_type.map((x) => `<tr><td>${x.emoji} ${esc(x.type)}<div class="faint">${esc(x.tip)}</div></td><td class="num">${x.count}</td><td class="num">${x.recent}</td><td>${x.defeated ? "✅" : "—"}</td></tr>`).join("") || `<tr><td colspan="4" class="faint">No crashes yet.</td></tr>`}</tbody></table></div></div>
      <div class="card"><h3>Recent error messages</h3><div class="tscroll" style="max-height:300px"><table class="t"><thead><tr><th>When</th><th>Where</th><th>Error</th></tr></thead>
        <tbody>${e.recent_messages.map((x) => `<tr><td>${fmtTime(x.ts)}</td><td>${esc(x.project_id)}/${esc(x.step_id)}${x.error_line ? ` L${x.error_line}` : ""}</td><td><b>${esc(x.error_type)}</b> ${esc(x.error_msg)}</td></tr>`).join("") || `<tr><td colspan="3" class="faint">—</td></tr>`}</tbody></table></div></div>
    </div>
    <div class="card" style="margin-top:16px"><h3>Mastery detail</h3><div class="tscroll"><table class="t"><thead><tr><th>Concept</th><th>Status</th><th class="num">Score</th><th class="num">Missions</th><th class="num">Avg quality</th><th class="num">Independent uses</th><th class="num">Practice</th><th class="num">Errors on related steps</th><th class="num">Asked Pixel</th></tr></thead>
      <tbody>${m.map((x) => `<tr><td>${esc(x.label)}</td><td>${esc(x.status)}</td><td class="num">${pct(x.score)}</td><td class="num">${x.steps_done}/${x.steps_total}</td><td class="num">${x.avg_quality}</td><td class="num">${x.independent_uses}</td><td class="num">${x.practice_done}</td><td class="num">${x.errors}</td><td class="num">${x.tutor_questions ?? 0}</td></tr>`).join("")}</tbody></table></div></div>`;
  const { col, grid } = chartSetup();
  makeChart(body.querySelector("#p-mastery"), {
    type: "bar",
    data: { labels: m.map((x) => x.label), datasets: [{ label: "Mastery %", data: m.map((x) => Math.round(x.score * 100)), backgroundColor: col[0], borderRadius: 4, maxBarThickness: 16 }] },
    options: baseOpts(grid, { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { min: 0, max: 100, grid: { color: grid } }, y: { grid: { display: false } } } }),
  });
  makeChart(body.querySelector("#p-style"), {
    type: "radar",
    data: { labels: Object.keys(st.traits), datasets: [{ label: "Learning traits", data: Object.values(st.traits).map((v) => Math.round(v * 100)), borderColor: col[6], backgroundColor: col[6] + "26", borderWidth: 2, pointRadius: 4, pointBackgroundColor: col[6] }] },
    options: { maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { r: { min: 0, max: 100, ticks: { display: false }, grid: { color: grid }, angleLines: { color: grid } } } },
  });
  if (body.querySelector("#p-ideas")) makeChart(body.querySelector("#p-ideas"), {
    type: "scatter",
    data: { datasets: [
      { label: "Idea score", data: r.ideas.ideas.map((i) => ({ x: i.ts * 1000, y: i.score })), backgroundColor: col[0], pointRadius: 6, showLine: true, borderColor: col[0], borderWidth: 2 },
      { label: "Remix complexity", data: r.ideas.remixes.map((i) => ({ x: i.ts * 1000, y: i.complexity })), backgroundColor: col[1], pointRadius: 6, pointStyle: "rectRot" },
      { label: "Original project complexity", data: r.ideas.remixes.map((i) => ({ x: i.ts * 1000, y: i.base_complexity })), backgroundColor: col[2], pointRadius: 5, pointStyle: "triangle" },
    ] },
    options: baseOpts(grid, { scales: { x: { type: "linear", ticks: { callback: (v) => new Date(v).toLocaleDateString([], { month: "short", day: "numeric" }) }, grid: { display: false } }, y: { min: 0, max: 100, grid: { color: grid } } } }),
  });
  const g = r.code_growth;
  makeChart(body.querySelector("#p-growth"), {
    type: "line",
    data: { labels: g.map((x) => `${x.project_id.slice(0, 10)}/${x.step_id}`), datasets: [
      { label: "Complexity (0–100)", data: g.map((x) => x.complexity), borderColor: col[0], backgroundColor: col[0], borderWidth: 2, pointRadius: 3, tension: 0.25 },
      { label: "Lines of code", data: g.map((x) => x.lines), borderColor: col[1], backgroundColor: col[1], borderWidth: 2, pointRadius: 3, tension: 0.25, borderDash: [5, 4] },
    ] },
    options: baseOpts(grid, { scales: { x: { ticks: { display: false }, grid: { display: false } }, y: { beginAtZero: true, grid: { color: grid } } } }),
  });
}

// ---------------------------------------------------------------- projects & time
async function projects(body, arg) {
  const r = reportCache[sel] || await report();
  const cur = state.curriculum.projects;
  body.innerHTML = `
    <div class="card"><h3>Time per project — actual vs expected</h3><div class="chart-box tall"><canvas id="p-time"></canvas></div></div>
    <div class="grid g2" style="margin-top:16px">
      <div class="card"><h3>Where the time goes</h3><div class="chart-box"><canvas id="p-mode"></canvas></div></div>
      <div class="card"><h3>When he codes (hour of day)</h3><div class="chart-box"><canvas id="p-hour"></canvas></div></div>
    </div>
    <div class="card" style="margin-top:16px"><h3>Project details</h3><div class="tscroll"><table class="t"><thead><tr><th>Project</th><th>Missions</th><th class="num">Time</th><th class="num">Expected</th><th class="num">Runs</th><th class="num">Crashes</th><th class="num">Checks</th><th class="num">First-try</th><th class="num">Hints</th><th>Boss</th><th>Remix</th><th>Fun / Hard</th><th>Finished</th></tr></thead>
      <tbody>${r.projects.map((p) => `<tr><td>${p.emoji} <a href="#/parent/projects/${p.id}">${esc(p.title)}</a></td><td>${p.steps_done}/${p.steps_total}</td>
        <td class="num">${fmtMin(p.seconds)}</td><td class="num">${fmtMin(p.expected_seconds)}</td><td class="num">${p.runs}</td><td class="num">${p.errors}</td><td class="num">${p.attempts}</td>
        <td class="num">${p.first_try}</td><td class="num">${p.hints}</td><td>${p.boss_done ? "✅" : "—"}</td><td>${p.remixed ? "✅" : "—"}</td>
        <td>${p.fun ? `${p.fun} / ${p.difficulty}` : "—"}</td><td>${p.completed_at ? fmtTime(p.completed_at) : "—"}</td></tr>`).join("")}</tbody></table></div></div>
    <div id="pdetail"></div>`;
  const { col, grid } = chartSetup();
  makeChart(body.querySelector("#p-time"), {
    type: "bar",
    data: { labels: r.projects.map((p) => p.title), datasets: [
      { label: "Actual minutes", data: r.projects.map((p) => Math.round(p.seconds / 60)), backgroundColor: col[0], borderRadius: 4, maxBarThickness: 22 },
      { label: "Expected minutes", data: r.projects.map((p) => Math.round(p.expected_seconds / 60)), backgroundColor: getComputedStyle(P()).getPropertyValue("--p-ref").trim(), borderRadius: 4, maxBarThickness: 22 },
    ] },
    options: baseOpts(grid),
  });
  const modes = r.activity.by_mode;
  const modeLabel = { projects: "Projects", _practice: "Side quests", _playground: "Playground", _home: "Home / map", _ideas: "Ideas", _journey: "My Journey", _parent: "Parent zone" };
  const mk = Object.keys(modes);
  makeChart(body.querySelector("#p-mode"), {
    type: "bar",
    data: { labels: mk.map((k) => modeLabel[k] || k), datasets: [{ label: "Minutes", data: mk.map((k) => modes[k]), backgroundColor: col[0], borderRadius: 4, maxBarThickness: 26 }] },
    options: baseOpts(grid, { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, grid: { color: grid } }, y: { grid: { display: false } } } }),
  });
  makeChart(body.querySelector("#p-hour"), {
    type: "bar",
    data: { labels: r.activity.by_hour.map((h) => `${h.hour}:00`), datasets: [{ label: "Minutes", data: r.activity.by_hour.map((h) => h.minutes), backgroundColor: col[0], borderRadius: 3, maxBarThickness: 14 }] },
    options: baseOpts(grid, { plugins: { legend: { display: false } } }),
  });
  if (arg) projectDetail(body.querySelector("#pdetail"), cur.find((p) => p.id === arg));
}

async function projectDetail(host, p) {
  if (!p) return;
  const steps = [...p.steps, p.boss];
  host.innerHTML = `<div class="card" style="margin-top:16px"><h3>${p.emoji} ${esc(p.title)} — code history</h3>
    <p class="muted">Pick a mission to see every version of his code (each run and check) side by side with the reference solution.</p>
    <div class="row">${steps.map((s) => `<button class="btn small" data-s="${s.id}">${esc(s.title)}</button>`).join("")}</div><div id="hist"></div></div>`;
  host.querySelectorAll("[data-s]").forEach((b) => b.onclick = async () => {
    const d = await api(`/api/parent/code/${sel}?project=${p.id}&step=${b.dataset.s}`);
    const h = host.querySelector("#hist");
    if (!d.snapshots.length) { h.innerHTML = `<p class="faint">No code yet for this mission.</p>`; return; }
    h.innerHTML = `<div class="row" style="margin:10px 0"><label>Version <input type="range" min="0" max="${d.snapshots.length - 1}" value="${d.snapshots.length - 1}" id="ver" style="width:260px"></label><span id="vinfo" class="muted"></span></div>
      <div class="codecmp"><div><b>His code</b><pre id="mine"></pre></div><div><b>Reference solution</b><pre>${esc(d.reference || "")}</pre></div></div>`;
    const show = () => {
      const s = d.snapshots[+h.querySelector("#ver").value];
      h.querySelector("#mine").textContent = s.code;
      h.querySelector("#vinfo").textContent = `${fmtTime(s.ts)} · ${s.kind} · ${s.lines} lines · complexity ${s.complexity}`;
    };
    h.querySelector("#ver").oninput = show;
    show();
  });
}

// ---------------------------------------------------------------- coaching guide
async function guide(body) {
  const r = reportCache[sel] || await report();
  const g = r.guide;
  body.innerHTML = `<div class="grid g2">
    <div class="card"><h3>Coaching notes for you</h3><p class="muted" style="margin-top:0">Generated from his progress, errors, pace, hint use, ideas and fun ratings. Updated live.</p>
      ${g.parent.map(note).join("") || `<p class="muted">Nothing needs attention — he's doing great. Ask him to demo his latest project!</p>`}
      <h3 style="margin-top:16px">Conversation starters</h3><ul class="muted">
      <li>"Show me the coolest thing you built this week."</li><li>"What was the hardest bug? How did you beat it?"</li>
      <li>"If you could add one feature to ${esc(r.projects.filter((p) => p.complete).slice(-1)[0]?.title || "your next project")}, what would it be?"</li>
      <li>"Explain ${esc((r.mastery.filter((m) => m.started).sort((a, b) => a.score - b.score)[0] || { label: "variables" }).label.toLowerCase())} to me like I'm 5."</li></ul></div>
    <div class="card"><h3>What he sees (his guide)</h3>${g.kid.map((k) => `<div class="note"><b>${k.emoji || ""} ${esc(k.title)}</b><span class="muted">${esc(k.text)}</span></div>`).join("")}
      <h3 style="margin-top:16px">Adaptive path</h3><ol class="path-list">${g.path.map((p) => p.type === "project"
        ? `<li class="${p.unlocked ? "" : "locked"}"><span>${esc(p.title)}</span><span class="pill ${p.complete ? "good" : ""}">${p.complete ? "Done" : p.unlocked ? `${p.steps_done}/${p.steps_total} missions` : "Locked"}</span></li>`
        : `<li class="side"><span>↳ ${esc(p.title.replace("Side quest: ", "Side quest · "))}</span><span class="pill">Recommended</span></li>`).join("")}</ol></div></div>`;
}

// ---------------------------------------------------------------- AI tutor
async function tutor(body) {
  const d = await api(`/api/parent/tutor/${sel}`);
  const st = d.status, s = d.stats;
  const setup = !st.configured
    ? `<div class="note warn"><b>Not connected yet</b><span class="muted">Pixel uses the Claude API (model <code>${esc(st.model)}</code>).
       Create an API key at console.anthropic.com, then start PyQuest with it, e.g. <code>ANTHROPIC_API_KEY=… ./run.sh</code>.
       ${st.sdk ? "" : "The <code>anthropic</code> package is also missing — run <code>.venv/bin/pip install anthropic</code>."}</span></div>` : "";
  const kindLabel = { concept_question: "Concept questions", debugging: "Debugging help", stuck: "Stuck", idea: "Ideas", check_my_work: "Check my work", off_topic: "Off topic", other: "Other" };
  body.innerHTML = `${setup}
    <div class="grid g2">
      <div class="card"><h3>Pixel settings</h3>
        <p class="muted" style="margin-top:0">Pixel is an AI tutor that gives Socratic hints and code reviews, but never full answers. When it's on, his questions, code and program output are sent to Anthropic's API. His name is not sent. Every conversation is saved here for you to read.</p>
        <p><label><input type="checkbox" id="t-en" ${st.enabled ? "checked" : ""}> Enable the AI tutor</label></p>
        <p><label>Daily question limit <input type="number" id="t-lim" min="1" max="500" value="${st.daily_limit}" style="width:90px"></label></p>
        <p><label><input type="checkbox" id="t-snip" ${st.allow_snippets ? "checked" : ""}> Allow tiny 1–2 line code examples (never his answer)</label></p>
        <div class="row"><button class="btn primary" id="t-save">Save</button><button class="btn" id="t-test" ${st.configured ? "" : "disabled"}>Test connection</button>
          <span class="pill ${st.available ? "good" : "warn"}">${st.available ? "Active" : st.configured ? "Off" : "Not connected"}</span></div>
        <p id="t-testout" class="muted"></p></div>
      <div class="card"><h3>Usage</h3><div class="kpis two" style="margin:0">
        ${kpi(s.questions, "Questions asked", `${s.error_help} about crashes`)}
        ${kpi(s.reviews, "Code reviews")}
        ${kpi(`${s.used_today}/${st.daily_limit}`, "Today")}
        ${kpi(`$${s.est_cost_usd.toFixed(2)}`, "Estimated API cost", `${(s.tokens_in + s.tokens_out).toLocaleString()} tokens`)}
        ${kpi(s.avg_latency_ms ? `${(s.avg_latency_ms / 1000).toFixed(1)}s` : "—", "Avg reply time", `${s.errors} errors · ${s.refused} declined`)}
        ${kpi(s.steps_with_questions, "Missions he asked about")}</div></div>
    </div>
    ${s.flagged.length ? `<div class="card alert" style="margin-top:16px"><h3>Messages flagged for you</h3>
      <p class="muted" style="margin-top:0">Pixel flags messages about safety, feeling unsafe, bullying or similar, and tells him to talk to a trusted adult.</p>
      ${s.flagged.map((f) => `<div class="note alert"><b>${fmtTime(f.ts)} · ${esc(f.project_id)}/${esc(f.step_id)}</b><span>${esc(f.text)}</span></div>`).join("")}</div>` : ""}
    <div class="grid g2" style="margin-top:16px">
      <div class="card"><h3>What he asks about</h3><p class="muted" style="margin-top:0">Pixel tags each question with a type and the concept it's about. Concepts he asks about often are good ones to review together.</p>
        ${Object.keys(s.by_concept).length ? `<div class="chart-box"><canvas id="t-concepts"></canvas></div>` : `<p class="faint">No questions yet.</p>`}</div>
      <div class="card"><h3>Question types & mood</h3>
        ${Object.keys(s.by_kind).length ? `<div class="chart-box"><canvas id="t-kinds"></canvas></div>` : `<p class="faint">No questions yet.</p>`}
        <p class="muted">Mood read from his messages: ${Object.entries(s.moods).map(([k, v]) => `<span class="pill">${esc(k)} ${v}</span>`).join(" ") || "—"}</p></div>
    </div>
    <div class="card" style="margin-top:16px"><h3>Conversations</h3><div class="tscroll" style="max-height:640px"><table class="t"><thead><tr><th>When</th><th>Where</th><th>Who</th><th>Message</th><th>Tags</th></tr></thead>
      <tbody>${d.transcripts.map((m) => `<tr><td style="white-space:nowrap">${fmtTime(m.ts)}</td><td>${esc(m.project_id)}/${esc(m.step_id)}</td>
        <td>${m.role === "kid" ? "🧒 him" : "🤖 Pixel"}${m.status !== "ok" ? ` <span class="pill warn">${esc(m.status)}</span>` : ""}</td>
        <td style="max-width:560px">${m.kind === "review" && m.role === "tutor" && m.meta?.suggestions ? `<b>${"⭐".repeat(m.meta.stars || 0)}</b> ${fmt(m.text)}<ul>${m.meta.suggestions.map((x) => `<li>${x.line ? `L${x.line}: ` : ""}${fmt(x.tip)}</li>`).join("")}</ul>` : fmt(m.text)}</td>
        <td class="faint">${m.role === "kid" && m.meta ? `${esc(m.meta.question_kind || "")} · ${esc(m.meta.concept || "")} · ${esc(m.meta.learner_mood || "")}${m.meta.needs_adult ? " · ⚠️" : ""}` : m.role === "tutor" && m.output_tokens ? `${m.input_tokens}+${m.output_tokens} tok · ${m.latency_ms} ms` : ""}</td></tr>`).join("") || `<tr><td colspan="5" class="faint">No conversations yet.</td></tr>`}</tbody></table></div>
      <p><a class="btn" href="/api/parent/export/tutor_messages.csv">⬇ Export CSV</a></p></div>`;
  body.querySelector("#t-save").onclick = async () => {
    await api("/api/parent/tutor/settings", { method: "POST", body: { enabled: body.querySelector("#t-en").checked,
      daily_limit: +body.querySelector("#t-lim").value, allow_snippets: body.querySelector("#t-snip").checked } });
    toast("Tutor settings saved"); tutor(body);
  };
  body.querySelector("#t-test").onclick = async () => {
    const out = body.querySelector("#t-testout"); out.textContent = "Testing…";
    const r = await api("/api/parent/tutor/test", { method: "POST" });
    out.textContent = r.ok ? `✅ Connected (${r.model}, ${r.ms} ms): "${r.reply}"` : `❌ ${r.error}`;
  };
  const { col, grid } = chartSetup();
  if (body.querySelector("#t-concepts")) {
    const ks = Object.keys(s.by_concept);
    makeChart(body.querySelector("#t-concepts"), { type: "bar",
      data: { labels: ks.map((k) => state.curriculum.concepts[k] || k), datasets: [{ label: "Questions", data: ks.map((k) => s.by_concept[k]), backgroundColor: col[0], borderRadius: 4, maxBarThickness: 18 }] },
      options: baseOpts(grid, { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: grid } }, y: { grid: { display: false } } } }) });
  }
  if (body.querySelector("#t-kinds")) {
    const ks = Object.keys(s.by_kind);
    makeChart(body.querySelector("#t-kinds"), { type: "bar",
      data: { labels: ks.map((k) => kindLabel[k] || k), datasets: [{ label: "Questions", data: ks.map((k) => s.by_kind[k]), backgroundColor: col[0], borderRadius: 4, maxBarThickness: 18 }] },
      options: baseOpts(grid, { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: grid } }, y: { grid: { display: false } } } }) });
  }
}

// ---------------------------------------------------------------- activity timeline (learner's audit trail)
async function timeline(body) {
  const d = await api(`/api/parent/timeline/${sel}?limit=300`);
  const icon = { "code.run": "▶", "check.pass": "✅", "check.fail": "❌", "hint.open": "💡", "solution.peek": "🫣", "idea.add": "💭", "remix.submit": "🎛️", "reflection.add": "⭐", "session.start": "🟢", "code.reset": "↺", "learner.update": "✏️", "learner.create": "🐣", "tutor.chat": "🤖", "tutor.review": "🔍", "tutor.error_help": "🐛🤖" };
  body.innerHTML = `<div class="card"><h3>Everything he did, newest first</h3><div class="tscroll" style="max-height:700px"><table class="t"><thead><tr><th>When</th><th>Action</th><th>Where</th><th>Details</th></tr></thead>
    <tbody>${d.rows.map((a) => `<tr><td style="white-space:nowrap">${fmtTime(a.ts)}</td><td><span class="action">${esc(a.action)}</span></td><td>${esc(a.entity_id || "")}</td><td class="details">${fmtDetails(a.details)}</td></tr>`).join("")}</tbody></table></div></div>`;
}

// ---------------------------------------------------------------- audit log
async function audit(body) {
  const params = new URLSearchParams(location.hash.split("?")[1] || "");
  const q = new URLSearchParams();
  ["actor", "action", "text"].forEach((k) => params.get(k) && q.set(k, params.get(k)));
  const days = +(params.get("days") || 0);
  if (days) q.set("since", Date.now() / 1000 - days * 86400);
  const page = +(params.get("page") || 0);
  q.set("limit", 100); q.set("offset", page * 100);
  const d = await api(`/api/parent/audit?${q}`);
  body.innerHTML = `<div class="card"><h3>Audit log</h3><p class="muted" style="margin-top:0">Append-only record of every meaningful action by learners, the parent, and the system — with timestamp, actor, IP and browser.</p>
    <form class="row" id="af">
      <select name="actor"><option value="">All actors</option>${d.facets.actors.map((a) => `<option ${params.get("actor") === a.actor ? "selected" : ""}>${esc(a.actor)}</option>`).join("")}</select>
      <select name="action"><option value="">All actions</option>${d.facets.actions.map((a) => `<option value="${esc(a.action)}" ${params.get("action") === a.action ? "selected" : ""}>${esc(a.action)} (${a.n})</option>`).join("")}</select>
      <select name="days"><option value="0">All time</option>${[1, 7, 30].map((n) => `<option value="${n}" ${days === n ? "selected" : ""}>Last ${n} day${n > 1 ? "s" : ""}</option>`).join("")}</select>
      <input name="text" placeholder="Search details…" value="${esc(params.get("text") || "")}"><button class="btn primary">Filter</button>
      <span class="spacer"></span><a class="btn" href="/api/parent/export/audit_log.csv">⬇ Export CSV</a></form>
    <p class="faint">${d.total} matching events</p>
    <div class="tscroll" style="max-height:640px"><table class="t"><thead><tr><th>#</th><th>Time</th><th>Actor</th><th>Action</th><th>Entity</th><th>Details</th><th>IP</th></tr></thead>
      <tbody>${d.rows.map((a) => `<tr><td class="num faint">${a.id}</td><td style="white-space:nowrap">${fmtTime(a.ts)}</td><td>${esc(a.actor)}</td><td><span class="action">${esc(a.action)}</span></td>
        <td>${esc(a.entity || "")} ${esc(a.entity_id || "")}</td><td class="details">${fmtDetails(a.details)}</td><td class="faint">${esc(a.ip || "")}</td></tr>`).join("")}</tbody></table></div>
    <div class="row" style="margin-top:10px">${page ? `<button class="btn" data-pg="${page - 1}">← Newer</button>` : ""}${(page + 1) * 100 < d.total ? `<button class="btn" data-pg="${page + 1}">Older →</button>` : ""}</div></div>`;
  const nav = (extra) => {
    const f = new FormData(body.querySelector("#af"));
    const p = new URLSearchParams();
    for (const [k, v] of f) if (v && v !== "0") p.set(k, v);
    Object.entries(extra).forEach(([k, v]) => p.set(k, v));
    location.hash = `#/parent/audit?${p}`;
  };
  body.querySelector("#af").onsubmit = (e) => { e.preventDefault(); nav({}); };
  body.querySelectorAll("[data-pg]").forEach((b) => b.onclick = () => nav({ page: b.dataset.pg }));
}

// ---------------------------------------------------------------- monitoring
async function monitoring(body) {
  const params = new URLSearchParams(location.hash.split("?")[1] || "");
  const hours = +(params.get("hours") || 24);
  const m = await api(`/api/parent/monitoring?hours=${hours}`);
  const h = m.health;
  const up = h.uptime_sec > 86400 ? `${Math.floor(h.uptime_sec / 86400)}d ${Math.floor((h.uptime_sec % 86400) / 3600)}h` : `${Math.floor(h.uptime_sec / 3600)}h ${Math.floor((h.uptime_sec % 3600) / 60)}m`;
  body.innerHTML = `
    <div class="row" style="margin-bottom:12px"><span><span class="health-dot"></span><b>System healthy</b></span><span class="faint">auto-refreshes every 15s</span><span class="spacer"></span>
      <select id="hrs">${[1, 6, 24, 168].map((n) => `<option value="${n}" ${n === hours ? "selected" : ""}>Last ${n < 168 ? n + "h" : "7 days"}</option>`).join("")}</select></div>
    <div class="kpis five">
      ${kpi(up, "Uptime", `since ${fmtTime(h.started_at)}`)}
      ${kpi(m.http.total, "API requests", `${m.http_5xx} server errors`)}
      ${kpi(m.runner.runs, "Programs run", `p50 ${m.runner.p50_ms ?? "—"} ms · p95 ${m.runner.p95_ms ?? "—"} ms`)}
      ${kpi(m.checker.checks, "Checks", `pass rate ${pct(m.checker.pass_rate)} · p95 ${m.checker.p95_ms ?? "—"} ms`)}
      ${kpi(m.runner.killed + m.runner.output_limit + m.checker.timeouts, "Runaway programs stopped", `${m.runner.killed} time limit · ${m.runner.output_limit} output flood · ${m.checker.timeouts} check timeouts`)}
      ${kpi(m.error_count_24h, "Server exceptions (24h)", `${m.checker.internal_errors} checker errors`)}
      ${kpi(`${(h.db_bytes / 1e6).toFixed(2)} MB`, "Database size", `${h.disk_free_gb} GB disk free`)}
      ${kpi(h.rss_mb ? `${h.rss_mb} MB` : "—", "Server memory (peak)", `Python ${h.python} · pid ${h.pid}`)}
      ${kpi(m.tutor.calls, "AI tutor calls", `avg ${m.tutor.avg_ms ?? "—"} ms · p95 ${m.tutor.p95_ms ?? "—"} ms · ${m.tutor.errors} errors · ${m.tutor.refused} declined`)}
      ${kpi((m.tutor.tokens_in + m.tutor.tokens_out).toLocaleString(), "AI tutor tokens", `${m.tutor.tokens_in.toLocaleString()} in · ${m.tutor.tokens_out.toLocaleString()} out`)}
    </div>
    <div class="grid g2">
      <div class="card"><h3>API requests (per 10 min)</h3><div class="chart-box"><canvas id="m-http"></canvas></div></div>
      <div class="card"><h3>Program runs & checks (per 10 min)</h3><div class="chart-box"><canvas id="m-run"></canvas></div></div>
    </div>
    <div class="grid g2" style="margin-top:16px">
      <div class="card"><h3>Endpoints</h3><div class="tscroll" style="max-height:360px"><table class="t"><thead><tr><th>Route</th><th class="num">Count</th><th class="num">Avg ms</th><th class="num">p95 ms</th><th class="num">Max ms</th></tr></thead>
        <tbody>${m.http.routes.map((r) => `<tr><td><code>${esc(r.route)}</code></td><td class="num">${r.count}</td><td class="num">${r.avg_ms}</td><td class="num">${r.p95_ms ?? "—"}</td><td class="num">${r.max_ms}</td></tr>`).join("")}</tbody></table></div></div>
      <div class="card"><h3>Server exceptions</h3><div class="tscroll" style="max-height:360px"><table class="t"><thead><tr><th>Time</th><th>Where</th><th>Message</th></tr></thead>
        <tbody>${m.errors.map((e) => `<tr><td>${fmtTime(e.ts)}</td><td>${esc(e.source)}</td><td><a href="#" data-err="${e.id}">${esc(e.message)}</a></td></tr>`).join("") || `<tr><td colspan="3" class="faint">No exceptions. 🎉</td></tr>`}</tbody></table></div>
        <pre id="errdetail" class="hidden" style="max-height:260px"></pre></div>
    </div>
    <div class="card" style="margin-top:16px"><h3>Runtime</h3><table class="t"><tbody>
      <tr><td>Platform</td><td>${esc(h.platform)}</td></tr><tr><td>Database</td><td><code>${esc(h.db_path)}</code></td></tr>
      <tr><td>Active programs right now</td><td>${m.gauges["runner.active"] ?? 0}</td></tr>
      <tr><td>Health endpoint</td><td><a href="/api/health" target="_blank">/api/health</a></td></tr></tbody></table></div>`;
  const { col, grid } = chartSetup();
  const ts = (arr) => arr.map((p) => ({ x: p.t * 1000, y: p.v }));
  const xTime = { type: "linear", ticks: { callback: (v) => new Date(v).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }), maxTicksLimit: 8 }, grid: { display: false } };
  makeChart(body.querySelector("#m-http"), {
    type: "line", data: { datasets: [{ label: "Requests", data: ts(m.http.series), borderColor: col[0], backgroundColor: col[0], borderWidth: 2, pointRadius: 0, tension: 0.2 }] },
    options: baseOpts(grid, { plugins: { legend: { display: false } }, scales: { x: xTime, y: { beginAtZero: true, grid: { color: grid } } } }),
  });
  makeChart(body.querySelector("#m-run"), {
    type: "line", data: { datasets: [
      { label: "Program runs", data: ts(m.runner_series), borderColor: col[0], backgroundColor: col[0], borderWidth: 2, pointRadius: 0, tension: 0.2 },
      { label: "Checks", data: ts(m.checker_series), borderColor: col[1], backgroundColor: col[1], borderWidth: 2, pointRadius: 0, tension: 0.2, borderDash: [5, 4] }] },
    options: baseOpts(grid, { scales: { x: xTime, y: { beginAtZero: true, grid: { color: grid } } } }),
  });
  body.querySelector("#hrs").onchange = (e) => { location.hash = `#/parent/monitoring?hours=${e.target.value}`; };
  body.querySelectorAll("[data-err]").forEach((a) => a.onclick = async (e) => {
    e.preventDefault();
    const d = await api(`/api/parent/errors/${a.dataset.err}`);
    const pre = body.querySelector("#errdetail"); pre.classList.remove("hidden"); pre.textContent = d.detail;
  });
  const timer = setInterval(() => {
    if (!location.hash.startsWith("#/parent/monitoring")) return clearInterval(timer);
    if (document.visibilityState === "visible") monitoring(body).then(() => clearInterval(timer));
  }, 15000);
}

// ---------------------------------------------------------------- data
async function data(body) {
  const d = await api("/api/parent/data");
  body.innerHTML = `
    <div class="card"><h3>Data catalog</h3><p class="muted" style="margin-top:0">Everything PyQuest stores, all locally in one SQLite file on this computer. Nothing is sent anywhere.</p>
      <div class="tscroll"><table class="t"><thead><tr><th>Table</th><th>What it holds</th><th class="num">Rows</th><th>First</th><th>Last</th><th>Export</th></tr></thead>
      <tbody>${d.tables.map((t) => `<tr><td><a href="#" data-t="${t.table}"><code>${t.table}</code></a></td><td class="muted">${esc(t.description)}</td><td class="num">${t.rows}</td>
        <td>${t.first ? fmtTime(t.first) : "—"}</td><td>${t.last ? fmtTime(t.last) : "—"}</td>
        <td>${t.table === "settings" ? "—" : `<a href="/api/parent/export/${t.table}.csv">CSV</a> · <a href="/api/parent/export/${t.table}.json">JSON</a>`}</td></tr>`).join("")}</tbody></table></div>
      <div class="row" style="margin-top:12px"><a class="btn primary" href="/api/parent/backup">⬇ Download full backup (.db)</a></div></div>
    <div class="grid g2" style="margin-top:16px">
      <div class="card"><h3>Data collected per day</h3><div class="chart-box"><canvas id="d-daily"></canvas></div></div>
      <div class="card"><h3>Data quality</h3><table class="t"><tbody>
        <tr><td>Runs without a learner</td><td class="num">${d.quality.runs_without_learner}</td></tr>
        <tr><td>Orphaned progress rows</td><td class="num">${d.quality.orphan_progress}</td></tr>
        <tr><td>Learning sessions active now</td><td class="num">${d.quality.sessions_open}</td></tr></tbody></table>
        <h3 style="margin-top:16px">Retention</h3><p class="muted">Prune bulky telemetry (run-time code snapshots and system metrics) older than N days. Progress, checks, ideas, and the audit log are kept.</p>
        <div class="row"><input id="ret" type="number" min="7" value="90" style="width:100px"> days <button class="btn" id="prune">Prune now</button></div></div>
    </div>
    <div class="card" style="margin-top:16px" id="browser"><h3>Browse a table</h3><p class="faint">Click a table name above.</p></div>`;
  const { col, grid } = chartSetup();
  const days = [...new Set(d.daily.map((r) => r.d))].sort();
  const kinds = ["runs", "checks", "hints", "snapshots", "audit"];
  makeChart(body.querySelector("#d-daily"), {
    type: "bar",
    data: { labels: days.map((x) => x.slice(5)), datasets: kinds.map((k, i) => ({ label: k, data: days.map((day) => d.daily.find((r) => r.d === day && r.k === k)?.n || 0), backgroundColor: col[i], borderRadius: 2, maxBarThickness: 22 })) },
    options: baseOpts(grid, { scales: { x: { stacked: true, grid: { display: false } }, y: { stacked: true, beginAtZero: true, grid: { color: grid } } } }),
  });
  body.querySelector("#prune").onclick = async () => {
    const n = +body.querySelector("#ret").value;
    if (!confirm(`Delete run snapshots and metrics older than ${n} days?`)) return;
    const r = await api("/api/parent/retention", { method: "POST", body: { days: n } });
    toast(`Pruned ${r.snapshots_deleted} snapshots and ${r.metrics_deleted} metric rows.`);
    data(body);
  };
  body.querySelectorAll("[data-t]").forEach((a) => a.onclick = (e) => { e.preventDefault(); browse(body.querySelector("#browser"), a.dataset.t, 0); });
}

async function browse(host, table, offset) {
  const d = await api(`/api/parent/data/${table}?limit=50&offset=${offset}`);
  const cell = (v) => { const s = v === null ? "" : String(v); return esc(s.length > 140 ? s.slice(0, 140) + "…" : s); };
  host.innerHTML = `<div class="row"><h3 style="margin:0">${esc(table)}</h3><span class="faint">${offset + 1}–${Math.min(offset + 50, d.total)} of ${d.total}</span><span class="spacer"></span>
    ${offset ? `<button class="btn small" data-o="${offset - 50}">← Prev</button>` : ""}${offset + 50 < d.total ? `<button class="btn small" data-o="${offset + 50}">Next →</button>` : ""}</div>
    <div class="tscroll" style="margin-top:10px"><table class="t"><thead><tr>${d.columns.map((c) => `<th>${esc(c)}</th>`).join("")}</tr></thead>
    <tbody>${d.rows.map((r) => `<tr>${d.columns.map((c) => `<td>${c === "ts" || c.endsWith("_at") || c === "last_seen" ? (r[c] ? fmtTime(r[c]) : "") : cell(r[c])}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  host.querySelectorAll("[data-o]").forEach((b) => b.onclick = () => browse(host, table, +b.dataset.o));
  host.scrollIntoView({ behavior: "smooth" });
}

// ---------------------------------------------------------------- settings
async function settings(body) {
  const l = learners.find((x) => x.id === sel);
  body.innerHTML = `<div class="grid g2">
    ${l ? `<div class="card settings-card"><h3>${esc(l.name)}</h3>
      <label class="s-field"><span>Plan start date</span><input type="date" id="sd" value="${l.start_date}"></label>
      <p class="muted small">The 6-week schedule, and whether he's ahead or behind, is measured from this date.</p>
      <button class="btn primary" id="save">Save</button>
      <div class="danger-zone"><h3>Delete learner</h3><p class="muted small">Permanently delete ${esc(l.name)} and all of their progress, code and analytics. The audit log keeps a record that it happened.</p>
        <button class="btn danger" id="del">Delete ${esc(l.name)}'s data</button></div></div>` : ""}
    <div class="card settings-card"><h3>Parent PIN</h3>
      <div class="s-inline"><label class="s-field"><span>New PIN</span><input type="password" id="np" placeholder="••••" inputmode="numeric" autocomplete="new-password"></label><button class="btn" id="chg">Change PIN</button></div>
      <label class="s-field"><span>Dashboard theme</span><select id="pt"><option value="">Follow system</option><option value="light">Light</option><option value="dark">Dark</option></select></label>
      <h3 style="margin-top:8px">Curriculum reference</h3><p class="muted small">Every mission's reference solution and hints, for helping when he's stuck.</p>
      <select id="sol">${state.curriculum.projects.flatMap((p) => [...p.steps, p.boss].map((s) => `<option value="${p.id}/${s.id}">${p.emoji} ${esc(p.title)} — ${esc(s.title)}</option>`)).join("")}</select>
      <button class="btn" id="showsol">Show</button><pre id="solout" class="hidden"></pre></div></div>`;
  body.querySelector("#save")?.addEventListener("click", async () => {
    await api(`/api/learners/${sel}`, { method: "PATCH", body: { start_date: body.querySelector("#sd").value } });
    toast("Saved"); reportCache = {};
  });
  body.querySelector("#del")?.addEventListener("click", async () => {
    if (prompt(`Type ${l.name} to confirm deleting all of their data`) !== l.name) return;
    await api(`/api/parent/learners/${sel}`, { method: "DELETE" });
    if (state.learner?.id === sel) { state.learner = null; try { localStorage.removeItem("pq_learner"); } catch (e) { /* */ } }
    toast("Deleted"); sel = null; location.hash = "#/parent/overview";
  });
  body.querySelector("#chg").onclick = async () => {
    try { await api("/api/parent/pin", { method: "POST", body: { pin: body.querySelector("#np").value } }); toast("PIN changed"); } catch (e) { toast(esc(e.message)); }
  };
  const pt = body.querySelector("#pt");
  try { pt.value = localStorage.getItem("pq_ptheme") || ""; } catch (e) { /* */ }
  pt.onchange = () => {
    try { localStorage.setItem("pq_ptheme", pt.value); } catch (e) { /* */ }
    if (pt.value) document.documentElement.dataset.ptheme = pt.value; else delete document.documentElement.dataset.ptheme;
  };
  body.querySelector("#showsol").onclick = async () => {
    const [p, s] = body.querySelector("#sol").value.split("/");
    const d = await api(`/api/parent/solution/${p}/${s}`);
    const pre = body.querySelector("#solout"); pre.classList.remove("hidden");
    pre.textContent = `${d.solution}\n\n# Hints:\n${d.hints.map((h, i) => `# ${i + 1}. ${h}`).join("\n")}`;
  };
}
