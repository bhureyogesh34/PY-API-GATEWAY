import sqlite3
import uuid

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            disabled BOOLEAN DEFAULT FALSE,
            scopes TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_user(username: str, password: str, scopes: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    user_id = str(uuid.uuid4())
    cursor.execute(
        'INSERT INTO users (id, username, hashed_password, scopes) VALUES (?, ?, ?, ?)',
        (user_id, username, password, scopes)
    )
    conn.commit()
    conn.close()
    return user_id

def get_user(username: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None