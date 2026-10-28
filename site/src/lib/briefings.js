// Published briefings: site/src/content/briefings/*.md (front matter + markdown body).
// Files only reach the repository's main branch through an approved pull request.
import fs from "node:fs";
import path from "node:path";
import yaml from "js-yaml";

const dir = path.resolve(process.cwd(), "src/content/briefings");

export function loadBriefings() {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter((f) => f.endsWith(".md")).map((f) => {
    const text = fs.readFileSync(path.join(dir, f), "utf8");
    const [, front, ...rest] = text.split(/^---$/m);
    return { slug: f.replace(/\.md$/, ""), ...yaml.load(front), body: rest.join("---").trim() };
  }).sort((a, b) => (a.date < b.date ? 1 : -1));
}
