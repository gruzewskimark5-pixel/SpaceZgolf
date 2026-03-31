## 2024-05-24 - [Medium] Added Missing Security Headers
**Vulnerability:** Fastapi application did not specify security headers like `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection` and `Strict-Transport-Security`.
**Learning:** This exposes the application to various attacks such as MIME sniffing, Clickjacking, and Cross-Site Scripting (XSS).
**Prevention:** Apply a middleware globally to inject security headers in every HTTP response.
