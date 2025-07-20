"""
Configuration validation utilities for the OkuoAgent application.
"""
import os
from typing import List, Dict, Any
from config import config

class ConfigValidator:
    """Validates application configuration and provides helpful error messages."""
    
    @staticmethod
    def validate_required_directories() -> List[str]:
        """Validate that all required directories exist or can be created."""
        errors = []
        required_dirs = [
            config.UPLOADS_DIR,
            config.IMAGES_DIR
        ]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except PermissionError:
                    errors.append(f"Cannot create directory: {directory}")
                except Exception as e:
                    errors.append(f"Error creating directory {directory}: {str(e)}")
        
        return errors
    
    @staticmethod
    def validate_file_permissions() -> List[str]:
        """Validate file permissions for critical files."""
        errors = []
        
        # Check if data dictionary can be read/written
        try:
            if os.path.exists(config.DATA_DICTIONARY_PATH):
                with open(config.DATA_DICTIONARY_PATH, 'r') as f:
                    f.read()
                with open(config.DATA_DICTIONARY_PATH, 'a') as f:
                    pass
        except PermissionError:
            errors.append(f"Cannot read/write data dictionary: {config.DATA_DICTIONARY_PATH}")
        except Exception as e:
            errors.append(f"Error accessing data dictionary: {str(e)}")
        
        return errors
    
    @staticmethod
    def validate_openai_config() -> List[str]:
        """Validate OpenAI configuration."""
        errors = []
        
        if not config.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        elif not config.OPENAI_API_KEY.startswith('sk-'):
            errors.append("OPENAI_API_KEY format appears invalid (should start with 'sk-')")
        
        if config.OPENAI_TEMPERATURE < 0 or config.OPENAI_TEMPERATURE > 2:
            errors.append("OPENAI_TEMPERATURE must be between 0 and 2")
        
        return errors
    
    @staticmethod
    def validate_security_config() -> List[str]:
        """Validate security-related configuration."""
        errors = []
        
        if config.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be greater than 0")
        
        if not config.ALLOWED_FILE_TYPES:
            errors.append("ALLOWED_FILE_TYPES cannot be empty")
        
        return errors
    
    @staticmethod
    def validate_all() -> Dict[str, List[str]]:
        """Validate all configuration aspects."""
        return {
            "directories": ConfigValidator.validate_required_directories(),
            "permissions": ConfigValidator.validate_file_permissions(),
            "openai": ConfigValidator.validate_openai_config(),
            "security": ConfigValidator.validate_security_config()
        }
    
    @staticmethod
    def has_errors(validation_results: Dict[str, List[str]]) -> bool:
        """Check if any validation errors exist."""
        return any(errors for errors in validation_results.values())
    
    @staticmethod
    def format_errors(validation_results: Dict[str, List[str]]) -> str:
        """Format validation errors for display."""
        if not ConfigValidator.has_errors(validation_results):
            return "Configuration is valid!"
        
        error_messages = []
        for category, errors in validation_results.items():
            if errors:
                error_messages.append(f"\n**{category.title()} Errors:**")
                for error in errors:
                    error_messages.append(f"  - {error}")
        
        return "\n".join(error_messages) 