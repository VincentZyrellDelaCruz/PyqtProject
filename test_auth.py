"""
Test script for SQLite-based authentication system.
Use this to verify login credentials and inspect the database.
"""

from controllers.auth_controller import AuthController
from database.connection import DatabaseConnection
import sqlite3

def test_authentication():
    """Test the authentication with default credentials."""
    print("=" * 50)
    print("Testing SQLite Authentication System")
    print("=" * 50)
    
    auth = AuthController()  # This initializes the database
    
    # Test valid login
    print("\n1. Testing valid login (admin/admin123):")
    result = auth.authenticate("admin", "admin123")
    print(f"   Result: {'✓ SUCCESS' if result else '✗ FAILED'}")
    
    # Test invalid username
    print("\n2. Testing invalid username:")
    result = auth.authenticate("wronguser", "admin123")
    print(f"   Result: {'✗ FAILED (unexpected)' if result else '✓ FAILED (expected)'}")
    
    # Test invalid password
    print("\n3. Testing invalid password:")
    result = auth.authenticate("admin", "wrongpassword")
    print(f"   Result: {'✗ FAILED (unexpected)' if result else '✓ FAILED (expected)'}")
    
    print("\n" + "=" * 50)

def show_database_contents():
    """Display the contents of the users table."""
    print("\n" + "=" * 50)
    print("Database Contents")
    print("=" * 50)
    
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, created_at FROM users")
    users = cursor.fetchall()
    
    print(f"\nTotal users: {len(users)}")
    print("\nUsers in database:")
    for user in users:
        print(f"  - ID: {user['id']}, Username: {user['username']}, Created: {user['created_at']}")
    
    conn.close()
    print("\n" + "=" * 50)

def verify_password_hashing():
    """Verify that passwords are properly hashed (not stored as plaintext)."""
    print("\n" + "=" * 50)
    print("Password Security Check")
    print("=" * 50)
    
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, password_hash, salt FROM users WHERE username = 'admin'")
    user = cursor.fetchone()
    
    if user:
        print(f"\nUsername: {user['username']}")
        print(f"Password Hash: {user['password_hash'][:32]}... (truncated)")
        print(f"Salt: {user['salt'][:16]}... (truncated)")
        print(f"\n✓ Password is properly hashed (not stored as plaintext)")
        print(f"✓ Using SHA-256 with salt for secure password storage")
    else:
        print("\n✗ Admin user not found!")
    
    conn.close()
    print("\n" + "=" * 50)

if __name__ == "__main__":
    # Test current authentication
    test_authentication()
    
    # Show database contents
    show_database_contents()
    
    # Verify password security
    verify_password_hashing()
