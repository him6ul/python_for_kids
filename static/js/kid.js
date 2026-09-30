// Kid-facing screens.
import { api, celebrate, chartDefaults, el, esc, fmtMin, makeChart, modal, seriesColors, setContext, sfx, state, toast, xpToast } from "./core.js";
import { createWorkspace, rewards, showBadge } from "./workspace.js";

const AVATARS = ["🦊", "🐉", "🤖", "🦖", "🐙", "🦄", "🐼", "🦁", "🐸", "👾", "🚀", "🧙", "🥷", "🦈", "🐧", "🦅"];
// keys are stored per learner; labels/swatches are what the learner sees
const THEMES = { space: ["Midnight", "#1f2229", "#e4e6eb"], jungle: ["Forest", "#1e2420", "#e3e8e3"], ocean: ["Harbor", "#1d2429", "#e2e8eb"], lava: ["Paper", "#fbfaf8", "#2b2d31"] };
let currentWs = null;

export function disposeWorkspace() {
  if (currentWs) { currentWs.dispose(); currentWs = null; }
}

const project = (id) => state.curriculum.projects.find((p) => p.id === id);
const bossTitle = (p) => p.boss.title.replace(/^boss:\s*/i, "");
const progressOf = (pid, sid) => state.kidState?.progress.find((r) => r.project_id === pid && r.step_id === sid);
const isDone = (pid, sid) => progressOf(pid, sid)?.status === "done";
const pstatus = (pid) => state.kidState?.projects.find((p) => p.id === pid);

// Missions unlock one at a time; the boss and remix need every mission done. (The server enforces this too.)
function stepOpen(pid, sid) {
  const p = project(pid), ps = pstatus(pid);
  if (!p || !ps?.unlocked) return false;
  const ids = p.steps.map((x) => x.id);
  if (sid === "boss" || sid === "remix") return ids.every((i) => isDone(pid, i));
  const i = ids.indexOf(sid);
  return i >= 0 && ids.slice(0, i).every((x) => isDone(pid, x));
}
function firstOpenStep(pid) {
  const p = project(pid);
  return p.steps.find((x) => !isDone(pid, x.id))?.id || "boss";
}
async function guard(pid, sid, fallbackHash) {
  const r = await api(`/api/learners/${state.learner.id}/access?project=${encodeURIComponent(pid)}&step=${encodeURIComponent(sid)}`);
  if (r.allowed) return true;
  toast(`🔒 ${esc(r.reason)}`);
  location.replace(fallbackHash);
  return false;
}

export async function refreshState() {
  state.kidState = await api(`/api/learners/${state.learner.id}/state`);
  state.learner = state.kidState.learner;
  renderTopbar();
  return state.kidState;
}

export function renderTopbar() {
  const s = state.kidState;
  if (!s) return;
  const L = s.level;
  document.getElementById("xpchip").innerHTML =
    `<span class="lvl">Lv ${L.level}</span><span>${esc(L.title)}</span><span class="bar"><i style="width:${Math.round((L.into / L.needed) * 100)}%"></i></span>`;
  document.getElementById("xpchip").title = `${L.xp} XP total — ${L.needed - L.into} XP to next level`;
  document.getElementById("streakchip").textContent = `🔥 ${s.streak.current}`;
  document.getElementById("whoami").textContent = state.learner.avatar;
  document.getElementById("soundbtn").textContent = state.learner.sound ? "🔊" : "🔇";
  document.documentElement.dataset.theme = state.learner.theme;
}

// ---------------------------------------------------------------- welcome
export async function viewWelcome(app) {
  setContext("_home", "welcome");
  const learners = await api("/api/learners");
  const points = [
    ["12 small projects", "A chatbot, games, turtle art, a secret-code machine and your own game."],
    ["One step at a time", "Short missions with a tiny lesson, a task, and hints when you need them."],
    ["See yourself grow", "Skills, badges and streaks track your progress through the 6 weeks."],
  ];
  app.innerHTML = `<div class="welcome">
    <section class="welcome-intro">
      <div class="brandmark" aria-hidden="true">🐍</div>
      <h1>PyQuest</h1>
      <p class="lead">Learn Python in six weeks by building things you actually want to use.</p>
      <ul class="welcome-points">${points.map(([t, d], i) => `<li><span class="n">0${i + 1}</span><div><b>${t}</b><span class="muted">${d}</span></div></li>`).join("")}</ul>
      <a class="faint parent-link" href="#/parent">Parent Zone →</a>
    </section>
    <section class="card welcome-panel">
      ${learners.length ? `<h2>Who's coding today?</h2>
        <div class="learner-list">${learners.map((l) => `<button class="learner-row" data-id="${l.id}">
          <span class="av">${l.avatar}</span><span class="who"><b>${esc(l.name)}</b><span class="faint">Level ${l.level.level} · ${esc(l.level.title)}</span></span>
          <span class="go" aria-hidden="true">→</span></button>`).join("")}</div>
        <button class="btn ghost small" id="newcoder">+ New coder</button>` : ""}
      <div class="new-coder ${learners.length ? "hidden" : ""}">
        <h2>${learners.length ? "New coder" : "Create your coder"}</h2>
        <label class="field"><span>Name</span><input id="nm" placeholder="Your name" maxlength="40" autocomplete="off"></label>
        <div class="field"><span>Avatar</span>
          <div class="avatar-grid">${AVATARS.map((a, i) => `<button data-av="${a}" class="${i ? "" : "sel"}" aria-label="Avatar ${a}">${a}</button>`).join("")}</div></div>
        <div class="field"><span>Look</span>
          <div class="theme-grid">${Object.entries(THEMES).map(([k, [n, c, ink]], i) => `<button data-th="${k}" class="${i ? "" : "sel"}">
            <i style="background:${c};border-color:${ink}33"></i>${n}</button>`).join("")}</div></div>
        <button class="btn primary" id="go">Start my quest</button>
      </div>
    </section></div>`;
  let av = AVATARS[0], th = "space";
  app.querySelectorAll("[data-av]").forEach((b) => b.onclick = () => { av = b.dataset.av; app.querySelectorAll("[data-av]").forEach((x) => x.classList.toggle("sel", x === b)); sfx("click"); });
  app.querySelectorAll("[data-th]").forEach((b) => b.onclick = () => { th = b.dataset.th; document.documentElement.dataset.theme = th; app.querySelectorAll("[data-th]").forEach((x) => x.classList.toggle("sel", x === b)); });
  app.querySelectorAll(".learner-row").forEach((c) => c.onclick = () => pickLearner(learners.find((l) => l.id == c.dataset.id)));
  app.querySelector("#newcoder")?.addEventListener("click", (e) => {
    e.currentTarget.classList.add("hidden");
    app.querySelector(".new-coder").classList.remove("hidden");
    app.querySelector("#nm").focus();
  });
  const go = async () => {
    const name = app.querySelector("#nm").value.trim();
    if (!name) { const nm = app.querySelector("#nm"); nm.focus(); nm.classList.remove("shake"); void nm.offsetWidth; nm.classList.add("shake"); return; }
    const l = await api("/api/learners", { method: "POST", body: { name, avatar: av, theme: th } });
    celebrate(1);
    pickLearner(l);
  };
  app.querySelector("#go").onclick = go;
  app.querySelector("#nm").addEventListener("keydown", (e) => e.key === "Enter" && go());
}

function pickLearner(l) {
  state.learner = l;
  try { localStorage.setItem("pq_learner", l.id); } catch (e) { /* storage blocked */ }
  location.hash = "#/home";
}

// ---------------------------------------------------------------- home
export async function viewHome(app) {
  setContext("_home", "home");
  const s = await refreshState();
  if (state.isStale?.()) return;
  const g = s.guide;
  const pos = g.position;
  const done = s.projects.filter((p) => p.complete).length;
  const steps = s.projects.reduce((a, p) => a + p.steps_done, 0), total = s.projects.reduce((a, p) => a + p.steps_total, 0);
  const cur = pos ? project(pos.project) : null;
  const curStatus = cur ? pstatus(cur.id) : null;
  const hour = new Date().getHours();
  const hello = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  const today = new Date().toLocaleDateString([], { weekday: "long", month: "long", day: "numeric" });
  const tips = g.kid.filter((r) => r.kind !== "next" && r.kind !== "done");
  const recent = s.badges.filter((b) => b.earned_at).sort((a, b) => b.earned_at - a.earned_at).slice(0, 6);
  const statTile = (v, l) => `<div class="stat-tile"><div class="v">${v}</div><div class="l">${l}</div></div>`;
  const schedule = { ahead: "Ahead of plan", "on track": "On track", behind: "A little behind plan" }[g.schedule.status] || g.schedule.status;
  app.innerHTML = `<div class="page">
    <header class="page-head">
      <div class="pe">${state.learner.avatar}</div>
      <div><div class="eyebrow">${today}</div><h1>${hello}, ${esc(state.learner.name)}</h1>
        <p class="muted">${schedule} · day ${g.schedule.days_in + 1} of 42</p></div>
    </header>
    ${cur ? `<a class="card continue-card" href="#/code/${pos.project}/${pos.step}">
        <div class="pe">${cur.emoji}</div>
        <div class="cc-body"><div class="eyebrow">Up next · Week ${cur.week} · ${esc(cur.title)}</div>
          <h2>${esc(pos.step_title)}</h2>
          <div class="cc-meta"><div class="progress"><i style="width:${(curStatus.steps_done / curStatus.steps_total) * 100}%"></i></div>
            <span class="faint">${curStatus.steps_done} of ${curStatus.steps_total} missions</span></div></div>
        <span class="btn primary">Continue</span></a>`
      : `<section class="card continue-card"><div class="pe">🎓</div><div class="cc-body"><div class="eyebrow">Quest complete</div>
          <h2>You finished all 12 projects</h2><p class="muted">Keep building in the Playground, or remix a favourite.</p></div>
          <a class="btn primary" href="#/playground">Open Playground</a></section>`}
    <div class="stat-strip five">
      ${statTile(`${done}<small>/12</small>`, "Projects")}
      ${statTile(`${steps}<small>/${total}</small>`, "Missions")}
      ${statTile(s.level.xp, "XP")}
      ${statTile(`${s.streak.current}<small> day${s.streak.current === 1 ? "" : "s"}</small>`, "Streak")}
      ${statTile(`${s.today_minutes}<small> min</small>`, "Today")}
    </div>
    <div class="split home-split">
      <div class="split-main">
        <div class="sec-head"><h3>Your 6-week quest</h3><a class="faint" href="#/map">Open map →</a></div>
        ${questMap(s)}
      </div>
      <aside class="split-side">
        <section class="card"><div class="sec-head"><h3>Your guide suggests</h3></div>
          ${tips.length ? `<div class="guide-list">${tips.map(guideItem).join("")}</div>` : `<p class="empty">Nothing extra right now. Keep going with your next mission.</p>`}</section>
        <section class="card"><div class="sec-head"><h3>Recent badges</h3><a class="faint" href="#/journey">All →</a></div>
          ${recent.length ? badgeGrid(recent) : `<p class="empty">Run your first program to earn your first badge.</p>`}</section>
      </aside>
    </div></div>`;
  bindGuide(app);
}

function guideItem(r) {
  // Some tips carry their emoji in the title ("🔥 2-day streak!"); show it as the icon instead of doubling up.
  const m = r.title.match(/^(\p{Extended_Pictographic}\uFE0F?)\s*(.*)$/u);
  const icon = m ? m[1] : r.emoji || "•", title = m ? m[2] : r.title;
  return `<div class="guide-item"><span class="e">${icon}</span><div class="gi-body"><b>${esc(title)}</b><span class="muted">${esc(r.text)}</span></div>
    ${r.action ? `<button class="btn ghost xs" data-action='${esc(JSON.stringify(r.action))}'>Go</button>` : ""}</div>`;
}

function bindGuide(app) {
  app.querySelectorAll("[data-action]").forEach((b) => b.onclick = () => {
    const a = JSON.parse(b.dataset.action);
    if (a.type === "step") location.hash = `#/code/${a.project}/${a.step}`;
    else if (a.type === "practice") location.hash = `#/practice/${a.id}`;
    else if (a.type === "remix") location.hash = `#/remix/${a.project}`;
    else if (a.type === "playground") location.hash = "#/playground";
    else if (a.type === "bestiary") location.hash = "#/journey";
    else if (a.type === "reflect") reflect(a.project);
  });
}

function badgeGrid(badges, onlyEarned = false) {
  if (onlyEarned && !badges.length) return `<p class="muted">No badges yet — run your first program to earn one!</p>`;
  return `<div class="badge-grid">${badges.map((b) => `<div class="badge ${b.earned_at ? "" : "locked"}" title="${esc(b.desc)}">
    <div class="e">${b.emoji}</div><div class="n">${esc(b.name)}</div><div class="d">${esc(b.desc)}</div></div>`).join("")}</div>`;
}

const WEEK_NAMES = { 1: "Talking to computers", 2: "Decisions & chance", 3: "Loops & art", 4: "Lists & functions", 5: "Dictionaries & worlds", 6: "Objects & your own game" };

function questMap(s) {
  const pos = s.guide.position;
  return `<div class="timeline">${[1, 2, 3, 4, 5, 6].map((w) => {
    const items = s.projects.filter((p) => p.week === w);
    const done = items.every((p) => p.complete), open = items.some((p) => p.unlocked);
    const status = done ? "Done" : open ? "In progress" : "Locked";
    return `<section class="week-row ${done ? "done" : open ? "open" : "locked"}">
      <div class="week-label"><span class="dot"></span><div><div class="eyebrow">Week ${w}</div><b>${WEEK_NAMES[w]}</b>
        <span class="faint">${status}</span></div></div>
      <div class="week-projects">${items.map((ps) => {
        const p = project(ps.id);
        if (!p) return "";
        const current = pos && pos.project === ps.id;
        const tags = [ps.complete && "Done", ps.boss_done && "Boss beaten", ps.remixed && "Remixed"].filter(Boolean);
        return `<a class="proj ${ps.unlocked ? "" : "locked"} ${ps.complete ? "complete" : ""} ${current ? "current" : ""}" ${ps.unlocked ? `href="#/project/${ps.id}"` : ""}
            title="${ps.unlocked ? "" : "Finish the previous project to unlock"}">
          <div class="pe">${ps.unlocked ? p.emoji : "🔒"}</div>
          <div class="proj-body"><div class="proj-title"><b>${esc(p.title)}</b>${current ? `<span class="tag accent">Up next</span>` : ""}</div>
            <div class="muted proj-tag">${esc(p.tagline)}</div>
            <div class="proj-meta"><div class="progress"><i style="width:${(ps.steps_done / ps.steps_total) * 100}%"></i></div>
              <span class="faint">${ps.steps_done}/${ps.steps_total}</span>${tags.map((t) => `<span class="tag">${t}</span>`).join("")}</div></div></a>`;
      }).join("")}</div></section>`;
  }).join("")}</div>`;
}

export async function viewMap(app) {
  setContext("_home", "map");
  const s = await refreshState();
  if (state.isStale?.()) return;
  const side = s.guide.kid.filter((r) => r.kind === "practice");
  const steps = s.projects.reduce((a, p) => a + p.steps_done, 0), total = s.projects.reduce((a, p) => a + p.steps_total, 0);
  const done = s.projects.filter((p) => p.complete).length;
  app.innerHTML = `<div class="page">
    <header class="page-head plain"><div><div class="eyebrow">6 weeks · 12 projects</div><h1>Quest Map</h1>
      <p class="muted">${done} of 12 projects and ${steps} of ${total} missions done. Each project unlocks the next one.</p></div></header>
    ${side.length ? `<section class="card side-callout"><div class="sec-head"><h3>Recommended side quests</h3><a class="faint" href="#/practice">All side quests →</a></div>
      <div class="row">${side.map((r) => `<a class="btn small" href="#/practice/${r.action.id}">${esc(r.title.replace("Side quest: ", ""))}</a>`).join("")}</div></section>` : ""}
    ${questMap(s)}</div>`;
}

// ---------------------------------------------------------------- project page
export async function viewProject(app, pid) {
  const p = project(pid);
  if (!p) { app.innerHTML = "<p>Unknown project</p>"; return; }
  setContext(pid, "-");
  await refreshState();
  if (state.isStale?.()) return;
  const ps = pstatus(pid);
  if (!ps.unlocked) {
    app.innerHTML = `<div class="card empty-state"><div class="pe">🔒</div><h2>This project is locked</h2>
      <p class="muted">Finish the previous project to unlock it.</p><a class="btn" href="#/map">Back to the map</a></div>`;
    return;
  }
  const concept = (c) => esc(state.curriculum.concepts[c]);
  let prevDone = true, next = null;
  const stepRows = p.steps.map((s, i) => {
    const done = isDone(pid, s.id);
    const locked = !prevDone;
    if (!done && !locked && !next) next = s;
    prevDone = done;
    return `<a class="step-row ${done ? "done" : ""} ${locked ? "locked" : ""} ${next === s ? "next" : ""}" ${locked ? "" : `href="#/code/${pid}/${s.id}"`}>
      <span class="num">${done ? "✓" : i + 1}</span>
      <span class="t"><b>${esc(s.title)}</b><span class="faint">${s.concepts.map(concept).join(" · ")}</span></span>
      <span class="xp">${locked ? "Locked" : `+${s.xp} XP`}</span></a>`;
  }).join("");
  const bossDone = isDone(pid, "boss");
  const pct = Math.round((ps.steps_done / ps.steps_total) * 100);
  app.innerHTML = `<div class="page">
    <div class="crumbs"><a href="#/map">Quest Map</a><span>/</span>Week ${p.week}</div>
    <header class="page-head">
      <div class="pe">${p.emoji}</div>
      <div><div class="eyebrow">Week ${p.week} · Project ${p.order}</div><h1>${esc(p.title)}</h1><p class="muted">${esc(p.tagline)}</p></div>
    </header>
    <div class="split">
      <div class="split-main">
        <p class="story">${esc(p.story)}</p>
        <section class="card flush">
          <div class="sec-head"><h3>Missions</h3><span class="faint">${ps.steps_done} of ${ps.steps_total} done</span></div>
          <div class="steps">${stepRows}</div>
        </section>
      </div>
      <aside class="split-side">
        <section class="card">
          <div class="sec-head"><h3>Progress</h3><span class="faint">${pct}%</span></div>
          <div class="progress"><i style="width:${pct}%"></i></div>
          <dl class="facts">
            <div><dt>Estimated time</dt><dd>about ${p.expected_minutes} min</dd></div>
            <div><dt>Time spent</dt><dd>${fmtMin(ps.seconds)}</dd></div>
            <div><dt>You'll learn</dt><dd>${p.concepts.map(concept).join(", ")}</dd></div>
          </dl>
          ${next ? `<a class="btn primary block" href="#/code/${pid}/${next.id}">${ps.steps_done ? "Continue" : "Start"}: ${esc(next.title)}</a>`
                 : `<div class="done-note">✓ All missions done</div>`}
        </section>
        <section class="card">
          <div class="sec-head"><h3>Boss challenge</h3><span class="faint">+${p.boss.xp} XP</span></div>
          <p class="muted"><b>${esc(bossTitle(p))}</b> — optional and harder. It unlocks when every mission is done.</p>
          ${ps.complete ? `<a class="btn ${bossDone ? "" : "primary"} block" href="#/code/${pid}/boss">${bossDone ? "✓ Beaten — play again" : "Take on the boss"}</a>`
                        : `<button class="btn block" disabled>Locked</button>`}
        </section>
        <section class="card">
          <div class="sec-head"><h3>Remix Lab</h3>${ps.remixed ? `<span class="faint">✓ remixed</span>` : ""}</div>
          <p class="muted">${esc(p.remix.prompt)}</p>
          ${ps.complete ? `<a class="btn block" href="#/remix/${pid}">Open Remix Lab</a>` : `<button class="btn block" disabled>Finish the missions first</button>`}
        </section>
        ${ps.complete ? `<section class="card"><div class="sec-head"><h3>How was it?</h3></div>
          <p class="muted">${ps.fun ? `You rated it ${ps.fun}/5 for fun.` : "Tell us how fun and how hard this project was."}</p>
          <button class="btn block" id="rate">${ps.fun ? "Rate again" : "Rate this project"}</button></section>` : ""}
      </aside>
    </div></div>`;
  app.querySelector("#rate")?.addEventListener("click", () => reflect(pid));
}

// ---------------------------------------------------------------- mission workspace
export async function viewCode(app, pid, sid) {
  const p = project(pid);
  const s = sid === "boss" ? p.boss : p.steps.find((x) => x.id === sid);
  if (!s) { app.innerHTML = "<p>Unknown step</p>"; return; }
  setContext(pid, sid);
  await refreshState();
  if (state.isStale?.()) return;
  if (!pstatus(pid)?.unlocked) { location.hash = `#/project/${pid}`; return; }
  if (!stepOpen(pid, sid)) {
    const target = firstOpenStep(pid);
    await guard(pid, sid, target === "boss" && sid === "boss" ? `#/project/${pid}` : `#/code/${pid}/${target}`);
    return;
  }
  const idx = p.steps.findIndex((x) => x.id === sid);
  const track = [...p.steps.map((x, i) => ({ id: x.id, title: `${i + 1}. ${x.title}` })), { id: "boss", title: `Boss: ${bossTitle(p)}` }]
    .map((x) => {
      const open = stepOpen(pid, x.id);
      return `<a ${open ? `href="#/code/${pid}/${x.id}"` : ""} class="${isDone(pid, x.id) ? "done" : ""} ${x.id === sid ? "cur" : ""} ${x.id === "boss" ? "boss" : ""} ${open ? "" : "locked"}"
        title="${esc(x.title)}${open ? "" : " (locked)"}"></a>`;
    }).join("");
  app.innerHTML = `<div class="workspace">
    <aside class="mission">
      <div class="mission-top">
        <div class="crumbs"><a href="#/map">Map</a><span>/</span><a href="#/project/${pid}">${esc(p.title)}</a></div>
        <div class="step-track">${track}</div>
        <div class="eyebrow">${sid === "boss" ? "Boss challenge" : `Mission ${idx + 1} of ${p.steps.length}`} · +${s.xp} XP</div>
      </div>
      ${missionCard(sid === "boss" ? bossTitle(p) : s.title, s.learn, s.task, s.concepts)}
    </aside>
    <section data-ws></section></div>`;
  disposeWorkspace();
  currentWs = createWorkspace(app.querySelector("[data-ws]"), {
    project: pid, step: sid, mode: "step",
    onPassed: (r) => afterPass(app, p, s, r),
  });
  setupHints(app, pid, sid, s.hint_count);
}

const DIFFICULTY = ["", "Easy", "Medium", "Tricky"];
const practiceSiblings = (pr) => state.curriculum.practice.filter((x) => x.concept === pr.concept).sort((a, b) => a.difficulty - b.difficulty);

// Other side quests for the same skill, so it's easy to see what's left and hop between them.
function siblingList(pr) {
  const sibs = practiceSiblings(pr);
  if (sibs.length < 2) return "";
  const done = sibs.filter((x) => isDone("_practice", x.id)).length;
  return `<section class="card sibling-card"><div class="sec-head"><h3>More in ${esc(state.curriculum.concepts[pr.concept])}</h3><span class="faint">${done}/${sibs.length} done</span></div>
    <div class="sibling-list">${sibs.map((x) => `<a href="#/practice/${x.id}" class="${x.id === pr.id ? "cur" : ""} ${isDone("_practice", x.id) ? "done" : ""}">
      <span class="mark"></span><span class="t">${esc(x.title)}</span><span class="faint">${DIFFICULTY[x.difficulty] || ""}</span></a>`).join("")}</div></section>`;
}

// One card holding the lesson, the task and the hints, so the left column reads top to bottom.
function missionCard(title, learn, task, concepts) {
  return `<article class="card mission-card">
    <h2>${esc(title)}</h2>
    ${learn ? `<div class="learn">${learn}</div>` : ""}
    <section class="task-box"><div class="label">Your task</div>${task}
      ${concepts?.length ? `<div class="tags">${concepts.map((c) => `<span class="tag">${esc(state.curriculum.concepts[c])}</span>`).join("")}</div>` : ""}</section>
    <section class="hints-sec"><div class="label">Hints</div><div data-hints></div>
      <div class="row"><button class="btn small" data-hint>Show a hint</button><button class="btn small ghost hidden" data-peek>Show me an answer</button></div>
      <p class="faint tip">Tip: run your code first and read the output. It's usually a clue.</p></section>
  </article>`;
}

async function setupHints(app, pid, sid, count) {
  const box = app.querySelector("[data-hints]");
  const btn = app.querySelector("[data-hint]"), peek = app.querySelector("[data-peek]");
  const info = await api(`/api/learners/${state.learner.id}/hints?project=${pid}&step=${sid}`);
  let used = info.used;
  const render = (text, level) => {
    const b = el(`<div class="hint-box"><b>Hint ${level}:</b> </div>`);
    b.append(...hintNodes(text));
    box.appendChild(b);
  };
  info.opened.forEach((t, i) => render(t, i + 1));
  if (info.solution) showSolution(box, info.solution);
  const refresh = (attempts) => {
    btn.classList.toggle("hidden", used >= count);
    peek.classList.toggle("hidden", !(used >= count && used < 4 && attempts >= 3));
  };
  refresh(info.attempts);
  btn.onclick = async () => {
    const r = await api(`/api/learners/${state.learner.id}/hint`, { method: "POST", body: { project: pid, step: sid, level: used + 1 } });
    used = r.level;
    render(r.text, r.level);
    refresh(info.attempts);
  };
  peek.onclick = async () => {
    if (!confirm("Peek at an answer? You'll still learn — but you'll get less XP for this step.")) return;
    try {
      const r = await api(`/api/learners/${state.learner.id}/hint`, { method: "POST", body: { project: pid, step: sid, level: 4 } });
      used = 4; showSolution(box, r.text); refresh(99);
    } catch (e) { toast(esc(e.message)); }
  };
  app.querySelector("[data-ws]").addEventListener("checked", (e) => { info.attempts = e.detail.attempts; refresh(info.attempts); });
}

function hintNodes(text) {
  // hints may contain a code line; show code-looking hints in a <pre>
  if (/\n/.test(text) || /^[\w\s]*(print|input|for|while|if|def|import|class)\b.*[()=:]/.test(text)) {
    const pre = document.createElement("pre"); pre.textContent = text; return [pre];
  }
  return [document.createTextNode(text)];
}

function showSolution(box, code) {
  const b = el(`<div class="hint-box" style="border-color:#d55181"><b>One possible answer</b> <span class="muted">(yours can be different!)</span><pre></pre></div>`);
  b.querySelector("pre").textContent = code;
  box.appendChild(b);
}

async function afterPass(app, p, s, r) {
  app.querySelector(".step-track a.cur")?.classList.add("done");
  await refreshState();
  const nextStep = r.next ? p.steps.find((x) => x.id === r.next.step) : null;
  const nextBtn = r.next ? `<a class="btn primary small" href="#/code/${r.next.project}/${r.next.step}">Next: ${esc(nextStep?.title || "next mission")}</a>` : "";
  if (r.project_complete) {
    setTimeout(() => { celebrate(2); projectComplete(p); }, 600);
  } else if (r.rewards?.xp) {
    const box = app.querySelector("[data-result]");
    box.insertAdjacentHTML("beforeend", `<div class="next-row">${nextBtn}${s.id === "boss" ? `<a class="btn primary small" href="#/project/${p.id}">Back to project</a>` : ""}
      <a class="btn ghost small" href="#/project/${p.id}">Project overview</a></div>`);
  }
}

// A 1–5 scale with words at both ends; returns [html, getValue].
function scale(name, low, high) {
  const html = `<div class="scale-field"><div class="scale-label">${name}</div>
    <div class="scale" data-scale>${[1, 2, 3, 4, 5].map((v) => `<button type="button" data-v="${v}" aria-label="${name} ${v} of 5">${v}</button>`).join("")}</div>
    <div class="scale-ends"><span>${low}</span><span>${high}</span></div></div>`;
  return html;
}
function bindScales(root) {
  const values = {};
  root.querySelectorAll("[data-scale]").forEach((row, i) => row.querySelectorAll("button").forEach((b) => b.onclick = () => {
    row.querySelectorAll("button").forEach((x) => x.classList.toggle("sel", x === b));
    values[i] = +b.dataset.v;
    sfx("click");
  }));
  return values;
}
async function saveReflection(pid, fun, difficulty, note) {
  const r = await api(`/api/learners/${state.learner.id}/reflection`, { method: "POST", body: { project: pid, fun, difficulty, note } });
  if (r.xp) xpToast(r.xp, "Thanks for rating", "Reflecting helps tune your quest");
  document.dispatchEvent(new CustomEvent("xp-changed"));
}

// Shown once, when the last mission of a project passes: what you did, a quick optional rating, and where to go next.
function projectComplete(p) {
  const ps = pstatus(p.id);
  const xp = (state.kidState?.progress || []).filter((r) => r.project_id === p.id).reduce((a, r) => a + (r.xp || 0), 0);
  const nextProject = state.curriculum.projects.find((x) => x.order === p.order + 1);
  const m = modal(`<div class="dialog">
    <div class="dialog-head"><div class="pe">${p.emoji}</div><div><div class="eyebrow">Project complete</div><h2>You built ${esc(p.title)}</h2></div></div>
    <div class="dialog-stats"><div><b>${ps?.steps_total ?? p.steps.length}</b><span>missions</span></div><div><b>${fmtMin(ps?.seconds || 0)}</b><span>coding time</span></div><div><b>+${xp}</b><span>XP earned</span></div></div>
    <p class="muted">Every mission done. Show someone what you made!</p>
    <section class="dialog-sec"><div class="label">Quick rating <span class="faint">(optional)</span></div>
      ${scale("How fun was it?", "Meh", "Loved it")}${scale("How hard was it?", "Easy", "Really hard")}</section>
    <section class="dialog-sec"><div class="label">What next?</div>
      <div class="choice-list">
        <a class="choice" href="#/code/${p.id}/boss" data-go><b>Take on the boss</b><span class="faint">A harder, optional challenge · +${p.boss.xp} XP</span></a>
        <a class="choice" href="#/remix/${p.id}" data-go><b>Remix it your way</b><span class="faint">Add your own twist · up to 80 XP</span></a>
        ${nextProject ? `<a class="choice" href="#/project/${nextProject.id}" data-go><b>Start ${esc(nextProject.title)}</b><span class="faint">Week ${nextProject.week} · the next project</span></a>` : ""}
      </div></section>
    <div class="dialog-foot"><button class="btn ghost small" data-close>Close</button></div></div>`);
  const values = bindScales(m.node);
  m.node.querySelectorAll("[data-go]").forEach((a) => a.addEventListener("click", async (e) => {
    e.preventDefault();
    if (values[0] && values[1]) await saveReflection(p.id, values[0], values[1], "");
    m.close();
    location.hash = a.getAttribute("href");
  }));
  m.node.querySelector("[data-close]").addEventListener("click", () => { if (values[0] && values[1]) saveReflection(p.id, values[0], values[1], ""); });
}

export function reflect(pid) {
  const p = project(pid);
  const m = modal(`<div class="dialog">
    <div class="dialog-head"><div class="pe">${p.emoji}</div><div><div class="eyebrow">Rate this project</div><h2>How was ${esc(p.title)}?</h2></div></div>
    <section class="dialog-sec">${scale("How fun was it?", "Meh", "Loved it")}${scale("How hard was it?", "Easy", "Really hard")}
      <label class="field"><span>Anything you loved or didn't like? (optional)</span><textarea id="note" rows="2"></textarea></label></section>
    <p class="dialog-error faint"></p>
    <div class="dialog-foot"><button class="btn ghost small" data-close>Skip</button><button class="btn primary small" id="send">Save</button></div></div>`);
  const values = bindScales(m.node);
  m.node.querySelector("#send").onclick = async () => {
    if (!values[0] || !values[1]) { m.node.querySelector(".dialog-error").textContent = "Pick a number for both questions."; return; }
    await saveReflection(pid, values[0], values[1], m.node.querySelector("#note").value);
    m.close();
    if (location.hash.startsWith(`#/project/${pid}`)) viewProject(document.getElementById("app"), pid);
  };
}

// ---------------------------------------------------------------- side quests
export async function viewPractice(app, id) {
  const list = state.curriculum.practice;
  if (id) {
    const pr = list.find((x) => x.id === id);
    setContext("_practice", id);
    await refreshState();
    if (state.isStale?.()) return;
    if (!pr || !(await guard("_practice", id, "#/practice"))) return;
    app.innerHTML = `<div class="workspace"><aside class="mission">
      <div class="mission-top">
        <div class="crumbs"><a href="#/practice">Side Quests</a><span>/</span>${esc(state.curriculum.concepts[pr.concept])}</div>
        <div class="eyebrow">Side quest · ${DIFFICULTY[pr.difficulty] || ""} · +${pr.xp} XP</div>
      </div>
      ${missionCard(pr.title, "", pr.task, [pr.concept])}
      ${siblingList(pr)}
    </aside><section data-ws></section></div>`;
    disposeWorkspace();
    currentWs = createWorkspace(app.querySelector("[data-ws]"), {
      project: "_practice", step: id, mode: "practice",
      onPassed: async () => {
        await refreshState();
        app.querySelector(".sibling-list a.cur")?.classList.add("done");
        const sibs = practiceSiblings(pr), cnt = app.querySelector(".sibling-card .sec-head .faint");
        if (cnt) cnt.textContent = `${sibs.filter((x) => isDone("_practice", x.id)).length}/${sibs.length} done`;
        const next = practiceSiblings(pr).find((x) => x.id !== pr.id && !isDone("_practice", x.id));
        app.querySelector("[data-result]").insertAdjacentHTML("beforeend", `<div class="next-row">
          ${next ? `<a class="btn primary small" href="#/practice/${next.id}">Next: ${esc(next.title)}</a>` : ""}
          <a class="btn ${next ? "ghost" : "primary"} small" href="#/practice">All side quests</a></div>`);
      },
    });
    setupHints(app, "_practice", id, pr.hint_count);
    return;
  }
  setContext("_practice", "-");
  const s = await refreshState();
  const rec = new Set(s.guide.kid.filter((r) => r.kind === "practice").map((r) => r.action.id));
  const learnedWeek = Math.max(1, ...s.projects.filter((p) => p.unlocked).map((p) => p.week));
  const byConcept = {};
  list.forEach((p) => (byConcept[p.concept] = byConcept[p.concept] || []).push(p));
  const conceptWeek = {};
  state.curriculum.projects.forEach((p) => p.concepts.forEach((c) => { conceptWeek[c] = Math.min(conceptWeek[c] || 99, p.week); }));
  const DIFF = ["", "Easy", "Medium", "Tricky"];
  const doneCount = list.filter((p) => isDone("_practice", p.id)).length;
  const weeks = {};
  Object.entries(byConcept).forEach(([c, items]) => { (weeks[conceptWeek[c] || 1] = weeks[conceptWeek[c] || 1] || []).push([c, items]); });
  const recItems = list.filter((p) => rec.has(p.id));
  app.innerHTML = `<div class="page">
    <header class="page-head plain"><div><div class="eyebrow">Practice</div><h1>Side Quests</h1>
      <p class="muted">Short challenges that sharpen one skill at a time. ${doneCount} of ${list.length} cleared.</p></div></header>
    ${recItems.length ? `<section class="card side-callout"><div class="sec-head"><h3>Recommended for you</h3><span class="faint">Picked by your guide</span></div>
      <div class="row">${recItems.map((p) => `<a class="btn small" href="#/practice/${p.id}">${esc(p.title)}</a>`).join("")}</div></section>` : ""}
    ${Object.keys(weeks).sort((x, y) => x - y).map((w) => {
      const locked = +w > learnedWeek;
      return `<section class="quest-week ${locked ? "locked" : ""}">
        <div class="sec-head"><h3>Week ${w} · ${WEEK_NAMES[w]}</h3><span class="faint">${locked ? "🔒 Unlocks when you reach this week" : ""}</span></div>
        ${locked ? "" : `<div class="quest-grid">${weeks[w].map(([c, items]) => {
          const d = items.filter((p) => isDone("_practice", p.id)).length;
          return `<article class="card flush"><div class="sec-head"><h3>${esc(state.curriculum.concepts[c])}</h3><span class="faint">${d}/${items.length}</span></div>
            <div class="steps">${items.sort((x, y) => x.difficulty - y.difficulty).map((p) => {
              const done = isDone("_practice", p.id);
              return `<a class="step-row ${done ? "done" : ""}" href="#/practice/${p.id}"><span class="num">${done ? "✓" : ""}</span>
                <span class="t"><b>${esc(p.title)}</b><span class="faint">${DIFF[p.difficulty] || ""} · +${p.xp} XP</span></span>
                ${rec.has(p.id) ? `<span class="tag accent">Recommended</span>` : ""}</a>`;
            }).join("")}</div></article>`;
        }).join("")}</div>`}
      </section>`;
    }).join("")}</div>`;
}

// ---------------------------------------------------------------- playground
export async function viewPlayground(app) {
  setContext("_playground", "main");
  await refreshState();
  if (state.isStale?.()) return;
  const examples = [
    ["🎨", "Rainbow spiral", "Turtle art with a loop", "import turtle\nt = turtle.Turtle()\nt.speed(0)\ncolors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']\nfor i in range(180):\n    t.pencolor(colors[i % 6])\n    t.forward(i * 2)\n    t.left(59)\n"],
    ["🎲", "Dice roller", "Random numbers in a loop", "import random\nwhile True:\n    input('Press Enter to roll (or press Stop)...')\n    print('🎲', random.randint(1, 6), random.randint(1, 6))\n"],
    ["🔤", "Word reverser", "Playing with strings", "word = input('Type a word: ')\nprint('Backwards:', word[::-1])\nprint('Shouting:', word.upper() + '!!!')\n"],
    ["⏰", "Countdown", "A for loop with a pause", "import time\nfor n in range(10, 0, -1):\n    print(n)\n    time.sleep(0.4)\nprint('🚀 Blast off!')\n"],
  ];
  app.innerHTML = `<div class="workspace"><aside class="mission">
    <div class="mission-top"><div class="eyebrow">Free space · no checks</div></div>
    <article class="card mission-card">
      <h2>Playground</h2>
      <p class="muted">Your own space to experiment. There are no checks and no rules. Anything you write here still counts toward your skills in <a href="#/journey">My Journey</a>.</p>
      <section><div class="label">Start from an example</div>
        <div class="example-list">${examples.map(([e, t, d, c]) => `<button class="example-row" data-code="${esc(c)}">
          <span class="e">${e}</span><span class="t"><b>${t}</b><span class="faint">${d}</span></span><span class="go">Load</span></button>`).join("")}</div></section>
      <section class="hints-sec"><div class="label">Got an idea?</div>
        <p class="muted small">Write it down in your <a href="#/ideas">idea journal</a>, then try building the smallest version here.</p></section>
    </article>
    </aside><section data-ws></section></div>`;
  disposeWorkspace();
  currentWs = createWorkspace(app.querySelector("[data-ws]"), { project: "_playground", step: "main", mode: "playground", checkable: false });
  app.querySelectorAll("[data-code]").forEach((b) => b.onclick = () => {
    if (currentWs.getCode().trim().length > 80 && !confirm("Replace your playground code?")) return;
    currentWs.setCode(b.dataset.code);
  });
}

// ---------------------------------------------------------------- ideas & remix
const IDEA_LEVELS = ["Spark", "Builder", "Inventor", "Architect", "Mastermind"];

function ideaMeter(a) {
  const concepts = Object.keys(a.concepts);
  return `<div class="meter-head"><span class="label">Idea level</span><b>${IDEA_LEVELS[a.level - 1]}</b><span class="faint">${a.score}/100</span></div>
    <div class="idea-meter"><i style="width:${Math.max(4, a.score)}%"></i></div>
    <div class="idea-levels">${IDEA_LEVELS.map((n, i) => `<span class="${a.level === i + 1 ? "on" : ""}">${n}</span>`).join("")}</div>
    ${concepts.length ? `<div class="tags">${concepts.map((c) => `<span class="tag ${a.new_concepts.includes(c) ? "new" : ""}" title="${a.new_concepts.includes(c) ? "You haven't learned this yet" : "You know this"}">${esc(state.curriculum.concepts[c])}</span>`).join("")}</div>` : ""}
    ${a.tips.length ? `<ul class="idea-tips">${a.tips.map((t) => `<li>${esc(t)}</li>`).join("")}</ul>` : ""}`;
}

function ideaComposer(host, pid, onSaved) {
  host.innerHTML = `<textarea rows="4" placeholder="What does it do? What happens when you win or lose? Any surprises?"></textarea>
    <div data-meter class="meter-box"><p class="faint small">Start typing and the idea meter will rate how ambitious your idea is.</p></div>
    <div class="row"><button class="btn primary" data-save>Save idea</button><span class="faint small">Bigger ideas earn more XP.</span></div>`;
  const ta = host.querySelector("textarea"), meter = host.querySelector("[data-meter]");
  const blank = meter.innerHTML;
  let t = null;
  ta.addEventListener("input", () => {
    clearTimeout(t);
    t = setTimeout(async () => {
      if (ta.value.trim().length < 5) { meter.innerHTML = blank; return; }
      const a = await api(`/api/learners/${state.learner.id}/ideas/analyze`, { method: "POST", body: { text: ta.value } });
      meter.innerHTML = ideaMeter(a);
    }, 350);
  });
  host.querySelector("[data-save]").onclick = async () => {
    try {
      const r = await api(`/api/learners/${state.learner.id}/ideas`, { method: "POST", body: { text: ta.value, project: pid } });
      sfx("ok");
      xpToast(r.xp, "Idea saved", `${r.analysis.level_name}-level idea`);
      r.badges.forEach(showBadge);
      ta.value = ""; meter.innerHTML = blank;
      document.dispatchEvent(new CustomEvent("xp-changed"));
      onSaved && onSaved(r);
    } catch (e) { toast(esc(e.message)); }
  };
}

export async function viewIdeas(app) {
  setContext("_ideas", "-");
  const data = await api(`/api/learners/${state.learner.id}/ideas`);
  if (state.isStale?.()) return;
  const ideas = data.ideas.slice().reverse();
  const title = (pid) => (pid ? project(pid)?.title : null);
  app.innerHTML = `<div class="page">
    <header class="page-head plain"><div><div class="eyebrow">Idea journal</div><h1>Ideas</h1>
      <p class="muted">Every great program starts as an idea. Write yours down; the meter shows how ambitious it is.</p></div></header>
    <div class="split">
      <div class="split-main">
        <section class="card"><div class="sec-head"><h3>New idea</h3></div><div data-comp></div></section>
        <section class="card flush"><div class="sec-head"><h3>Your ideas</h3><span class="faint">${ideas.length}</span></div>
          ${ideas.length ? `<div class="idea-list">${ideas.map((i) => `<article class="idea-row">
            <div class="idea-meta"><span class="tag accent">${esc(i.analysis.level_name || "")}</span><span class="faint">${i.score}/100</span>
              ${i.status === "built" ? `<span class="tag">Built</span>` : ""}${title(i.project_id) ? `<span class="faint">· ${esc(title(i.project_id))}</span>` : ""}
              <span class="spacer"></span><span class="faint">${new Date(i.ts * 1000).toLocaleDateString([], { month: "short", day: "numeric" })}</span></div>
            <p>${esc(i.text)}</p></article>`).join("")}</div>` : `<p class="empty">No ideas yet. What would you build?</p>`}
        </section>
      </div>
      <aside class="split-side">
        <section class="card"><div class="sec-head"><h3>Idea levels</h3></div>
          <ol class="level-list">${IDEA_LEVELS.map((n, i) => `<li><b>${n}</b><span class="faint">${["One simple feature", "A couple of features", "Several features working together", "A bigger system with many parts", "An ambitious, complete game or app"][i]}</span></li>`).join("")}</ol></section>
        <section class="card"><div class="sec-head"><h3>Idea sparks</h3></div>
          <ul class="spark-list"><li>What happens when you win? When you lose?</li><li>Could something random make it replayable?</li>
            <li>Is there a score, lives or a timer?</li><li>Could a friend play against you?</li><li>What's the smallest version you could build first?</li></ul></section>
      </aside>
    </div></div>`;
  ideaComposer(app.querySelector("[data-comp]"), null, () => viewIdeas(app));
}

export async function viewRemix(app, pid) {
  const p = project(pid);
  setContext(pid, "remix");
  await refreshState();
  if (state.isStale?.() || !(await guard(pid, "remix", `#/project/${pid}`))) return;
  const ideas = (await api(`/api/learners/${state.learner.id}/ideas`)).ideas.filter((i) => i.project_id === pid);
  if (state.isStale?.()) return;
  const latest = ideas[ideas.length - 1];
  app.innerHTML = `<div class="workspace"><aside class="mission">
    <div class="mission-top">
      <div class="crumbs"><a href="#/map">Map</a><span>/</span><a href="#/project/${pid}">${esc(p.title)}</a><span>/</span>Remix Lab</div>
      <div class="eyebrow">Remix Lab · up to 80 XP</div>
    </div>
    <article class="card mission-card">
      <h2>Remix ${esc(p.title)}</h2>
      <p class="muted">${esc(p.remix.prompt)}</p>
      <section><div class="label">Ideas to try</div><ul class="spark-list">${p.remix.ideas.map((i) => `<li>${esc(i)}</li>`).join("")}</ul></section>
      <ol class="remix-steps">
        <li><b>Plan your twist</b>${latest ? `<p class="muted small">Your latest idea: “${esc(latest.text)}”</p>` : `<p class="muted small">Describe what you'll change. The meter shows how ambitious it is.</p>`}<div data-comp></div></li>
        <li><b>Build it</b><p class="muted small">Change the code on the right and run it until it works the way you want.</p></li>
        <li><b>Submit</b><p class="muted small">Press <b>Submit remix</b> above the editor. Bigger changes earn more XP.</p><div data-remixres></div></li>
      </ol>
    </article>
    </aside><section data-ws></section></div>`;
  let ideaId = ideas.length ? ideas[ideas.length - 1].id : null;
  ideaComposer(app.querySelector("[data-comp]"), pid, (r) => { ideaId = r.id; });
  disposeWorkspace();
  const host = app.querySelector("[data-ws]");
  currentWs = createWorkspace(host, { project: pid, step: "remix", mode: "remix", checkable: false,
    extraButtons: `<button class="btn check" data-submit>Submit remix</button>` });
  host.querySelector("[data-submit]").onclick = async () => {
    await currentWs.save();
    const r = await api(`/api/learners/${state.learner.id}/remix`, { method: "POST", body: { project: pid, code: currentWs.getCode(), idea_id: ideaId } });
    const box = app.querySelector("[data-remixres]");
    if (!r.accepted) { sfx("fail"); box.innerHTML = `<div class="check-result fail">Not yet. ${esc(r.message)}</div>`; return; }
    sfx("pass"); celebrate(1);
    box.innerHTML = `<div class="check-result pass"><b>${esc(r.message)}</b>
      <div class="remix-stats"><span>Complexity <b>${r.base_complexity}</b> → <b>${r.complexity}</b></span>
      <span>${r.xp ? `<b>+${r.xp} XP</b>` : "Make it bigger to earn more XP"}</span></div></div>`;
    r.badges.forEach(showBadge);
    document.dispatchEvent(new CustomEvent("xp-changed"));
  };
}

// ---------------------------------------------------------------- my journey (kid analytics)
export async function viewJourney(app) {
  setContext("_journey", "-");
  const [s, j] = await Promise.all([refreshState(), api(`/api/learners/${state.learner.id}/journey`)]);
  if (state.isStale?.()) return;
  const st = j.style;
  const seen = Object.fromEntries(j.errors.by_type.map((e) => [e.type, e]));
  const allMonsters = Object.values(state.curriculum.bestiary).filter((m, i, arr) => arr.findIndex((x) => x.name === m.name) === i);
  const defeated = j.errors.by_type.filter((e) => e.defeated).length;
  const earned = s.badges.filter((b) => b.earned_at).length;
  const started = j.mastery.filter((m) => m.started).length;
  const statTile = (v, l) => `<div class="stat-tile"><div class="v">${v}</div><div class="l">${l}</div></div>`;
  app.innerHTML = `<div class="page">
    <header class="page-head plain"><div><div class="eyebrow">Your progress</div><h1>My Journey</h1>
      <p class="muted">How your skills, habits and ideas are growing.</p></div></header>
    <div class="stat-strip">
      ${statTile(`${j.activity.total_minutes}<small> min</small>`, "Coding time")}
      ${statTile(j.activity.sessions, "Sessions")}
      ${statTile(`${j.activity.streak.best}<small> days</small>`, "Best streak")}
      ${statTile(`${started}<small>/16</small>`, "Skills started")}
      ${statTile(`${defeated}<small>/${allMonsters.length}</small>`, "Bugs defeated")}
      ${statTile(`${earned}<small>/${s.badges.length}</small>`, "Badges")}
    </div>
    <div class="split journey-split">
      <div class="split-main">
        <section class="card"><div class="sec-head"><h3>Skills</h3><span class="faint">Grows faster when you use a skill on your own</span></div>
          <div class="skill-list">${j.mastery.map((m) => `<div class="skill-row ${m.started ? "" : "not-started"}" title="${m.steps_done}/${m.steps_total} missions · used on your own ${m.independent_uses}×">
            <span class="name">${esc(m.label)}</span><div class="progress"><i style="width:${Math.round(m.score * 100)}%"></i></div>
            <span class="pct">${m.started ? `${Math.round(m.score * 100)}%` : "—"}</span><span class="state faint">${esc(m.status)}</span></div>`).join("")}</div></section>
        <section class="card"><div class="sec-head"><h3>Your code is growing</h3><span class="faint">Complexity of each passed mission</span></div>
          ${j.code_growth.length >= 2 ? `<div class="chart-box"><canvas id="c-growth"></canvas></div>`
            : `<p class="empty">Pass a couple of missions and a chart of how your code grows will appear here.</p>`}</section>
        <section class="card"><div class="sec-head"><h3>Bug Bestiary</h3><span class="faint">${defeated} of ${allMonsters.length} defeated</span></div>
          <p class="muted small">Every bug type is a monster. Fix one and it counts as defeated.</p>
          ${(() => {
            const met = allMonsters.map((m) => ({ m, e: seen[m.type] || Object.values(seen).find((x) => x.name === m.name) })).filter((x) => x.e);
            const unseen = allMonsters.length - met.length;
            return `${met.length ? `<div class="bestiary">${met.map(({ m, e }) => `<div class="monster ${e.defeated ? "defeated" : ""}"><div class="e">${m.emoji}</div>
              <div><b>${esc(m.name)}</b>${e.defeated ? ` <span class="tag">Defeated</span>` : ""}<div class="faint">Met ${e.count}× · ${esc(m.desc)}</div></div></div>`).join("")}</div>`
              : `<p class="empty">No bugs met yet. When your code crashes, the bug's monster shows up here.</p>`}
            ${met.length && unseen ? `<p class="faint small">${unseen} more to discover.</p>` : ""}`;
          })()}</section>
      </div>
      <aside class="split-side">
        <section class="card"><div class="sec-head"><h3>Your coder type</h3></div>
          <div class="persona"><div class="pe">${st.persona.emoji}</div><div><b>${esc(st.persona.name)}</b><p class="muted small">${esc(st.persona.desc)}</p></div></div>
          ${s.progress.some((r) => r.status === "done") ? `<div class="chart-box small-chart"><canvas id="c-style"></canvas></div>`
            : `<p class="empty">Finish your first mission to see your coder profile.</p>`}</section>
        <section class="card"><div class="sec-head"><h3>Coding days</h3><span class="faint">Last 4 weeks</span></div>
          ${heat(j.activity.daily)}</section>
        <section class="card"><div class="sec-head"><h3>Idea power</h3><a class="faint" href="#/ideas">Idea journal →</a></div>
          ${j.ideas.ideas.length >= 2 ? `<div class="chart-box small-chart"><canvas id="c-ideas"></canvas></div>`
            : j.ideas.ideas.length ? `<p class="muted small">Latest idea: <b>${esc(j.ideas.ideas[0].analysis?.level_name || "")}</b> (${j.ideas.ideas[0].score}/100). Save another to see a trend.</p>`
            : `<p class="empty">Save ideas in your journal to watch your idea power grow.</p>`}</section>
        <section class="card"><div class="sec-head"><h3>Badges</h3><span class="faint">${earned} of ${s.badges.length}</span></div>${badgeGrid(s.badges)}</section>
      </aside>
    </div></div>`;
  const root = document.documentElement;
  const { text, grid } = chartDefaults(root, "--muted", "--line");
  const col = seriesColors(root);
  const accent = getComputedStyle(root).getPropertyValue("--accent").trim();
  if (app.querySelector("#c-style")) makeChart(app.querySelector("#c-style"), {
    type: "radar",
    data: { labels: Object.keys(st.traits), datasets: [{ label: "You", data: Object.values(st.traits).map((v) => Math.round(v * 100)),
      borderColor: accent, backgroundColor: accent + "26", borderWidth: 2, pointRadius: 3, pointBackgroundColor: accent }] },
    options: { maintainAspectRatio: false, plugins: { legend: { display: false } },
      scales: { r: { min: 0, max: 100, ticks: { display: false }, grid: { color: grid }, angleLines: { color: grid }, pointLabels: { color: text, font: { size: 11, weight: 500 } } } } },
  });
  if (app.querySelector("#c-growth")) makeChart(app.querySelector("#c-growth"), {
    type: "line",
    data: { labels: j.code_growth.map((r, i) => i + 1), datasets: [{ label: "Complexity", data: j.code_growth.map((r) => r.complexity),
      borderColor: col[0], backgroundColor: col[0], borderWidth: 2, pointRadius: 3, tension: 0.3 }] },
    options: { maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { title: (it) => `${j.code_growth[it[0].dataIndex].project_id} / ${j.code_growth[it[0].dataIndex].step_id}` } } },
      scales: { x: { title: { display: true, text: "Missions passed" }, grid: { display: false } }, y: { beginAtZero: true, grid: { color: grid } } } },
  });
  if (app.querySelector("#c-ideas")) makeChart(app.querySelector("#c-ideas"), {
    type: "line",
    data: { labels: j.ideas.ideas.map((i) => new Date(i.ts * 1000).toLocaleDateString([], { month: "short", day: "numeric" })), datasets: [{ label: "Idea score", data: j.ideas.ideas.map((i) => i.score),
      borderColor: col[0], backgroundColor: col[0], borderWidth: 2, pointRadius: 3, tension: 0.3 }] },
    options: { maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100, grid: { color: grid } }, x: { grid: { display: false } } } },
  });
}

// Calendar of active days: 4 weeks × 7 days, Monday first, shade = minutes coded.
function heat(daily) {
  const max = Math.max(10, ...daily.map((d) => d.minutes));
  const days = daily.slice(-28);
  const lead = (new Date(days[0].day + "T00:00").getDay() + 6) % 7;
  const cells = Array(lead).fill(`<div class="pad"></div>`).concat(days.map((d) => {
    const a = d.minutes ? 0.3 + 0.7 * (d.minutes / max) : 0;
    const label = new Date(d.day + "T00:00").toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });
    return `<div data-tip="${label}: ${d.minutes} min" style="${a ? `background:color-mix(in srgb, var(--accent) ${Math.round(a * 100)}%, var(--panel2))` : ""}"></div>`;
  }));
  const total = days.reduce((a, d) => a + d.minutes, 0), active = days.filter((d) => d.minutes > 0).length;
  return `<div class="heat-head">${["M", "T", "W", "T", "F", "S", "S"].map((d) => `<span>${d}</span>`).join("")}</div>
    <div class="heat">${cells.join("")}</div>
    <p class="faint small heat-note">${active} active day${active === 1 ? "" : "s"} · ${Math.round(total)} min</p>`;
}
