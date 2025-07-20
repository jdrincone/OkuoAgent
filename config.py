import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Centralized configuration class for the application."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0"))
    
    # Streamlit Configuration
    STREAMLIT_SERVER_MAX_UPLOAD_SIZE: str = os.getenv("STREAMLIT_SERVER_MAX_UPLOAD_SIZE", "2000")
    STREAMLIT_PAGE_TITLE: str = os.getenv("STREAMLIT_PAGE_TITLE", "OkuoAgent - Análisis Inteligente de Datos")
    STREAMLIT_PAGE_ICON: str = os.getenv("STREAMLIT_PAGE_ICON", "🤖")
    
    # Application Configuration
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "uploads")
    IMAGES_DIR: str = os.getenv("IMAGES_DIR", "images/plotly_figures/pickle")
    DATA_DICTIONARY_PATH: str = os.getenv("DATA_DICTIONARY_PATH", "uploads/data_dictionary.json")
    
    # LangGraph Configuration
    RECURSION_LIMIT: int = int(os.getenv("RECURSION_LIMIT", "50"))  # Increased from 25 to 50
    
    # Security Configuration
    ALLOWED_FILE_TYPES: list = os.getenv("ALLOWED_FILE_TYPES", "csv,json").split(",")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    
    # Database Configuration
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "postgresql")  # postgresql, mysql, sqlite
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "okuoagent")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Corporate Colors Configuration
    CORPORATE_COLORS: list = [
        "#1C8074",  # PANTONE 3295 U
        "#666666",  # PANTONE 426 U
        "#1A494C",  # PANTONE 175-16 U
        "#94AF92",  # PANTONE 7494 U
        "#E6ECD8",  # PANTONE 152-2 U
        "#C9C9C9",  # PANTONE COLOR GRAY 2 U
    ]
    
    # Streamlit Theme Configuration
    STREAMLIT_THEME: dict = {
        "primaryColor": "#1C8074",  # PANTONE 3295 U - Verde principal
        "backgroundColor": "#FFFFFF",  # Fondo blanco
        "secondaryBackgroundColor": "#E6ECD8",  # PANTONE 152-2 U - Verde claro
        "textColor": "#1A494C",  # PANTONE 175-16 U - Verde oscuro
        "font": "sans serif"
    }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
        return True
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """Get OpenAI configuration as a dictionary."""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL,
            "temperature": cls.OPENAI_TEMPERATURE
        }
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Get database configuration as a dictionary."""
        return {
            "type": cls.DATABASE_TYPE,
            "host": cls.DATABASE_HOST,
            "port": cls.DATABASE_PORT,
            "name": cls.DATABASE_NAME,
            "user": cls.DATABASE_USER,
            "password": cls.DATABASE_PASSWORD,
            "url": cls.DATABASE_URL
        }
    
    @classmethod
    def get_database_connection_string(cls) -> str:
        """Get database connection string."""
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        
        if cls.DATABASE_TYPE == "postgresql":
            return f"postgresql://{cls.DATABASE_USER}:{cls.DATABASE_PASSWORD}@{cls.DATABASE_HOST}:{cls.DATABASE_PORT}/{cls.DATABASE_NAME}"
        elif cls.DATABASE_TYPE == "mysql":
            return f"mysql+pymysql://{cls.DATABASE_USER}:{cls.DATABASE_PASSWORD}@{cls.DATABASE_HOST}:{cls.DATABASE_PORT}/{cls.DATABASE_NAME}"
        elif cls.DATABASE_TYPE == "sqlite":
            return f"sqlite:///{cls.DATABASE_NAME}.db"
        else:
            raise ValueError(f"Unsupported database type: {cls.DATABASE_TYPE}")

# Create a config instance
config = Config() 