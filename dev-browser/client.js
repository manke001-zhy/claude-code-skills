import { createClient } from "playwright-stdio-client";

export async function connect() {
  const client = await createClient({
    host: "localhost",
    port: 3000,
  });

  return client;
}

export async function waitForPageLoad(page) {
  await Promise.race([
    page.loadState("domcontentloaded"),
    page.waitForTimeout(5000),
  ]);
}
