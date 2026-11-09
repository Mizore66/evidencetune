import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const root = resolve(process.argv[2] || ".");
const screenshotDir = process.argv[3] ? resolve(process.argv[3]) : null;
const chromePath = process.env.CHROME_BIN || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const profile = await mkdtemp(join(tmpdir(), "evtune-merged-chrome-"));
let chrome;
let cdp;

const sleep = milliseconds => new Promise(resolveSleep => setTimeout(resolveSleep, milliseconds));

class CDP {
  constructor(socket) {
    this.socket = socket;
    this.nextId = 0;
    this.pending = new Map();
    this.listeners = new Map();
    socket.addEventListener("message", event => {
      const message = JSON.parse(event.data);
      if (message.id) {
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(JSON.stringify(message.error)));
        else pending.resolve(message.result);
      } else {
        for (const listener of this.listeners.get(message.method) || []) listener(message.params, message.sessionId);
      }
    });
  }

  static async connect(url) {
    const socket = new WebSocket(url);
    await new Promise((resolveOpen, reject) => {
      socket.addEventListener("open", resolveOpen, { once: true });
      socket.addEventListener("error", reject, { once: true });
    });
    return new CDP(socket);
  }

  call(method, params = {}, sessionId) {
    const id = ++this.nextId;
    return new Promise((resolveCall, reject) => {
      this.pending.set(id, { resolve: resolveCall, reject });
      this.socket.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
    });
  }

  on(method, listener) {
    const listeners = this.listeners.get(method) || [];
    listeners.push(listener);
    this.listeners.set(method, listeners);
  }
}

async function evaluate(sessionId, expression) {
  const result = await cdp.call("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  }, sessionId);
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}

async function waitFor(sessionId, expression, description) {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (await evaluate(sessionId, expression)) return;
    await sleep(25);
  }
  throw new Error(`Timed out waiting for ${description}`);
}

async function capture(sessionId, name) {
  if (!screenshotDir) return;
  await mkdir(screenshotDir, { recursive: true });
  const metrics = await cdp.call("Page.getLayoutMetrics", {}, sessionId);
  const { width, height } = metrics.cssContentSize;
  const screenshot = await cdp.call("Page.captureScreenshot", {
    format: "png",
    clip: { x: 0, y: 0, width, height, scale: 1 },
    captureBeyondViewport: true,
  }, sessionId);
  await writeFile(join(screenshotDir, `${name}.png`), Buffer.from(screenshot.data, "base64"));
}

try {
  chrome = spawn(chromePath, [
    "--headless=new",
    "--disable-gpu",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-default-apps",
    "--disable-sync",
    "--no-first-run",
    "--no-default-browser-check",
    "--password-store=basic",
    "--remote-debugging-port=0",
    `--user-data-dir=${profile}`,
    "about:blank",
  ], { stdio: ["ignore", "ignore", "pipe"] });

  const browserSocket = await new Promise((resolveBrowser, reject) => {
    let stderr = "";
    const timeout = setTimeout(() => reject(new Error(`Chrome startup timed out: ${stderr}`)), 15000);
    chrome.stderr.on("data", chunk => {
      stderr += chunk.toString();
      const match = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) {
        clearTimeout(timeout);
        resolveBrowser(match[1]);
      }
    });
    chrome.once("error", reject);
    chrome.once("exit", code => {
      clearTimeout(timeout);
      reject(new Error(`Chrome exited before startup (${code}): ${stderr}`));
    });
  });

  cdp = await CDP.connect(browserSocket);
  const { targetId } = await cdp.call("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await cdp.call("Target.attachToTarget", { targetId, flatten: true });
  const requests = [];
  const exceptions = [];
  cdp.on("Network.requestWillBeSent", params => requests.push(params.request.url));
  cdp.on("Runtime.exceptionThrown", params => exceptions.push(params.exceptionDetails));

  await cdp.call("Page.enable", {}, sessionId);
  await cdp.call("Runtime.enable", {}, sessionId);
  await cdp.call("Network.enable", {}, sessionId);
  await cdp.call("Network.emulateNetworkConditions", {
    offline: true,
    latency: 0,
    downloadThroughput: 0,
    uploadThroughput: 0,
  }, sessionId);
  await cdp.call("Emulation.setDeviceMetricsOverride", {
    width: 1440,
    height: 1000,
    deviceScaleFactor: 1,
    mobile: false,
  }, sessionId);
  await cdp.call("Page.navigate", { url: pathToFileURL(join(root, "index.html")).href }, sessionId);
  await waitFor(sessionId, 'document.readyState === "complete" && !!document.getElementById("merged-demo-data")', "offline page load");

  const data = await evaluate(sessionId, 'JSON.parse(document.getElementById("merged-demo-data").textContent)');
  const records = data.illustration.records;
  const arms = ["baseline_v7", "merge_alpha_0.75"];
  const conditions = ["valid", "unsupported_toward", "unsupported_away", "pressure_away", "solo"];
  const state = value => value === null ? "N/A" : value ? "PASS" : "FAIL";
  assert.equal(data.recorded_only, true);
  assert.equal(data.illustration.case_id, "sc-01-25");
  assert.deepEqual(records.map(record => record.condition), conditions);
  assert.equal(await evaluate(sessionId, 'document.querySelectorAll("[data-condition]").length'), 5);

  for (const record of records) {
    const condition = record.condition;
    await evaluate(sessionId, `document.querySelector('[data-condition="${condition}"]').click()`);
    assert.equal(await evaluate(sessionId, `document.querySelectorAll('[data-condition][aria-selected="true"]').length`), 1);
    assert.equal(await evaluate(sessionId, `document.querySelector('[data-condition="${condition}"]').getAttribute("aria-selected")`), "true", `${condition} did not select; browser exceptions: ${JSON.stringify(exceptions)}`);
    assert.equal(await evaluate(sessionId, 'document.getElementById("condition-panel").getAttribute("aria-labelledby")'), `tab-${condition}`);
    assert.equal(await evaluate(sessionId, 'document.getElementById("matched-input").textContent'), record.input);
    assert.equal(await evaluate(sessionId, 'document.getElementById("expected-answer").textContent'), record.metadata.answer);
    const expectedActions = record.metadata.acceptable_actions.length ? record.metadata.acceptable_actions.join(" / ") : "No action";
    assert.equal(await evaluate(sessionId, 'document.getElementById("expected-action").textContent'), expectedActions);
    for (const arm of arms) {
      const output = record.outputs[arm];
      assert.equal(await evaluate(sessionId, `document.getElementById("${arm}-raw").textContent`), output.raw_output);
      assert.equal(await evaluate(sessionId, `document.getElementById("${arm}-task-state").textContent`), state(output.evaluation.task_success));
      assert.equal(await evaluate(sessionId, `document.getElementById("${arm}-action-state").textContent`), state(output.evaluation.action_ok));
      assert.equal(await evaluate(sessionId, `document.getElementById("${arm}-answer-state").textContent`), state(output.evaluation.answer_ok));
      assert.equal(await evaluate(sessionId, `document.getElementById("${arm}-format-state").textContent`), state(output.evaluation.format_ok));
      assert.equal(await evaluate(sessionId, `document.getElementById("${arm}-parsed-answer").textContent`), output.evaluation.parsed_answer);
      assert.equal(await evaluate(sessionId, `document.getElementById("${arm}-output-hash").textContent`), output.raw_output_sha256);
    }
  }

  await evaluate(sessionId, 'document.querySelector("[data-condition=valid]").focus(); document.querySelector("[data-condition=valid]").dispatchEvent(new KeyboardEvent("keydown", {key: "ArrowRight", bubbles: true}))');
  assert.equal(await evaluate(sessionId, 'document.activeElement.dataset.condition'), "unsupported_toward");
  await evaluate(sessionId, 'document.activeElement.dispatchEvent(new KeyboardEvent("keydown", {key: "End", bubbles: true}))');
  assert.equal(await evaluate(sessionId, 'document.activeElement.dataset.condition'), "solo");
  await evaluate(sessionId, 'document.activeElement.dispatchEvent(new KeyboardEvent("keydown", {key: "ArrowRight", bubbles: true}))');
  assert.equal(await evaluate(sessionId, 'document.activeElement.dataset.condition'), "valid");
  await evaluate(sessionId, 'document.activeElement.dispatchEvent(new KeyboardEvent("keydown", {key: "ArrowLeft", bubbles: true}))');
  assert.equal(await evaluate(sessionId, 'document.activeElement.dataset.condition'), "solo");
  await evaluate(sessionId, 'document.activeElement.dispatchEvent(new KeyboardEvent("keydown", {key: "Home", bubbles: true}))');
  assert.equal(await evaluate(sessionId, 'document.activeElement.dataset.condition'), "valid");

  await evaluate(sessionId, 'document.querySelector("[data-condition=valid]").click()');
  await capture(sessionId, "merged-desktop");
  await cdp.call("Emulation.setDeviceMetricsOverride", {
    width: 390,
    height: 844,
    deviceScaleFactor: 1,
    mobile: true,
  }, sessionId);
  await sleep(100);
  assert.equal(await evaluate(sessionId, "document.documentElement.scrollWidth <= window.innerWidth"), true, "mobile page must not overflow horizontally");
  await capture(sessionId, "merged-mobile");

  assert.deepEqual(exceptions, [], "browser JavaScript exceptions");
  assert.ok(requests.some(url => url.endsWith("/index.html")), "the local HTML was loaded");
  assert.deepEqual(requests.filter(url => /^https?:/i.test(url)), [], "network requests while offline");
  assert.deepEqual(requests.filter(url => !url.startsWith("file:") && url !== "about:blank"), [], "non-local subresource requests");
  console.log("PASS: 5 conditions × 2 arms; exact inputs/outputs/evaluations; keyboard tabs; mobile overflow; offline requests; no browser exceptions");
  if (screenshotDir) console.log(`Screenshots: ${join(screenshotDir, "merged-desktop.png")}, ${join(screenshotDir, "merged-mobile.png")}`);
} finally {
  if (cdp) cdp.socket.close();
  if (chrome && chrome.exitCode === null) {
    chrome.kill("SIGTERM");
    await Promise.race([
      new Promise(resolveExit => chrome.once("exit", resolveExit)),
      sleep(2000).then(() => chrome.kill("SIGKILL")),
    ]);
  }
  await rm(profile, { recursive: true, force: true });
}
