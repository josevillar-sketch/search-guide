// Shared by the browser suites: no persistent server or file-URL workaround needed.
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");

function usable(file) {
  try { fs.accessSync(file, fs.constants.X_OK); return fs.statSync(file).isFile(); }
  catch { return false; }
}

function executablePath(chromium) {
  const override = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
  if (override) {
    if (!usable(override)) throw new Error("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH must name an executable browser file.");
    return override;
  }
  const bundled = chromium.executablePath();
  if (usable(bundled)) return bundled;
  const names = process.platform === "win32" ? ["chrome.exe", "chromium.exe"]
    : ["chromium", "chromium-browser", "google-chrome-stable", "google-chrome"];
  const candidates = (process.env.PATH || "").split(path.delimiter)
    .flatMap((dir) => dir ? names.map((name) => path.join(dir, name)) : []);
  if (process.platform === "darwin") candidates.push("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome");
  const system = candidates.find(usable);
  if (system) return system;
  throw new Error("Chromium is unavailable. Run npx playwright install chromium, or set PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH.");
}

async function launchHarness(index, { browserName = "chromium", additionalFiles = {} } = {}) {
  if (!["chromium", "webkit"].includes(browserName)) throw new Error("browserName must be chromium or webkit.");
  let browserType;
  try { browserType = require("playwright")[browserName]; }
  catch { throw new Error("Playwright is unavailable. Run npm ci in the project directory first."); }
  // Fail before opening a socket if either input or browser setup is missing.
  fs.accessSync(index, fs.constants.R_OK);
  const served = new Map([["/index.html", index]]);
  for (const [route, file] of Object.entries(additionalFiles)) {
    if (!route.startsWith("/") || route.includes("?") || route.includes("#") || typeof file !== "string") {
      throw new Error("Additional browser-test files require explicit URL paths and local filenames.");
    }
    fs.accessSync(file, fs.constants.R_OK);
    served.set(route, file);
  }
  const executable = browserName === "chromium" ? executablePath(browserType) : browserType.executablePath();
  if (browserName === "webkit" && !usable(executable)) throw new Error("WebKit is unavailable. Run npx playwright install webkit.");
  const server = http.createServer((req, res) => {
    const pathname = new URL(req.url, "http://localhost").pathname;
    if (pathname === "/favicon.ico") { res.writeHead(204); res.end(); return; }
    const file = served.get(pathname);
    if (!file) { res.writeHead(404); res.end(); return; }
    if (!['GET', 'HEAD'].includes(req.method)) { res.writeHead(405); res.end(); return; }
    fs.readFile(file, (error, body) => {
      if (error) { res.writeHead(500); res.end("Cannot read the test page."); return; }
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" });
      res.end(req.method === "HEAD" ? undefined : body);
    });
  });
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  let browserPromise;
  let closing;
  const signals = new Map();
  const close = () => closing || (closing = (async () => {
    for (const [signal, handler] of signals) process.removeListener(signal, handler);
    try { const browser = await browserPromise; if (browser) await browser.close(); }
    finally {
      await new Promise((resolve) => {
        server.close(resolve);
        server.closeAllConnections?.();
      });
    }
  })());
  for (const [signal, code] of [["SIGINT", 130], ["SIGTERM", 143]]) {
    const handler = () => { close().catch(() => {}).finally(() => process.exit(code)); };
    signals.set(signal, handler);
    process.once(signal, handler);
  }
  try {
    browserPromise = browserType.launch({ executablePath: executable });
    const browser = await browserPromise;
    const baseURL = `http://127.0.0.1:${server.address().port}`;
    return { browser, url: baseURL + "/index.html", baseURL, close };
  } catch (error) {
    await close().catch(() => {});
    throw error;
  }
}

module.exports = { launchHarness, executablePath };
