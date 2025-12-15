"""
Database Configuration
Configuration settings for database connections.
"""

class DatabaseConfig:
    """Database configuration settings."""
    
    # Default database settings
    DEFAULT_DRIVER = "sqlite"
    DEFAULT_DATABASE = "app.db"
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 3306
    DEFAULT_USERNAME = "user"
    DEFAULT_PASSWORD = ""
    
    def __init__(self, driver=None, database=None, host=None, port=None, username=None, password=None):
        self.driver = driver or self.DEFAULT_DRIVER
        self.database = database or self.DEFAULT_DATABASE
        self.host = host or self.DEFAULT_HOST
        self.port = port or self.DEFAULT_PORT
        self.username = username or self.DEFAULT_USERNAME
        self.password = password or self.DEFAULT_PASSWORD
    
    def get_connection_string(self) -> str:
        """Generate a database connection string."""
        if self.driver == "sqlite":
            return f"{self.driver}:///{self.database}"
        else:
            return f"{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "driver": self.driver,
            "database": self.database,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password
        }

# Default configuration instances
development_config = DatabaseConfig(
    driver="sqlite",
    database="dev.db"
)

production_config = DatabaseConfig(
    driver="mysql",
    database="flashflow_prod",
    host="prod-db.example.com",
    port=3306,
    username="flashflow_user",
    password="secure_password"
)