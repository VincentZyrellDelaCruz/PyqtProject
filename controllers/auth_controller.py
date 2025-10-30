from database.connection import DatabaseConnection

class AuthController:
    """
    Authentication controller that uses SQLite database.
    Handles user authentication with hashed passwords and salt.
    """
    
    def __init__(self):
        # Initialize database on first use
        DatabaseConnection.initialize_database()
    
    @staticmethod
    def authenticate(username: str, password: str) -> bool:
        """
        Authenticate a user with username and password.
        
        Args:
            username: The username to check
            password: The plain text password to verify
            
        Returns:
            True if authentication successful, False otherwise
        """
        return DatabaseConnection.verify_credentials(username, password)
    
    @staticmethod
    def user_exists(username: str) -> bool:
        """
        Check if a username exists in the database.
        
        Args:
            username: The username to check
            
        Returns:
            True if user exists, False otherwise
        """
        return DatabaseConnection.user_exists(username)
