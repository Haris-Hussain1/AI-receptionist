// auth.js already declares: API_BASE, token, authHeaders(), requireAuth(), logout()

const conversationHistory = [];

// ── Auth guard ────────────────────────────────────────────────────────────────
if (!localStorage.getItem("token")) {
  window.location.replace("/login.html");
  throw new Error("redirect");
}

// ── Voice output ─────────────────────────────────────────────────────────────
function speak(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 1;
  utter.pitch = 1;
  window.speechSynthesis.speak(utter);
}

// ── Voice input ───────────────────────────────────────────────────────────────
function initVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const micBtn   = document.getElementById("mic-btn");
  const input    = document.getElementById("chat-input");
  const statusEl = document.getElementById("voice-status");

  if (!SpeechRecognition) {
    micBtn.disabled = true;
    micBtn.title = "Speech recognition not supported — use Chrome or Edge";
    micBtn.style.opacity = "0.35";
    micBtn.style.cursor = "not-allowed";
    return;
  }

  let recognition = null;
  let listening   = false;

  function buildRecognition() {
    const r = new SpeechRecognition();
    r.lang = "en-US";
    r.continuous = false;
    r.interimResults = false;
    r.maxAlternatives = 1;
    r.onstart  = function() { listening = true;  micBtn.classList.add("listening");    showStatus("🎙 Listening…", false); };
    r.onend    = function() { listening = false; micBtn.classList.remove("listening"); hideStatus(); recognition = null; };
    r.onerror  = function(e) {
      listening = false;
      micBtn.classList.remove("listening");
      recognition = null;
      const msgs = {
        "not-allowed": "⚠ Mic blocked — click the 🔒 icon in the address bar and allow microphone",
        "no-speech":   "No speech detected — try again",
        "network":     "⚠ Mic needs HTTPS or localhost",
        "aborted":     "",
      };
      const msg = msgs[e.error] || ("⚠ " + e.error);
      if (msg) { showStatus(msg, true); setTimeout(hideStatus, 4000); }
    };
    r.onresult = function(e) {
      const transcript = e.results[0][0].transcript;
      input.value = transcript;
      input.focus();
      setTimeout(function() {
        if (input.value.trim()) document.getElementById("chat-form").requestSubmit();
      }, 400);
    };
    return r;
  }

  function showStatus(msg, isError) {
    statusEl.textContent = msg;
    statusEl.style.color = isError ? "var(--red)" : "var(--green)";
    statusEl.classList.add("visible");
  }
  function hideStatus() {
    statusEl.classList.remove("visible");
    setTimeout(function() { statusEl.textContent = "🎙 Listening…"; statusEl.style.color = ""; }, 200);
  }

  micBtn.addEventListener("click", function() {
    if (listening && recognition) { recognition.stop(); return; }
    recognition = buildRecognition();
    try { recognition.start(); }
    catch(e) { showStatus("⚠ " + e.message, true); setTimeout(hideStatus, 3000); }
  });
}


function appendMessage(role, content) {
  const chatWindow = document.getElementById("chat-window");
  const msgEl  = document.createElement("div");
  msgEl.className = "chat-message " + role;

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar";
  avatar.textContent = role === "user" ? (localStorage.getItem("user_name") || "U")[0].toUpperCase() : "AI";

  const bubble = document.createElement("div");
  bubble.className = "chat-bubble";

  const text = document.createElement("div");
  text.className = "chat-text";
  text.textContent = content;

  bubble.appendChild(text);
  msgEl.appendChild(avatar);
  msgEl.appendChild(bubble);
  chatWindow.appendChild(msgEl);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return text;
}

async function sendChatMessage(message) {
  appendMessage("user", message);
  conversationHistory.push({ role: "user", content: message });

  const replyText = appendMessage("assistant", "Thinking...");
  const submitBtn = document.querySelector("#chat-form .send-btn");
  if (submitBtn) submitBtn.disabled = true;

  try {
    const resp = await fetch("/api/chat/", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ message }),
    });

    const data = await resp.json();

    if (resp.status === 401) {
      logout();
      return;
    }

    if (!resp.ok) throw new Error(data.error || "Server error " + resp.status);

    const reply = data.data && data.data.reply ? data.data.reply : "(No reply)";
    replyText.textContent = reply;
    conversationHistory.push({ role: "assistant", content: reply });
    speak(reply);

  } catch (err) {
    replyText.textContent = "Error: " + err.message;
  } finally {
    if (submitBtn) submitBtn.disabled = false;
  }
}

function initChat() {
  const form  = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");

  form.addEventListener("submit", function(e) {
    e.preventDefault();
    const value = input.value.trim();
    if (!value) return;
    input.value = "";
    sendChatMessage(value);
  });

  appendMessage("assistant", "Hello. I am your AI receptionist. How may I assist you today?");
  speak("Hello. I am your AI receptionist. How may I assist you today?");
}

// ── Booking ───────────────────────────────────────────────────────────────────
async function submitBookingForm(form) {
  const statusEl = document.getElementById("booking-status");
  statusEl.textContent = "Saving appointment...";

  const payload = {
    name:   form.name.value.trim(),
    email:  form.email.value.trim(),
    date:   form.date.value,
    time:   form.time.value,
    reason: form.reason.value.trim(),
  };

  try {
    const resp = await fetch("/api/booking/", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok || !data.success) throw new Error(data.error || "Server error");
    statusEl.textContent = "Appointment saved!";
    form.reset();
    await loadAppointments();
  } catch (err) {
    statusEl.textContent = "Could not save: " + err.message;
    statusEl.style.color = "#f97373";
  } finally {
    setTimeout(function() { statusEl.textContent = ""; statusEl.style.color = ""; }, 4000);
  }
}

async function loadAppointments() {
  const listEl = document.getElementById("appointments-list");
  listEl.innerHTML = "<li>Loading...</li>";
  try {
    const resp = await fetch("/api/booking/", { headers: authHeaders() });
    if (resp.status === 401) { listEl.innerHTML = "<li>Please log in.</li>"; return; }
    const data = await resp.json();
    if (!resp.ok || !data.success) throw new Error(data.error || "Server error");
    const items = data.data || [];
    if (!items.length) { listEl.innerHTML = "<li class='appt-empty'>No appointments yet.</li>"; return; }
    listEl.innerHTML = "";
    items.forEach(function(a) {
      const li   = document.createElement("li");
      const main = document.createElement("div");
      main.className = "appt-main-line";
      const nameSpan = document.createElement("span");
      nameSpan.className = "appt-name";
      nameSpan.textContent = a.name || "Unknown";
      const when = document.createElement("span");
      when.className = "appt-when";
      when.textContent = (a.date || "?") + " - " + (a.time || "?");
      main.appendChild(nameSpan);
      main.appendChild(when);
      li.appendChild(main);
      if (a.reason) {
        const r = document.createElement("div");
        r.className = "appt-reason";
        r.textContent = a.reason;
        li.appendChild(r);
      }
      listEl.appendChild(li);
    });
  } catch (err) {
    listEl.innerHTML = "<li>Unable to load: " + err.message + "</li>";
  }
}

function initBooking() {
  const form = document.getElementById("booking-form");
  if (!form) return;
  form.addEventListener("submit", function(e) {
    e.preventDefault();
    submitBookingForm(form);
  });
  document.getElementById("refresh-appointments")
    .addEventListener("click", function() { loadAppointments(); });
  loadAppointments();
}

// ── Boot ──────────────────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", function() {
  var name = localStorage.getItem("user_name") || "";
  var nameEl = document.getElementById("user-display-name");
  if (nameEl) nameEl.textContent = name;
  var avatarEl = document.getElementById("user-avatar-initials");
  if (avatarEl && name) avatarEl.textContent = name.trim().split(" ").map(function(w){ return w[0]; }).slice(0,2).join("").toUpperCase();
  initChat();
  initBooking();
  initVoiceInput();
});
