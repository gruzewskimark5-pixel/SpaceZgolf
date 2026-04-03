## 2024-05-24 - [Medium] Added Missing Security Headers
**Vulnerability:** Fastapi application did not specify security headers like `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection` and `Strict-Transport-Security`.
**Learning:** This exposes the application to various attacks such as MIME sniffing, Clickjacking, and Cross-Site Scripting (XSS).
**Prevention:** Apply a middleware globally to inject security headers in every HTTP response.

## 2024-05-24 - [Medium] Fixed Error Detail Leakage
**Vulnerability:** The application was exposing internal database error messages (like `err.message`) directly to the client via `res.status(500).json({error: err.message})`.
**Learning:** Returning raw backend error objects violates the 'fail securely' principle and can leak sensitive information about the database schema or internal structures.
**Prevention:** Always log detailed errors internally (e.g., using `console.error`) and return generic, secure error messages (e.g., 'Internal server error') to the client.
## 2026-04-03 - 🛡️ Sentinel: Fix XSS via innerHTML in simulator dashboard
**Vulnerability:** Cross-Site Scripting (XSS) via `innerHTML` assignment with unescaped/inadequately escaped dynamically interpolated JSON data from websockets.
**Learning:** Even if helper functions like `escapeHTML` are used, passing string-interpolated JSON data directly to `innerHTML` poses XSS risks.
**Prevention:** Use strictly `document.createElement()` and assign user input via `.textContent` to guarantee safe text representation by the browser.
