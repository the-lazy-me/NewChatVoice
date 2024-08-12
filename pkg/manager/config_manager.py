import json
import os
from typing import Any, Dict

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.global_config = self._load_global_config()

    def _load_global_config(self) -> Dict[str, Any]:
        with open(os.path.join(self.config_path, "global_config.json"), "r", encoding="utf-8") as file:
            return json.load(file)
