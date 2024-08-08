import json
import os
import re
from plugins.NewChatVoice.pkg.utlis.synchronize_templates import synchronize_templates
from plugins.NewChatVoice.pkg.provider.provider_factory import ProviderFactory


class NCV:
    def __init__(self):
        # 同步模板文件
        synchronize_templates("plugins/NewChatVoice/templates/config", "data/plugins/NewChatVoice/config")
        synchronize_templates("plugins/NewChatVoice/templates/data", "data/plugins/NewChatVoice/data")

        self.global_config_path = "data/plugins/NewChatVoice/config"
        self.user_data_template_path = "data/plugins/NewChatVoice/data"

        # 加载全局配置并存储 data_dir_path
        global_config = self._load_global_config()
        self.data_dir_path = global_config["data_dir_path"]
        self.temp_dir_path = global_config["temp_dir_path"]

        # 检查 temp_dir_path 是否存在
        self._check_temp_dir_path()

    # 检测 temp_dir_path 是否存在
    def _check_temp_dir_path(self):
        if not os.path.exists(self.temp_dir_path):
            os.makedirs(self.temp_dir_path)

    # 加载全局配置
    def _load_global_config(self):
        # 读取全局配置文件，为global_config_path下的global_config.json
        with open(os.path.join(self.global_config_path, "global_config.json"), "r", encoding="utf-8") as file:
            return json.load(file)

    # 校验provider状态
    async def validate_provider(self, provider_name):
        global_config = self._load_global_config()
        provider_config = global_config[provider_name]
        provider = ProviderFactory.get_provider(provider_name, provider_config, self.data_dir_path)
        return_value = None
        if provider_name == "acgn_ttson":
            return_value = await provider.check_token()
        elif provider_name == "gpt_sovits":
            return_value = await provider.get_character_list()
        return return_value

    # 获取角色列表
    async def get_character_list(self, provider_name):
        global_config = self._load_global_config()
        provider_config = global_config[provider_name]
        provider = ProviderFactory.get_provider(provider_name, provider_config, self.data_dir_path)
        return await provider.get_character_list()

    # 加载角色列表，如果不存在则获取并保存
    async def _load_character_list(self, provider_name):
        character_list_path = os.path.join(self.data_dir_path, f"character_list_{provider_name}.json")

        if os.path.exists(character_list_path):
            with open(character_list_path, "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            character_list = await self.get_character_list(provider_name)
            if character_list is not None:
                with open(character_list_path, "w", encoding="utf-8") as file:
                    json.dump(character_list, file, ensure_ascii=False, indent=4)
                return character_list
            else:
                return None

    # 加载用户数据模板
    def _load_user_data_template(self):
        try:
            with open(os.path.join(self.user_data_template_path, "userData.json"), "r",
                      encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading user data template: {e}")
            return {}

    # 加载用户偏好
    def load_user_preference(self, user_id):
        try:
            user_id = int(user_id)
        except ValueError:
            raise ValueError("Invalid user_id: must be an integer")

        user_preferences_file = os.path.join(self.data_dir_path, f"userData_{user_id}.json")
        if os.path.exists(user_preferences_file):
            with open(user_preferences_file, "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            preferences = self._load_user_data_template()
            self._save_user_preference(user_id, preferences)
            return preferences

    # 更新用户的提供商信息
    def update_user_provider(self, user_id, provider_name):
        try:
            user_id = int(user_id)
        except ValueError:
            return "Invalid user_id: must be an integer"

        if provider_name not in ["acgn_ttson", "gpt_sovits"]:
            return f"无效的提供者名称：{provider_name}"

        preferences = self.load_user_preference(user_id)
        preferences["provider"] = provider_name
        self._save_user_preference(user_id, preferences)

        return f"用户 {user_id} 的TTS服务平台更新为 {provider_name}。"

    def updata_voice_switch(self, user_id, voice_switch: bool):
        try:
            user_id = int(user_id)
        except ValueError:
            return "Invalid user_id: must be an integer"

        preferences = self.load_user_preference(user_id)
        preferences["voice_switch"] = voice_switch
        self._save_user_preference(user_id, preferences)

        return f"用户 {user_id} 的语音开关更新为 {voice_switch}。"

    # 保存用户偏好
    def _save_user_preference(self, user_id, preferences):
        user_preferences_file = os.path.join(self.data_dir_path, f"userData_{user_id}.json")
        os.makedirs(self.data_dir_path, exist_ok=True)
        try:
            with open(user_preferences_file, "w", encoding="utf-8") as file:
                json.dump(preferences, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving user preferences: {e}")

    # 更新提供商配置
    async def update_character_config(self, user_id, provider_name, config_updates):
        try:
            user_id = int(user_id)
        except ValueError:
            return "Invalid user_id: must be an integer"

        preferences = self.load_user_preference(user_id)
        if provider_name not in preferences:
            preferences[provider_name] = {}

        character_list = await self._load_character_list(provider_name)

        if provider_name == "acgn_ttson":
            character_id = config_updates.get("character_id")
            character_id = int(character_id) if character_id is not None else None
            if character_id is not None:
                character_name = next(
                    (char["character_name"] for char in character_list if char["id"] == character_id), None)
                if character_name is not None:
                    preferences[provider_name]["character_id"] = character_id
                    preferences[provider_name]["character_name"] = character_name
                    self._save_user_preference(user_id, preferences)
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
                    self._save_user_preference(user_id, preferences)
                    return f"用户 {user_id} 的 gpt_sovits 角色名称更新为 {character_name}，情感更新为 {emotion}。"
                else:
                    return f"角色名称 {character_name} 和情感 {emotion} 在 gpt_sovits 的角色列表中未找到。"
            else:
                return "未提供 gpt_sovits 的角色名称或情感。"

        else:
            return f"未知的TTS平台: {provider_name}"

    # 创建用户偏好
    def _create_user_preference(self, user_id):
        try:
            user_id = int(user_id)
        except ValueError:
            raise ValueError("Invalid user_id: must be an integer")

        preferences = self._load_user_data_template()
        self._save_user_preference(user_id, preferences)
        return preferences

    def _split_long_sentence(self, text):
        global_config = self._load_global_config()
        max_length = global_config["max_characters"]

        # 移除多余的空行
        text = re.sub(r'\n+', '\n', text).strip()

        # 根据换行符切分段落
        paragraphs = text.split('\n')
        short_sentences = []

        # 处理每个段落
        for paragraph in paragraphs:
            if len(paragraph) <= max_length:
                short_sentences.append(paragraph)
            else:
                # 使用正则表达式在标点符号后切分
                sentences = re.split(r"(?<=[。！？；：.!?;:])", paragraph)
                current_sentence = ""
                for sentence in sentences:
                    if len(current_sentence) + len(sentence) > max_length:
                        if current_sentence:
                            short_sentences.append(current_sentence)
                        current_sentence = sentence
                    else:
                        current_sentence += sentence
                if current_sentence:
                    short_sentences.append(current_sentence)

        return short_sentences

    # 自动切分长句并生成音频
    async def auto_split_generate_audio(self, user_id, text):
        try:
            user_id = int(user_id)
        except ValueError:
            raise ValueError("Invalid user_id: must be an integer")

        global_config = self._load_global_config()
        temp_dir_path = self.temp_dir_path

        user_preference = self.load_user_preference(user_id)

        if not user_preference:
            user_preference = self._create_user_preference(user_id)

        provider_name = user_preference.get("provider", global_config["provider"])
        provider_config = global_config[provider_name]

        provider = ProviderFactory.get_provider(provider_name, provider_config, temp_dir_path)

        if len(text) > global_config["max_characters"]:
            short_sentences = self._split_long_sentence(text)
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

    # 不切分长句生成音频
    async def no_split_generate_audio(self, user_id, text):
        try:
            user_id = int(user_id)
        except ValueError:
            raise ValueError("Invalid user_id: must be an integer")

        global_config = self._load_global_config()
        temp_dir_path = self.temp_dir_path

        user_preference = self.load_user_preference(user_id)

        if not user_preference:
            user_preference = self._create_user_preference(user_id)

        provider_name = user_preference.get("provider", global_config["provider"])
        provider_config = global_config[provider_name]

        provider = ProviderFactory.get_provider(provider_name, provider_config, temp_dir_path)

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