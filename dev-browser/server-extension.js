#!/usr/bin/env node

import { chromium } from "playwright";
import { createServer } from "playwright-stdio-server";

const server = await createServer({
  browser: chromium,
  headless: false,
  extensionMode: true,
});

console.log("Waiting for extension to connect...");
console.log(`Server running on port ${server.port}`);

// Keep process alive
await new Promise(() => {});
