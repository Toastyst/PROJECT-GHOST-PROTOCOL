import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration management for Ghost Protocol system."""

    # OpenAI API settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

    # Database settings
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # MCP Server settings
    NEXUS_SERVER_PORT = int(os.getenv("NEXUS_SERVER_PORT", "3001"))
    WEAVER_SERVER_PORT = int(os.getenv("WEAVER_SERVER_PORT", "3002"))
    YOLO_SERVER_PORT = int(os.getenv("YOLO_SERVER_PORT", "3003"))

    # System settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

    # Git settings
    DEFAULT_REPO_PATH = os.getenv("DEFAULT_REPO_PATH", ".")

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        return True