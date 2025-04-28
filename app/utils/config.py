"""Configuration utilities for the application"""
from typing import Dict, Any
import os
import json
from dotenv import load_dotenv
from pathlib import Path

class AppConfig:
    """Application configuration handler"""
    
    def __init__(self, env_path: str = None):
        """
        Initialize configuration
        
        Args:
            env_path (str, optional): Path to .env file. If None, looks in default locations
        """
        # Load environment variables from .env file
        if env_path:
            load_dotenv(env_path)
        else:
            # Look for .env in current directory and parent directories
            env_file = self.find_dotenv()
            if env_file:
                load_dotenv(env_file)
        
        self.default_config = {
            "model_name": "gpt-3.5-turbo",
            "temperature": 0,
            "min_qa_score": 0.85,
            "data_dir": "data",
            "supported_file_types": [".txt"],
        }
        
        self.qa_weights = {
            "opening": 0.06,
            "communication": 0.25,
            "negotiation": 0.40,
            "compliance": 0.29
        }
        
        # Load environment variables
        self.load_env_config()
        
    def find_dotenv(self) -> str:
        """
        Find .env file in current and parent directories
        
        Returns:
            str: Path to .env file or None if not found
        """
        current_dir = Path.cwd()
        
        while current_dir.parent != current_dir:
            env_file = current_dir / ".env"
            if env_file.exists():
                return str(env_file)
            current_dir = current_dir.parent
            
        return None
        
    def load_env_config(self):
        """Load configuration from environment variables"""
        env_vars = {
            "OPENAI_API_KEY": "api_key",
            "MODEL_NAME": "model_name",
            "DATA_DIR": "data_dir",
            "MIN_QA_SCORE": "min_qa_score",
            "TEMPERATURE": "temperature"
        }
        
        for env_var, config_key in env_vars.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert to appropriate type
                if config_key in ["min_qa_score", "temperature"]:
                    try:
                        value = float(value)
                    except ValueError:
                        continue
                self.default_config[config_key] = value
                
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.default_config
        
    def get_qa_weights(self) -> Dict[str, float]:
        """Get QA scoring weights"""
        return self.qa_weights
        
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration values"""
        self.default_config.update(updates)
        
    def save_config(self, filepath: str):
        """Save configuration to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.default_config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def load_config(self, filepath: str):
        """Load configuration from file"""
        try:
            with open(filepath, 'r') as f:
                loaded_config = json.load(f)
                self.update_config(loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def create_default_env(self, filepath: str = ".env.example"):
        """
        Create a default .env file template
        
        Args:
            filepath (str): Path to create the example .env file
        """
        example_env = """# OpenAI Configuration
OPENAI_API_KEY=your-api-key-here
MODEL_NAME=gpt-3.5-turbo

# Application Settings
DATA_DIR=data
MIN_QA_SCORE=0.85
TEMPERATURE=0

# Add other environment variables as needed
"""
        
        try:
            with open(filepath, 'w') as f:
                f.write(example_env)
            print(f"Created example environment file at {filepath}")
        except Exception as e:
            print(f"Error creating example environment file: {e}")
            
# Create global config instance
config = AppConfig()
