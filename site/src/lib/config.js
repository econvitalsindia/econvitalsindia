// Site identity comes only from ../site.config.yaml (AGENTS.md hard rule 1).
import fs from "node:fs";
import path from "node:path";
import yaml from "js-yaml";

const root = path.resolve(process.cwd(), "..");
export const config = yaml.load(fs.readFileSync(path.join(root, "site.config.yaml"), "utf8"));
