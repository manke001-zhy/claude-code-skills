#!/usr/bin/env node

import { chromium } from "playwright";
import { WebSocketServer } from "ws";
import { createServer } from "playwright-stdio-server";

const server = await createServer({
  browser: chromium,
  headless: false,
});

console.log("Ready");
console.log(`Server running on port ${server.port}`);

// Keep process alive
await new Promise(() => {});
