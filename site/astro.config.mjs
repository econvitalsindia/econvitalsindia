import { defineConfig } from "astro/config";

// Static output only (docs/guidebook/decisions/0001-static-site-astro.md).
export default defineConfig({
  output: "static",
  trailingSlash: "always",
});
