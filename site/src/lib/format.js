// Number and date formatting per docs/guidebook/02-conventions.md.
const MINUS = "−";
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function num(v, digits = 1) {
  if (v === null || v === undefined || Number.isNaN(v)) return "–";
  const s = Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  return (v < 0 ? MINUS : "") + s;
}

export function signed(v, digits = 1, suffix = "") {
  if (v === null || v === undefined) return "–";
  return (v > 0 ? "+" : v < 0 ? MINUS : "") + num(Math.abs(v), digits) + suffix;
}

export function byFmt(v, fmt) {
  const map = { pct1: [1, "%"], pct2: [2, "%"], num0: [0, ""], num2: [2, ""] };
  const [d, suf] = map[fmt] ?? [1, ""];
  return num(v, d) + suf;
}

// "2026-09-01" + freq -> "Sep 2026" (M), "28 Oct 2026" (D), "Q2 FY27" (Q)
export function period(iso, freq) {
  const [y, m, d] = iso.split("-").map(Number);
  if (freq === "M") return `${MONTHS[m - 1]} ${y}`;
  if (freq === "Q") {
    const fyEnd = m >= 4 ? y + 1 : y;
    const q = Math.floor(((m - 4 + 12) % 12) / 3) + 1;
    return `Q${q} FY${String(fyEnd).slice(2)}`;
  }
  return `${d} ${MONTHS[m - 1]} ${y}`;
}
