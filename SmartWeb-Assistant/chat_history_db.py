import os
import sqlite3
import time

class ChatHistoryDB:
    def __init__(self, db_path="chat_history.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            collection_name TEXT,
            timestamp INTEGER
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER,
            question TEXT,
            answer TEXT,
            timestamp INTEGER,
            FOREIGN KEY (website_id) REFERENCES websites (id)
        )
        ''')
        self.conn.commit()
    
    def save_qdrant_collection(self, website_url, collection_name):
        cursor = self.conn.cursor()
        timestamp = int(time.time())
        cursor.execute(
            "INSERT OR REPLACE INTO websites (url, collection_name, timestamp) VALUES (?, ?, ?)",
            (website_url, collection_name, timestamp)
        )
        self.conn.commit()
    
    def get_qdrant_collection(self, website_url):
        cursor = self.conn.cursor()
        cursor.execute("SELECT collection_name FROM websites WHERE url = ?", (website_url,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def save_chat(self, website_url, question, answer):
        cursor = self.conn.cursor()
        timestamp = int(time.time())
        
        # Get website_id
        cursor.execute("SELECT id FROM websites WHERE url = ?", (website_url,))
        result = cursor.fetchone()
        if not result:
            return False
        
        website_id = result[0]
        cursor.execute(
            "INSERT INTO chat_history (website_id, question, answer, timestamp) VALUES (?, ?, ?, ?)",
            (website_id, question, answer, timestamp)
        )
        self.conn.commit()
        return True
    
    def get_chat_history(self, website_url):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ch.question, ch.answer, ch.timestamp 
            FROM chat_history ch
            JOIN websites w ON ch.website_id = w.id
            WHERE w.url = ?
            ORDER BY ch.timestamp ASC
        """, (website_url,))
        return cursor.fetchall()
    
    def close(self):
        if self.conn:
            self.conn.close()
