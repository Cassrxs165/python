# config.py - Config Manager untuk testGUI.py
import yaml
import os

class ConfigManager:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self):
        """Load config.yaml dengan smart defaults"""
        defaults = {
            "gui": {
                "title": "Robocon 2026 - Vision Control",
                "start_maximized": True
            },
            "camera": {
                "device_path": "/dev/v4l/by-id/usb-046d_C922_Pro_Stream_Webcam_8E3AFE4F-video-index0",
                "backend": "CAP_V4L2",
                "buffer_size": 1,
                "fps": 30,
                "flip_method": 1,
                "retry_delay_ms": 500
            },
            "ros2": {
                "node_name": "gui_node",
                "topic": "robot_command",
                "qos_depth": 10,
                "spin_interval_ms": 10,
                "commands": {
                    "start": "start",
                    "retry": "retry",
                    "stop": "stop"
                }
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    custom_config = yaml.safe_load(f)
                    print(f"✅ Config loaded: {self.config_path}")
                    
                    # Merge custom + defaults
                    self.merge_configs(defaults, custom_config)
                    return defaults
            else:
                print(f"⚠️  {self.config_path} not found - using defaults")
        except Exception as e:
            print(f"❌ Config error: {e} - using defaults")
        
        return defaults
    
    def merge_configs(self, defaults, custom):
        """Deep merge"""
        for key, value in custom.items():
            if isinstance(value, dict) and defaults.get(key):
                self.merge_configs(defaults[key], value)
            else:
                defaults[key] = value
    
    def get(self, key, default=None):
        """Safe config access"""
        keys = key.split('.')
        config = self.config
        for k in keys:
            config = config.get(k, {})
        return config if config else default

# Global instance
config = ConfigManager()