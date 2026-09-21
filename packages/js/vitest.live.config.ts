import { defineConfig } from "vitest/config";

/** Live suite only — requires TYPESAFE_API_KEY. */
export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/live.test.ts"],
  },
});
