const API_BASE = "";

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function clearToken() {
  localStorage.removeItem("token");
  localStorage.removeItem("user_name");
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${getToken()}`,
  };
}

// Redirect to login if no token — call this on protected pages
function requireAuth() {
  if (!getToken()) {
    window.location.replace("/login.html");
  }
}

function showAuthError(message) {
  const el = document.getElementById("auth-error");
  if (el) el.textContent = message;
}

async function loginUser(email, password) {
  showAuthError("");
  try {
    const resp = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await resp.json();
    if (!resp.ok || !data.success) throw new Error(data.error || "Login failed.");
    setToken(data.data.token);
    localStorage.setItem("user_name", data.data.name || email);
    window.location.replace("/index.html");
  } catch (err) {
    showAuthError(err.message);
  }
}

async function registerUser(name, email, password) {
  showAuthError("");
  try {
    const resp = await fetch(`${API_BASE}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });
    const data = await resp.json();
    if (!resp.ok || !data.success) throw new Error(data.error || "Registration failed.");

    // Show success state — do not auto-login, let user go to login page manually
    const form = document.getElementById("register-form");
    const btn  = form.querySelector("button[type='submit']");

    // Hide all form fields
    form.querySelectorAll(".field").forEach(f => f.style.display = "none");

    // Show success message
    const msg = document.getElementById("auth-error");
    msg.style.color = "#6ee7b7";
    msg.textContent = "Account created successfully!";

    // Swap button to "Back to Login"
    btn.textContent = "Back to Login Page";
    btn.type = "button";
    btn.onclick = () => window.location.replace("/login.html");
  } catch (err) {
    showAuthError(err.message);
  }
}

function logout() {
  clearToken();
  window.location.replace("/login.html");
}
