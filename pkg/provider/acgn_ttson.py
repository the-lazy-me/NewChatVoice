import aiohttp
import json
import os
from graiax import silkcoder
from .base_provider import TTSInterface


class ACGNTTSon(TTSInterface):
    def __init__(self, temp_dir_path: str):
        self.base_url = "https://u95167-bd74-2aef8085.westx.seetacloud.com:8443/flashsummary"
        self.temp_dir_path = temp_dir_path
        self.token = None
        self.character_list = None

    def set_token(self, token):
        self.token = self._extract_token(token)

    def _extract_token(self, token):
        if "http" in token:
            return token.split("=")[1]
        return token

    async def check_token(self):
        if not self.token:
            raise ValueError("未设置Token。请使用set_token方法设置Token。")

        url = f"{self.base_url}/getTokenData?token={self.token}"

        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return f"Token有效，您的会员将于 {data['data']['expiry_date']} 到期。"
                else:
                    return f"Token（{self.token}）" + await response.text()

    async def generate_audio(self, text, character_id: int, **kwargs):
        if not self.token:
            raise ValueError("未设置Token。请使用set_token方法设置Token。")

        audio_url = await self._get_audio_url(text, character_id)
        if audio_url:
            file_name = audio_url.split("/")[-1].split(".")[0][:8]
            save_path = os.path.join(self.temp_dir_path, file_name + ".mp3")
            if await self._download_audio(audio_url, save_path):
                silk_path = self._convert_to_silk(save_path)
                # os.remove(save_path)
                return silk_path
        return None

    async def get_character_list(self, file_path: str = None):
        url = f"{self.base_url}/voices?language=zh-CN&tag_id=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.character_list = self._process_characters(data["data"])
                    if file_path:
                        if os.path.isdir(file_path):
                            file_path = os.path.join(file_path, "acgn_ttson_character_list.json")
                        self._save_data(file_path, self.character_list)
                    return self.character_list
                else:
                    print(f"获取角色列表失败: {response.status}")
                    return None

    def _convert_to_silk(self, mp3_path: str) -> str:
        silk_path = mp3_path.replace(".mp3", ".silk")
        silkcoder.encode(mp3_path, silk_path)
        return silk_path

    async def _get_audio_url(self, text, voice_id: int):
        if not self.token:
            raise ValueError("未设置Token。请使用set_token方法设置Token。")

        url = f"{self.base_url}/tts?token={self.token}"
        payload = json.dumps(
            {
                "voice_id": voice_id,
                "text": text,
                "format": "mp3",
                "to_lang": "auto",
                "auto_translate": 0,
                "voice_speed": "0%",
                "speed_factor": 1,
                "rate": "1.0",
                "client_ip": "ACGN",
                "emotion": 1,
            }
        )
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    json_response = await response.json()
                    return f"{json_response['url']}:{json_response['port']}/flashsummary/retrieveFileData?stream=True&token={self.token}&voice_audio_path={json_response['voice_path']}"
                else:
                    print(await response.text())
                    return None

    async def _download_audio(self, url, save_path):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(save_path, "wb") as f:
                            f.write(await response.read())
                        return True
                    else:
                        print(f"下载音频出错: {response.status}")
                        return False
        except Exception as e:
            print(f"下载音频出错: {str(e)}")
            return False

    def _process_characters(self, data):
        characters_list = []
        for item in data:
            character_name = item["voice_name"].split("|")[0]
            character = {
                "character_name": character_name,
                "id": int(item["id"]),  # 确保ID为整数
                "tags": item["tags"][0]["tag_name"],
            }
            characters_list.append(character)
        return characters_list

    def _save_data(self, file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def update_user_preference(self, user_id: str, character_id: int):
        # 检查角色列表是否已加载
        if self.character_list is None:
            raise ValueError("角色列表尚未加载。请先加载角色列表。")

        # 查找角色名称
        character_name = next((char["character_name"] for char in self.character_list if char["id"] == character_id), None)
        if not character_name:
            raise ValueError(f"在角色列表中未找到角色 ID {character_id}。")

        # 构建用户偏好文件路径
        user_preferences_file = os.path.join(self.temp_dir_path, f"userData_{user_id}.json")

        # 读取现有的用户偏好文件
        if os.path.exists(user_preferences_file):
            with open(user_preferences_file, "r", encoding="utf-8") as file:
                preferences = json.load(file)
        else:
            preferences = {}

        # 更新或添加 acgn_ttson 偏好
        if "acgn_ttson" not in preferences:
            preferences["acgn_ttson"] = {}
        preferences["acgn_ttson"]["character_id"] = character_id
        preferences["acgn_ttson"]["character_name"] = character_name

        # 保存更新后的用户偏好
        with open(user_preferences_file, "w", encoding="utf-8") as file:
            json.dump(preferences, file, ensure_ascii=False, indent=4)

        # 返回保存成功的信息
        return f"用户 {user_id} 的偏好已保存为：角色 {character_name}（ID：{character_id}）"
