from database import get_db


class User:
    @staticmethod
    def get_all():
        db = get_db()
        return db.execute("SELECT * FROM users").fetchall()

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    @staticmethod
    def get_by_username(username):
        db = get_db()
        return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    @staticmethod
    def create(username, email, password):
        db = get_db()
        db.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password),
        )
        db.commit()
