import sqlite3
import os
import hashlib
import secrets

class DatabaseConnection:
    """
    SQLite database connection and initialization.
    Creates users table and initializes with one admin account.
    """
    
    DB_PATH = "user_database.db"
    
    @classmethod
    def get_connection(cls):
        """Get a connection to the SQLite database."""
        conn = sqlite3.connect(cls.DB_PATH)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    
    @classmethod
    def initialize_database(cls):
        """
        Initialize the database with users table.
        Creates the table if it doesn't exist and adds default admin user.
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if admin user already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create default admin user
            password = "admin123"
            salt = secrets.token_hex(16)  # 32 character hex string
            password_hash = cls.hash_password(password, salt)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, salt)
                VALUES (?, ?, ?)
            ''', ("admin", password_hash, salt))
            
            print("Database initialized with default admin user.")
            print("Username: admin")
            print("Password: admin123")
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """
        Hash a password with salt using SHA-256.
        
        Args:
            password: Plain text password
            salt: Salt string
            
        Returns:
            Hexadecimal hash string
        """
        salted_password = password + salt
        return hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    
    @classmethod
    def verify_credentials(cls, username: str, password: str) -> bool:
        """
        Verify username and password against database.
        
        Args:
            username: Username to check
            password: Plain text password to verify
            
        Returns:
            True if credentials are valid, False otherwise
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT password_hash, salt FROM users 
                WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            
            if result is None:
                return False
            
            stored_hash = result['password_hash']
            salt = result['salt']
            
            # Hash the provided password with the stored salt
            input_hash = cls.hash_password(password, salt)
            
            # Compare hashes
            return input_hash == stored_hash
            
        finally:
            conn.close()
    
    @classmethod
    def user_exists(cls, username: str) -> bool:
        """Check if a username exists in the database."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            conn.close()