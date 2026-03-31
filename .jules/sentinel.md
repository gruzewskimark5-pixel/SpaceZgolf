## 2024-05-24 - [Medium] Added Missing Security Headers
**Vulnerability:** Fastapi application did not specify security headers like `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection` and `Strict-Transport-Security`.
**Learning:** This exposes the application to various attacks such as MIME sniffing, Clickjacking, and Cross-Site Scripting (XSS).
**Prevention:** Apply a middleware globally to inject security headers in every HTTP response.

## 2024-05-24 - [Medium] Fix Information Exposure in Database Errors
**Vulnerability:** Node.js Express application returned raw database error messages (`err.message`) to the client on SQL query failures.
**Learning:** This leaks internal database structure details, query context, or schema information which can be leveraged by attackers for SQL injection or reconnaissance.
**Prevention:** Always log the detailed error internally (`console.error` or logging library) and return a generic, secure error message (e.g., "Database error occurred") to the client.
