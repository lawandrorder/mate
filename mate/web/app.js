const log = document.getElementById("log");
const form = document.getElementById("form");
const input = document.getElementById("text");

function addBubble(text, who) {
  const el = document.createElement("div");
  el.className = `bubble ${who}`;
  el.textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}

function uid() {
  const key = "mate-demo-user";
  let value = localStorage.getItem(key);
  if (!value) {
    value = "web-" + Math.random().toString(36).slice(2, 10);
    localStorage.setItem(key, value);
  }
  return value;
}

addBubble(
  "Illustrative starter thread. Example codes, deliveries and cashback are fictional.",
  "system"
);
addBubble(
  "Hey — text me before you shop. Try cashback at a store, a code, a tracking number, or a link to watch.",
  "them"
);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addBubble(text, "you");
  try {
    const response = await fetch("/api/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, user_id: uid() }),
    });
    const data = await response.json();
    if (!response.ok) {
      addBubble(data.error || "Something went wrong.", "them");
      return;
    }
    addBubble(data.reply, "them");
  } catch (err) {
    addBubble("Couldn't reach the local starter. Is the server still running?", "them");
  }
});

document.querySelectorAll("[data-fill]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.getAttribute("data-fill");
    input.focus();
    form.requestSubmit();
  });
});
