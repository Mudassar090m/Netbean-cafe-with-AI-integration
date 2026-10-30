/* ==================================================
   BRIGHT BEAN CAFÉ — AI CHAT WIDGET + RECOMMENDATIONS
   Self-contained. Injects own CSS + HTML.
   Bottom-LEFT (cart is bottom-right).
   ================================================== */
(function () {
  // ---- Styles ----
  const css = `
  #bb-chat-bubble {
    position:fixed; bottom:28px; left:28px; z-index:890;
    width:56px; height:56px; border-radius:50%;
    background:#D89B4A; color:#2B1A10;
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 8px 24px -6px rgba(43,26,16,.4);
    cursor:pointer; border:none; font-family:inherit;
    transition:transform .25s ease;
  }
  #bb-chat-bubble:hover{transform:translateY(-3px) scale(1.06);}
  #bb-chat-bubble svg{width:26px;height:26px;}
  #bb-chat-badge-dot{
    position:absolute;top:-2px;right:-2px;
    width:12px;height:12px;border-radius:50%;
    background:#2B1A10;border:2px solid #FBF4E9;display:none;
  }
  #bb-chat-badge-dot.show{display:block;}

  #bb-chat-panel {
    position:fixed; bottom:96px; left:28px; z-index:891;
    width:min(370px,calc(100vw - 56px));
    background:#FDF9F2; border-radius:20px;
    box-shadow:0 20px 50px -16px rgba(43,26,16,.3);
    display:none; flex-direction:column;
    overflow:hidden; max-height:500px;
  }
  #bb-chat-panel.open{display:flex;}
  .bb-chat-head{
    background:#2B1A10; color:#FBF4E9;
    padding:16px 20px; display:flex; align-items:center; gap:10px;
  }
  .bb-chat-head svg{width:20px;height:20px;color:#D89B4A;flex-shrink:0;}
  .bb-chat-head h3{font-family:"Fraunces",Georgia,serif;font-size:16px;font-weight:600;flex:1;}
  .bb-chat-head .bb-chat-close{
    width:28px;height:28px;border-radius:50%;border:none;
    background:rgba(255,255,255,.12);cursor:pointer;color:#FBF4E9;
    display:flex;align-items:center;justify-content:center;
  }
  .bb-chat-head .bb-chat-close svg{width:14px;height:14px;color:#FBF4E9;}
  .bb-chat-body{
    flex:1; overflow-y:auto; padding:16px;
    display:flex; flex-direction:column; gap:10px;
    min-height:200px; max-height:320px;
  }
  .bb-msg{max-width:82%; padding:10px 14px; border-radius:14px; font-size:14px; line-height:1.5;}
  .bb-msg.user{background:#2B1A10;color:#FBF4E9;align-self:flex-end;border-bottom-right-radius:4px;}
  .bb-msg.bot{background:#F1E6D3;color:#2B1A10;align-self:flex-start;border-bottom-left-radius:4px;}
  .bb-msg.err{background:rgba(178,74,60,.1);color:#B24A3C;font-size:13px;}
  .bb-typing{display:flex;gap:4px;align-self:flex-start;padding:8px 14px;background:#F1E6D3;border-radius:14px;border-bottom-left-radius:4px;}
  .bb-typing span{width:7px;height:7px;border-radius:50%;background:#8A6748;animation:bbBlink 1.4s infinite;}
  .bb-typing span:nth-child(2){animation-delay:.2s;}
  .bb-typing span:nth-child(3){animation-delay:.4s;}
  @keyframes bbBlink{0%,60%,100%{opacity:.3;}30%{opacity:1;}}
  .bb-chat-input-row{display:flex;gap:8px;padding:12px 16px;border-top:1px solid rgba(59,36,21,.1);}
  .bb-chat-input-row input{
    flex:1;padding:11px 16px;border-radius:100px;
    border:1.5px solid rgba(59,36,21,.15);
    background:#FBF4E9;font-family:inherit;font-size:14px;color:#2B1A10;
    transition:border-color .2s;
  }
  .bb-chat-input-row input:focus{outline:none;border-color:#D89B4A;box-shadow:0 0 0 3px rgba(216,155,74,.15);}
  .bb-chat-send{
    width:42px;height:42px;border-radius:50%;border:none;
    background:#2B1A10;color:#FBF4E9;cursor:pointer;
    display:flex;align-items:center;justify-content:center;flex-shrink:0;
    transition:transform .2s;
  }
  .bb-chat-send:hover{transform:scale(1.08);}
  .bb-chat-send svg{width:16px;height:16px;}

  /* You might also like strip */
  #bb-rec-strip{
    position:fixed;bottom:28px;right:28px;z-index:888;
    transform:translateY(0);opacity:1;
    transition:transform .4s ease,opacity .4s ease;
    display:none;
  }
  #bb-rec-strip.show{display:flex;gap:8px;align-items:center;}
  #bb-rec-strip.hide{transform:translateY(20px);opacity:0;}
  .bb-rec-card{
    background:#FDF9F2;border:1px solid rgba(59,36,21,.12);
    border-radius:14px;padding:8px 14px;font-size:13px;font-weight:600;
    color:#2B1A10;cursor:pointer;white-space:nowrap;
    box-shadow:0 6px 16px -8px rgba(43,26,16,.2);
    transition:transform .2s;
  }
  .bb-rec-card:hover{transform:translateY(-2px);border-color:#D89B4A;}
  .bb-rec-label{font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#C1802E;}
  `;
  const s = document.createElement("style");
  s.textContent = css;
  document.head.appendChild(s);

  // ---- DOM ----
  document.body.insertAdjacentHTML("beforeend", `
    <button id="bb-chat-bubble" aria-label="Chat with café assistant">
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M4 5h16a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H8l-4 4V7a2 2 0 0 1 2-2z"
              stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
        <path d="M8 10h8M8 13h5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
      </svg>
      <span id="bb-chat-badge-dot"></span>
    </button>

    <div id="bb-chat-panel" role="dialog" aria-label="Café chat assistant">
      <div class="bb-chat-head">
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 20s-7.5-4.5-9.5-9C1 7 3 4 6.3 4c2 0 3.4 1.1 4 2.2.6-1.1 2-2.2 4-2.2C17.6 4 19.6 7 18 10.7c-2 4.5-6 9.3-6 9.3z"
                stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
        </svg>
        <h3>Café Assistant</h3>
        <button class="bb-chat-close" id="bb-chat-close" aria-label="Close chat">
          <svg viewBox="0 0 24 24" fill="none"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
      </div>
      <div class="bb-chat-body" id="bb-chat-body">
        <div class="bb-msg bot">Hi! I'm the Bright Bean Café assistant. Ask me about our menu, prices, or what's popular! ☕</div>
      </div>
      <div class="bb-chat-input-row">
        <input id="bb-chat-input" type="text" placeholder="Ask about our menu…" maxlength="300" autocomplete="off">
        <button class="bb-chat-send" id="bb-chat-send" aria-label="Send">
          <svg viewBox="0 0 24 24" fill="none"><path d="M4 12l16-8-6 16-3-6-7-2z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>
        </button>
      </div>
    </div>

    <div id="bb-rec-strip"></div>
  `);

  // ---- Chat logic ----
  const panel  = document.getElementById("bb-chat-panel");
  const body   = document.getElementById("bb-chat-body");
  const input  = document.getElementById("bb-chat-input");
  const send   = document.getElementById("bb-chat-send");
  const bubble = document.getElementById("bb-chat-bubble");
  const dot    = document.getElementById("bb-chat-badge-dot");

  function togglePanel() {
    panel.classList.toggle("open");
    if (panel.classList.contains("open")) {
      dot.classList.remove("show");
      input.focus();
    }
  }

  bubble.addEventListener("click", togglePanel);
  document.getElementById("bb-chat-close").addEventListener("click", togglePanel);

  function addMsg(text, cls) {
    const div = document.createElement("div");
    div.className = `bb-msg ${cls}`;
    div.textContent = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  function addTyping() {
    const t = document.createElement("div");
    t.className = "bb-typing";
    t.id = "bb-typing-ind";
    t.innerHTML = "<span></span><span></span><span></span>";
    body.appendChild(t);
    body.scrollTop = body.scrollHeight;
  }
  function removeTyping() {
    const t = document.getElementById("bb-typing-ind");
    if (t) t.remove();
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    addMsg(text, "user");
    input.value = "";
    addTyping();
    send.disabled = true;

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      removeTyping();

      if (resp.status === 503) {
        addMsg("Assistant is offline right now. Please call us at (555) 123-4567.", "err");
        return;
      }
      if (resp.status === 422) {
        addMsg("Please keep your message under 300 characters.", "err");
        return;
      }
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const data = await resp.json();
      addMsg(data.reply || "Hmm, I'm not sure about that.", "bot");
    } catch (e) {
      removeTyping();
      addMsg("Assistant is offline right now. Please call us at (555) 123-4567.", "err");
    } finally {
      send.disabled = false;
      input.focus();
    }
  }

  send.addEventListener("click", sendMessage);
  input.addEventListener("keydown", e => { if (e.key === "Enter") sendMessage(); });

  // ---- You might also like (recommendations) ----
  // Hook into cart additions — listens for localStorage changes from cart.js
  let recTimer;
  function getCartIds() {
    try { return JSON.parse(localStorage.getItem("bb_cart") || "[]").map(c => c.id); }
    catch { return []; }
  }

  async function showRecommendations() {
    const ids = getCartIds();
    if (ids.length === 0) return;

    try {
      const resp = await fetch("/api/recommend/cart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_ids: ids }),
      });
      if (!resp.ok) return;
      const items = await resp.json();
      if (!items || items.length === 0) return;

      const strip = document.getElementById("bb-rec-strip");
      strip.innerHTML = '<span class="bb-rec-label">You might also like</span>';
      items.slice(0, 3).forEach(item => {
        const card = document.createElement("div");
        card.className = "bb-rec-card";
        card.textContent = item.name;
        card.addEventListener("click", () => {
          if (typeof window.bbAddToCart === "function") {
            window.bbAddToCart({ id: item.id, name: item.name, price: item.price });
          }
          strip.classList.add("hide");
          setTimeout(() => strip.classList.remove("show"), 400);
        });
        strip.appendChild(card);
      });
      strip.classList.add("show");
      strip.classList.remove("hide");

      clearTimeout(recTimer);
      recTimer = setTimeout(() => {
        strip.classList.add("hide");
        setTimeout(() => strip.classList.remove("show"), 400);
      }, 12000);
    } catch {
      // silently fail
    }
  }

  // Listen for cart changes
  window.addEventListener("storage", e => {
    if (e.key === "bb_cart") showRecommendations();
  });
  // Also poll every 2s for cart changes (storage event doesn't fire in same tab)
  let lastCartSig = "";
  setInterval(() => {
    const sig = localStorage.getItem("bb_cart") || "";
    if (sig !== lastCartSig) {
      lastCartSig = sig;
      if (getCartIds().length > 0) showRecommendations();
    }
  }, 2000);

})();
