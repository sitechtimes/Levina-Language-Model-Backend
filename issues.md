# Levina Language Model Backend — Issues Report

Audit date: 2026-10-13

---

## CRITICAL Security Issues

### 1. Secret Key Hardcoded in Source Code
**File:** `mysite/core/settings.py:35`

The Django `SECRET_KEY` is hardcoded in version-controlled code. Anyone with repo access can forge sessions, CSRF tokens, and cryptographic signatures.

**Fix:** Move to environment variable:
```python
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
```

---

### 2. DEBUG = True
**File:** `mysite/core/settings.py:38`

Debug mode exposes full stack traces, file paths, local variables, and database queries to anyone who triggers an error.

**Fix:**
```python
DEBUG = os.getenv("DEBUG", "False") == "True"
```

---

### 3. Deterministic Session Tokens
**File:** `mysite/utils/create.py:74-76`

```python
token_string = f"token_{session_instance.id}"
token = hashlib.sha256(token_string.encode()).hexdigest()
```

Tokens are derived from sequential IDs — an attacker who knows any session instance ID can compute the token and access that session without authentication.

**Fix:** Use `secrets.token_urlsafe(32)` instead.

---

### 4. Password Reset Codes Are Only 6 Characters
**File:** `mysite/users/models.py` — `PasswordResetCode.code` has `max_length=6`

The code is generated as 20 characters in `create.py` but truncated to 6 by the model field. Combined with no rate limiting and a 10-minute window, this is brute-forceable.

**Fix:** Increase `max_length` to at least 32, add rate limiting on the confirm endpoint, and use `secrets.token_urlsafe()`.

---

### 5. Role Escalation via `>=` Comparison
**File:** `mysite/core/permissions.py`

```python
def has_user_type(user, user_type):
    return user.user_type >= user_type
```

This means every higher-privilege role also passes lower-privilege checks. A Teacher passes `IsStudent`, an Admin passes `IsTeacher`, etc. This is a privilege escalation flaw if any endpoint should be restricted to students only.

**Fix:** Use `==` for exact role matching, or redesign permissions to explicitly list allowed roles per endpoint.

---

### 6. Session Endpoints Allow Unauthenticated Access
**Files:** `mysite/assignments/views.py` — `join_session` and `update_answer` actions

These endpoints use `AllowAny` permission and authenticate solely via a token in the request body. Combined with the deterministic token issue (#3), any unauthenticated attacker can access and modify session data.

**Fix:** Require JWT authentication on these endpoints, or at minimum fix the token generation to be cryptographically random.

---

## HIGH Priority Issues

### 7. No Rate Limiting on Auth Endpoints
**File:** `mysite/core/urls.py:15-16`

`/api/token/` and `/api/token/refresh/` have no throttling. Attackers can brute-force credentials indefinitely.

**Fix:** Add DRF throttle classes:
```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "20/minute"},
}
```

---

### 8. Email Address Hardcoded in Settings
**File:** `mysite/core/settings.py:27`

```python
EMAIL_HOST_USER = "sam.kipnis@gmail.com"
```

Personal email exposed in version control. Move to environment variable.

---

### 9. ALLOWED_HOSTS Is Empty
**File:** `mysite/core/settings.py:40`

```python
ALLOWED_HOSTS = []
```

No Host header validation. In production with `DEBUG=False` this breaks the site; with `DEBUG=True` it allows all hosts.

**Fix:** `ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")`

---

### 10. File Upload Validation Is Broken
**File:** `mysite/questions/views.py:99-103`

```python
if initial_statement_file.content_type != "audio/mp4":
    return Response({"error": "Initial statement file must be a WAV audio file."}, ...)
```

Problems:
- Checks for `audio/mp4` but error message says "WAV" — copy-paste bug
- MIME type is client-supplied and trivially spoofed
- No file size limits anywhere
- No magic-byte validation

**Fix:** Validate using `python-magic` on actual file bytes, enforce size limits, and correct the error message.

---

### 11. No Object-Level Authorization on Question Assignment
**File:** `mysite/assignments/views.py:163-196`

When updating an assignment's questions, the IDs from the request body are added directly without verifying the user owns those questions. An attacker could attach any question ID to their assignment.

**Fix:** Filter question IDs by `author=request.user`.

---

### 12. Inconsistent Permission Systems
**Files:** `mysite/core/permissions.py` vs `mysite/users/permissions.py`

Two separate permission implementations exist:
- `core/permissions.py` uses `>=` (broken, see #5)
- `users/permissions.py` uses `==` (correct)

Different views use different permission modules, leading to inconsistent authorization.

**Fix:** Consolidate into one permission module and remove the duplicate.

---

## MEDIUM Priority Issues

### 13. Print Statements in Production Code
**Files:**
- `mysite/questions/serializers.py:63-67`
- `mysite/assignments/views.py:125`

Debug `print()` calls leak data to stdout/logs and hurt performance.

**Fix:** Replace with `logging.getLogger(__name__).debug(...)`.

---

### 14. No Negative/Overflow Check on `time_used`
**File:** `mysite/assignments/views.py:234-245`

```python
delta = int(request.data.get("time_used", 0))
instance.time_used += delta
```

No check for negative values (could reduce time) or unreasonably large values.

**Fix:** Validate `0 <= delta <= 86400`.

---

### 15. SQLite in Production
**File:** `mysite/core/settings.py:131-136`

SQLite doesn't support concurrent writes and has no network authentication. Not suitable for production.

**Fix:** Configure PostgreSQL via environment variables for production deployments.

---

### 16. Missing Security Headers
**File:** `mysite/core/settings.py`

No configuration for:
- `SECURE_SSL_REDIRECT`
- `SECURE_HSTS_SECONDS`
- `SECURE_BROWSER_XSS_FILTER`
- `SECURE_CONTENT_TYPE_NOSNIFF`
- Content Security Policy

**Fix:** Add these settings for production:
```python
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

---

### 17. Synchronous Email Sending Blocks Requests
**File:** `mysite/users/views.py`

`send_mail()` is called synchronously during the request cycle. A slow SMTP server will hang the user's request.

**Fix:** Use Celery or `django.core.mail.send_mail` with an async email backend.

---

### 18. No Logging Configuration
**File:** `mysite/core/settings.py`

No `LOGGING` dict is configured. Failed login attempts, permission denials, and errors are not captured in a structured way.

**Fix:** Add a `LOGGING` configuration with handlers for security events.

---

### 19. Password Reset Code Not Bound to User in Confirmation
**File:** `mysite/users/views.py:46-58`

The confirm endpoint looks up the code globally, not scoped to a specific user/email. If two users request resets simultaneously, codes could theoretically collide or be used cross-account.

**Fix:** Require the email in the confirm request and filter by both code and user.

---

### 20. `.env` File Contains Placeholder Values
**File:** `.env`

```
DJANGO_SECRET_KEY=your_secret_key_here
```

The placeholder value is not actually used in `settings.py` (the hardcoded key is used instead), making the `.env` file misleading. The settings file should actually read from the environment.

---

## LOW Priority / Best Practices

### 21. No `.env.example` File
There's no template showing which environment variables are required. New developers must read settings.py to discover them.

### 22. No Dependency Vulnerability Scanning
No `safety`, `bandit`, or `pip-audit` configuration. Dependencies could have known CVEs.

### 23. No Test Suite
No `tests.py` files contain any tests. No CI/CD pipeline is configured.

### 24. No API Versioning
All endpoints are unversioned (`/api/token/`, `/courses/`, etc.). Breaking changes will affect all clients.

### 25. `db.sqlite3` Should Be in `.gitignore`
The database file should not be tracked in version control.

---

## Deployment Checklist

Before going to production:

- [ ] Rotate SECRET_KEY and move to env var
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Fix deterministic token generation
- [ ] Fix role escalation in permissions
- [ ] Add rate limiting to auth and reset endpoints
- [ ] Increase password reset code length
- [ ] Fix file upload validation
- [ ] Enable HTTPS and security headers
- [ ] Switch to PostgreSQL
- [ ] Set up structured logging
- [ ] Add automated tests
- [ ] Run `pip-audit` on dependencies
- [ ] Remove all `print()` statements
- [ ] Move all credentials to environment variables
