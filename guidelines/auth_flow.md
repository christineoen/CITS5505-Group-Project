# Auth Flow: Signup & Login

## Overview

Authentication uses Flask-Login with email/password. On signup, users select their role(s) — Parent, Babysitter, or both — and empty profile records are created immediately so the rest of the app can check `user.is_parent` / `user.is_babysitter` from day one.

---

## Signup Flow

```
GET /auth/signup
  → render signup.html

POST /auth/signup
  → validate form
  → check email/username not already taken
  → create User, call set_password()
  → if is_parent checked: create ParentProfile(user_id=user.id)
  → if is_babysitter checked: create BabysitterProfile(user_id=user.id)
  → db.session.commit()
  → login_user(user)
  → redirect to home (main.index)
```

### Signup form fields

| Field | Type | Validation |
|-------|------|-----------|
| username | StringField | Required, length 2–64, unique |
| email | EmailField | Required, valid email, unique |
| password | PasswordField | Required, min length 8 |
| confirm_password | PasswordField | Must match password |
| is_parent | BooleanField | At least one role required |
| is_babysitter | BooleanField | At least one role required |

### UI layout

```
┌─────────────────────────────┐
│         Create Account      │
│                             │
│  Username  [_____________]  │
│  Email     [_____________]  │
│  Password  [_____________]  │
│  Confirm   [_____________]  │
│                             │
│  I am a:                    │
│  ☐ Parent                   │
│  ☐ Babysitter               │
│                             │
│       [ Sign Up ]           │
│                             │
│  Already have an account?   │
│  Log in →                   │
└─────────────────────────────┘
```

---

## Login Flow

```
GET /auth/login
  → render login.html

POST /auth/login
  → look up User by email
  → call user.check_password(password)
  → if valid: login_user(user, remember=form.remember.data)
              redirect to request.args.get('next') or home
  → if invalid: flash error, re-render login.html
```

### Login form fields

| Field | Type | Validation |
|-------|------|-----------|
| email | EmailField | Required |
| password | PasswordField | Required |
| remember | BooleanField | Optional |

### UI layout

```
┌─────────────────────────────┐
│           Log In            │
│                             │
│  Email     [_____________]  │
│  Password  [_____________]  │
│  ☐ Remember me              │
│                             │
│         [ Log In ]          │
│                             │
│  Don't have an account?     │
│  Sign up →                  │
└─────────────────────────────┘
```

---

## Logout

```
GET /auth/logout
  → @login_required
  → logout_user()
  → redirect to home
```

---

## Files to Create / Modify

| File | What to do |
|------|------------|
| `routes/auth.py` | New `auth_bp` blueprint with `/signup`, `/login`, `/logout` routes |
| `forms.py` | `RegistrationForm` and `LoginForm` using Flask-WTF |
| `templates/auth/signup.html` | Signup page extending `base.html` |
| `templates/auth/login.html` | Login page extending `base.html` |
| `app.py` | Register `auth_bp`: `app.register_blueprint(auth_bp)` |
| `templates/base.html` | Navbar: show Login/Register when logged out; profile dropdown when logged in |

---

## Navbar Logic (base.html)

```html
{% if current_user.is_authenticated %}
  <!-- profile dropdown (already exists) -->
{% else %}
  <li class="nav-item"><a class="nav-link" href="{{ url_for('auth.login') }}">Log In</a></li>
  <li class="nav-item"><a class="nav-link" href="{{ url_for('auth.signup') }}">Sign Up</a></li>
{% endif %}
```

---

## Key Imports

```python
# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from models.babysitter_profile import BabysitterProfile
from models.parent_profile import ParentProfile
from forms import RegistrationForm, LoginForm
```

---

## Validation Notes

- Flash errors using `flash(message, 'danger')` so Bootstrap alert styling works
- Check for duplicate email/username before committing — query DB and flash specific error if taken
- `login_view = "auth.login"` is already set in `app.py`, so `@login_required` redirects automatically
- After signup/login, use `redirect(request.args.get('next') or url_for('main.index'))` — but validate `next` is a relative URL to prevent open redirect attacks
