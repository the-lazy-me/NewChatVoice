import json
from plugins.NewChatVoice.pkg.config import ConfigManager


class UserPreference:
    def __init__(self, launcher_id: str = ""):
        self.launcher_id = launcher_id
        self.config = ConfigManager("plugins/NewChatVoice/config/config", "plugins/NewChatVoice/templates/config", launcher_id=self.launcher_id)
        self.character_path = "plugins/NewChatVoice/data/character.json"
        self.temp_dir_path = "plugins/NewChatVoice/audio_temp"
        self.voice_switch = True
        self.character_id = 430
        self.character_dict = {}
        self.voice_type = "path"
        self.token = ""

    async def load_config(self) -> None:
        """
        加载配置文件，并更新实例变量
        """
        await self.config.load_config(completion=True)
        self.voice_switch = self.config.data.get("voice_switch", True)
        self.character_id = self.config.data.get("character_id", 430)
        self.voice_type = self.config.data.get("voice_type", "path")
        self.temp_dir_path = self.config.data.get("temp_dir_path", "plugins/NewChatVoice/audio_temp")
        self.token = self.config.data.get("token","")
        self.character_dict = await self._load_character_dict()

    async def change_preference(self, content: dict) -> None:
        """
        更新用户偏好设置，并保存到配置文件
        调用示例：change_preference({"switch": True})
        """
        preferences = ["voice_switch", "character_id", "voice_type"]

        for preference in preferences:
            if preference in content:
                self.config.data[preference] = content[preference]
                await self.config.update_config(preference, content[preference])

        # 重新加载配置
        await self.load_config()

    async def get_character_info(self, id: str) -> dict:
        return self.character_dict.get(id)

    async def _load_character_dict(self) -> dict:
        # 若已加载过则不重新加载
        if self.character_dict:
            return self.character_dict
        try:
            with open(self.character_path, "r", encoding="UTF-8") as file:
                character_list = json.load(file)
                return {str(ch["id"]): ch for ch in character_list}
        except Exception as e:
            print(f"Error loading characters: {e}")
            return {}

    def get_character_by_id(self) -> None:
        if str(self.character_id) in self.character_dict:
            return self.character_dict[str(self.character_id)]["voice_name"]
        else:
            return "未知角色"
