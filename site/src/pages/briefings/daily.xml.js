import { feed } from "../../lib/rss.js";
export const GET = () => feed({ product: "daily-note", title: "daily note", path: "/briefings/daily.xml" });
