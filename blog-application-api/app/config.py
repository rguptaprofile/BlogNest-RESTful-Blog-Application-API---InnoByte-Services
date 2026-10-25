import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base MongoDB configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "default-fallback-secret-key-blognest-api")
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY", "default-fallback-jwt-secret-key-32-bytes-long!"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 24))
    )
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/blognest_db")
    MONGO_DBNAME = os.getenv("MONGO_DBNAME", "blognest_db")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration (in-memory mock collection backend)."""
    TESTING = True
    DEBUG = True
    MONGO_URI = "mongodb://mock"
    MONGO_DBNAME = "blognest_test"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
