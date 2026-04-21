# Database Model Design

## Approach

Use a single `User` table for authentication + separate optional profile tables for role-specific data.

A user with a `BabysitterProfile` is a babysitter. A user with a `ParentProfile` is a parent. A user can have both, making dual roles work naturally with no extra flags or nullable columns on the User table.

---

## Relationship Diagram

```
User (users)
 ├── BabysitterProfile (babysitter_profiles)  — one-to-one, optional
 └── ParentProfile     (parent_profiles)      — one-to-one, optional
```

---

## Models

### `User` → `users` table

| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary key |
| username | String(64) | Unique, not null |
| email | String(120) | Unique, not null |
| password_hash | String(256) | Not null |
| created_at | DateTime | Auto-set on creation |

**Relationships:** `babysitter_profile`, `parent_profile` (both one-to-one, optional)

**Helper properties:**
- `user.is_babysitter` → `True` if a `BabysitterProfile` exists for this user
- `user.is_parent` → `True` if a `ParentProfile` exists for this user

**Methods:**
- `user.set_password(password)` — hashes and stores the password
- `user.check_password(password)` — verifies a password against the hash

---

### `BabysitterProfile` → `babysitter_profiles` table

| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary key |
| user_id | Integer | FK → users.id, unique |
| bio | Text | Self-introduction |
| hourly_rate | Float | Rate in dollars |
| experience_years | Integer | Years of experience |
| location | String(128) | Service area |
| availability | String(256) | Available days/times (JSON string) |

---

### `ParentProfile` → `parent_profiles` table

| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary key |
| user_id | Integer | FK → users.id, unique |
| num_children | Integer | Number of children |
| location | String(128) | Home location |
| special_requirements | Text | Any special needs or notes |

---

## Files to Create / Modify

| File | What to do |
|------|------------|
| `models/__init__.py` | Create `db = SQLAlchemy()` instance, import all models |
| `models/user.py` | `User` model (see above) |
| `models/babysitter_profile.py` | `BabysitterProfile` model |
| `models/parent_profile.py` | `ParentProfile` model |
| `app.py` | Add `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, `db.init_app(app)`, Flask-Login setup, `db.create_all()` |

---

## `app.py` Changes Needed

```python
app.config["SECRET_KEY"] = "dev-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
```

---

## Usage Examples

```python
# Check if a user is a babysitter
if current_user.is_babysitter:
    profile = current_user.babysitter_profile

# Make a user a babysitter
profile = BabysitterProfile(user_id=user.id, bio="...", hourly_rate=25.0)
db.session.add(profile)
db.session.commit()

# A dual-role user
user.is_babysitter  # True
user.is_parent      # True
```
