(() => {
  "use strict";

  const chat = document.getElementById("chat");
  const welcome = document.getElementById("welcome");
  const form = document.getElementById("composer");
  const input = document.getElementById("input");
  const sendBtn = document.getElementById("send");
  const themeBtn = document.getElementById("theme-toggle");

  const history = []; // {role, content}
  let busy = false;

  /* ---------- Theme ---------- */
  themeBtn.addEventListener("click", () => {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("reel-theme", next); } catch (e) { /* storage unavailable */ }
  });

  /* ---------- Minimal, safe markdown ---------- */
  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function inline(s) {
    return escapeHtml(s)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
               '<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g,
               '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
  }

  function render(text) {
    const lines = text.split("\n");
    let html = "";
    let inList = false;
    let para = [];

    const flushPara = () => {
      if (para.length) { html += "<p>" + para.join("<br>") + "</p>"; para = []; }
    };

    for (const raw of lines) {
      const line = raw.trimEnd();
      const bullet = line.match(/^\s*[-*•]\s+(.*)$/);
      if (bullet) {
        flushPara();
        if (!inList) { html += "<ul>"; inList = true; }
        html += "<li>" + inline(bullet[1]) + "</li>";
      } else {
        if (inList) { html += "</ul>"; inList = false; }
        if (line.trim() === "") flushPara();
        else para.push(inline(line));
      }
    }
    if (inList) html += "</ul>";
    flushPara();
    return html;
  }

  /* ---------- Messages ---------- */
  function addMessage(role, text) {
    const wrap = document.createElement("div");
    wrap.className = "msg " + role;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    if (role === "user") bubble.textContent = text;
    else bubble.innerHTML = render(text);
    wrap.appendChild(bubble);
    chat.appendChild(wrap);
    scrollDown();
    return bubble;
  }

  function addTyping() {
    const wrap = document.createElement("div");
    wrap.className = "msg bot";
    wrap.innerHTML =
      '<div class="bubble"><span class="typing" role="status" aria-label="Reel is typing">' +
      "<span></span><span></span><span></span></span></div>";
    chat.appendChild(wrap);
    scrollDown();
    return wrap;
  }

  function scrollDown() {
    chat.scrollTop = chat.scrollHeight;
  }

  function setBusy(state) {
    busy = state;
    sendBtn.disabled = state;
    input.disabled = state;
    if (!state) input.focus();
  }

  /* ---------- Sending ---------- */
  async function send(text) {
    text = text.trim();
    if (!text || busy) return;

    if (welcome) welcome.remove();
    addMessage("user", text);
    history.push({ role: "user", content: text });
    input.value = "";
    autoGrow();
    setBusy(true);

    const typing = addTyping();
    let bubble = null;
    let reply = "";

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history }),
      });

      if (!res.ok) {
        let message = "Something went wrong. Please try again.";
        try { message = (await res.json()).error || message; } catch (e) { /* not JSON */ }
        throw new Error(message);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        reply += decoder.decode(value, { stream: true });
        if (!bubble) {
          typing.remove();
          bubble = addMessage("bot", reply);
        } else {
          bubble.innerHTML = render(reply);
          scrollDown();
        }
      }

      if (!reply.trim()) throw new Error("The assistant returned an empty reply. Please try again.");
      history.push({ role: "assistant", content: reply });
    } catch (err) {
      typing.remove();
      if (bubble) bubble.parentElement.remove();
      history.pop(); // drop the unanswered user message so a retry stays consistent
      const errBubble = addMessage("bot", err.message || "Something went wrong.");
      errBubble.classList.add("error");
    } finally {
      setBusy(false);
    }
  }

  /* ---------- Input behaviour ---------- */
  function autoGrow() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 140) + "px";
  }

  input.addEventListener("input", autoGrow);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    send(input.value);
  });

  document.getElementById("chips").addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (chip) send(chip.textContent);
  });

  input.focus();
})();
