# Requirements Document

## Introduction

This document describes the requirements for adding a FastAPI backend to the existing Bright Bean Café static frontend. The backend will replace the static `data/menu.json` file fetch with a proper REST API, handle contact form submissions, and serve as the foundation for future dynamic features such as order management and image serving. The frontend pages affected are `html/menu.html` (menu data and filtering), `html/contact.html` (contact form), and `gallery.html` (gallery image metadata). All existing frontend HTML/CSS/JS remains unchanged except for fetch URL updates.

---

## Glossary

- **API**: The FastAPI application that handles all HTTP requests from the frontend.
- **MenuItem**: A structured data object representing a single item on the café menu, containing id, name, category, description, price, image URL, and optional featured/tags fields.
- **ContactMessage**: A structured data object representing a contact form submission, containing name, email, subject, and message fields.
- **GalleryItem**: A structured data object representing a single gallery photo entry, containing id, category, image path, and label fields.
- **Category**: A string identifier used to filter MenuItems or GalleryItems (e.g., "Coffee", "Cold Drinks", "Pastries", "Desserts", "Tea" for menu; "Café", "Coffee", "Food", "Team", "Events" for gallery).
- **CORS**: Cross-Origin Resource Sharing — HTTP headers that allow the browser-hosted frontend to call the API when served from a different origin.
- **Client**: The browser running the Bright Bean Café HTML/JS frontend pages.

---

## Requirements

### Requirement 1: Menu Items API

**User Story:** As a café visitor, I want the menu page to load items from a live API, so that menu changes made by the café owner are reflected immediately without editing static files.

#### Acceptance Criteria

1. THE API SHALL expose a `GET /api/menu` endpoint that returns all MenuItem objects as a JSON array with HTTP status 200.
2. WHEN the Client sends `GET /api/menu?category={Category}`, THE API SHALL return only MenuItem objects whose category field matches the provided Category value exactly (case-sensitive) as a JSON array with HTTP status 200.
3. WHEN the Client sends `GET /api/menu?category=All` or omits the `category` query parameter, THE API SHALL return all MenuItem objects as a JSON array with HTTP status 200.
4. WHEN a `GET /api/menu` request is received, THE API SHALL respond within 500ms under normal operating conditions with a load of up to 200 concurrent requests.
5. THE API SHALL return MenuItem objects that each contain the fields: `id` (unique positive integer), `name` (non-empty string, maximum 100 characters), `category` (non-empty string, maximum 50 characters), `description` (string, maximum 500 characters), `price` (positive number in the range 0.01 to 9999.99), `image` (non-empty string URL, maximum 2048 characters), `featured` (boolean, optional), and `tags` (array of strings with maximum 20 tags and each tag up to 50 characters, optional).
6. THE API SHALL seed the menu dataset from the existing `data/menu.json` file on startup so no existing menu data is lost, and SHALL log an error and halt startup if the file is missing or contains invalid JSON.
7. WHEN the request URL contains a `category` value that matches no MenuItem, THE API SHALL return an empty JSON array with HTTP status 200.
8. IF the `GET /api/menu` request fails due to a server error, THEN THE API SHALL return an error response with HTTP status 500 indicating the failure, without exposing internal error details.

---

### Requirement 2: Single Menu Item Retrieval

**User Story:** As a café visitor, I want the frontend to be able to fetch details for a specific menu item, so that future detail views or featured-item logic can request a single record efficiently.

#### Acceptance Criteria

1. THE API SHALL expose a `GET /api/menu/{id}` endpoint that accepts a positive integer `id` path parameter and returns a single MenuItem object matching the provided `id`.
2. WHEN the Client requests `GET /api/menu/{id}` and a MenuItem with that `id` exists, THE API SHALL return the MenuItem as a JSON object with HTTP status 200 within 500ms.
3. WHEN the Client requests `GET /api/menu/{id}` and no MenuItem with that `id` exists, THE API SHALL return a JSON error object with HTTP status 404 and a `detail` field describing the error.
4. IF the Client provides an `id` that is not a positive integer (e.g., zero, negative, or non-numeric), THEN THE API SHALL return HTTP status 422 with a JSON validation error object.

---

### Requirement 3: Contact Form Submission

**User Story:** As a café visitor, I want my contact form message to be saved by the server, so that the café team can review and respond to my enquiry.

#### Acceptance Criteria

1. THE API SHALL expose a `POST /api/contact` endpoint that accepts a ContactMessage JSON body.
2. WHEN the Client submits a valid ContactMessage to `POST /api/contact`, THE API SHALL persist the message and return HTTP status 201 with a confirmation JSON object containing a `message` field and a generated `id` field.
3. IF the Client submits a ContactMessage where the `email` field is not a syntactically valid email address, THEN THE API SHALL return HTTP status 422 with a JSON validation error object.
4. IF the Client submits a ContactMessage where the `name`, `subject`, or `message` fields are empty strings or contain only whitespace, THEN THE API SHALL return HTTP status 422 with a JSON validation error object.
5. THE ContactMessage model SHALL require the fields: `name` (string, minimum 2 non-whitespace characters, maximum 100 characters), `email` (valid email format, maximum 254 characters), `subject` (string, minimum 2 non-whitespace characters, maximum 150 characters), and `message` (string, minimum 6 non-whitespace characters, maximum 2000 characters).
6. THE API SHALL expose a `GET /api/contact` endpoint that returns all stored ContactMessage submissions as a JSON array, ordered by submission time descending.
7. IF the Client submits a request body to `POST /api/contact` that is not valid JSON, THEN THE API SHALL return HTTP status 400 with a JSON error object.
8. IF the persistence layer is unavailable when `POST /api/contact` is called, THEN THE API SHALL return HTTP status 503 with a JSON error object, and no partial record SHALL be written.

---

### Requirement 4: Gallery Metadata API

**User Story:** As a café visitor, I want the gallery page to load image metadata from the API, so that new gallery photos can be added by the café team without modifying frontend code.

#### Acceptance Criteria

1. THE API SHALL expose a `GET /api/gallery` endpoint that returns all GalleryItem objects as a JSON array with HTTP status 200.
2. WHEN the Client sends `GET /api/gallery?category={Category}`, THE API SHALL return only GalleryItem objects whose category field matches the provided Category value exactly (case-sensitive) with HTTP status 200.
3. WHEN the Client sends `GET /api/gallery?category=All` or omits the `category` query parameter, THE API SHALL return all GalleryItem objects with HTTP status 200.
4. WHEN the request URL contains a `category` value that matches no GalleryItem, THE API SHALL return an empty JSON array with HTTP status 200.
5. THE API SHALL return GalleryItem objects that each contain the fields: `id` (unique positive integer), `category` (non-empty string), `image` (non-empty string representing a relative URL path to the image file), and `label` (non-empty string).
6. THE API SHALL seed the gallery dataset from the `galleryItems` array defined in `gallery.html` on startup, and the seeding operation SHALL be idempotent so that restarting the server does not create duplicate records.

---

### Requirement 5: CORS Support

**User Story:** As a developer, I want the API to allow requests from the frontend origin, so that the browser does not block API calls when the frontend is served from a local development server or a different domain.

#### Acceptance Criteria

1. THE API SHALL include CORS middleware that permits requests from `http://localhost` and `http://127.0.0.1` on any port, including the `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers` response headers.
2. WHEN a browser preflight `OPTIONS` request is received for any `/api/*` endpoint, THE API SHALL respond with HTTP status 200 and include the headers `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods` (including GET, POST, OPTIONS), and `Access-Control-Allow-Headers`.
3. WHERE a production origin is configured via an environment variable `ALLOWED_ORIGINS` (a comma-separated list of origin URLs), THE API SHALL include each listed origin in the CORS allow-list in addition to the localhost defaults.

---

### Requirement 6: API Health Check

**User Story:** As a developer, I want a health-check endpoint, so that I can verify the API is running correctly without inspecting application logs.

#### Acceptance Criteria

1. THE API SHALL expose a `GET /health` endpoint that returns a JSON object containing a `status` field with the value `"ok"` and a `service` field with the value `"bright-bean-api"` with HTTP status 200.
2. WHEN the API is running and all dependencies are reachable, THE API SHALL respond to `GET /health` with HTTP status 200 within 200ms.
3. IF a dependency (e.g., data store) is unreachable at the time of the health check, THEN THE API SHALL return HTTP status 503 with a JSON object containing `"status": "degraded"` and a `detail` field describing the unavailable dependency.

---

### Requirement 7: API Data Validation and Error Responses

**User Story:** As a developer, I want all API errors to return structured JSON responses, so that the frontend can display meaningful error messages to visitors.

#### Acceptance Criteria

1. IF any `/api/*` endpoint receives a request with a malformed JSON body, THEN THE API SHALL return HTTP status 422 with a JSON object containing a `detail` field describing the validation error.
2. IF any `/api/*` endpoint encounters an unexpected internal error, THEN THE API SHALL return HTTP status 500 with a JSON object containing a `detail` field with the value `"Internal server error"`.
3. THE API SHALL return all error responses with the `Content-Type: application/json` header.
4. THE API SHALL never expose internal stack traces or file paths in error responses returned to the Client.
5. IF any `/api/*` endpoint receives an invalid query parameter (e.g., wrong type or out-of-range value), THEN THE API SHALL return HTTP status 422 with a JSON object containing a `detail` field describing the invalid parameter.
6. THE API SHALL return all successful responses with the `Content-Type: application/json` header.

---

### Requirement 8: Static File and Frontend Compatibility

**User Story:** As a developer, I want the FastAPI server to serve the existing static frontend files, so that both the frontend and backend can be run from a single server during development.

#### Acceptance Criteria

1. THE API SHALL mount the existing `cafe` project directory as a static file server accessible at the root path `/`, with `/api/*` and `/health` routes taking precedence over static file resolution.
2. WHEN the Client requests a path that does not match any `/api/*` or `/health` route, THE API SHALL serve the corresponding static file from the mounted directory.
3. IF the Client requests a static path for which no file exists, THEN THE API SHALL return HTTP status 404.
4. THE API SHALL serve static files with appropriate `Content-Type` headers (e.g., `text/html` for `.html`, `text/css` for `.css`, `application/javascript` for `.js`, `image/jpeg` for `.jpg`).
5. IF the Client requests a path matching `/api/*` for which no API route is defined, THEN THE API SHALL return a JSON 404 error object rather than attempting static file resolution.
