# Bright Bean Café — Complete Project Guide

## What This Project Is

A café website with a Python backend. Customers can browse the menu, place orders, send messages, and chat with an AI assistant about the menu.

---

## How to Start the Server

Open a terminal and run:

```
python d:\backend\cafe\cafe\start.py
```

Then open your browser at: **http://127.0.0.1:8000**

Keep the terminal open while using the site. Closing it stops the server.

---

## Tech Stack

| Layer         | Technology                          |
|---------------|-------------------------------------|
| Backend       | Python + FastAPI + uvicorn          |
| Database       | SQLite (bright_bean.db file)       |
| Frontend      | HTML, CSS, JavaScript (no framework)|
| AI Chatbot    | Ollama (gemma4:cloud model)        |
| Recommendations| scikit-learn (TF-IDF + cosine sim) |

No external API keys. No paid services. Everything runs locally.

---

## Project Structure

```
cafe/
│
├── backend/                    ← Python backend (FastAPI)
│   ├── main.py                 ← App setup, CORS, error handlers, startup
│   ├── requirements.txt        ← All Python dependencies
│   ├── routers/                ← API endpoints (one file per feature)
│   │   ├── menu.py             ← GET /api/menu, GET /api/menu/{id}
│   │   ├── contact.py          ← POST /api/contact, GET /api/contact
│   │   ├── gallery.py          ← GET /api/gallery
│   │   ├── orders.py           ← POST /api/orders, GET /api/orders
│   │   ├── health.py          ← GET /health
│   │   ├── chat.py            ← POST /api/chat (AI chatbot)
│   │   └── recommend.py       ← GET /api/recommend/{id}, POST /api/recommend/cart
│   ├── models/                 ← Pydantic data models (validation)
│   │   ├── menu.py
│   │   ├── contact.py
│   │   ├── gallery.py
│   │   └── order.py
│   ├── db/                     ← SQLAlchemy database layer
│   │   ├── database.py         ← Engine, session, get_db dependency
│   │   └── models.py           ← ORM tables (contacts, orders, order_items)
│   ├── data/
│   │   └── store.py            ← In-memory menu & gallery stores + seed logic
│   ├── services/
│   │   └── recommender.py      ← TF-IDF recommendation engine
│   ├── seeds/
│   │   └── gallery_seed.py     ← Gallery data (mirrored from gallery.html)
│   └── tests/                   ← pytest + hypothesis tests
│       ├── conftest.py          ← Test fixtures
│       ├── test_store.py        ← Store unit + property tests
│       ├── test_integration.py  ← HTTP endpoint tests
│       └── test_ai_features.py  ← Chat + recommender tests
│
├── js/                          ← Frontend JavaScript
│   ├── menu.js                  ← Menu page logic (loads from inlined data)
│   ├── cart.js                  ← Cart, checkout, orders (saves to localStorage)
│   └── chat-widget.js           ← AI chat bubble + recommendations UI
│
├── html/                        ← Inner pages
│   ├── menu.html                ← Menu page
│   └── contact.html             ← Contact form page
│
├── css/                         ← Stylesheets
│   └── menu.css
│
├── data/                        ← Static data
│   └── menu.json                ← Menu items (seed source for backend)
│
├── images/                      ← Menu item photos
├── Images2/                     ← Hero/banner photos
├── Gallery/                     ← Gallery photos
│
├── index.html                   ← Homepage
├── gallery.html                  ← Gallery page
├── bright_bean.db                ← SQLite database (created on first run)
├── start.py                     ← Resets DB + starts server
└── START_SERVER.bat             ← Double-click to start (Windows)
```

---

## API Endpoints

### Menu
| Method | URL | What it does |
|--------|-----|-------------|
| GET | `/api/menu` | All menu items (optional `?category=Coffee` filter) |
| GET | `/api/menu/1` | Single item by id |

### Orders
| Method | URL | What it does |
|--------|-----|-------------|
| POST | `/api/orders` | Place a new order (pickup or delivery) |
| GET | `/api/orders` | List all orders (newest first) |
| GET | `/api/orders/1` | Single order by id |

### Contact
| Method | URL | What it does |
|--------|-----|-------------|
| POST | `/api/contact` | Submit contact form |
| GET | `/api/contact` | List all submissions |

### Gallery
| Method | URL | What it does |
|--------|-----|-------------|
| GET | `/api/gallery` | All gallery items (optional `?category=` filter) |

### AI Features
| Method | URL | What it does |
|--------|-----|-------------|
| POST | `/api/chat` | Send message to AI assistant, get reply |
| GET | `/api/recommend/1?limit=3` | Get 3 items similar to item 1 |
| POST | `/api/recommend/cart` | Get recommendations based on cart contents |

### Health
| Method | URL | What it does |
|--------|-----|-------------|
| GET | `/health` | Check if server and database are running |

Interactive API docs: **http://127.0.0.1:8000/docs**

---

## Database Tables (bright_bean.db)

### contact_messages
Stores contact form submissions.
- id, name, email, subject, message, submitted_at

### orders
Stores customer orders.
- id, customer_name, customer_email, customer_phone, order_type (pickup/delivery),
  delivery_address, notes, total, status, placed_at

### order_items
Stores individual items within an order.
- id, order_id (links to orders), menu_item_id, name, price, quantity

### menu & gallery
NOT in the database. Loaded into memory (RAM) on startup from `data/menu.json`
and `seeds/gallery_seed.py`. Fast lookups, no disk reads.

---

## How Each Feature Works

### Menu Page
1. Browser loads `html/menu.html`
2. `js/menu.js` renders menu cards from inlined data
3. Category filter buttons filter items client-side
4. "Add to Order" button sends item to `js/cart.js`

### Cart & Checkout
1. Items added to cart are stored in browser's localStorage
2. Floating cart button (bottom-right) opens a slide-out panel
3. Customer adjusts quantities, clicks "Proceed to Checkout"
4. Checkout form collects: name, email, phone, pickup or delivery, address, notes
5. On confirm, order is saved to SQLite database via POST /api/orders
6. Confirmation screen shows order number and total

### Contact Form
1. Customer fills form on `html/contact.html`
2. Validates name (2+ chars), email format, subject, message (6+ chars)
3. Saves to browser localStorage (works without server)
4. If server is running, also available at GET /api/contact

### AI Chatbot
1. Gold chat bubble appears bottom-left of menu page
2. Customer types a question about the menu
3. Backend builds a compact menu context (id|name|category|price|description)
4. Sends to Ollama at localhost:11434/api/chat using gemma4:cloud model
5. System prompt tells AI: answer ONLY from menu data, keep under 3 sentences
6. If Ollama is offline, shows "Assistant is offline" — rest of site keeps working

### Recommendation Engine
1. When customer adds items to cart, chat-widget.js calls POST /api/recommend/cart
2. Backend builds TF-IDF matrix from all menu items (name + category + description)
3. Computes cosine similarity between cart items and all menu items
4. Returns top 3 most similar items NOT already in cart
5. Shows as "You might also like" strip — clicking adds item to cart
6. If it fails, silently does nothing

---

## How to Run Tests

```
cd d:\backend\cafe\cafe
python -m pytest backend/tests/ -v
```

61 tests total:
- 13 store unit/property tests (Hypothesis)
- 38 HTTP integration tests
- 10 AI feature tests (mocked Ollama, real recommender)

---

## How to Start the AI Chatbot

1. Install Ollama: https://ollama.com/download
2. Open Ollama app, sign in (free plan)
3. Start your server: `python start.py`
4. Open http://127.0.0.1:8000/html/menu.html
5. Click the gold bubble bottom-left, ask about the menu

The chatbot uses `gemma4:cloud` (free Ollama cloud plan, no download needed).
To change the model, set environment variable: `OLLAMA_MODEL=other_model_name`

---

## Environment Variables (all optional)

| Variable | Default | What it does |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `gemma4:cloud` | Which AI model the chatbot uses |
| `OLLAMA_URL` | `http://localhost:11434/api/chat` | Ollama API endpoint |
| `DATABASE_URL` | `sqlite:///./bright_bean.db` | Database connection string |
| `ALLOWED_ORIGINS` | (none) | Extra CORS origins for production |

---

## Files Safe to Delete

These were temporary helpers during development:
- `diagnose.py` — diagnostic script (not needed)
- `check_port.py` — port checker (not needed)

Keep everything else.
