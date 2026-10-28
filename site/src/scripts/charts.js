// Draws every [data-chart] element with Observable Plot. House style: 02-conventions.md.
import * as Plot from "@observablehq/plot";

const css = getComputedStyle(document.documentElement);
const palette = [css.getPropertyValue("--primary").trim(), css.getPropertyValue("--accent").trim(), "#5b8c5a", "#8c5a7a"];

function draw(el) {
  const spec = JSON.parse(el.dataset.chart);
  const rows = spec.series.flatMap((s) => s.points.map(([d, v]) => ({ date: new Date(d), value: v, label: s.label })));
  const last = rows.reduce((m, r) => (r.date > m ? r.date : m), new Date(0));
  const start = new Date(last); start.setFullYear(start.getFullYear() - spec.years);
  const data = rows.filter((r) => r.date >= start);
  const ref = spec.reference;
  const marks = [];
  if (ref?.band) marks.push(Plot.rectY([ref.band], { x1: start, x2: last, y1: (b) => b[0], y2: (b) => b[1], fill: "var(--accent)", fillOpacity: 0.1 }));
  if (ref?.target !== undefined) marks.push(Plot.ruleY([ref.target], { stroke: "var(--accent)", strokeDasharray: "4,3" }));
  // Zero line only when the data reach zero; level series (e.g. USD/INR) keep a tight axis.
  const lo = Math.min(...data.map((r) => r.value));
  if (lo <= 0 || ref) marks.push(Plot.ruleY([0], { stroke: "currentColor", strokeOpacity: 0.25 }));
  marks.push(Plot.lineY(data, { x: "date", y: "value", stroke: "label", strokeWidth: 1.8 }));
  const lastPoints = spec.series.map((s) => { const p = data.filter((r) => r.label === s.label).at(-1); return p; }).filter(Boolean);
  marks.push(Plot.dot(lastPoints, { x: "date", y: "value", fill: "label", r: 3 }));
  marks.push(Plot.text(lastPoints, { x: "date", y: "value", text: (d) => d.value.toLocaleString("en-US", { maximumFractionDigits: 2 }), dx: 6, textAnchor: "start", fontSize: 11 }));
  marks.push(Plot.tip(data, Plot.pointerX({ x: "date", y: "value", stroke: "label", title: (d) => `${d.label}\n${d.date.toISOString().slice(0, 10)}: ${d.value.toLocaleString("en-US", { maximumFractionDigits: 2 })}` })));
  const width = el.clientWidth || 600;
  const plot = Plot.plot({
    width, height: Math.max(240, Math.min(340, width * 0.55)), marginRight: 48,
    style: { fontFamily: "Inter, system-ui, sans-serif", fontSize: "11px", background: "transparent" },
    x: { type: "utc" }, y: { grid: true, label: spec.yLabel || null, zero: lo <= 0 || !!ref },
    color: { range: palette, legend: spec.series.length > 1 },
    marks,
  });
  el.replaceChildren(plot);
}

const charts = [...document.querySelectorAll("[data-chart]")];
charts.forEach(draw);
let timer;
window.addEventListener("resize", () => { clearTimeout(timer); timer = setTimeout(() => charts.forEach(draw), 200); });
