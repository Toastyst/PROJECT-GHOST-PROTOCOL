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

    # LLM Fallback settings
    LLM_PROVIDERS = os.getenv("LLM_PROVIDERS", "openai/gpt-4").split(",")

    # System settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

    # Git settings
    DEFAULT_REPO_PATH = os.getenv("DEFAULT_REPO_PATH", ".")

    # Iteration Protocol settings
    HOOKS_ENABLED = os.getenv("HOOKS_ENABLED", "true").lower() == "true"
    WORKFLOWS_ENABLED = os.getenv("WORKFLOWS_ENABLED", "true").lower() == "true"
    SKILLS_ENABLED = os.getenv("SKILLS_ENABLED", "true").lower() == "true"
    RULES_ENABLED = os.getenv("RULES_ENABLED", "true").lower() == "true"

    # Hook settings
    HOOK_REFLECTION_MODE = os.getenv("HOOK_REFLECTION_MODE", "question")

    # Workflow settings
    WORKFLOW_FACILITATION_MODE = os.getenv("WORKFLOW_FACILITATION_MODE", "guided")

    # Skills settings
    LISTENING_THRESHOLD = float(os.getenv("LISTENING_THRESHOLD", "0.6"))
    PATTERN_THRESHOLD = float(os.getenv("PATTERN_THRESHOLD", "0.7"))
    SILENCE_THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", "0.8"))
    SKILLS_LEARNING_ENABLED = os.getenv("SKILLS_LEARNING_ENABLED", "true").lower() == "true"

    # Rules settings
    PRESENCE_ENFORCEMENT = os.getenv("PRESENCE_ENFORCEMENT", "flexible")
    MEMORY_ENFORCEMENT = os.getenv("MEMORY_ENFORCEMENT", "strict")
    GROWTH_ENFORCEMENT = os.getenv("GROWTH_ENFORCEMENT", "advisory")

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        return True
