/* ==================================================
   BRIGHT BEAN CAFÉ — CART & ORDER SYSTEM
   Works completely standalone — no server needed.
   Cart and orders are saved to localStorage.
   ================================================== */

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------
(function injectStyles() {
  const css = `
  #bb-cart-btn {
    position:fixed; bottom:28px; right:28px; z-index:900;
    width:60px; height:60px; border-radius:50%;
    background:#2B1A10; color:#FBF4E9;
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 8px 24px -6px rgba(43,26,16,.55);
    cursor:pointer; border:none; font-family:inherit;
    transition:transform .25s ease, box-shadow .25s ease;
  }
  #bb-cart-btn:hover{transform:translateY(-3px) scale(1.06);}
  #bb-cart-btn svg{width:26px;height:26px;}
  #bb-cart-badge{
    position:absolute;top:-4px;right:-4px;
    min-width:22px;height:22px;border-radius:11px;
    background:#D89B4A;color:#2B1A10;
    font-size:12px;font-weight:800;line-height:22px;
    text-align:center;padding:0 5px;display:none;
  }
  #bb-cart-backdrop{
    position:fixed;inset:0;z-index:910;
    background:rgba(15,9,5,.55);opacity:0;pointer-events:none;
    transition:opacity .3s ease;
  }
  #bb-cart-backdrop.open{opacity:1;pointer-events:all;}
  #bb-cart-panel{
    position:fixed;top:0;right:0;bottom:0;z-index:920;
    width:min(430px,100vw);background:#FDF9F2;
    display:flex;flex-direction:column;
    transform:translateX(100%);
    transition:transform .35s cubic-bezier(.4,0,.2,1);
    box-shadow:-12px 0 40px -10px rgba(43,26,16,.22);
  }
  #bb-cart-panel.open{transform:translateX(0);}
  .bb-cart-head{
    display:flex;align-items:center;justify-content:space-between;
    padding:22px 24px;border-bottom:1px solid rgba(59,36,21,.1);
  }
  .bb-cart-head h2{font-family:"Fraunces",Georgia,serif;font-size:22px;font-weight:600;color:#2B1A10;}
  .bb-cart-close{
    width:36px;height:36px;border-radius:50%;border:none;
    background:#F1E6D3;cursor:pointer;display:flex;align-items:center;justify-content:center;
  }
  .bb-cart-close svg{width:16px;height:16px;color:#2B1A10;}
  .bb-cart-items{flex:1;overflow-y:auto;padding:16px 24px;}
  .bb-cart-empty{
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    height:100%;gap:12px;color:#8A6748;font-size:14px;
  }
  .bb-cart-empty svg{width:48px;height:48px;opacity:.35;}
  .bb-cart-item{
    display:grid;grid-template-columns:1fr auto;
    align-items:start;gap:10px;
    padding:14px 0;border-bottom:1px solid rgba(59,36,21,.08);
  }
  .bb-cart-item:last-child{border-bottom:none;}
  .bb-item-name{font-weight:700;font-size:14.5px;color:#2B1A10;margin-bottom:4px;}
  .bb-item-price{font-size:13px;color:#8A6748;}
  .bb-item-controls{display:flex;align-items:center;gap:8px;}
  .bb-qty-btn{
    width:28px;height:28px;border-radius:50%;
    border:1.5px solid rgba(59,36,21,.18);background:#FBF4E9;
    cursor:pointer;font-size:16px;font-weight:700;color:#2B1A10;
    display:flex;align-items:center;justify-content:center;
  }
  .bb-qty-num{font-size:14px;font-weight:700;color:#2B1A10;min-width:18px;text-align:center;}
  .bb-remove-btn{
    width:28px;height:28px;border-radius:50%;border:none;
    background:transparent;cursor:pointer;color:#B24A3C;
    display:flex;align-items:center;justify-content:center;
  }
  .bb-remove-btn svg{width:14px;height:14px;}
  .bb-cart-foot{padding:20px 24px;border-top:1px solid rgba(59,36,21,.1);}
  .bb-cart-total{
    display:flex;justify-content:space-between;align-items:center;
    font-size:16px;font-weight:700;color:#2B1A10;margin-bottom:16px;
  }
  .bb-cart-total span:last-child{color:#D89B4A;font-size:20px;}
  .bb-checkout-btn{
    width:100%;padding:14px;border-radius:100px;border:none;
    background:#2B1A10;color:#FBF4E9;
    font-family:inherit;font-size:15px;font-weight:700;cursor:pointer;
    display:flex;align-items:center;justify-content:center;gap:8px;
    box-shadow:0 8px 20px -8px rgba(43,26,16,.5);
    transition:transform .2s;
  }
  .bb-checkout-btn:hover{transform:translateY(-2px);}
  .bb-clear-btn{
    width:100%;padding:10px;border-radius:100px;
    border:1.5px solid rgba(59,36,21,.15);background:transparent;
    font-family:inherit;font-size:13px;font-weight:600;color:#8A6748;
    cursor:pointer;margin-top:8px;
  }
  /* checkout modal */
  #bb-checkout-modal{
    position:fixed;inset:0;z-index:950;
    background:rgba(15,9,5,.72);
    display:none;align-items:flex-start;justify-content:center;
    padding:20px;overflow-y:auto;backdrop-filter:blur(4px);
  }
  #bb-checkout-modal.open{display:flex;}
  .bb-modal-box{
    background:#FDF9F2;border-radius:24px;padding:36px;
    width:min(500px,100%);margin:auto;
    box-shadow:0 30px 60px -20px rgba(43,26,16,.45);
  }
  .bb-modal-box h3{font-family:"Fraunces",Georgia,serif;font-size:22px;font-weight:600;color:#2B1A10;margin-bottom:6px;}
  .bb-modal-sub{font-size:13.5px;color:#8A6748;margin-bottom:20px;}
  .bb-modal-section{font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#C1802E;margin:18px 0 10px;}
  .bb-modal-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
  .bb-modal-field{margin-bottom:14px;}
  .bb-modal-field label{display:block;font-size:13px;font-weight:700;color:#5C3D26;margin-bottom:6px;}
  .bb-modal-field input,.bb-modal-field textarea,.bb-modal-field select{
    width:100%;padding:12px 16px;border-radius:12px;
    border:1.5px solid rgba(59,36,21,.15);
    background:#FBF4E9;font-family:inherit;font-size:14px;color:#2B1A10;
    transition:border-color .2s;
  }
  .bb-modal-field textarea{resize:vertical;min-height:72px;}
  .bb-modal-field input:focus,.bb-modal-field textarea:focus{
    outline:none;border-color:#D89B4A;box-shadow:0 0 0 4px rgba(216,155,74,.15);
  }
  .bb-modal-field input.bb-invalid,.bb-modal-field textarea.bb-invalid{border-color:#B24A3C;}
  .bb-field-err{font-size:12px;color:#B24A3C;margin-top:4px;display:none;}
  .bb-field-err.show{display:block;}
  .bb-type-toggle{display:flex;gap:10px;margin-bottom:14px;}
  .bb-type-btn{
    flex:1;padding:11px;border-radius:100px;
    border:1.5px solid rgba(59,36,21,.15);background:#FBF4E9;
    font-family:inherit;font-size:13.5px;font-weight:600;color:#8A6748;cursor:pointer;
  }
  .bb-type-btn.active{background:#2B1A10;color:#FBF4E9;border-color:#2B1A10;}
  .bb-modal-summary{background:#F1E6D3;border-radius:14px;padding:16px;margin-bottom:18px;}
  .bb-modal-summary-title{font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#5C3D26;margin-bottom:10px;}
  .bb-summary-row{display:flex;justify-content:space-between;font-size:13.5px;color:#2B1A10;margin-bottom:6px;}
  .bb-summary-row.total{font-weight:700;border-top:1px solid rgba(59,36,21,.15);padding-top:8px;margin-top:4px;}
  .bb-modal-actions{display:flex;gap:10px;margin-top:22px;}
  .bb-modal-confirm{
    flex:1;padding:13px;border-radius:100px;border:none;
    background:#2B1A10;color:#FBF4E9;
    font-family:inherit;font-size:14px;font-weight:700;cursor:pointer;
  }
  .bb-modal-cancel{
    padding:13px 20px;border-radius:100px;
    border:1.5px solid rgba(59,36,21,.15);background:transparent;
    font-family:inherit;font-size:14px;font-weight:600;color:#8A6748;cursor:pointer;
  }
  /* confirmed */
  #bb-order-confirmed{
    position:fixed;inset:0;z-index:960;
    background:rgba(15,9,5,.72);
    display:none;align-items:center;justify-content:center;
    padding:20px;backdrop-filter:blur(4px);
  }
  #bb-order-confirmed.open{display:flex;}
  .bb-confirmed-box{
    background:#FDF9F2;border-radius:24px;padding:44px 36px;
    width:min(400px,100%);text-align:center;
    box-shadow:0 30px 60px -20px rgba(43,26,16,.45);
  }
  .bb-confirmed-icon{
    width:64px;height:64px;border-radius:50%;
    background:rgba(75,91,65,.12);margin:0 auto 20px;
    display:flex;align-items:center;justify-content:center;
  }
  .bb-confirmed-icon svg{width:32px;height:32px;color:#4B5B41;}
  .bb-confirmed-box h3{font-family:"Fraunces",Georgia,serif;font-size:22px;font-weight:600;color:#2B1A10;margin-bottom:8px;}
  .bb-confirmed-box p{font-size:14px;color:#8A6748;line-height:1.6;margin-bottom:6px;}
  .bb-confirmed-box strong{color:#D89B4A;}
  .bb-confirmed-close{
    margin-top:24px;padding:13px 32px;border-radius:100px;border:none;
    background:#2B1A10;color:#FBF4E9;
    font-family:inherit;font-size:14px;font-weight:700;cursor:pointer;
  }
  /* toast */
  #bb-toast{
    position:fixed;bottom:100px;right:28px;z-index:999;
    background:#2B1A10;color:#FBF4E9;
    padding:12px 20px;border-radius:100px;
    font-size:13.5px;font-weight:600;
    display:flex;align-items:center;gap:8px;
    transform:translateY(20px);opacity:0;
    transition:transform .3s ease,opacity .3s ease;pointer-events:none;
  }
  #bb-toast.show{transform:translateY(0);opacity:1;}
  #bb-toast svg{width:15px;height:15px;color:#D89B4A;flex-shrink:0;}
  @media(max-width:520px){.bb-modal-row{grid-template-columns:1fr;}}
  `;
  const s = document.createElement("style");
  s.textContent = css;
  document.head.appendChild(s);
})();

// ---------------------------------------------------------------------------
// DOM
// ---------------------------------------------------------------------------
(function injectDOM() {
  document.body.insertAdjacentHTML("beforeend", `
    <button id="bb-cart-btn" aria-label="Open cart">
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M6 2l1.5 4M18 2l-1.5 4M4 8h16l-1.5 10.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5L4 8z"
              stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="9" cy="22" r="1" fill="currentColor"/>
        <circle cx="15" cy="22" r="1" fill="currentColor"/>
      </svg>
      <span id="bb-cart-badge"></span>
    </button>

    <div id="bb-cart-backdrop"></div>

    <div id="bb-cart-panel" role="dialog" aria-label="Your cart">
      <div class="bb-cart-head">
        <h2>Your Order</h2>
        <button class="bb-cart-close" id="bb-cart-close" aria-label="Close">
          <svg viewBox="0 0 24 24" fill="none"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
      </div>
      <div class="bb-cart-items" id="bb-cart-items"></div>
      <div class="bb-cart-foot" id="bb-cart-foot" style="display:none">
        <div class="bb-cart-total">
          <span>Total</span>
          <span id="bb-cart-total-price">$0.00</span>
        </div>
        <button class="bb-checkout-btn" id="bb-checkout-open">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M6 2l1.5 4M18 2l-1.5 4M4 8h16l-1.5 10.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5L4 8z"
                  stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Proceed to Checkout
        </button>
        <button class="bb-clear-btn" id="bb-cart-clear">Clear cart</button>
      </div>
    </div>

    <!-- Checkout modal -->
    <div id="bb-checkout-modal">
      <div class="bb-modal-box">
        <h3>Complete Your Order</h3>
        <p class="bb-modal-sub">Fill in your details and we'll get it ready.</p>

        <div class="bb-modal-summary">
          <div class="bb-modal-summary-title">Order Summary</div>
          <div id="bb-summary-lines"></div>
        </div>

        <p class="bb-modal-section">How would you like it?</p>
        <div class="bb-type-toggle">
          <button class="bb-type-btn active" data-type="pickup">🏪 Pick Up In Store</button>
          <button class="bb-type-btn" data-type="delivery">🚴 Home Delivery</button>
        </div>

        <div class="bb-modal-field" id="bb-address-field" style="display:none">
          <label for="bb-cust-address">Delivery Address <span style="color:#B24A3C">*</span></label>
          <textarea id="bb-cust-address" rows="2" placeholder="Street, City, Postcode"></textarea>
          <div class="bb-field-err" id="bb-address-err">Please enter your delivery address.</div>
        </div>

        <p class="bb-modal-section">Your Details</p>
        <div class="bb-modal-row">
          <div class="bb-modal-field">
            <label for="bb-cust-name">Full Name <span style="color:#B24A3C">*</span></label>
            <input id="bb-cust-name" type="text" placeholder="Jane Smith" autocomplete="name">
            <div class="bb-field-err" id="bb-name-err">Please enter your name.</div>
          </div>
          <div class="bb-modal-field">
            <label for="bb-cust-phone">Phone Number</label>
            <input id="bb-cust-phone" type="tel" placeholder="+1 555 123 4567" autocomplete="tel">
          </div>
        </div>
        <div class="bb-modal-field">
          <label for="bb-cust-email">Email Address <span style="color:#B24A3C">*</span></label>
          <input id="bb-cust-email" type="email" placeholder="jane@example.com" autocomplete="email">
          <div class="bb-field-err" id="bb-email-err">Please enter a valid email.</div>
        </div>
        <div class="bb-modal-field">
          <label for="bb-cust-notes">Special Instructions <span style="color:#8A6748;font-weight:400">(optional)</span></label>
          <textarea id="bb-cust-notes" rows="2" placeholder="Allergies, extra sugar, pickup time…"></textarea>
        </div>

        <div class="bb-modal-actions">
          <button class="bb-modal-cancel" id="bb-modal-cancel">Back</button>
          <button class="bb-modal-confirm" id="bb-modal-confirm">Place Order →</button>
        </div>
      </div>
    </div>

    <!-- Order confirmed -->
    <div id="bb-order-confirmed">
      <div class="bb-confirmed-box">
        <div class="bb-confirmed-icon">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3>Order Placed!</h3>
        <p>Thanks, <strong id="bb-conf-name"></strong>!</p>
        <p>Order <strong id="bb-conf-id"></strong> — <strong id="bb-conf-total"></strong></p>
        <p id="bb-conf-type" style="margin-top:6px;font-size:13px;"></p>
        <p style="margin-top:8px;font-size:13px;color:#8A6748">
          Confirmation sent to <strong id="bb-conf-email"></strong> ☕
        </p>
        <button class="bb-confirmed-close" id="bb-confirmed-close">Great, thanks!</button>
      </div>
    </div>

    <!-- Toast -->
    <div id="bb-toast">
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span id="bb-toast-msg"></span>
    </div>
  `);
})();

// ---------------------------------------------------------------------------
// Cart state — localStorage
// ---------------------------------------------------------------------------
const CART_KEY   = "bb_cart";
const ORDERS_KEY = "bb_orders";

function loadCart() {
  try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
  catch { return []; }
}
function saveCart(c) { localStorage.setItem(CART_KEY, JSON.stringify(c)); }

let cart = loadCart();

// ---------------------------------------------------------------------------
// Public API used by menu.js
// ---------------------------------------------------------------------------
window.bbAddToCart = function (item) {
  const existing = cart.find(c => c.id === item.id);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ id: item.id, name: item.name, price: item.price, qty: 1 });
  }
  saveCart(cart);
  renderCart();
  showToast(`${item.name} added to order`);
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function totalItems() { return cart.reduce((s, c) => s + c.qty, 0); }
function totalPrice() { return cart.reduce((s, c) => s + c.price * c.qty, 0); }

function renderCart() {
  const badge   = document.getElementById("bb-cart-badge");
  const itemsEl = document.getElementById("bb-cart-items");
  const footEl  = document.getElementById("bb-cart-foot");
  const totalEl = document.getElementById("bb-cart-total-price");

  badge.textContent  = totalItems();
  badge.style.display = totalItems() > 0 ? "block" : "none";

  if (cart.length === 0) {
    itemsEl.innerHTML = `
      <div class="bb-cart-empty">
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M6 2l1.5 4M18 2l-1.5 4M4 8h16l-1.5 10.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5L4 8z"
                stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>Your cart is empty</span>
        <span style="font-size:12.5px">Add items from the menu above</span>
      </div>`;
    footEl.style.display = "none";
    return;
  }

  footEl.style.display = "block";
  totalEl.textContent  = `$${totalPrice().toFixed(2)}`;
  itemsEl.innerHTML    = "";

  cart.forEach(item => {
    const row = document.createElement("div");
    row.className = "bb-cart-item";
    row.innerHTML = `
      <div>
        <div class="bb-item-name">${item.name}</div>
        <div class="bb-item-price">$${(item.price * item.qty).toFixed(2)}
          ${item.qty > 1 ? `<span style="color:#aaa;font-size:12px"> (${item.qty} × $${item.price.toFixed(2)})</span>` : ""}
        </div>
      </div>
      <div class="bb-item-controls">
        <button class="bb-qty-btn" data-id="${item.id}" data-action="dec">−</button>
        <span class="bb-qty-num">${item.qty}</span>
        <button class="bb-qty-btn" data-id="${item.id}" data-action="inc">+</button>
        <button class="bb-remove-btn" data-id="${item.id}" data-action="remove" aria-label="Remove">
          <svg viewBox="0 0 24 24" fill="none"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
      </div>`;
    itemsEl.appendChild(row);
  });
}

// qty / remove (delegated)
document.getElementById("bb-cart-items").addEventListener("click", e => {
  const btn = e.target.closest("[data-action]");
  if (!btn) return;
  const id     = Number(btn.dataset.id);
  const action = btn.dataset.action;
  const item   = cart.find(c => c.id === id);
  if (!item) return;
  if (action === "inc")    { item.qty += 1; }
  else if (action === "dec") { item.qty -= 1; if (item.qty <= 0) cart = cart.filter(c => c.id !== id); }
  else if (action === "remove") { cart = cart.filter(c => c.id !== id); }
  saveCart(cart);
  renderCart();
});

// ---------------------------------------------------------------------------
// Panel open / close
// ---------------------------------------------------------------------------
function openCart()  {
  document.getElementById("bb-cart-panel").classList.add("open");
  document.getElementById("bb-cart-backdrop").classList.add("open");
  document.body.style.overflow = "hidden";
}
function closeCart() {
  document.getElementById("bb-cart-panel").classList.remove("open");
  document.getElementById("bb-cart-backdrop").classList.remove("open");
  document.body.style.overflow = "";
}

document.getElementById("bb-cart-btn").addEventListener("click", openCart);
document.getElementById("bb-cart-close").addEventListener("click", closeCart);
document.getElementById("bb-cart-backdrop").addEventListener("click", closeCart);
document.getElementById("bb-cart-clear").addEventListener("click", () => {
  cart = []; saveCart(cart); renderCart();
});

// ---------------------------------------------------------------------------
// Checkout modal
// ---------------------------------------------------------------------------
let orderType = "pickup";

document.querySelectorAll(".bb-type-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    orderType = btn.dataset.type;
    document.querySelectorAll(".bb-type-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    const af = document.getElementById("bb-address-field");
    af.style.display = orderType === "delivery" ? "block" : "none";
    if (orderType === "pickup") {
      document.getElementById("bb-cust-address").classList.remove("bb-invalid");
      document.getElementById("bb-address-err").classList.remove("show");
    }
  });
});

document.getElementById("bb-checkout-open").addEventListener("click", () => {
  const lines = document.getElementById("bb-summary-lines");
  lines.innerHTML = "";
  cart.forEach(item => {
    const row = document.createElement("div");
    row.className = "bb-summary-row";
    row.innerHTML = `<span>${item.qty} × ${item.name}</span><span>$${(item.price * item.qty).toFixed(2)}</span>`;
    lines.appendChild(row);
  });
  const tot = document.createElement("div");
  tot.className = "bb-summary-row total";
  tot.innerHTML = `<span>Total</span><span>$${totalPrice().toFixed(2)}</span>`;
  lines.appendChild(tot);
  document.getElementById("bb-checkout-modal").classList.add("open");
});

document.getElementById("bb-modal-cancel").addEventListener("click", () => {
  document.getElementById("bb-checkout-modal").classList.remove("open");
});

// ---------------------------------------------------------------------------
// Place order — save to localStorage
// ---------------------------------------------------------------------------
document.getElementById("bb-modal-confirm").addEventListener("click", () => {
  const nameEl  = document.getElementById("bb-cust-name");
  const emailEl = document.getElementById("bb-cust-email");
  const phoneEl = document.getElementById("bb-cust-phone");
  const addrEl  = document.getElementById("bb-cust-address");
  const notesEl = document.getElementById("bb-cust-notes");
  const confirmBtn = document.getElementById("bb-modal-confirm");

  let valid = true;

  const nameOk = nameEl.value.trim().length >= 2;
  nameEl.classList.toggle("bb-invalid", !nameOk);
  document.getElementById("bb-name-err").classList.toggle("show", !nameOk);
  if (!nameOk) valid = false;

  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailEl.value.trim());
  emailEl.classList.toggle("bb-invalid", !emailOk);
  document.getElementById("bb-email-err").classList.toggle("show", !emailOk);
  if (!emailOk) valid = false;

  const addrOk = orderType === "pickup" || addrEl.value.trim().length >= 5;
  addrEl.classList.toggle("bb-invalid", !addrOk);
  document.getElementById("bb-address-err").classList.toggle("show", !addrOk);
  if (!addrOk) valid = false;

  if (!valid) return;

  confirmBtn.disabled = true;
  confirmBtn.textContent = "Placing order…";

  try {
    // Build order object
    const orderId = "BB-" + Date.now();
    const order = {
      id:               orderId,
      customer_name:    nameEl.value.trim(),
      customer_email:   emailEl.value.trim(),
      customer_phone:   phoneEl.value.trim() || null,
      order_type:       orderType,
      delivery_address: orderType === "delivery" ? addrEl.value.trim() : null,
      notes:            notesEl.value.trim() || null,
      total:            Math.round(totalPrice() * 100) / 100,
      status:           "pending",
      placed_at:        new Date().toISOString(),
      items:            cart.map(c => ({
        menu_item_id: c.id,
        name:         c.name,
        price:        c.price,
        quantity:     c.qty
      }))
    };

    // Save to localStorage
    const orders = JSON.parse(localStorage.getItem(ORDERS_KEY) || "[]");
    orders.unshift(order);
    localStorage.setItem(ORDERS_KEY, JSON.stringify(orders));

    // Show confirmation
    document.getElementById("bb-checkout-modal").classList.remove("open");
    document.getElementById("bb-conf-name").textContent  = order.customer_name;
    document.getElementById("bb-conf-id").textContent    = order.id;
    document.getElementById("bb-conf-total").textContent = `$${order.total.toFixed(2)}`;
    document.getElementById("bb-conf-email").textContent = order.customer_email;
    document.getElementById("bb-conf-type").textContent  =
      orderType === "delivery"
        ? `📦 Delivery to: ${order.delivery_address}`
        : "🏪 Pick up in store";
    document.getElementById("bb-order-confirmed").classList.add("open");

    // Reset
    cart = []; saveCart(cart); renderCart(); closeCart();
    nameEl.value = ""; emailEl.value = ""; phoneEl.value = "";
    addrEl.value = ""; notesEl.value = "";

  } catch (err) {
    console.error("Order failed:", err);
    alert("Sorry, could not place order: " + err.message);
  } finally {
    confirmBtn.disabled = false;
    confirmBtn.textContent = "Place Order →";
  }
});

document.getElementById("bb-confirmed-close").addEventListener("click", () => {
  document.getElementById("bb-order-confirmed").classList.remove("open");
});

document.addEventListener("keydown", e => {
  if (e.key !== "Escape") return;
  document.getElementById("bb-order-confirmed").classList.remove("open");
  document.getElementById("bb-checkout-modal").classList.remove("open");
  closeCart();
});

// ---------------------------------------------------------------------------
// Toast
// ---------------------------------------------------------------------------
let _toastTimer;
function showToast(msg) {
  const toast = document.getElementById("bb-toast");
  document.getElementById("bb-toast-msg").textContent = msg;
  toast.classList.add("show");
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => toast.classList.remove("show"), 2400);
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
renderCart();
