## 2024-05-24 - [Medium] Added Missing Security Headers
**Vulnerability:** Fastapi application did not specify security headers like `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection` and `Strict-Transport-Security`.
**Learning:** This exposes the application to various attacks such as MIME sniffing, Clickjacking, and Cross-Site Scripting (XSS).
**Prevention:** Apply a middleware globally to inject security headers in every HTTP response.

## 2024-05-24 - [Medium] Fix Information Exposure in Database Errors
**Vulnerability:** Node.js Express application returned raw database error messages (`err.message`) to the client on SQL query failures.
**Learning:** This leaks internal database structure details, query context, or schema information which can be leveraged by attackers for SQL injection or reconnaissance.
**Prevention:** Always log the detailed error internally (`console.error` or logging library) and return a generic, secure error message (e.g., "Database error occurred") to the client.

## 2024-05-24 - [Medium] Fixed Error Detail Leakage
**Vulnerability:** The application was exposing internal database error messages (like `err.message`) directly to the client via `res.status(500).json({error: err.message})`.
**Learning:** Returning raw backend error objects violates the 'fail securely' principle and can leak sensitive information about the database schema or internal structures.
**Prevention:** Always log detailed errors internally (e.g., using `console.error`) and return generic, secure error messages (e.g., 'Internal server error') to the client.

## 2024-10-27 - [High] Cross-Site Scripting (XSS) via innerHTML in Simulator Dashboard
**Vulnerability:** The simulator dashboard (`spacez-visual-intelligence/services/simulator/main.py`) constructed dynamic HTML using `.innerHTML` combined with template strings that interpolated user-provided/dynamic data (such as `event_id`, `description`, `engagement_score`). Even with a custom `escapeHTML` function applied to some fields, directly creating DOM nodes via string concatenation is error-prone, brittle, and introduces a high risk of DOM-based XSS if the escaping logic is ever bypassed or forgotten on a newly added field.
**Learning:** XSS can occur anytime untrusted or unverified data is parsed as HTML. Using `.innerHTML` circumvents the browser's built-in protections against script injection. The previous approach relied on manual, piece-meal escaping which is difficult to maintain securely.
**Prevention:** Always use safe DOM manipulation APIs like `document.createElement()`, `document.createTextNode()`, and `.textContent`. These APIs treat input strictly as text or data, ensuring it cannot be executed as code, regardless of its contents.
