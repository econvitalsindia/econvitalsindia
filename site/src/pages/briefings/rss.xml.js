import { feed } from "../../lib/rss.js";
export const GET = () => feed({ title: "all briefings", path: "/briefings/rss.xml" });
