/* ==================================================
   BRIGHT BEAN CAFÉ — MENU PAGE LOGIC
   ==================================================
   1. Fetches menu data from data/menu.json
   2. Stores it in an array
   3. Renders menu cards dynamically
   4. Filters cards by category on button click
   5. Renders the Café Special from the JSON data
   6. Handles loading / error states
   ================================================== */

// ---------- Element references ----------
const menuGrid = document.getElementById("menuGrid");
const menuStatus = document.getElementById("menuStatus");
const specialCard = document.getElementById("specialCard");
const filterBar = document.getElementById("filterBar");

// ---------- App state ----------
let allMenuItems = [];      // every item loaded from menu.json
let currentCategory = "All"; // which filter is currently active

// ---------- Category badge class helper ----------
// Turns "Cold Drinks" into "badge-cold-drinks" so it matches our CSS classes
function getBadgeClass(category) {
  const slug = category.toLowerCase().replace(/\s+/g, "-");
  return `badge-${slug}`;
}

// ---------- Build a placeholder block for missing images ----------
function createImagePlaceholder(label) {
  const placeholder = document.createElement("div");
  placeholder.className = "ph";
  placeholder.setAttribute("data-label", label);
  placeholder.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none">
      <path d="M4 9h13a3 3 0 0 1 0 6h-.5" stroke="currentColor" stroke-width="1.3"/>
      <path d="M4 9v6.5A3.5 3.5 0 0 0 7.5 19h5A3.5 3.5 0 0 0 16 15.5V15" stroke="currentColor" stroke-width="1.3"/>
    </svg>`;
  return placeholder;
}

// ---------- Build the image element for a menu card ----------
// If the image fails to load (because the user hasn't added the file yet),
// it is automatically swapped out for a placeholder so the layout never breaks.
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
    media.appendChild(createImagePlaceholder(`Add: ${item.name} photo`));
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
    </div>
  `;
  card.appendChild(body);

  // Little "added" confirmation animation on click
  const addBtn = body.querySelector(".add-order-btn");
  addBtn.addEventListener("click", () => {
    addBtn.classList.add("added");
    addBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      Added
    `;
    setTimeout(() => {
      addBtn.classList.remove("added");
      addBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none"><path d="M6 2l1.5 4M18 2l-1.5 4M4 8h16l-1.5 10.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5L4 8z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
        Add to Order
      `;
    }, 1400);
  });

  return card;
}

// ---------- Render the full grid for a given category ----------
function renderMenuGrid(category) {
  menuGrid.innerHTML = "";

  const itemsToShow =
    category === "All"
      ? allMenuItems
      : allMenuItems.filter((item) => item.category === category);

  if (itemsToShow.length === 0) {
    menuStatus.textContent = "No items found in this category yet.";
    menuStatus.classList.remove("hidden");
    return;
  }

  menuStatus.classList.add("hidden");

  itemsToShow.forEach((item, index) => {
    const card = createMenuCard(item);
    menuGrid.appendChild(card);

    // small staggered entrance animation
    setTimeout(() => card.classList.add("visible"), index * 60);
  });
}

// ---------- Render the Café Special section ----------
// Picks the item flagged as "featured": true in menu.json.
// Falls back to the first item if nothing is flagged, so the
// section always has something meaningful to show.
function renderSpecial() {
  const special =
    allMenuItems.find((item) => item.featured === true) || allMenuItems[0];

  if (!special) {
    specialCard.innerHTML = "";
    return;
  }

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
    </div>
  `;

  // image (with placeholder fallback) into the media block
  const media = specialCard.querySelector(".special-media");
  const img = document.createElement("img");
  img.src = special.image;
  img.alt = special.name;
  img.onerror = function () {
    img.remove();
    const fallback = createImagePlaceholder(`Add: ${special.name} photo`);
    media.appendChild(fallback);
  };
  media.appendChild(img);

  // optional tags, e.g. ["Rich & Creamy", "Customer Favorite"]
  const tagsWrap = document.getElementById("specialTags");
  const tags = special.tags && special.tags.length ? special.tags : [];
  tags.forEach((tag) => {
    const span = document.createElement("span");
    span.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none"><path d="M12 20s-7.5-4.5-9.5-9C1 7 3 4 6.3 4c2 0 3.4 1.1 4 2.2.6-1.1 2-2.2 4-2.2C17.6 4 19.6 7 18 10.7c-2 4.5-6 9.3-6 9.3z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>
      ${tag}
    `;
    tagsWrap.appendChild(span);
  });
}

// ---------- Handle category filter clicks ----------
filterBar.addEventListener("click", (event) => {
  const button = event.target.closest(".filter-btn");
  if (!button) return;

  currentCategory = button.getAttribute("data-category");

  // update active button styling
  filterBar
    .querySelectorAll(".filter-btn")
    .forEach((btn) => btn.classList.remove("active"));
  button.classList.add("active");

  renderMenuGrid(currentCategory);
});

// ---------- Fetch the menu data and boot up the page ----------
function loadMenuData() {
  menuStatus.textContent = "Loading our menu...";
  menuStatus.classList.remove("hidden", "error");

  fetch("")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      allMenuItems = data;
      menuStatus.classList.add("hidden");
      renderMenuGrid(currentCategory);
      renderSpecial();
    })
    .catch((error) => {
      console.error("Could not load menu data:", error);
      menuGrid.innerHTML = "";
      menuStatus.textContent =
        "Sorry, we couldn't load the menu right now. Please refresh the page or try again shortly.";
      menuStatus.classList.remove("hidden");
      menuStatus.classList.add("error");
    });
}

// ---------- Mobile nav toggle (shared behaviour with other pages) ----------
const burger = document.getElementById("burgerBtn");
const navLinks = document.getElementById("navLinks");
if (burger && navLinks) {
  burger.addEventListener("click", () => navLinks.classList.toggle("open"));
  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => navLinks.classList.remove("open"));
  });
}

// ---------- Kick things off ----------
document.addEventListener("DOMContentLoaded", loadMenuData);
