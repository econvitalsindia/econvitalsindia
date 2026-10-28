// RSS 2.0 for briefings. Feeds are the simplest input for a newsletter service later.
import { config } from "./config.js";
import { loadBriefings } from "./briefings.js";
import { marked } from "marked";

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export function feed({ product = null, title, path }) {
  const base = config.site.url.replace(/\/$/, "");
  const items = loadBriefings().filter((b) => !product || b.product === product).slice(0, 50);
  const body = items.map((b) => `
    <item>
      <title>${esc(b.title)}</title>
      <link>${base}/briefings/${b.slug}/</link>
      <guid isPermaLink="true">${base}/briefings/${b.slug}/</guid>
      <pubDate>${new Date(b.date + "T18:30:00+05:30").toUTCString()}</pubDate>
      <description>${esc(marked.parse(b.body))}</description>
    </item>`).join("");
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${esc(config.site.name)}: ${esc(title)}</title>
    <link>${base}/briefings/</link>
    <atom:link href="${base}${path}" rel="self" type="application/rss+xml" />
    <description>${esc(config.site.tagline)}</description>
    <language>${config.site.language}</language>${body}
  </channel>
</rss>`;
  return new Response(xml, { headers: { "Content-Type": "application/rss+xml; charset=utf-8" } });
}
