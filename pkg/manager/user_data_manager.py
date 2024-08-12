import json
import os
from typing import Any, Dict

class UserDataManager:
    def __init__(self, data_dir_path: str, user_data_template_path: str, global_config: Dict[str, Any]):
        self.data_dir_path = data_dir_path
        self.user_data_template_path = user_data_template_path
        self.global_config = global_config

    def load_user_preference(self, user_id: int) -> Dict[str, Any]:
        user_preferences_file = os.path.join(self.data_dir_path, f"userData_{user_id}.json")
        if os.path.exists(user_preferences_file):
            with open(user_preferences_file, "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            preferences = self._load_user_data_template()
            preferences["provider"] = self.global_config["provider"]
            self._save_user_preference(user_id, preferences)
            return preferences

    def _load_user_data_template(self) -> Dict[str, Any]:
        with open(os.path.join(self.user_data_template_path, "userData.json"), "r", encoding="utf-8") as file:
            return json.load(file)

    def _save_user_preference(self, user_id: int, preferences: Dict[str, Any]) -> None:
        user_preferences_file = os.path.join(self.data_dir_path, f"userData_{user_id}.json")
        os.makedirs(self.data_dir_path, exist_ok=True)
        with open(user_preferences_file, "w", encoding="utf-8") as file:
            json.dump(preferences, file, ensure_ascii=False, indent=4)
