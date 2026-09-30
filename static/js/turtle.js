// Renders turtle events (from app/sandbox/turtle.py) onto a canvas, animated by speed.

const W = 800, H = 600;
const SPEED_PX = { 0: Infinity, 1: 2, 2: 4, 3: 6, 4: 9, 5: 12, 6: 16, 7: 22, 8: 30, 9: 45, 10: 70 };

export class TurtleCanvas {
  constructor(wrap) {
    this.wrap = wrap;
    this.base = document.createElement("canvas");
    this.over = document.createElement("canvas");
    for (const c of [this.base, this.over]) { c.width = W * 2; c.height = H * 2; wrap.appendChild(c); }
    this.bctx = this.base.getContext("2d");
    this.octx = this.over.getContext("2d");
    this.bctx.scale(2, 2); this.octx.scale(2, 2);
    this.turbo = false;
    this.reset();
    this.loop = this.loop.bind(this);
    requestAnimationFrame(this.loop);
  }

  reset() {
    this.queue = [];
    this.cur = null;
    this.prog = 0;
    this.turtles = {};
    this.used = false;
    this.bctx.clearRect(0, 0, W, H);
    this.wrap.style.background = "#fff";
  }

  push(events) {
    this.used = true;
    this.queue.push(...events);
  }

  finishNow() { this.turbo = true; }

  X(x) { return W / 2 + x; }
  Y(y) { return H / 2 - y; }

  t(id) {
    return this.turtles[id] || (this.turtles[id] = { x: 0, y: 0, h: 0, visible: true, shape: "classic", color: "#222" });
  }

  apply(e) {
    const ctx = this.bctx;
    const t = e.id !== undefined ? this.t(e.id) : null;
    switch (e.op) {
      case "line":
        ctx.strokeStyle = e.c; ctx.lineWidth = e.w; ctx.lineCap = "round";
        ctx.beginPath(); ctx.moveTo(this.X(e.x1), this.Y(e.y1)); ctx.lineTo(this.X(e.x2), this.Y(e.y2)); ctx.stroke();
        t.x = e.x2; t.y = e.y2; t.color = e.c; break;
      case "move": t.x = e.x2; t.y = e.y2; break;
      case "turn": t.h = e.h; break;
      case "fill":
        ctx.fillStyle = e.c; ctx.beginPath();
        e.pts.forEach(([x, y], i) => (i ? ctx.lineTo(this.X(x), this.Y(y)) : ctx.moveTo(this.X(x), this.Y(y))));
        ctx.closePath(); ctx.fill(); break;
      case "dot":
        ctx.fillStyle = e.c; ctx.beginPath(); ctx.arc(this.X(e.x), this.Y(e.y), e.r / 2, 0, Math.PI * 2); ctx.fill(); break;
      case "write":
        ctx.fillStyle = e.c; ctx.font = `${Math.max(8, e.size) * 1.3}px Nunito, sans-serif`;
        ctx.textAlign = e.align === "center" ? "center" : e.align === "right" ? "right" : "left";
        ctx.fillText(e.text, this.X(e.x), this.Y(e.y)); break;
      case "stamp":
        this.drawSprite(ctx, { ...t, x: e.x, y: e.y, h: e.h, color: e.c }); break;
      case "bg": this.wrap.style.background = e.c; break;
      case "clear": case "clearall": ctx.clearRect(0, 0, W, H); break;
      case "hide": t.visible = false; break;
      case "show": t.visible = true; break;
      case "shape": t.shape = e.shape; break;
      case "new": this.t(e.id); break;
      default: break;
    }
  }

  loop() {
    let budget = this.turbo ? Infinity : null;
    let ops = 0;
    while ((this.cur || this.queue.length) && ops < 20000) {
      if (!this.cur) { this.cur = this.queue.shift(); this.prog = 0; }
      const e = this.cur;
      if (e.op === "line" || e.op === "move") {
        if (budget === null) budget = SPEED_PX[e.s] ?? 6;
        const len = Math.hypot(e.x2 - e.x1, e.y2 - e.y1);
        const remaining = len - this.prog;
        if (budget >= remaining) {
          this.apply(e);
          budget -= Math.max(remaining, e.s === 0 ? 0 : 0.5);
          this.cur = null;
        } else {
          this.prog += budget;
          budget = 0;
          break;
        }
      } else {
        this.apply(e);
        this.cur = null;
      }
      ops++;
      if (budget !== null && budget <= 0) break;
    }
    if (!this.cur && !this.queue.length) this.turbo = false;
    this.drawOverlay();
    requestAnimationFrame(this.loop);
  }

  drawOverlay() {
    const o = this.octx;
    o.clearRect(0, 0, W, H);
    // partially drawn segment
    const e = this.cur;
    if (e && (e.op === "line" || e.op === "move")) {
      const len = Math.hypot(e.x2 - e.x1, e.y2 - e.y1) || 1;
      const f = this.prog / len;
      const x = e.x1 + (e.x2 - e.x1) * f, y = e.y1 + (e.y2 - e.y1) * f;
      if (e.op === "line") {
        o.strokeStyle = e.c; o.lineWidth = e.w; o.lineCap = "round";
        o.beginPath(); o.moveTo(this.X(e.x1), this.Y(e.y1)); o.lineTo(this.X(x), this.Y(y)); o.stroke();
      }
      const t = this.t(e.id);
      t.x = x; t.y = y;
    }
    if (!this.used) return;
    for (const t of Object.values(this.turtles)) if (t.visible) this.drawSprite(o, t);
  }

  drawSprite(ctx, t) {
    ctx.save();
    ctx.translate(this.X(t.x), this.Y(t.y));
    ctx.rotate(-t.h * Math.PI / 180);
    if (t.shape === "turtle") {
      ctx.fillStyle = "#2f9e44";
      ctx.beginPath(); ctx.ellipse(0, 0, 9, 7, 0, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#69db7c";
      ctx.beginPath(); ctx.arc(11, 0, 3.5, 0, Math.PI * 2); ctx.fill();
      for (const [a, b] of [[5, 7], [5, -7], [-6, 7], [-6, -7]]) { ctx.beginPath(); ctx.arc(a, b, 2.5, 0, Math.PI * 2); ctx.fill(); }
    } else if (t.shape === "circle") {
      ctx.fillStyle = t.color; ctx.beginPath(); ctx.arc(0, 0, 7, 0, Math.PI * 2); ctx.fill();
    } else if (t.shape === "square") {
      ctx.fillStyle = t.color; ctx.fillRect(-7, -7, 14, 14);
    } else {
      ctx.fillStyle = t.color || "#222";
      ctx.strokeStyle = "#fff"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(10, 0); ctx.lineTo(-6, 6); ctx.lineTo(-3, 0); ctx.lineTo(-6, -6); ctx.closePath(); ctx.fill(); ctx.stroke();
    }
    ctx.restore();
  }

  download(name = "turtle-art.png") {
    const c = document.createElement("canvas");
    c.width = W * 2; c.height = H * 2;
    const x = c.getContext("2d");
    x.fillStyle = this.wrap.style.background || "#fff";
    x.fillRect(0, 0, c.width, c.height);
    x.drawImage(this.base, 0, 0);
    const a = document.createElement("a");
    a.href = c.toDataURL("image/png"); a.download = name; a.click();
  }
}
