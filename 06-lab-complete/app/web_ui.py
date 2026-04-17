from __future__ import annotations

import re


CHAT_PAGE_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Render AI Operations Console</title>
    <style>
      :root {
        color-scheme: light;
        --ink: #111614;
        --muted: #5b6661;
        --line: #cad6d0;
        --panel: #ffffff;
        --soft: #eef7f3;
        --accent: #0b7f5b;
        --accent-strong: #07573f;
        --warn: #b53030;
        --gold: #b58b00;
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
        min-width: 320px;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f7faf8;
        color: var(--ink);
      }

      header {
        border-bottom: 1px solid var(--line);
        background: #ffffff;
      }

      .topbar {
        max-width: 1180px;
        margin: 0 auto;
        padding: 18px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
      }

      .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 0;
      }

      .brand img {
        width: 42px;
        height: 42px;
        border-radius: 8px;
        border: 1px solid var(--line);
      }

      h1, h2, h3, p { margin: 0; }

      h1 {
        font-size: 1.35rem;
        line-height: 1.2;
      }

      .eyebrow {
        color: var(--muted);
        font-size: 0.88rem;
        line-height: 1.4;
      }

      .badge {
        border: 1px solid #a7d9c4;
        color: var(--accent-strong);
        background: var(--soft);
        padding: 8px 10px;
        border-radius: 8px;
        font-weight: 700;
        white-space: nowrap;
      }

      main {
        max-width: 1180px;
        margin: 0 auto;
        padding: 24px 20px 48px;
        display: grid;
        grid-template-columns: minmax(0, 1.55fr) minmax(300px, 0.9fr);
        gap: 18px;
      }

      .panel {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
      }

      .chat-panel {
        min-height: 660px;
        display: grid;
        grid-template-rows: auto minmax(260px, 1fr) auto;
      }

      .panel-head {
        padding: 18px;
        border-bottom: 1px solid var(--line);
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 14px;
      }

      .panel-title {
        display: grid;
        gap: 5px;
      }

      h2 {
        font-size: 1.12rem;
        line-height: 1.25;
      }

      .model-pill {
        border: 1px solid #c9d5d0;
        border-radius: 8px;
        color: var(--muted);
        padding: 7px 9px;
        font-size: 0.86rem;
        white-space: nowrap;
      }

      .chat-log {
        min-height: 260px;
        max-height: 460px;
        overflow-y: auto;
        padding: 18px;
        display: flex;
        flex-direction: column;
        gap: 12px;
        background: #fbfdfc;
      }

      .empty-state {
        border: 1px dashed #aebdb6;
        border-radius: 8px;
        padding: 16px;
        color: var(--muted);
        line-height: 1.5;
      }

      .message {
        width: min(92%, 720px);
        padding: 13px 14px;
        border: 1px solid var(--line);
        border-radius: 8px;
        line-height: 1.5;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
      }

      .message.user {
        align-self: flex-end;
        background: #e9f6f1;
        border-color: #b9dccd;
      }

      .message.bot {
        align-self: flex-start;
        background: #ffffff;
      }

      form {
        padding: 18px;
        border-top: 1px solid var(--line);
        display: grid;
        gap: 12px;
      }

      .field-grid {
        display: grid;
        grid-template-columns: minmax(160px, 0.42fr) minmax(0, 1fr);
        gap: 12px;
      }

      label {
        display: grid;
        gap: 6px;
        font-weight: 700;
        color: #24302c;
      }

      label span {
        font-size: 0.88rem;
      }

      input, textarea, button {
        font: inherit;
      }

      input, textarea {
        width: 100%;
        border: 1px solid #b7c7c0;
        border-radius: 8px;
        background: #ffffff;
        color: var(--ink);
        padding: 12px;
      }

      textarea {
        min-height: 112px;
        resize: vertical;
      }

      input:focus, textarea:focus {
        outline: 3px solid #a8e3ca;
        border-color: var(--accent);
      }

      .actions {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
      }

      button {
        border: 0;
        border-radius: 8px;
        background: var(--accent);
        color: #ffffff;
        cursor: pointer;
        font-weight: 800;
        padding: 12px 16px;
      }

      button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      button:hover:not(:disabled) {
        background: var(--accent-strong);
      }

      .status {
        min-height: 22px;
        color: var(--warn);
        font-weight: 700;
      }

      .side-stack {
        display: grid;
        gap: 18px;
        align-content: start;
      }

      .side-panel {
        padding: 18px;
        display: grid;
        gap: 14px;
      }

      .check-grid {
        display: grid;
        gap: 10px;
      }

      .check-row {
        display: grid;
        grid-template-columns: 88px minmax(0, 1fr);
        gap: 10px;
        align-items: center;
        padding: 11px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #fbfdfc;
      }

      .check-row strong {
        font-size: 0.86rem;
      }

      .check-row span {
        color: var(--muted);
        font-size: 0.9rem;
        overflow-wrap: anywhere;
      }

      .state {
        text-align: center;
        border-radius: 8px;
        padding: 6px 8px;
        font-size: 0.78rem;
        font-weight: 800;
        background: #edf1ef;
        color: #4d5b55;
      }

      .state.ok {
        background: #dff5ea;
        color: var(--accent-strong);
      }

      .state.fail {
        background: #f9e4e4;
        color: var(--warn);
      }

      code {
        border: 1px solid #d3ddd8;
        border-radius: 6px;
        background: #f4f8f6;
        padding: 2px 5px;
        overflow-wrap: anywhere;
      }

      .env-list {
        display: grid;
        gap: 8px;
        padding: 0;
        margin: 0;
        list-style: none;
      }

      .env-list li {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        border-bottom: 1px solid #edf2ef;
        padding-bottom: 8px;
        color: var(--muted);
      }

      .env-list li:last-child {
        border-bottom: 0;
        padding-bottom: 0;
      }

      .env-list strong {
        color: var(--ink);
      }

      .note {
        border-left: 4px solid var(--gold);
        padding: 10px 12px;
        background: #fff9df;
        color: #594800;
        line-height: 1.45;
      }

      @media (max-width: 880px) {
        .topbar {
          align-items: flex-start;
          flex-direction: column;
        }

        main {
          grid-template-columns: 1fr;
        }

        .chat-panel {
          min-height: 560px;
        }
      }

      @media (max-width: 640px) {
        .field-grid {
          grid-template-columns: 1fr;
        }

        .panel-head,
        .actions {
          align-items: stretch;
          flex-direction: column;
        }

        .model-pill,
        button {
          width: 100%;
        }

        .check-row {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <header>
      <div class="topbar">
        <div class="brand">
          <img alt="Cloud console mark" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='84' height='84' viewBox='0 0 84 84'%3E%3Crect width='84' height='84' rx='14' fill='%230b7f5b'/%3E%3Cpath d='M23 52h36a11 11 0 0 0 1-22 16 16 0 0 0-31-3 13 13 0 0 0-6 25Z' fill='white'/%3E%3Cpath d='M29 55h26' stroke='%23b58b00' stroke-width='5' stroke-linecap='round'/%3E%3C/svg%3E" />
          <div>
            <p class="eyebrow">Render deploy console</p>
            <h1>OpenAI model gateway</h1>
          </div>
        </div>
        <div class="badge">Production route: /web/ask</div>
      </div>
    </header>

    <main>
      <section class="panel chat-panel" aria-label="OpenAI chat workspace">
        <div class="panel-head">
          <div class="panel-title">
            <h2>Ask the deployed agent</h2>
            <p class="eyebrow">Conversation state is stored in Redis and trimmed before each model call.</p>
          </div>
          <div class="model-pill">Default model: gpt-5-mini</div>
        </div>

        <section id="chat-log" class="chat-log" aria-live="polite">
          <div class="empty-state" id="empty-state">
            Send a deployment question, then check the response, trace header, and service status before promoting the build.
          </div>
        </section>

        <form id="chat-form">
          <div class="field-grid">
            <label>
              <span>Nickname</span>
              <input id="nickname" name="nickname" maxlength="40" autocomplete="nickname" placeholder="student-1" required />
            </label>
            <label>
              <span>Question</span>
              <textarea id="question" name="question" maxlength="2000" placeholder="How do I verify this Render deployment?" required></textarea>
            </label>
          </div>
          <div class="actions">
            <button id="send-button" type="submit">Send to OpenAI</button>
            <div id="status" class="status" aria-live="polite"></div>
          </div>
        </form>
      </section>

      <aside class="side-stack">
        <section class="panel side-panel">
          <div class="panel-title">
            <h2>Service checks</h2>
            <p class="eyebrow">Live probes from this running instance.</p>
          </div>
          <div id="service-checks" class="check-grid">
            <div class="check-row" data-path="/health">
              <strong>/health</strong>
              <span class="state">checking</span>
            </div>
            <div class="check-row" data-path="/ready">
              <strong>/ready</strong>
              <span class="state">checking</span>
            </div>
            <div class="check-row" data-path="/metrics">
              <strong>/metrics</strong>
              <span class="state">checking</span>
            </div>
          </div>
        </section>

        <section class="panel side-panel">
          <div class="panel-title">
            <h2>Render environment</h2>
            <p class="eyebrow">Set these before the first production deploy.</p>
          </div>
          <ul class="env-list">
            <li><strong>OPENAI_API_KEY</strong><span>secret</span></li>
            <li><strong>OPENAI_MODEL</strong><span>gpt-5-mini</span></li>
            <li><strong>REDIS_URL</strong><span>internal Redis URL</span></li>
            <li><strong>AGENT_API_KEY</strong><span>generated secret</span></li>
            <li><strong>ENVIRONMENT</strong><span>production</span></li>
          </ul>
          <p class="note">Use `/ready` as the Render health check. A 503 usually means Redis is missing or the service was not redeployed after env changes.</p>
        </section>

        <section class="panel side-panel">
          <div class="panel-title">
            <h2>Protected API</h2>
            <p class="eyebrow"><code>POST /ask</code> requires <code>X-API-Key</code>. Browser chat uses <code>POST /web/ask</code>.</p>
          </div>
        </section>
      </aside>
    </main>

    <script>
      const form = document.getElementById("chat-form");
      const chatLog = document.getElementById("chat-log");
      const statusEl = document.getElementById("status");
      const nicknameEl = document.getElementById("nickname");
      const questionEl = document.getElementById("question");
      const sendButton = document.getElementById("send-button");
      const emptyState = document.getElementById("empty-state");

      function appendMessage(role, content) {
        if (emptyState) {
          emptyState.remove();
        }
        const item = document.createElement("article");
        item.className = `message ${role}`;
        item.textContent = content;
        chatLog.appendChild(item);
        chatLog.scrollTop = chatLog.scrollHeight;
      }

      async function refreshChecks() {
        const rows = document.querySelectorAll("[data-path]");
        await Promise.all(Array.from(rows).map(async (row) => {
          const path = row.dataset.path;
          const state = row.querySelector(".state");
          try {
            const response = await fetch(path, { cache: "no-store" });
            state.textContent = response.ok ? "ok" : `HTTP ${response.status}`;
            state.className = response.ok ? "state ok" : "state fail";
          } catch (error) {
            state.textContent = "offline";
            state.className = "state fail";
          }
        }));
      }

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        statusEl.textContent = "Waiting for model response...";
        sendButton.disabled = true;

        const nickname = nicknameEl.value.trim();
        const question = questionEl.value.trim();
        appendMessage("user", question);

        try {
          const response = await fetch("/web/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nickname, question }),
          });
          const payload = await response.json();
          if (!response.ok) {
            throw new Error(payload.detail || "The bot is temporarily unavailable. Please try again.");
          }
          appendMessage("bot", payload.answer);
          questionEl.value = "";
          statusEl.textContent = "";
        } catch (error) {
          statusEl.textContent = error.message;
        } finally {
          sendButton.disabled = false;
          refreshChecks();
        }
      });

      refreshChecks();
      setInterval(refreshChecks, 30000);
    </script>
  </body>
</html>
"""


def normalize_nickname(value: str) -> str:
    cleaned = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9_-]+", "-", cleaned)
    cleaned = cleaned.strip("-")
    return cleaned[:40]
