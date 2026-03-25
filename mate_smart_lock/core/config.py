import os
import json
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/mate-smart-lock")
        self.config_path = os.path.join(self.config_dir, "config.json")
        
        # Default settings
        self.settings = {
            "target_device_mac": "",
            "target_device_name": "",
            "auto_lock_enabled": False,
            "auto_unlock_enabled": False,
            "polling_interval": 5,
            "debounce_limit": 2,
            "lock_command": "loginctl lock-session",
            "unlock_command": "loginctl unlock-session"
        }
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    loaded_config = json.load(f)
                    self.settings.update(loaded_config)
                logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
        else:
            logger.info("Configuration file not found, using defaults.")

    def save(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.settings, f, indent=4)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()
