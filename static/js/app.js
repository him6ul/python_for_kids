// Router & boot.
import { api, destroyCharts, sfx, state } from "./core.js";
import * as kid from "./kid.js";
import { viewParent } from "./parent.js";
import { refreshTutorStatus } from "./tutor.js";

const app = document.getElementById("app");

let routeSeq = 0;
async function route() {
  const seq = ++routeSeq;
  state.isStale = () => seq !== routeSeq;
  const [path] = location.hash.replace(/^#\/?/, "").split("?");
  const parts = path.split("/").filter(Boolean);
  const [page, a, b] = parts;
  kid.disposeWorkspace();
  destroyCharts();
  document.body.classList.remove("parent-mode");
  window.scrollTo(0, 0);

  if (page === "parent") {
    state.tutorFor = null;   // tutor settings may change here; re-check on the way back
    document.getElementById("topbar").classList.add("hidden");
    return viewParent(app, a || "overview", b);
  }
  if (state.learner && state.tutorFor !== state.learner.id) { state.tutorFor = state.learner.id; await refreshTutorStatus(); }
  if (!state.learner || page === "welcome") {
    document.getElementById("topbar").classList.add("hidden");
    return kid.viewWelcome(app);
  }
  document.getElementById("topbar").classList.remove("hidden");
  document.querySelectorAll("#kidnav a").forEach((x) => x.classList.toggle("active", x.dataset.nav === (page || "home")));
  try {
    switch (page) {
      case "map": return await kid.viewMap(app);
      case "project": return await kid.viewProject(app, a);
      case "code": return await kid.viewCode(app, a, b);
      case "practice": return await kid.viewPractice(app, a);
      case "playground": return await kid.viewPlayground(app);
      case "ideas": return await kid.viewIdeas(app);
      case "remix": return await kid.viewRemix(app, a);
      case "journey": return await kid.viewJourney(app);
      default: return await kid.viewHome(app);
    }
  } catch (e) {
    console.error(e);
    app.innerHTML = `<div class="card"><h2>😵 Oops</h2><p>${e.message}</p><a class="btn" href="#/home">Home</a></div>`;
  }
}

async function boot() {
  try {
    const pt = localStorage.getItem("pq_ptheme");
    if (pt) document.documentElement.dataset.ptheme = pt;
  } catch (e) { /* storage blocked */ }
  state.curriculum = await api("/api/curriculum");
  let saved = null;
  try { saved = localStorage.getItem("pq_learner"); } catch (e) { /* storage blocked */ }
  if (saved) {
    const learners = await api("/api/learners");
    state.learner = learners.find((l) => String(l.id) === saved) || null;
  }
  document.getElementById("whoami").onclick = () => { location.hash = "#/welcome"; state.learner = null; };
  document.getElementById("soundbtn").onclick = async () => {
    state.learner = await api(`/api/learners/${state.learner.id}`, { method: "PATCH", body: { sound: state.learner.sound ? 0 : 1 } });
    kid.renderSoundButton();
    if (state.learner.sound) sfx("click");   // a tiny confirmation that sound is back on
  };
  document.addEventListener("xp-changed", () => kid.refreshState());
  window.addEventListener("hashchange", route);
  route();
}

boot();
