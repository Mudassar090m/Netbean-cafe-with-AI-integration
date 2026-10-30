/* ==================================================
   BRIGHT BEAN CAFÉ — MENU PAGE LOGIC
   Works completely standalone — no server needed.
   Data is inlined directly; no fetch() required.
   ================================================== */

// ---------- Inlined menu data (no server/fetch needed) ----------
const MENU_DATA = [
  {
    "id": 1,
    "name": "Classic Cappuccino",
    "category": "Coffee",
    "description": "Rich espresso topped with smooth steamed milk and creamy foam.",
    "price": 4.50,
    "image": "../images/cappuccino.jpg",
    "featured": true,
    "tags": ["Customer Favorite", "Rich & Creamy"]
  },
  {
    "id": 2,
    "name": "Caramel Latte",
    "category": "Coffee",
    "description": "Smooth espresso blended with steamed milk and sweet caramel.",
    "price": 5.00,
    "image": "../images/caramel-latte.jpg"
  },
  {
    "id": 3,
    "name": "Mocha Delight",
    "category": "Coffee",
    "description": "A delicious combination of espresso, chocolate, steamed milk, and foam.",
    "price": 5.25,
    "image": "../images/mocha.jpg"
  },
  {
    "id": 4,
    "name": "Iced Vanilla Latte",
    "category": "Cold Drinks",
    "description": "Chilled espresso with creamy milk, vanilla, and ice.",
    "price": 5.00,
    "image": "../images/iced-vanilla-latte.jpg"
  },
  {
    "id": 5,
    "name": "Fresh Berry Smoothie",
    "category": "Cold Drinks",
    "description": "A refreshing blend of fresh strawberries, blueberries, yogurt, and honey.",
    "price": 5.50,
    "image": "../images/berry-smoothie.jpg"
  },
  {
    "id": 6,
    "name": "Butter Croissant",
    "category": "Pastries",
    "description": "Freshly baked, flaky croissant with a rich buttery flavor.",
    "price": 3.50,
    "image": "../images/croissant.jpg"
  },
  {
    "id": 7,
    "name": "Chocolate Muffin",
    "category": "Pastries",
    "description": "Soft and moist chocolate muffin filled with rich chocolate chips.",
    "price": 3.75,
    "image": "../images/chocolate-muffin.jpg"
  },
  {
    "id": 8,
    "name": "Chocolate Fudge Cake",
    "category": "Desserts",
    "description": "Rich chocolate cake layered with smooth chocolate fudge frosting.",
    "price": 4.75,
    "image": "../images/chocolate-cake.jpg"
  }
];

// ---------- Element references ----------
const menuGrid   = document.getElementById("menuGrid");
const menuStatus = document.getElementById("menuStatus");
const specialCard = document.getElementById("specialCard");
const filterBar  = document.getElementById("filterBar");

// ---------- App state ----------
let allMenuItems   = [];
let currentCategory = "All";

// ---------- Category badge class ----------
function getBadgeClass(category) {
  return `badge-${category.toLowerCase().replace(/\s+/g, "-")}`;
}

// ---------- Placeholder for missing images ----------
function createImagePlaceholder(label) {
  const div = document.createElement("div");
  div.className = "ph";
  div.setAttribute("data-label", label);
  div.innerHTML = `<svg viewBox="0 0 24 24" fill="none">
    <path d="M4 9h13a3 3 0 0 1 0 6h-.5" stroke="currentColor" stroke-width="1.3"/>
    <path d="M4 9v6.5A3.5 3.5 0 0 0 7.5 19h5A3.5 3.5 0 0 0 16 15.5V15" stroke="currentColor" stroke-width="1.3"/>
  </svg>`;
  return div;
}

// ---------- Build menu card image ----------
function createMenuImage(item) {
  const media = document.createElement("div");
  media.className = "menu-card-media";

  const badge = document.createElement("span");
  badge.className = `category-badge ${getBadgeClass(item.category)}`;
  badge.textContent = item.category;
  media.appendChild(badge);

  const img = document.createElement("img");
  img.src = item.image;
  img.alt = item.name;
  img.loading = "lazy";
  img.onerror = function () {
    img.remove();
    media.appendChild(createImagePlaceholder(item.name));
  };
  media.appendChild(img);
  return media;
}

// ---------- Build a single menu card ----------
function createMenuCard(item) {
  const card = document.createElement("article");
  card.className = "menu-card";
  card.setAttribute("data-category", item.category);
  card.appendChild(createMenuImage(item));

  const body = document.createElement("div");
  body.className = "menu-card-body";
  body.innerHTML = `
    <h3>${item.name}</h3>
    <p>${item.description}</p>
    <div class="menu-card-foot">
      <span class="price">$${item.price.toFixed(2)}</span>
      <button class="add-order-btn" type="button">
        <svg viewBox="0 0 24 24" fill="none"><path d="M6 2l1.5 4M18 2l-1.5 4M4 8h16l-1.5 10.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5L4 8z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
        Add to Order
      </button>
    </div>`;
  card.appendChild(body);

  const addBtn = body.querySelector(".add-order-btn");
  addBtn.addEventListener("click", () => {
    if (typeof window.bbAddToCart === "function") {
      window.bbAddToCart({ id: item.id, name: item.name, price: item.price });
    }
    addBtn.classList.add("added");
    addBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Added`;
    setTimeout(() => {
      addBtn.classList.remove("added");
      addBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none"><path d="M6 2l1.5 4M18 2l-1.5 4M4 8h16l-1.5 10.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5L4 8z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg> Add to Order`;
    }, 1400);
  });

  return card;
}

// ---------- Render grid ----------
function renderMenuGrid(category) {
  menuGrid.innerHTML = "";
  const items = category === "All"
    ? allMenuItems
    : allMenuItems.filter(i => i.category === category);

  if (items.length === 0) {
    menuStatus.textContent = "No items found in this category.";
    menuStatus.classList.remove("hidden");
    return;
  }
  menuStatus.classList.add("hidden");
  items.forEach((item, idx) => {
    const card = createMenuCard(item);
    menuGrid.appendChild(card);
    setTimeout(() => card.classList.add("visible"), idx * 60);
  });
}

// ---------- Render Café Special ----------
function renderSpecial() {
  const special = allMenuItems.find(i => i.featured) || allMenuItems[0];
  if (!special) return;

  specialCard.innerHTML = `
    <div class="special-media">
      <span class="special-ribbon">Café<br>Special</span>
    </div>
    <div class="special-content">
      <span class="eyebrow">Our Signature</span>
      <h2>${special.name}</h2>
      <p>${special.description}</p>
      <div class="special-tags" id="specialTags"></div>
      <div class="special-bottom">
        <span class="special-price">$${special.price.toFixed(2)}</span>
        <a href="#menuGrid" class="btn btn-primary">Try Our Special
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M6 2l1.5 4M18 2l-1.5 4M4 8h16l-1.5 10.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5L4 8z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </a>
      </div>
    </div>`;

  const media = specialCard.querySelector(".special-media");
  const img = document.createElement("img");
  img.src = special.image;
  img.alt = special.name;
  img.onerror = () => { img.remove(); media.appendChild(createImagePlaceholder(special.name)); };
  media.appendChild(img);

  const tagsWrap = document.getElementById("specialTags");
  (special.tags || []).forEach(tag => {
    const span = document.createElement("span");
    span.innerHTML = `<svg viewBox="0 0 24 24" fill="none"><path d="M12 20s-7.5-4.5-9.5-9C1 7 3 4 6.3 4c2 0 3.4 1.1 4 2.2.6-1.1 2-2.2 4-2.2C17.6 4 19.6 7 18 10.7c-2 4.5-6 9.3-6 9.3z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg> ${tag}`;
    tagsWrap.appendChild(span);
  });
}

// ---------- Filter clicks ----------
filterBar.addEventListener("click", (e) => {
  const btn = e.target.closest(".filter-btn");
  if (!btn) return;
  currentCategory = btn.getAttribute("data-category");
  filterBar.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  renderMenuGrid(currentCategory);
});

// ---------- Mobile nav ----------
const burger = document.getElementById("burgerBtn");
const navLinks = document.getElementById("navLinks");
if (burger && navLinks) {
  burger.addEventListener("click", () => navLinks.classList.toggle("open"));
  navLinks.querySelectorAll("a").forEach(l => l.addEventListener("click", () => navLinks.classList.remove("open")));
}

// ---------- Boot — use inlined data directly, no server needed ----------
document.addEventListener("DOMContentLoaded", () => {
  allMenuItems = MENU_DATA;
  if (menuStatus) menuStatus.classList.add("hidden");
  renderMenuGrid(currentCategory);
  renderSpecial();
});
