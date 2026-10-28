import { feed } from "../../lib/rss.js";
export const GET = () => feed({ product: "release-note", title: "data release notes", path: "/briefings/release-notes.xml" });
