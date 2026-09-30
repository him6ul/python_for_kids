// The coding workspace: editor + console + turtle canvas, used by missions, side quests, playground and remix.
import { api, celebrate, el, esc, modal, sfx, state, toast } from "./core.js";
import { TurtleCanvas } from "./turtle.js";
import { createTutor } from "./tutor.js";

export function createWorkspace(host, { project, step, mode = "step", checkable = true, onPassed, extraButtons = "" }) {
  host.innerHTML = `
    <div class="coding">
      <div class="toolbar">
        <button class="btn run" data-act="run">Run</button>
        <button class="btn stop hidden" data-act="stop">Stop</button>
        ${checkable ? `<button class="btn check" data-act="check">Check my code</button>` : ""}
        ${extraButtons}
        <span class="spacer"></span>
        ${state.tutor?.available ? `<button class="btn small ghost" data-act="tutor" title="Ask Pixel, your AI tutor">Ask Pixel</button>
        <button class="btn small ghost" data-act="review" title="Get feedback on your code">Review code</button>` : ""}
        <button class="btn ghost small" data-act="font" title="Bigger / smaller text">A±</button>
        <button class="btn ghost small" data-act="reset" title="Start this step over">↺ Reset</button>
      </div>
      <div class="pane editor-pane">
        <div class="pane-head"><span class="file">main.py</span><span class="spacer"></span><span class="saved-ind" data-saved></span></div>
        <div class="editor-wrap"></div>
      </div>
      <div class="output-area no-canvas">
        <div class="pane">
          <div class="pane-head"><span>Output</span></div>
          <div class="console" aria-live="polite"><span class="sys">Press Run to start your program. Output shows up here.</span></div>
        </div>
        <div class="pane canvas-pane hidden">
          <div class="pane-head"><span>Drawing</span><span class="spacer"></span>
            <button class="btn ghost xs" data-act="skip" title="Finish drawing instantly">Skip</button>
            <button class="btn ghost xs" data-act="save-art" title="Save picture">Save</button></div>
          <div class="canvas-body"><div class="canvas-wrap"></div></div>
        </div>
      </div>
      <div data-result></div>
    </div>`;
  const $ = (s) => host.querySelector(s);
  const cm = CodeMirror($(".editor-wrap"), {
    mode: "python", lineNumbers: true, indentUnit: 4, tabSize: 4, indentWithTabs: false, matchBrackets: true,
    autoCloseBrackets: true, styleActiveLine: true, lineWrapping: false, value: "",
    extraKeys: {
      Tab: (c) => (c.somethingSelected() ? c.indentSelection("add") : c.replaceSelection("    ", "end")),
      "Shift-Tab": (c) => c.indentSelection("subtract"),
      "Ctrl-Enter": () => run(), "Cmd-Enter": () => run(),
    },
  });
  const consoleEl = $(".console");
  const canvasWrap = $(".canvas-wrap");
  const canvasPane = $(".canvas-pane");
  const turtle = new TurtleCanvas(canvasWrap);
  let ws = null, errorMark = null, fontSize = 15, saveTimer = null, loaded = false;
  let lastRun = null;   // {output, error} of the most recent run, shared with the AI tutor
  const tutor = state.tutor?.available
    ? createTutor({ project, step, cm, getCode: () => cm.getValue(), getRun: () => lastRun }) : null;

  // ---------- load & autosave ----------
  async function load() {
    const r = await api(`/api/learners/${state.learner.id}/code?project=${encodeURIComponent(project)}&step=${encodeURIComponent(step)}`);
    cm.setValue(r.code || "");
    cm.clearHistory();
    loaded = true;
    setTimeout(() => cm.refresh(), 30);
    if (r.source === "carried") toast("📦 Your code from the last step came along!");
  }
  cm.on("change", () => {
    if (!loaded) return;
    clearError();
    $("[data-saved]").textContent = "…";
    clearTimeout(saveTimer);
    saveTimer = setTimeout(save, 1200);
  });
  async function save() {
    clearTimeout(saveTimer);
    await api(`/api/learners/${state.learner.id}/code`, { method: "PUT", body: { project, step, code: cm.getValue() } });
    $("[data-saved]").textContent = "✓ saved";
  }

  // ---------- console ----------
  function write(text, cls = "") {
    if (lastRun && cls !== "sys") lastRun.output = (lastRun.output + text).slice(-4000);
    const s = document.createElement("span");
    if (cls) s.className = cls;
    s.textContent = text;
    const inp = consoleEl.querySelector(".stdin");
    consoleEl.insertBefore(s, inp || null);
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }
  function askInput() {
    const wrap = el(`<span class="stdin"><input type="text" autocomplete="off" spellcheck="false" aria-label="Type your answer"></span>`);
    consoleEl.appendChild(wrap);
    const inp = wrap.querySelector("input");
    inp.focus();
    consoleEl.scrollTop = consoleEl.scrollHeight;
    inp.addEventListener("keydown", (e) => {
      if (e.key !== "Enter") return;
      const v = inp.value;
      wrap.remove();
      write(v + "\n", "in");
      ws && ws.readyState === 1 && ws.send(JSON.stringify({ type: "stdin", data: v }));
    });
  }
  function clearError() {
    if (errorMark !== null) { cm.removeLineClass(errorMark, "background", "cm-error-line"); errorMark = null; }
  }
  function showError(m) {
    sfx("error");
    if (lastRun) lastRun.error = { type: m.type, line: m.line, msg: m.msg };
    const card = el(`<div class="bugcard">
      <div class="m">${m.monster.emoji}</div>
      <div><b>A wild ${esc(m.monster.name)} appeared${m.line ? ` on line ${m.line}` : ""}!</b>
        <div>${esc(m.friendly)}</div>
        ${m.code_line ? `<div class="raw">line ${m.line}: ${esc(m.code_line.trim())}</div>` : ""}
        <div class="raw">${esc(m.text || m.type)}</div>
        ${tutor ? `<button class="btn small ghost" data-act="explain" style="margin-top:8px">Ask Pixel about this bug</button>` : ""}</div></div>`);
    consoleEl.appendChild(card);
    consoleEl.scrollTop = consoleEl.scrollHeight;
    if (m.line) {
      errorMark = m.line - 1;
      cm.addLineClass(errorMark, "background", "cm-error-line");
      cm.scrollIntoView({ line: errorMark, ch: 0 }, 80);
    }
  }

  // ---------- run ----------
  function setRunning(on) {
    $("[data-act=run]").classList.toggle("hidden", on);
    $("[data-act=stop]").classList.toggle("hidden", !on);
  }
  function run() {
    if (ws) return;
    save();
    clearError();
    consoleEl.innerHTML = "";
    lastRun = { output: "", error: null };
    $("[data-result]").innerHTML = "";
    turtle.reset();
    const usesTurtle = /\bimport\s+turtle|\bfrom\s+turtle\b/.test(cm.getValue());
    canvasPane.classList.toggle("hidden", !usesTurtle);
    host.querySelector(".output-area").classList.toggle("no-canvas", !usesTurtle);
    host.querySelector(".coding").classList.toggle("with-canvas", usesTurtle);
    sfx("run");
    setRunning(true);
    const proto = location.protocol === "https:" ? "wss" : "ws";
    ws = new WebSocket(`${proto}://${location.host}/ws/run`);
    ws.onopen = () => ws.send(JSON.stringify({ type: "run", learner: state.learner.id, project, step, mode, code: cm.getValue() }));
    ws.onmessage = (ev) => {
      const m = JSON.parse(ev.data);
      if (m.t === "out") write(m.d);
      else if (m.t === "err") write(m.d, "err");
      else if (m.t === "input") askInput();
      else if (m.t === "turtle") {
        if (canvasPane.classList.contains("hidden")) { canvasPane.classList.remove("hidden"); host.querySelector(".output-area").classList.remove("no-canvas"); host.querySelector(".coding").classList.add("with-canvas"); }
        turtle.push(m.e);
      } else if (m.t === "error") showError(m);
      else if (m.t === "end") {
        consoleEl.querySelector(".stdin")?.remove();
        write(m.ok ? "\n✨ Program finished." : m.reason === "stopped" ? "\n⏹ Stopped." : "\n", "sys");
        if (m.ok) sfx("ok");
      } else if (m.t === "badges") m.badges.forEach(showBadge);
    };
    ws.onclose = () => { ws = null; setRunning(false); consoleEl.querySelector(".stdin")?.remove(); };
    ws.onerror = () => write("\n[Couldn't reach the Python engine. Is the server running?]\n", "err");
  }
  function stop() {
    if (ws && ws.readyState === 1) ws.send(JSON.stringify({ type: "stop" }));
    write("\n⏹ Stopped.", "sys");
  }

  // ---------- check ----------
  async function check() {
    await save();
    const btn = $("[data-act=check]");
    btn.disabled = true;
    btn.textContent = "Checking…";
    try {
      const r = await api(`/api/learners/${state.learner.id}/check`, { method: "POST", body: { project, step, code: cm.getValue() } });
      const box = $("[data-result]");
      if (r.passed) {
        box.innerHTML = `<div class="check-result pass">${esc(r.message || "You did it!")}</div>`;
        rewards(r);
        onPassed && onPassed(r);
      } else {
        sfx("fail");
        box.innerHTML = `<div class="check-result fail">Not yet. ${esc(r.message)}
          ${r.output ? `<details><summary class="muted">What your program printed during the test</summary><pre>${esc(r.output)}</pre></details>` : ""}
          <div class="muted" style="font-weight:600;margin-top:4px">Attempt ${r.attempts}. ${r.attempts >= 3 ? "Stuck? Open a hint — that's what they're for." : "You're close — tweak and try again!"}</div>
          ${tutor && r.attempts >= 2 ? `<button class="btn small ghost" data-askcheck style="margin-top:6px">Ask Pixel why</button>` : ""}</div>`;
        box.querySelector("[data-askcheck]")?.addEventListener("click", () => tutor.ask(`The checker says: "${r.message}". What am I missing? Just give me a clue!`));
        box.firstElementChild.classList.add("shake");
      }
      host.dispatchEvent(new CustomEvent("checked", { detail: r }));
    } catch (e) {
      toast("⚠️ " + esc(e.message));
    } finally {
      btn.disabled = false;
      btn.textContent = "Check my code";
    }
  }

  host.addEventListener("click", async (e) => {
    const act = e.target.closest("[data-act]")?.dataset.act;
    if (act === "run") run();
    else if (act === "stop") stop();
    else if (act === "check") check();
    else if (act === "skip") turtle.finishNow();
    else if (act === "tutor") tutor?.toggle();
    else if (act === "review") tutor?.review();
    else if (act === "explain") tutor?.explainError(lastRun?.error || {});
    else if (act === "save-art") turtle.download();
    else if (act === "font") {
      fontSize = fontSize >= 20 ? 13 : fontSize + 2;
      host.querySelector(".CodeMirror").style.fontSize = fontSize + "px";
      cm.refresh();
    } else if (act === "reset") {
      if (!confirm("Start this step over with the starter code? (Your current code will be replaced.)")) return;
      const r = await api(`/api/learners/${state.learner.id}/code/reset`, { method: "POST", body: { project, step } });
      loaded = false; cm.setValue(r.code); loaded = true;
      save();
    }
  });

  load();
  return {
    cm, run, save, getCode: () => cm.getValue(),
    setCode: (c) => { cm.setValue(c); },
    tutor,
    dispose: () => { if (ws) ws.close(); tutor?.dispose(); save(); },
  };
}

export function showBadge(b) {
  sfx("badge");
  toast(`<span style="font-size:1.6rem">${b.emoji}</span> Badge unlocked: <b>${esc(b.name)}</b><br><span class="muted">${esc(b.desc)}</span>`, 5000);
}

export function rewards(r) {
  const rw = r.rewards || {};
  if (!rw.xp) { sfx("ok"); return; }
  sfx("pass");
  celebrate(r.project_complete ? 2 : 1);
  const bonus = (rw.bonuses || []).map((b) => `<span class="pill good">${esc(b)}</span>`).join(" ");
  toast(`<span class="xp-pop" style="font-size:1.4rem">+${rw.xp} XP</span> ${bonus}`);
  (rw.badges || []).forEach((b, i) => setTimeout(() => showBadge(b), 600 + i * 700));
  if (rw.level_up) {
    setTimeout(() => {
      sfx("level");
      celebrate(1.5);
      modal(`<div class="dialog">
        <div class="dialog-head"><div class="pe">⬆️</div><div><div class="eyebrow">Level up</div><h2>Level ${rw.level_up.level} · ${esc(rw.level_up.title)}</h2></div></div>
        <p class="muted">Your Python skills just grew. Keep going to reach level ${rw.level_up.level + 1}.</p>
        <div class="level-progress">
          <div class="lp-head"><span>Level ${rw.level_up.level + 1}</span><span class="faint">${rw.level_up.into} of ${rw.level_up.needed} XP</span></div>
          <div class="progress"><i data-w="${Math.round((rw.level_up.into / rw.level_up.needed) * 100)}" style="width:0"></i></div>
          <div class="faint lp-foot">${rw.level_up.xp} XP total · ${rw.level_up.needed - rw.level_up.into} XP to go</div>
        </div>
        <div class="dialog-foot"><button class="btn primary small" data-close>Nice</button></div></div>`);
      // let the bar fill in gently from empty once the dialog is on screen
      requestAnimationFrame(() => requestAnimationFrame(() => document.querySelectorAll(".level-progress [data-w]").forEach((b) => { b.style.width = `${Math.max(2, +b.dataset.w)}%`; })));
    }, 900);
  }
  document.dispatchEvent(new CustomEvent("xp-changed"));
}
