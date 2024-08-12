import os
from typing import Any, Dict, List, Union

from .manager.config_manager import ConfigManager
from .manager.user_data_manager import UserDataManager
from .utils.split_long_sentence import split_long_sentence
from .provider.provider_factory import ProviderFactory


class NCV:
    def __init__(self):
        # 实例化配置管理器
        self.config_manager = ConfigManager("data/plugins/NewChatVoice/config")
        # 实例化用户数据管理器
        self.user_data_manager = UserDataManager(
            self.config_manager.global_config["data_dir_path"],
            "data/plugins/NewChatVoice/data",
            self.config_manager.global_config
        )

        self.temp_dir_path = self.config_manager.global_config["temp_dir_path"]
        self._check_temp_dir_path()

    def _check_temp_dir_path(self) -> None:
        # 检查临时目录路径，如果不存在则创建
        if not os.path.exists(self.temp_dir_path):
            os.makedirs(self.temp_dir_path)

    async def validate_provider(self, provider_name: str) -> Union[str, None]:
        # 验证提供者是否有效
        provider_config = self.config_manager.global_config[provider_name]
        provider = ProviderFactory.get_provider(provider_name, provider_config, self.temp_dir_path)
        if provider_name == "acgn_ttson":
            return await provider.check_token()
        elif provider_name == "gpt_sovits":
            return await provider.get_character_list()
        return None

    async def get_character_list(self, provider_name: str) -> List[Dict[str, Any]]:
        # 获取提供者的角色列表
        provider_config = self.config_manager.global_config[provider_name]
        provider = ProviderFactory.get_provider(provider_name, provider_config, self.temp_dir_path)
        return await provider.get_character_list()

    def load_user_preference(self, user_id: int) -> Dict[str, Any]:
        # 加载用户偏好设置
        return self.user_data_manager.load_user_preference(user_id)

    def update_user_provider(self, user_id: int, provider_name: str) -> str:
        # 更新用户的TTS服务提供者
        if provider_name not in ["acgn_ttson", "gpt_sovits"]:
            return f"无效的TTS平台名称：{provider_name}"

        preferences = self.load_user_preference(user_id)
        preferences["provider"] = provider_name
        self.user_data_manager._save_user_preference(user_id, preferences)

        return f"用户 {user_id} 的TTS服务平台更新为 {provider_name}。"

    async def update_voice_switch(self, user_id: int, voice_switch: bool) -> str:
        # 更新用户的语音开关设置
        preferences = self.load_user_preference(user_id)
        preferences["voice_switch"] = voice_switch
        self.user_data_manager._save_user_preference(user_id, preferences)

        return f"用户 {user_id} 的语音开关更新为 {voice_switch}。"

    async def update_character_config(self, user_id: int, provider_name: str, config_updates: Dict[str, Any]) -> str:
        # 更新用户的角色配置
        preferences = self.load_user_preference(user_id)
        if provider_name not in preferences:
            preferences[provider_name] = {}

        character_list = await self.get_character_list(provider_name)

        if provider_name == "acgn_ttson":
            character_id = config_updates.get("character_id")
            if character_id is not None:
                character_id = int(character_id)
                character_name = next((char["character_name"] for char in character_list if char["id"] == character_id),
                                      None)
                if character_name is not None:
                    preferences[provider_name]["character_id"] = character_id
                    preferences[provider_name]["character_name"] = character_name
                    self.user_data_manager._save_user_preference(user_id, preferences)
                    return f"用户 {user_id} 的 acgn_ttson 角色名称更新为 {character_name}。"
                else:
                    return f"角色 ID {character_id} 在 acgn_ttson 的角色列表中未找到。"
            else:
                return "未提供 acgn_ttson 的角色 ID。"

        elif provider_name == "gpt_sovits":
            character_name = config_updates.get("character_name")
            emotion = config_updates.get("emotion")
            if character_name is not None and emotion is not None:
                if any(char["character_name"] == character_name and char["emotion"] == emotion for char in
                       character_list):
                    preferences[provider_name]["character_name"] = character_name
                    preferences[provider_name]["emotion"] = emotion
                    self.user_data_manager._save_user_preference(user_id, preferences)
                    return f"用户 {user_id} 的 gpt_sovits 角色名称更新为 {character_name}，情感更新为 {emotion}。"
                else:
                    return f"角色名称 {character_name} 和情感 {emotion} 在 gpt_sovits 的角色列表中未找到。"
            else:
                return "未提供 gpt_sovits 的角色名称或情感。"

        else:
            return f"未知的TTS平台: {provider_name}"

    async def auto_split_generate_audio(self, user_id: int, text: str) -> List[str]:
        # 自动分割文本并生成音频
        global_config = self.config_manager.global_config

        user_preference = self.load_user_preference(user_id)
        if not user_preference:
            user_preference = self.user_data_manager._load_user_data_template()

        provider_name = user_preference.get("provider", global_config["provider"])
        provider_config = global_config[provider_name]

        provider = ProviderFactory.get_provider(provider_name, provider_config, self.temp_dir_path)

        if len(text) > global_config["max_characters"]:
            short_sentences = split_long_sentence(text, global_config["max_characters"])
        else:
            short_sentences = [text]

        voice_paths = []

        if provider_name == "acgn_ttson":
            character_id = user_preference.get("acgn_ttson", {}).get("character_id", provider_config["character_id"])
            for sentence in short_sentences:
                audio_path = await provider.generate_audio(sentence, character_id=character_id)
                voice_paths.append(audio_path)
        elif provider_name == "gpt_sovits":
            character_name = user_preference.get("gpt_sovits", {}).get("character_name",
                                                                       provider_config["character_name"])
            emotion = user_preference.get("gpt_sovits", {}).get("emotion", provider_config["emotion"])
            for sentence in short_sentences:
                audio_path = await provider.generate_audio(sentence, character_name=character_name, emotion=emotion)
                voice_paths.append(audio_path)
        else:
            raise ValueError(f"未知的TTS平台: {provider_name}")

        return voice_paths

    async def no_split_generate_audio(self, user_id: int, text: str) -> str:
        # 不分割文本直接生成音频
        global_config = self.config_manager.global_config

        user_preference = self.load_user_preference(user_id)
        if not user_preference:
            user_preference = self.user_data_manager._load_user_data_template()

        provider_name = user_preference.get("provider", global_config["provider"])
        provider_config = global_config[provider_name]

        provider = ProviderFactory.get_provider(provider_name, provider_config, self.temp_dir_path)

        if provider_name == "acgn_ttson":
            character_id = user_preference.get("acgn_ttson", {}).get("character_id", provider_config["character_id"])
            audio_path = await provider.generate_audio(text, character_id=character_id)
        elif provider_name == "gpt_sovits":
            character_name = user_preference.get("gpt_sovits", {}).get("character_name",
                                                                       provider_config["character_name"])
            emotion = user_preference.get("gpt_sovits", {}).get("emotion", provider_config["emotion"])
            audio_path = await provider.generate_audio(text, character_name=character_name, emotion=emotion)
        else:
            raise ValueError(f"未知的TTS平台: {provider_name}")

        return audio_path
