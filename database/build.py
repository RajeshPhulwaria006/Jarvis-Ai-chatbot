import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("database/memory.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()


    def save_message(self, role, message):
        self.cursor.execute(
            "INSERT INTO conversations(role, message) VALUES (?, ?)",
            (role, message)
        )
        self.conn.commit()


    def load_history(self, limit=20):
        self.cursor.execute("""
            SELECT role, message
            FROM conversations
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        rows = self.cursor.fetchall()
        rows.reverse()
        return rows


    def clear_history(self):
        self.cursor.execute("DELETE FROM conversations")
        self.conn.commit()