// Kid-facing screens.
import { api, celebrate, chartDefaults, el, esc, fmtMin, makeChart, modal, seriesColors, setContext, sfx, state, toast } from "./core.js";
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
  const g = s.guide;
  const pos = g.position;
  const done = s.projects.filter((p) => p.complete).length;
  const steps = s.projects.reduce((a, p) => a + p.steps_done, 0), total = s.projects.reduce((a, p) => a + p.steps_total, 0);
  const cur = pos ? project(pos.project) : null;
  const greet = ["Ready to code?", "Let's build something awesome!", "Your Python powers are growing!", "Adventure awaits!"][new Date().getDate() % 4];
  app.innerHTML = `
    <div class="hello"><div class="av">${state.learner.avatar}</div>
      <div><h1>Hey ${esc(state.learner.name)}! 👋</h1><div class="muted" style="font-size:1.1rem">${greet}</div></div></div>
    <div class="grid g2">
      ${cur ? `<a class="card continue-card" href="#/code/${pos.project}/${pos.step}" style="text-decoration:none">
        <div class="big-emoji">${cur.emoji}</div>
        <div><div style="opacity:.85;font-weight:700">Week ${cur.week} · ${esc(cur.title)}</div>
        <h2 style="margin:4px 0">${esc(pos.step_title)}</h2><span class="btn primary">Continue ▶</span></div></a>`
      : `<div class="card continue-card"><div class="big-emoji">🎓</div><div><h2>Quest complete!</h2><p>You finished all 12 projects. Legend.</p>
        <a class="btn primary" href="#/playground">Open Playground</a></div></div>`}
      <div class="card"><div class="grid g4" style="grid-template-columns:repeat(4,1fr)">
        <div class="stat"><div class="num">${done}/12</div><div class="lbl">Projects</div></div>
        <div class="stat"><div class="num">${s.level.xp}</div><div class="lbl">XP</div></div>
        <div class="stat"><div class="num">🔥${s.streak.current}</div><div class="lbl">Day streak</div></div>
        <div class="stat"><div class="num">${s.today_minutes}</div><div class="lbl">Min today</div></div></div>
        <div style="margin-top:14px"><div class="row"><b>Quest progress</b><span class="spacer"></span><span class="muted">${steps}/${total} missions · ${esc(g.schedule.status)}</span></div>
        <div class="progress" style="margin-top:6px"><i style="width:${total ? (steps / total) * 100 : 0}%"></i></div></div>
      </div>
    </div>
    <div class="grid g2" style="margin-top:16px">
      <div class="card"><h3>🧭 Your guide says…</h3><div class="guide-list">${g.kid.map(guideItem).join("")}</div></div>
      <div class="card"><h3>🏅 Recent badges</h3>${badgeGrid(s.badges.filter((b) => b.earned_at).sort((a, b) => b.earned_at - a.earned_at).slice(0, 6), true)}
        <p><a href="#/journey">See all badges & your stats →</a></p></div>
    </div>
    <h2 style="margin-top:26px">🗺️ Your 6-week quest</h2>
    ${questMap(s)}`;
  bindGuide(app);
}

function guideItem(r) {
  return `<div class="guide-item"><span class="e">${r.emoji || "👉"}</span><div><b>${esc(r.title)}</b><span class="muted">${esc(r.text)}</span></div>
    <span class="spacer"></span>${r.action ? `<button class="btn small primary" data-action='${esc(JSON.stringify(r.action))}'>Go</button>` : ""}</div>`;
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

function questMap(s) {
  const pos = s.guide.position;
  const weeks = [1, 2, 3, 4, 5, 6];
  const names = { 1: "Talking to computers", 2: "Decisions & chance", 3: "Loops & art", 4: "Lists & functions", 5: "Dictionaries & worlds", 6: "Objects & your own game" };
  return `<div class="weeks">${weeks.map((w) => `<div class="week">
    <div class="week-head"><span class="wk">WEEK ${w}</span><span class="muted">${names[w]}</span></div>
    <div class="proj-row">${s.projects.filter((p) => p.week === w).map((ps) => {
      const p = project(ps.id);
      if (!p) return "";
      const cls = !ps.unlocked ? "locked" : ps.complete ? "complete" : pos && pos.project === ps.id ? "current" : "";
      return `<a class="proj ${cls}" ${ps.unlocked ? `href="#/project/${ps.id}"` : ""} title="${ps.unlocked ? "" : "Finish the previous project to unlock"}">
        <div class="pe">${ps.unlocked ? p.emoji : "🔒"}</div>
        <div style="flex:1"><h3 style="margin:0">${esc(p.title)}</h3><div class="muted" style="font-size:.9rem">${esc(p.tagline)}</div>
        <div class="progress" style="margin-top:8px;height:8px"><i style="width:${(ps.steps_done / ps.steps_total) * 100}%"></i></div></div>
        <div class="badges">${ps.complete ? "✅" : ""}${ps.boss_done ? "👾" : ""}${ps.remixed ? "🎛️" : ""}</div></a>`;
    }).join("")}</div></div>`).join("")}</div>`;
}

export async function viewMap(app) {
  setContext("_home", "map");
  const s = await refreshState();
  const side = s.guide.kid.filter((r) => r.kind === "practice");
  app.innerHTML = `<h1>🗺️ Quest Map</h1><p class="muted">12 projects, 6 weeks. Each one unlocks the next. ✅ done · 👾 boss beaten · 🎛️ remixed</p>
    ${side.length ? `<div class="card" style="margin-bottom:16px"><h3>🗡️ Recommended side quests</h3><div class="row">${side.map((r) =>
      `<a class="sidequest-node" href="#/practice/${r.action.id}">🗡️ ${esc(r.title.replace("Side quest: ", ""))}</a>`).join("")}</div></div>` : ""}
    ${questMap(s)}`;
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
  const idx = p.steps.findIndex((x) => x.id === sid);
  const track = [...p.steps.map((x, i) => ({ id: x.id, title: `${i + 1}. ${x.title}` })), { id: "boss", title: `Boss: ${bossTitle(p)}` }]
    .map((x) => `<a href="#/code/${pid}/${x.id}" class="${isDone(pid, x.id) ? "done" : ""} ${x.id === sid ? "cur" : ""} ${x.id === "boss" ? "boss" : ""}" title="${esc(x.title)}"></a>`).join("");
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
  const nextBtn = r.next ? `<a class="btn primary big" href="#/code/${r.next.project}/${r.next.step}" data-close>Next mission ▶</a>` : "";
  if (r.project_complete) {
    setTimeout(() => {
      celebrate(3);
      const m = modal(`<div class="big">${p.emoji}🏆</div><h2>You built ${esc(p.title)}!</h2>
        <p class="xp-pop">Project complete!</p><p>Every mission done. You should be proud — show someone what you made!</p>
        <div class="row" style="justify-content:center"><button class="btn primary big" id="rateit">⭐ Rate it & continue</button></div>`);
      m.node.querySelector("#rateit").onclick = () => { m.close(); reflect(p.id, true); };
    }, 700);
  } else if (r.rewards?.xp) {
    const box = app.querySelector("[data-result]");
    box.insertAdjacentHTML("beforeend", `<div class="row" style="margin-top:8px">${nextBtn}${s.id === "boss" ? `<a class="btn" href="#/project/${p.id}">Back to project</a>` : ""}</div>`);
  }
}

export function reflect(pid, thenRoute = false) {
  const p = project(pid);
  const fun = ["😴", "😐", "🙂", "😃", "🤩"], hard = ["🍰", "🙂", "🤔", "😅", "🥵"];
  let f = 0, d = 0;
  const m = modal(`<div class="big">${p.emoji}</div><h2>How was ${esc(p.title)}?</h2>
    <p><b>How fun was it?</b></p><div class="rating" data-r="fun">${fun.map((e, i) => `<button data-v="${i + 1}">${e}</button>`).join("")}</div>
    <p><b>How hard was it?</b></p><div class="rating" data-r="hard">${hard.map((e, i) => `<button data-v="${i + 1}">${e}</button>`).join("")}</div>
    <textarea id="note" rows="2" placeholder="Anything you loved or hated? (optional)"></textarea>
    <p><button class="btn primary big" id="send">Send</button> <button class="btn ghost" data-close>Skip</button></p>`);
  m.node.querySelectorAll(".rating").forEach((row) => row.querySelectorAll("button").forEach((b) => b.onclick = () => {
    row.querySelectorAll("button").forEach((x) => x.classList.toggle("sel", x === b));
    if (row.dataset.r === "fun") f = +b.dataset.v; else d = +b.dataset.v;
    sfx("click");
  }));
  m.node.querySelector("#send").onclick = async () => {
    if (!f || !d) { toast("Pick one for each! 🙏"); return; }
    const r = await api(`/api/learners/${state.learner.id}/reflection`, { method: "POST", body: { project: pid, fun: f, difficulty: d, note: m.node.querySelector("#note").value } });
    m.close();
    if (r.xp) toast(`+${r.xp} XP for reflecting! 🧠`);
    document.dispatchEvent(new CustomEvent("xp-changed"));
    if (thenRoute) {
      const m2 = modal(`<div class="big">🎉</div><h2>What next?</h2><div class="grid">
        <a class="btn primary big" href="#/code/${pid}/boss" data-close>👾 Fight the boss</a>
        <a class="btn big" href="#/remix/${pid}" data-close>🎛️ Remix it your way</a>
        <a class="btn big" href="#/map" data-close>🗺️ Next project</a></div>`);
      m2.node.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => m2.close()));
    }
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
    app.innerHTML = `<div class="workspace"><aside class="mission">
      <div class="mission-top">
        <div class="crumbs"><a href="#/practice">Side Quests</a><span>/</span>${esc(state.curriculum.concepts[pr.concept])}</div>
        <div class="eyebrow">Side quest · ${["", "Easy", "Medium", "Tricky"][pr.difficulty] || ""} · +${pr.xp} XP</div>
      </div>
      ${missionCard(pr.title, "", pr.task, [pr.concept])}
    </aside><section data-ws></section></div>`;
    disposeWorkspace();
    currentWs = createWorkspace(app.querySelector("[data-ws]"), {
      project: "_practice", step: id, mode: "practice",
      onPassed: async () => { await refreshState(); app.querySelector("[data-result]").insertAdjacentHTML("beforeend", `<p><a class="btn primary" href="#/practice">More side quests</a> <a class="btn" href="#/home">Home</a></p>`); },
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
  app.innerHTML = `<h1>🗡️ Side Quests</h1><p class="muted">Quick challenges to sharpen one skill. Your guide marks the ones that will help you most with ⭐.</p>
    <div class="grid g3">${Object.entries(byConcept).sort((a, b) => (conceptWeek[a[0]] || 9) - (conceptWeek[b[0]] || 9)).map(([c, items]) => {
      const locked = (conceptWeek[c] || 1) > learnedWeek;
      return `<div class="card ${locked ? "faint" : ""}"><h3>${esc(state.curriculum.concepts[c])} ${locked ? "🔒" : ""}</h3>
      ${locked ? `<p class="muted">Unlocks in week ${conceptWeek[c]}</p>` : `<div class="steps">${items.sort((a, b) => a.difficulty - b.difficulty).map((p) => `
        <a class="step-row ${isDone("_practice", p.id) ? "done" : ""}" href="#/practice/${p.id}"><span class="num">${isDone("_practice", p.id) ? "✓" : "⭐".repeat(p.difficulty).length}</span>
        <b style="flex:1">${esc(p.title)} ${rec.has(p.id) ? "⭐" : ""}</b><span class="pill">${"⭐".repeat(p.difficulty)}</span></a>`).join("")}</div>`}</div>`;
    }).join("")}</div>`;
}

// ---------------------------------------------------------------- playground
export async function viewPlayground(app) {
  setContext("_playground", "main");
  await refreshState();
  if (state.isStale?.()) return;
  app.innerHTML = `<div class="workspace"><aside class="mission">
    <div class="card"><h2>🧪 Playground</h2><p>Your own space to experiment. No checks, no rules — just try stuff!</p>
    <p class="muted">Everything you build here counts toward your skills in <b>My Journey</b>.</p></div>
    <div class="card"><h3>🎲 Try one of these</h3><div class="guide-list">${[
      ["🎨", "Draw a rainbow spiral", "import turtle\nt = turtle.Turtle()\nt.speed(0)\ncolors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']\nfor i in range(180):\n    t.pencolor(colors[i % 6])\n    t.forward(i * 2)\n    t.left(59)\n"],
      ["🎲", "Dice roller", "import random\nwhile True:\n    input('Press Enter to roll (or close with Stop)...')\n    print('🎲', random.randint(1, 6), random.randint(1, 6))\n"],
      ["🔤", "Word reverser", "word = input('Type a word: ')\nprint('Backwards:', word[::-1])\nprint('Shouting:', word.upper() + '!!!')\n"],
      ["⏰", "Countdown", "import time\nfor n in range(10, 0, -1):\n    print(n)\n    time.sleep(0.4)\nprint('🚀 BLAST OFF!')\n"],
    ].map(([e, t, c]) => `<div class="guide-item"><span class="e">${e}</span><b>${t}</b><span class="spacer"></span><button class="btn small" data-code="${esc(c)}">Load</button></div>`).join("")}</div></div>
    <div class="card"><h3>💾 Save an idea</h3><p class="muted">Thought of something cool? Add it to your <a href="#/ideas">idea journal</a>.</p></div>
    </aside><section data-ws></section></div>`;
  disposeWorkspace();
  currentWs = createWorkspace(app.querySelector("[data-ws]"), { project: "_playground", step: "main", mode: "playground", checkable: false });
  app.querySelectorAll("[data-code]").forEach((b) => b.onclick = () => {
    if (currentWs.getCode().trim().length > 80 && !confirm("Replace your playground code?")) return;
    currentWs.setCode(b.dataset.code);
  });
}

// ---------------------------------------------------------------- ideas & remix
function ideaMeter(a) {
  const names = ["⚡ Spark", "🧱 Builder", "💡 Inventor", "🏗️ Architect", "🧠 Mastermind"];
  return `<div class="idea-meter"><i style="width:${Math.max(4, a.score)}%"></i></div>
    <div class="idea-levels">${names.map((n, i) => `<span style="${a.level === i + 1 ? "color:var(--accent);font-weight:800" : ""}">${n}</span>`).join("")}</div>
    <div class="row" style="margin-top:8px">${Object.keys(a.concepts).map((c) => `<span class="pill ${a.new_concepts.includes(c) ? "warn" : "good"}">${esc(state.curriculum.concepts[c])}</span>`).join("")}</div>
    ${a.tips.map((t) => `<p class="muted" style="margin:.4em 0">💬 ${esc(t)}</p>`).join("")}`;
}

function ideaComposer(host, pid, onSaved) {
  host.innerHTML = `<textarea rows="4" placeholder="Describe your idea… What does it do? What happens when you win or lose? Any surprises?"></textarea>
    <div data-meter style="margin-top:10px"></div>
    <div class="row" style="margin-top:10px"><button class="btn primary" data-save>💾 Save idea</button><span class="faint">Ideas earn XP — bigger ideas earn more!</span></div>`;
  const ta = host.querySelector("textarea"), meter = host.querySelector("[data-meter]");
  let t = null;
  ta.addEventListener("input", () => {
    clearTimeout(t);
    t = setTimeout(async () => {
      if (ta.value.trim().length < 5) { meter.innerHTML = ""; return; }
      const a = await api(`/api/learners/${state.learner.id}/ideas/analyze`, { method: "POST", body: { text: ta.value } });
      meter.innerHTML = ideaMeter(a);
    }, 350);
  });
  host.querySelector("[data-save]").onclick = async () => {
    try {
      const r = await api(`/api/learners/${state.learner.id}/ideas`, { method: "POST", body: { text: ta.value, project: pid } });
      sfx("ok");
      toast(`${r.analysis.level_emoji} ${esc(r.analysis.level_name)}-level idea saved! +${r.xp} XP`);
      r.badges.forEach(showBadge);
      ta.value = ""; meter.innerHTML = "";
      document.dispatchEvent(new CustomEvent("xp-changed"));
      onSaved && onSaved(r);
    } catch (e) { toast(esc(e.message)); }
  };
}

export async function viewIdeas(app) {
  setContext("_ideas", "-");
  const data = await api(`/api/learners/${state.learner.id}/ideas`);
  app.innerHTML = `<h1>💡 Idea Journal</h1><p class="muted">Every great program starts as an idea. Write yours down — the idea-o-meter shows how ambitious it is.</p>
    <div class="grid g2"><div class="card"><h3>✍️ New idea</h3><div data-comp></div></div>
    <div class="card"><h3>📜 Your ideas (${data.ideas.length})</h3><div class="grid">${data.ideas.slice().reverse().map((i) => `<div class="idea">
      <div class="row"><b>${i.analysis.level_emoji || ""} ${esc(i.analysis.level_name || "")}</b><span class="pill">${i.score}/100</span>
      ${i.status === "built" ? `<span class="pill good">Built!</span>` : ""}<span class="spacer"></span><span class="faint">${new Date(i.ts * 1000).toLocaleDateString()}</span></div>
      <p style="margin:.4em 0">${esc(i.text)}</p></div>`).join("") || `<p class="muted">No ideas yet. What would YOU build?</p>`}</div></div></div>`;
  ideaComposer(app.querySelector("[data-comp]"), null, () => viewIdeas(app));
}

export async function viewRemix(app, pid) {
  const p = project(pid);
  setContext(pid, "remix");
  await refreshState();
  const ideas = (await api(`/api/learners/${state.learner.id}/ideas`)).ideas.filter((i) => i.project_id === pid);
  if (state.isStale?.()) return;
  app.innerHTML = `<div class="workspace"><aside class="mission">
    <div class="crumbs"><a href="#/project/${pid}">${p.emoji} ${esc(p.title)}</a> › Remix Lab</div>
    <div class="card"><h2>🎛️ Remix ${esc(p.title)}</h2><p>${esc(p.remix.prompt)}</p>
      <ul>${p.remix.ideas.map((i) => `<li>${esc(i)}</li>`).join("")}</ul></div>
    <div class="card"><h3>1️⃣ Plan your twist</h3>${ideas.length ? `<p class="muted">Your idea: <i>${esc(ideas[ideas.length - 1].text)}</i></p>` : ""}<div data-comp></div></div>
    <div class="card"><h3>2️⃣ Build it → 3️⃣ Submit</h3><p class="muted">Change the code on the right, run it, then submit. Bigger remixes earn more XP (up to 80!).</p>
      <div data-remixres></div></div>
    </aside><section data-ws></section></div>`;
  let ideaId = ideas.length ? ideas[ideas.length - 1].id : null;
  ideaComposer(app.querySelector("[data-comp]"), pid, (r) => { ideaId = r.id; });
  disposeWorkspace();
  const host = app.querySelector("[data-ws]");
  currentWs = createWorkspace(host, { project: pid, step: "remix", mode: "remix", checkable: false,
    extraButtons: `<button class="btn check" data-submit>🚀 Submit remix</button>` });
  host.querySelector("[data-submit]").onclick = async () => {
    await currentWs.save();
    const r = await api(`/api/learners/${state.learner.id}/remix`, { method: "POST", body: { project: pid, code: currentWs.getCode(), idea_id: ideaId } });
    const box = app.querySelector("[data-remixres]");
    if (!r.accepted) { sfx("fail"); box.innerHTML = `<div class="check-result fail">🤔 ${esc(r.message)}</div>`; return; }
    sfx("pass"); celebrate(1.5);
    box.innerHTML = `<div class="check-result pass">✅ ${esc(r.message)}<br>Complexity: original ${r.base_complexity} → yours <b>${r.complexity}</b>
      ${r.xp ? `<br><span class="xp-pop" style="font-size:1.3rem">+${r.xp} XP</span>` : "<br>(Make it even bigger to earn more XP!)"}</div>`;
    r.badges.forEach(showBadge);
    document.dispatchEvent(new CustomEvent("xp-changed"));
  };
}

// ---------------------------------------------------------------- my journey (kid analytics)
export async function viewJourney(app) {
  setContext("_journey", "-");
  const [s, j] = await Promise.all([refreshState(), api(`/api/learners/${state.learner.id}/journey`)]);
  const st = j.style;
  const seen = Object.fromEntries(j.errors.by_type.map((e) => [e.type, e]));
  const allMonsters = Object.values(state.curriculum.bestiary).filter((m, i, arr) => arr.findIndex((x) => x.name === m.name) === i);
  app.innerHTML = `<h1>📈 My Journey</h1>
    <div class="grid g2">
      <div class="card"><h3>🧬 Your coder type</h3><div class="persona"><div class="e">${st.persona.emoji}</div>
        <div><h2 style="margin:0">${esc(st.persona.name)}</h2><p class="muted">${esc(st.persona.desc)}</p></div></div>
        <div class="chart-box"><canvas id="c-style"></canvas></div></div>
      <div class="card"><h3>🌳 Skill tree</h3><p class="muted" style="margin-top:0">Rings fill up as you use a skill — especially when you use it on your own in the Playground or a remix.</p>
        <div class="skills">${j.mastery.map((m) => `<div class="skill ${m.started ? "" : "not-started"}" title="${m.steps_done}/${m.steps_total} missions · used on your own ${m.independent_uses}×">
        <div class="ring" style="--p:${Math.round(m.score * 100)}"><span>${Math.round(m.score * 100)}%</span></div><b>${esc(m.label)}</b><div class="faint" style="font-size:.78rem">${esc(m.status)}</div></div>`).join("")}</div></div>
    </div>
    <div class="grid g2" style="margin-top:16px">
      <div class="card"><h3>⏱️ Coding time (last 4 weeks)</h3><p class="muted" style="margin-top:0">${j.activity.total_minutes} minutes total · ${j.activity.sessions} sessions · best streak ${j.activity.streak.best} days</p>
        <div class="heat">${heat(j.activity.daily)}</div></div>
      <div class="card"><h3>📊 Your code is growing</h3><p class="muted" style="margin-top:0">Complexity of the code you passed each mission with.</p>
        <div class="chart-box"><canvas id="c-growth"></canvas></div></div>
    </div>
    <div class="card" style="margin-top:16px"><h3>🐛 Bug Bestiary</h3><p class="muted" style="margin-top:0">Every bug is a monster. Fix one and it's defeated! (${j.errors.by_type.filter((e) => e.defeated).length} of ${allMonsters.length} defeated)</p>
      <div class="bestiary">${allMonsters.map((m) => { const e = seen[m.type] || Object.values(seen).find((x) => x.name === m.name);
        return `<div class="monster ${e ? (e.defeated ? "defeated" : "") : "unseen"}"><div class="e">${e ? m.emoji : "❔"}</div>
        <div><b>${e ? esc(m.name) : "???"}</b> ${e?.defeated ? "✅" : ""}<div class="faint" style="font-size:.8rem">${e ? `Met ${e.count}× · ` + esc(m.desc) : "Not met yet"}</div></div></div>`; }).join("")}</div></div>
    <div class="grid g2" style="margin-top:16px">
      <div class="card"><h3>💡 Idea power</h3>${j.ideas.ideas.length ? `<div class="chart-box"><canvas id="c-ideas"></canvas></div>` : `<p class="muted">Save ideas in your <a href="#/ideas">journal</a> to see your idea power grow.</p>`}</div>
      <div class="card"><h3>🏅 All badges (${s.badges.filter((b) => b.earned_at).length}/${s.badges.length})</h3>${badgeGrid(s.badges)}</div>
    </div>`;
  const root = document.documentElement;
  const { text, grid } = chartDefaults(root, "--muted", "--line");
  const col = seriesColors(root);
  makeChart(app.querySelector("#c-style"), {
    type: "radar",
    data: { labels: Object.keys(st.traits), datasets: [{ label: "You", data: Object.values(st.traits).map((v) => Math.round(v * 100)),
      borderColor: col[0], backgroundColor: col[0] + "33", borderWidth: 2, pointRadius: 4, pointBackgroundColor: col[0] }] },
    options: { maintainAspectRatio: false, plugins: { legend: { display: false } },
      scales: { r: { min: 0, max: 100, ticks: { display: false }, grid: { color: grid }, angleLines: { color: grid }, pointLabels: { color: text, font: { size: 13, weight: 700 } } } } },
  });
  makeChart(app.querySelector("#c-growth"), {
    type: "line",
    data: { labels: j.code_growth.map((r, i) => i + 1), datasets: [{ label: "Complexity", data: j.code_growth.map((r) => r.complexity),
      borderColor: col[2], backgroundColor: col[2], borderWidth: 2, pointRadius: 4, tension: 0.3 }] },
    options: { maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { title: (it) => `${j.code_growth[it[0].dataIndex].project_id} / ${j.code_growth[it[0].dataIndex].step_id}` } } },
      scales: { x: { title: { display: true, text: "Missions passed" }, grid: { display: false } }, y: { beginAtZero: true, grid: { color: grid } } } },
  });
  if (j.ideas.ideas.length) makeChart(app.querySelector("#c-ideas"), {
    type: "line",
    data: { labels: j.ideas.ideas.map((i) => new Date(i.ts * 1000).toLocaleDateString()), datasets: [{ label: "Idea score", data: j.ideas.ideas.map((i) => i.score),
      borderColor: col[4], backgroundColor: col[4], borderWidth: 2, pointRadius: 5, tension: 0.3 }] },
    options: { maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100, grid: { color: grid } }, x: { grid: { display: false } } } },
  });
}

function heat(daily) {
  const max = Math.max(10, ...daily.map((d) => d.minutes));
  const col = getComputedStyle(document.documentElement).getPropertyValue("--series-3").trim() || "#199e70";
  return daily.map((d) => {
    const a = d.minutes ? 0.25 + 0.75 * (d.minutes / max) : 0;
    return `<div data-tip="${d.day}: ${d.minutes} min" style="${a ? `background:color-mix(in srgb, ${col} ${Math.round(a * 100)}%, transparent)` : ""}"></div>`;
  }).join("");
}
