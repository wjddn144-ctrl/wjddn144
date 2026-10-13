import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "../../.agents/skills/anatomy/kit/iso-kit.mjs";
import * as G from "../../.agents/skills/anatomy/kit/lathe.mjs";
import { kitScript } from "../../.agents/skills/anatomy/scripts/inline-kit.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const theme = process.argv.includes("--light") ? "light" : "dark";

const WIDTH = 600;
const HEIGHT = 380;

// The model: 48 frames at 24 fps between two keyframes, value 0 → 100 %.
const FRAMES = 48;
const FPS = 24;
const PER_FRAME = 4;
const T0 = -96;
const V0 = -30;
const SPAN = 60;
const xOfFrame = (f) => T0 + f * PER_FRAME;
const yOfValue = (v) => V0 + v * SPAN;

const EASES = {
  linear: (t) => t,
  "ease-in-out": (t) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2),
  overshoot: (t) => 1 + 2.70158 * (t - 1) ** 3 + 1.70158 * (t - 1) ** 2,
};
const NAMES = Object.keys(EASES);
const START = 1;

const BASE = { x: -144, y: -82, w: 288, d: 178, r: 8 };
const BASE_H = 12;
const FOOT_H = 5;

const CAM = { x: -108, y: -44, w: 216, d: 88, r: 4 };
const CAM_Z = 8;
const CAM_TOP = 11;
const SLOT = 2.7;

const FAR_RAIL = { x: -114, y: -66, w: 228, d: 6, r: 1 };
const NEAR_RAIL = { x: -114, y: 52, w: 228, d: 6, r: 1 };
const RAIL_H = 4;
const CAR_Z = RAIL_H;
const CAR_TOP = 11;
const TOWER_TOP = 28;
const FAR_TOWER = { x: -7, y: -60, w: 14, d: 6, r: 1 };
const NEAR_TOWER = { x: -7, y: 46, w: 14, d: 6, r: 1 };
const ROD_Z = 22;
const ROD_R = 1.8;
const ROD_X = 4;
const SLIDER_Z = ROD_Z + ROD_R;
const SLIDER_H = 6;
const PIN_R = 1.2;
const ROLLER_R = 2.2;

const FRAME_STRIP = { x: -102, y: 79, w: 204, d: 7, r: 1 };
const VALUE_STRIP = { x: 123, y: -36, w: 7, d: 78, r: 1 };

// Drive: a stepper motor and an idler carry a toothed belt; the near carriage is clamped to its back run.
const PULLEY_X = 126;
const PULLEY_R = 4.4;
const BELT_T = 0.8;
const BELT_Y = 63;
const PULLEY_Y = BELT_Y + BELT_T + PULLEY_R;
const BELT_Z = 15.2;
const BELT_H = 3;
const FLANGE_R = PULLEY_R + 1.8;

const P = k.fitProjection(
  [...k.boxCorners(BASE, -BASE_H - FOOT_H, 0), [0, -60, TOWER_TOP + 4], [0, 52, TOWER_TOP + 4]],
  WIDTH,
  HEIGHT,
  { pad: 22, azimuth: 40 },
);

const at = (point) => k.iso(point, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);
const byDepth = (points) => [...points].sort((a, b) => k.depthOf([a[0], a[1], 0], P) - k.depthOf([b[0], b[1], 0], P));
const diamond = (cx, cy, r) => [[cx, cy - r], [cx + r, cy], [cx, cy + r], [cx - r, cy]];

// The slot is the curve value(time) cut into the plate: a closed outline with round ends.
function slotRing(ease) {
  const centre = [];
  for (let i = 0; i <= 96; i++) {
    const t = i / 96;
    centre.push([T0 + t * FRAMES * PER_FRAME, yOfValue(ease(t))]);
  }
  const side = (sign) =>
    centre.map(([x, y], i) => {
      const [ax, ay] = centre[Math.max(0, i - 1)];
      const [bx, by] = centre[Math.min(centre.length - 1, i + 1)];
      const len = Math.hypot(bx - ax, by - ay);
      return [x - ((by - ay) / len) * SLOT * sign, y + ((bx - ax) / len) * SLOT * sign];
    });
  const cap = (point, from, sign) => {
    const out = [];
    for (let i = 1; i < 12; i++) {
      const a = from + (sign * Math.PI * i) / 12;
      out.push([point[0] + Math.cos(a) * SLOT, point[1] + Math.sin(a) * SLOT]);
    }
    return out;
  };
  const a = side(1);
  const b = side(-1).reverse();
  const end = centre[centre.length - 1];
  const endAngle = Math.atan2(a[a.length - 1][1] - end[1], a[a.length - 1][0] - end[0]);
  const startAngle = Math.atan2(b[b.length - 1][1] - centre[0][1], b[b.length - 1][0] - centre[0][0]);
  return [...a, ...cap(end, endAngle, -1), ...b, ...cap(centre[0], startAngle, -1)];
}

function base() {
  const out = [`<path class="iso-halo" d="${k.haloOf(BASE, -BASE_H - FOOT_H, BASE_H, P)}"/>`];
  for (const [x, y] of byDepth(k.corners(BASE, 22))) {
    out.push(S(k.cylinder(x, y, 7, -BASE_H - FOOT_H, 1.6, P, 28), { tone: "lo" }));
    out.push(S(k.cylinder(x, y, 5.4, -BASE_H - FOOT_H + 1.6, FOOT_H - 1.6, P, 28), { tone: "mid" }));
  }
  out.push(S(k.slabOf(BASE, -BASE_H, BASE_H, P, 8, 1.6), { tone: "mid", inner: L(k.sideSeam(BASE, -4, P, 8), { tone: "faint" }) }));
  out.push(L(k.planOutline(k.insetPlan(BASE, 5), 0, P), { tone: "lo" }));
  const screws = k.corners(BASE, 10);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.2, 0, P, 16)).join(""), { tone: "lo" }));
  out.push(D(screws.map(([x, y]) => at([x, y, 0])), { size: 0.5 }));

  // Frame ruler: one tick per frame, a major tick every 6 frames (a quarter second at 24 fps).
  out.push(S(k.slabOf(FRAME_STRIP, 0, 0.6, P, 3), { tone: "lo", crease: "none" }));
  const ft = k.topTicks(T0, xOfFrame(FRAMES), PER_FRAME, 6, FRAME_STRIP.y + 0.8, 0.6, [2, 3.8], P);
  out.push(L(ft.minor, { tone: "lo" }), L(ft.major, { tone: "mid" }));
  out.push(D([at([FRAME_STRIP.x + 2.5, FRAME_STRIP.y + 3.5, 0.6]), at([FRAME_STRIP.x + FRAME_STRIP.w - 2.5, FRAME_STRIP.y + 3.5, 0.6])], { size: 0.45 }));

  // Value ruler: a tick every 10 %, majors at 0, 50 and 100 %, running on to 110 % for the overshoot.
  out.push(S(k.slabOf(VALUE_STRIP, 0, 0.6, P, 3), { tone: "lo", crease: "none" }));
  const vt = k.topTicks(V0, yOfValue(1.1), SPAN / 10, 5, VALUE_STRIP.x + 0.8, 0.6, [2, 3.8], P, "y");
  out.push(L(vt.minor, { tone: "lo" }), L(vt.major, { tone: "mid" }));
  out.push(D([at([VALUE_STRIP.x + 3.5, VALUE_STRIP.y + 2.5, 0.6]), at([VALUE_STRIP.x + 3.5, VALUE_STRIP.y + VALUE_STRIP.d - 2.5, 0.6])], { size: 0.45 }));

  // Keyframe studs: diamonds at the two keyframes, in time under the frame ruler and in value beside the value ruler.
  const studs = byDepth([
    [xOfFrame(0), FRAME_STRIP.y + 10.5],
    [xOfFrame(FRAMES), FRAME_STRIP.y + 10.5],
    [VALUE_STRIP.x + 13, yOfValue(0)],
    [VALUE_STRIP.x + 13, yOfValue(1)],
  ]);
  for (const [x, y] of studs) {
    out.push(S(k.extrude(diamond(x, y, 2.6), 0, 1.6, P, { bevel: 0.3 }), { tone: "hi", crease: "lo" }));
  }

  // Label plate with the frame rate engraved.
  const label = { x: -134, y: 79, w: 22, d: 12, r: 1.2 };
  out.push(S(k.slabOf(label, 0, 0.8, P, 4), { tone: "lo", crease: "none" }));
  out.push(L(k.planOutline(k.insetPlan(label, 1.4), 0.8, P, 4), { tone: "faint" }));
  out.push(k.faceTextSvg(k.topMatrix([label.x + 11, label.y + 6.4], 0.8, P, "x"), `${FPS} fps`, { size: 3, tone: "mid", anchor: "middle" }));
  out.push(L(k.lineOnTop([label.x + 5, label.y + 8.6], [label.x + 17, label.y + 8.6], 0.8, P), { tone: "lo", free: true }));
  out.push(D([at([label.x + 2.6, label.y + 2.6, 0.8]), at([label.x + label.w - 2.6, label.y + 2.6, 0.8])], { size: 0.4 }));
  return out.join("");
}

function rail(plan) {
  const out = [S(k.slabOf(plan, 0, RAIL_H, P, 3, 0.4), { tone: "mid" })];
  out.push(D([-100, -50, 0, 50, 100].map((x) => at([x, plan.y + plan.d / 2, RAIL_H])), { size: 0.4, tone: "lo" }));
  return out.join("");
}

function stops(plan) {
  const out = [];
  for (const x of [plan.x - 5, plan.x + plan.w]) {
    const stop = { x, y: plan.y - 3, w: 5, d: plan.d + 6, r: 1.2 };
    out.push(S(k.slabOf(stop, 0, 8, P, 3, 0.5), { tone: "mid" }));
    out.push(D([at([x + 2.5, stop.y + 2, 8]), at([x + 2.5, stop.y + stop.d - 2, 8])], { size: 0.45 }));
  }
  return out.join("");
}

function carriage(railPlan, tower) {
  const plan = { x: -10, y: railPlan.y - 5, w: 20, d: railPlan.d + 10, r: 2 };
  const out = [`<path class="iso-halo" d="${k.haloOf(k.insetPlan(plan, 2), CAR_Z, 0.1, P)}" style="filter:blur(3px)"/>`];
  // Bearing blocks gripping the rail, then the saddle plate on them.
  for (const y of [plan.y, railPlan.y + railPlan.d]) {
    out.push(S(k.slabOf({ x: -9, y, w: 18, d: 5, r: 1 }, 0.6, CAR_Z + 2 - 0.6, P, 3, 0.4), { tone: "lo" }));
  }
  out.push(S(k.slabOf(plan, CAR_Z + 2, CAR_TOP - CAR_Z - 2, P, 4, 0.6), { tone: "mid" }));
  out.push(D([[-7, plan.y + 2.4], [7, plan.y + 2.4], [-7, plan.y + plan.d - 2.4], [7, plan.y + plan.d - 2.4]].map(([x, y]) => at([x, y, CAR_TOP])), { size: 0.45 }));
  out.push(S(k.slabOf(tower, CAR_TOP, TOWER_TOP - CAR_TOP, P, 3, 0.5), { tone: "mid", inner: L(k.sideSeam(tower, CAR_TOP + 4, P, 3), { tone: "faint" }) }));
  out.push(D([-ROD_X, ROD_X].map((x) => at([x, tower.y + tower.d / 2, TOWER_TOP])), { size: 0.45, tone: "hi" }));
  return out.join("");
}

function rod(x) {
  const F = G.frameAlong([x, FAR_TOWER.y + FAR_TOWER.d, ROD_Z], [0, 1, 0]);
  return S(G.disc(0, NEAR_TOWER.y - FAR_TOWER.y - FAR_TOWER.d, ROD_R, F, P), { tone: "mid" });
}

function nearFront() {
  // Playhead pointer: a tab off the near carriage hanging over the frame ruler, its index line lit.
  // It runs low off the front bearing block, under the belt, so it reads the ruler without parallax.
  const front = NEAR_RAIL.y + NEAR_RAIL.d + 5;
  const tab = { x: -2.5, y: front - 0.4, w: 5, d: FRAME_STRIP.y + 6 - front, r: 1 };
  const out = [S(k.slabOf(tab, 1, 1, P, 3, 0.3), { tone: "mid" })];
  out.push(L(k.lineOnTop([0, FRAME_STRIP.y - 1.5], [0, tab.y + tab.d], 2, P), { tone: "lit", free: "start" }));
  out.push(D([at([0, tab.y + 3, 2])], { size: 0.45 }));
  // Scrub knob on top of the near tower.
  out.push(S(k.cylinder(0, NEAR_TOWER.y + 3, 4, TOWER_TOP, 3.5, P, 28), { tone: "mid" }));
  out.push(L(k.knurl(0, NEAR_TOWER.y + 3, 4, TOWER_TOP, TOWER_TOP + 3.5, 28, P), { tone: "lo" }));
  out.push(L(k.ring(0, NEAR_TOWER.y + 3, 1.4, TOWER_TOP + 3.5, P, 16), { tone: "mid" }));
  return out.join("");
}

function driveBody(x, motor) {
  const out = [];
  const body = { x: x - 7, y: PULLEY_Y - 7, w: 14, d: 14, r: motor ? 1.4 : 2 };
  const top = BELT_Z - 1.2;
  if (motor) {
    out.push(S(k.slabOf({ x: body.x - 3, y: PULLEY_Y - 3, w: 3.4, d: 6, r: 0.6 }, 3, 5, P, 2, 0.3), { tone: "lo" }));
    out.push(S(k.slabOf(body, 0, top, P, 3, 0.6), { tone: "mid", inner: L(k.sideSeam(body, 3, P, 3) + k.sideSeam(body, top - 3, P, 3), { tone: "lo" }) }));
    out.push(D(k.corners(body, 2.2).map(([px, py]) => at([px, py, top])), { size: 0.45, tone: "lo" }));
  } else {
    out.push(S(k.slabOf(body, 0, top, P, 4, 0.6), { tone: "mid", inner: L(k.sideSeam(body, 4, P, 4), { tone: "faint" }) }));
    out.push(L(k.planOutline({ x: x - 5.5, y: PULLEY_Y + 4.2, w: 11, d: 1.8, r: 0.9 }, top, P, 3), { tone: "lo" }));
    out.push(D([at([x + 3, PULLEY_Y + 5.1, top]), at([x - 5.5, PULLEY_Y - 5.2, top])], { size: 0.45 }));
  }
  out.push(S(k.cylinder(x, PULLEY_Y, 3, top, 0.8, P, 20), { tone: "lo" }));
  out.push(S(k.cylinder(x, PULLEY_Y, FLANGE_R, BELT_Z - 0.4, 0.4, P, 32), { tone: "mid" }));
  return out.join("");
}

function beltRun(y) {
  return S(k.slabOf({ x: -PULLEY_X, y, w: PULLEY_X * 2, d: BELT_T, r: 0 }, BELT_Z, BELT_H, P, 2), { tone: "lo", crease: "lo" });
}

function pulleyWrap(x) {
  return S(k.cylinder(x, PULLEY_Y, PULLEY_R + BELT_T, BELT_Z, BELT_H, P, 36), { tone: "lo", crease: "lo" }) + L(k.knurl(x, PULLEY_Y, PULLEY_R + BELT_T, BELT_Z, BELT_Z + BELT_H, 30, P, 0.3), { tone: "faint" });
}

function pulleyTop(x) {
  const out = [];
  out.push(S(k.cylinder(x, PULLEY_Y, FLANGE_R, BELT_Z + BELT_H, 0.4, P, 36), { tone: "mid" }));
  out.push(L(k.ring(x, PULLEY_Y, 1.4, BELT_Z + BELT_H + 0.4, P, 16), { tone: "mid" }));
  out.push(D([0, 1, 2].map((i) => at([x + Math.cos((i * 2 * Math.PI) / 3) * 3.6, PULLEY_Y + Math.sin((i * 2 * Math.PI) / 3) * 3.6, BELT_Z + BELT_H + 0.4])), { size: 0.4, tone: "lo" }));
  return out.join("");
}

function beltClamp() {
  // A post on the near carriage and a jaw plate pinch the belt's back run.
  const post = { x: 3, y: 58, w: 6.4, d: BELT_Y - 58, r: 0.8 };
  const out = [S(k.slabOf(post, CAR_TOP, BELT_Z + BELT_H + 1 - CAR_TOP, P, 3, 0.4), { tone: "mid" })];
  return out.join("");
}

function beltJaw() {
  const jaw = { x: 2.6, y: BELT_Y + BELT_T, w: 7.2, d: 1.4, r: 0.5 };
  const out = [S(k.slabOf(jaw, BELT_Z - 1, BELT_H + 2, P, 2, 0.3), { tone: "mid" })];
  out.push(D([4.4, 7.8].map((x) => at([x, jaw.y + jaw.d, BELT_Z + BELT_H / 2])), { size: 0.4, tone: "lo" }));
  return out.join("");
}

function camPlate(ease) {
  const out = [];
  for (const [x, y] of byDepth(k.corners(CAM, 9))) {
    out.push(S(k.cylinder(x, y, 4, 0, CAM_Z, P, 24), { tone: "lo" }));
  }
  out.push(`<path class="iso-halo" d="${k.haloOf(k.insetPlan(CAM, 4), 0, 0.1, P)}" style="filter:blur(4px)"/>`);
  out.push(S(k.slabOf(CAM, CAM_Z, CAM_TOP - CAM_Z, P, 6, 0.8), { tone: "hi", crease: "lo" }));
  // Keyframe guides: the two keyframe times and the 0 % and 100 % values, engraved edge to edge.
  const guides = [
    k.lineOnTop([CAM.x, yOfValue(0)], [CAM.x + CAM.w, yOfValue(0)], CAM_TOP, P),
    k.lineOnTop([CAM.x, yOfValue(1)], [CAM.x + CAM.w, yOfValue(1)], CAM_TOP, P),
    k.lineOnTop([xOfFrame(0), CAM.y], [xOfFrame(0), CAM.y + CAM.d], CAM_TOP, P),
    k.lineOnTop([xOfFrame(FRAMES), CAM.y], [xOfFrame(FRAMES), CAM.y + CAM.d], CAM_TOP, P),
  ];
  out.push(L(guides.join(""), { tone: "faint" }));
  const screws = k.corners(CAM, 9);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 1.8, CAM_TOP, P, 16)).join(""), { tone: "lo" }));
  out.push(D(screws.map(([x, y]) => at([x, y, CAM_TOP])), { size: 0.45 }));
  out.push(`<path data-part="slot" class="iso-line" data-tone="mid" d="${k.onTop(slotRing(ease), CAM_TOP, P, true)}"/>`);
  out.push(`<g data-part="frames" class="iso-dots" data-tone="mid">${framePoints(ease).map(([x, y]) => `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="0.75"/>`).join("")}</g>`);
  return out.join("");
}

const framePoints = (ease) => Array.from({ length: FRAMES + 1 }, (_, f) => at([xOfFrame(f), yOfValue(ease(f / FRAMES)), CAM_TOP]));

function pin() {
  const out = [];
  out.push(S(k.cylinder(0, 0, ROLLER_R, CAM_TOP, 2, P, 20), { tone: "hi", lit: true }));
  out.push(S(k.cylinder(0, 0, PIN_R, CAM_TOP + 2, SLIDER_Z - CAM_TOP - 2, P, 16), { tone: "hi", crease: "none", lit: true }));
  return out.join("");
}

function slider() {
  const plan = { x: -8, y: -6, w: 16, d: 12, r: 1.6 };
  const out = [S(k.slabOf(plan, SLIDER_Z, SLIDER_H, P, 4, 0.5), { tone: "hi", crease: "lo", inner: L(k.sideSeam(plan, SLIDER_Z + 2, P, 4), { tone: "faint" }) })];
  const top = SLIDER_Z + SLIDER_H;
  out.push(D([[-5.5, -3.5], [5.5, -3.5], [-5.5, 3.5], [5.5, 3.5]].map(([x, y]) => at([x, y, top])), { size: 0.4, tone: "lo" }));
  out.push(S(k.cylinder(0, 0, 2.6, top, 3, P, 20), { tone: "mid" }));
  out.push(L(k.knurl(0, 0, 2.6, top, top + 3, 18, P), { tone: "lo" }));
  return out.join("");
}

const ease0 = EASES[NAMES[START]];
const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label:
    "A keyframe cam bench. A gantry rides two rails across a cam plate; its position along the rails is time, ticked off one frame at a time on a ruler at the front. A pin on a slider drops into a slot cut in the plate in the shape of an easing curve, so as the gantry crosses from the first keyframe to the second, the slot pushes the slider from 0 to 100 percent. Dots in the slot mark where the slider sits on each of the 48 frames.",
  body: [
    base(),
    rail(FAR_RAIL),
    stops(FAR_RAIL),
    `<g data-part="far" transform="${k.translateAlong(P, [xOfFrame(0), 0, 0])}">${carriage(FAR_RAIL, FAR_TOWER)}</g>`,
    camPlate(ease0),
    rail(NEAR_RAIL),
    stops(NEAR_RAIL),
    driveBody(-PULLEY_X, true),
    driveBody(PULLEY_X, false),
    beltRun(BELT_Y),
    pulleyWrap(-PULLEY_X),
    `<g data-part="rod-back" transform="${k.translateAlong(P, [xOfFrame(0), 0, 0])}">${rod(-ROD_X)}</g>`,
    `<g data-part="pin" transform="${k.translateAlong(P, [xOfFrame(0), yOfValue(0), 0])}">${pin()}</g>`,
    `<g data-part="rod-front" transform="${k.translateAlong(P, [xOfFrame(0), 0, 0])}">${rod(ROD_X)}</g>`,
    `<g data-part="slider" transform="${k.translateAlong(P, [xOfFrame(0), yOfValue(0), 0])}">${slider()}</g>`,
    `<g data-part="near" transform="${k.translateAlong(P, [xOfFrame(0), 0, 0])}">${carriage(NEAR_RAIL, NEAR_TOWER)}${nearFront()}${beltClamp()}${beltJaw()}</g>`,
    pulleyWrap(PULLEY_X),
    beltRun(PULLEY_Y + PULLEY_R),
    pulleyTop(-PULLEY_X),
    pulleyTop(PULLEY_X),
  ],
});

const live = `
const P = ${JSON.stringify(P)};
const FRAMES = ${FRAMES}, FPS = ${FPS}, PER_FRAME = ${PER_FRAME}, T0 = ${T0}, V0 = ${V0}, SPAN = ${SPAN}, SLOT = ${SLOT}, CAM_TOP = ${CAM_TOP};
const EASES = { linear: ${EASES.linear.toString()}, "ease-in-out": ${EASES["ease-in-out"].toString()}, overshoot: ${EASES.overshoot.toString()} };
const NAMES = Object.keys(EASES);
const yOfValue = (v) => V0 + v * SPAN;
const xOfFrame = (f) => T0 + f * PER_FRAME;
const slotRing = ${slotRing.toString()};
const stage = document.querySelector(".iso-stage");
const svg = stage.querySelector("svg");
const part = (name) => svg.querySelector('[data-part="' + name + '"]');
const alongX = ["far", "rod-back", "rod-front", "near"].map(part);
const alongXY = ["pin", "slider"].map(part);
const slot = part("slot");
const dots = [...part("frames").querySelectorAll("circle")];
const readout = document.querySelector("[data-readout]");
const still = matchMedia("(prefers-reduced-motion: reduce)");
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

let pick = ${START}, from = ${START}, morph = 1;
let x = xOfFrame(0), target = x, tau = 0.12;
let frame = 0, last = 0, clock = 0, touring = !still.matches, visible = false, idle = 0, swapped = false;
const curve = (t) => {
  const a = EASES[NAMES[from]](t), b = EASES[NAMES[pick]](t);
  const m = morph * morph * (3 - 2 * morph);
  return a + (b - a) * m;
};
function reshape() {
  slot.setAttribute("d", onTop(slotRing(curve), CAM_TOP, P, true));
  dots.forEach((dot, f) => {
    const [sx, sy] = iso([xOfFrame(f), yOfValue(curve(f / FRAMES)), CAM_TOP], P);
    dot.setAttribute("cx", sx.toFixed(1));
    dot.setAttribute("cy", sy.toFixed(1));
  });
}
function swap(to) {
  from = pick; pick = (to + NAMES.length) % NAMES.length; morph = still.matches ? 1 : 0;
  if (morph === 1) { from = pick; reshape(); }
  stage.setAttribute("aria-valuetext", "Cam: " + NAMES[pick] + ", frame " + Math.round((target - T0) / PER_FRAME));
}
function draw() {
  const t = clamp((x - T0) / (FRAMES * PER_FRAME), 0, 1);
  const value = curve(t);
  const y = yOfValue(value);
  const shift = translateAlong(P, [x, 0, 0]);
  const shiftXY = translateAlong(P, [x, y, 0]);
  alongX.forEach((el) => el.setAttribute("transform", shift));
  alongXY.forEach((el) => el.setAttribute("transform", shiftXY));
  const f = Math.round(t * FRAMES);
  const text = "frame " + String(f).padStart(2, "0") + " / " + FRAMES + " · " + (morph < 1 ? "swapping cam" : NAMES[pick]) + " · " + Math.round(value * 100) + " %";
  if (readout.textContent !== text) readout.textContent = text;
  stage.setAttribute("aria-valuenow", String(f));
}
// The tour: hold on the first keyframe, play the 48 frames at 24 fps, hold, swap the cam while rewinding.
const CYCLE = 4.6;
function tour(dt) {
  clock += dt;
  const c = clock % CYCLE;
  if (c < 0.6) { target = xOfFrame(0); tau = 0.25; swapped = false; }
  else if (c < 0.6 + FRAMES / FPS) { target = xOfFrame(Math.min(FRAMES, Math.floor((c - 0.6) * FPS))); tau = 0.03; }
  else if (c < 3.6) { target = xOfFrame(FRAMES); tau = 0.03; }
  else { if (!swapped) { swapped = true; swap(pick + 1); } target = xOfFrame(0); tau = 0.28; }
}
function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  const calm = still.matches;
  if (touring) tour(dt);
  x = calm ? target : x + (target - x) * (1 - Math.exp(-dt / tau));
  if (Math.abs(target - x) < 0.01) x = target;
  if (morph < 1) { morph = calm ? 1 : Math.min(1, morph + dt / 0.7); reshape(); if (morph === 1) from = pick; }
  draw();
  const settled = !touring && x === target && morph === 1;
  frame = visible && !settled ? requestAnimationFrame(tick) : 0;
}
const run = () => { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } };
const hold = () => { touring = false; clearTimeout(idle); idle = setTimeout(() => { touring = !still.matches; clock = 0; run(); }, 3600); };
const steer = (f, slow) => { hold(); target = xOfFrame(clamp(Math.round(f), 0, FRAMES)); tau = slow ? 0.18 : 0.06; run(); };
new IntersectionObserver((entries) => { visible = entries[entries.length - 1].isIntersecting; if (visible) run(); }, { rootMargin: "120px 0px" }).observe(stage);
stage.addEventListener("pointermove", (event) => {
  if (event.pointerType !== "mouse") return;
  const box = svg.getBoundingClientRect();
  steer(clamp(((event.clientX - box.left) / box.width - 0.2) / 0.6, 0, 1) * FRAMES);
});
stage.addEventListener("click", () => { hold(); swap(pick + 1); run(); });
stage.addEventListener("keydown", (event) => {
  const now = Math.round((target - T0) / PER_FRAME);
  const step = event.shiftKey ? 6 : 1;
  let to = null;
  if (event.key === "ArrowRight" || event.key === "ArrowUp") to = now + step;
  if (event.key === "ArrowLeft" || event.key === "ArrowDown") to = now - step;
  if (event.key === "Home") to = 0;
  if (event.key === "End") to = FRAMES;
  if (event.key === "Enter" || event.key === " ") { event.preventDefault(); hold(); swap(pick + 1); run(); return; }
  if (["1", "2", "3"].includes(event.key)) { hold(); swap(Number(event.key) - 1); run(); return; }
  if (to === null) return;
  event.preventDefault();
  steer(to, true);
});
draw();
`;

const body = k.plateHtml({
  fig: "Fig 1",
  title: "Keyframe cam bench",
  hint: "Hover to scrub · click to swap the cam",
  readout: `frame 00 / ${FRAMES} · ${NAMES[START]} · 0 %`,
  keys: [
    { mark: "lit", label: "Follower pin: the animated value, read off the cam at each frame" },
    { mark: "raised", label: "Keyframe studs: frame 0 at 0 %, frame 48 at 100 %" },
    { mark: "dotted", label: "Dots in the slot: where the pin sits on each of the 48 frames" },
  ],
  caption:
    "How motion graphics move: you set only two keyframes, a start and an end value. The software fills every frame between them by reading an easing curve, the slot in this plate, once per frame: 48 frames at 24 fps is two seconds. Linear spaces the dots evenly; ease-in-out bunches them at the keyframes so the move starts and stops softly; overshoot runs past 100 % and settles back.",
  body: `<div class="iso-stage" tabindex="0" role="slider" aria-label="Keyframe cam bench: arrow keys step one frame, Shift steps six, Enter or 1 to 3 swap the easing cam" aria-valuemin="0" aria-valuemax="${FRAMES}" aria-valuenow="0" aria-valuetext="Cam: ${NAMES[START]}, frame 0">${svg}</div>`,
});

const file = theme === "light" ? "motion-graphics-light.html" : "motion-graphics.html";
writeFileSync(join(HERE, file), k.pageHtml({ title: "Keyframe cam bench", theme, body, script: kitScript() + live }));
console.log("wrote", file);
