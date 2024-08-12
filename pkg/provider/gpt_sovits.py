import aiohttp
import json
import os
import time
from graiax import silkcoder
from .base_provider import TTSInterface


class GPTSovits(TTSInterface):
    def __init__(self, service_url: str, temp_dir_path: str):
        self.service_url = service_url
        self.temp_dir_path = temp_dir_path
        self.character_list = None

    async def get_character_list(self, file_path: str = None):
        url = f"{self.service_url}/character_list"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if file_path:
                        # 检查 file_path 是否为目录
                        if os.path.isdir(file_path):
                            file_path = os.path.join(file_path, "gpt_sovits_character_list.json")
                        self._save_data(file_path, data)
                    self.character_list = data
                    return data
                else:
                    print(f"Failed to fetch characters: {response.status}")
                    return None

    async def generate_audio(self, text, character_name, **kwargs):
        emotion = kwargs.get('emotion', 'default')
        batch_size = kwargs.get('batch_size', 1)
        speed = kwargs.get('speed', 1.0)
        save_temp = kwargs.get('save_temp', True)

        url = f"{self.service_url}/tts"
        payload = json.dumps({
            "character": character_name,
            "emotion": emotion,
            "text": text,
            "batch_size": batch_size,
            "speed": speed,
            "stream": "False",
            "save_temp": save_temp,
            "text_language": "多语种混合"
        })
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    file_name = f"{character_name}_{emotion}_{int(time.time())}.wav"
                    save_path = os.path.join(self.temp_dir_path, file_name)
                    with open(save_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)

                    # Convert to silk format
                    silk_path = self._convert_to_silk(save_path)
                    return silk_path
                else:
                    print(f"Error generating audio: {response.status}")
                    return None

    def _convert_to_silk(self, audio_path: str) -> str:
        silk_path = audio_path.replace(".wav", ".silk")
        silkcoder.encode(audio_path, silk_path)
        return silk_path

    def _save_data(self, file_path: str, data):
        """Saves data to a file in JSON format."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    async def _download_audio(self, url, save_path):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(save_path, "wb") as f:
                            f.write(await response.read())
                        return True
                    else:
                        print(f"Error downloading audio: {response.status}")
                        return False
        except Exception as e:
            print(f"Error downloading audio: {str(e)}")
            return False

    def update_user_preference(self, user_id: str, character_name: str, emotion: str):
        # 检查角色列表是否已加载
        if self.character_list is None:
            raise ValueError("角色列表尚未加载。请先加载角色列表。")

        # 打印角色列表以调试
        print("角色列表:", self.character_list)

        # 查找角色和情感是否存在
        if character_name not in self.character_list:
            raise ValueError(f"未找到角色名称 {character_name}。")

        if emotion not in self.character_list[character_name]:
            raise ValueError(f"未找到角色 {character_name} 的情感 {emotion}。")

        # 构建用户偏好文件路径
        user_preferences_file = os.path.join(self.temp_dir_path, f"userData_{user_id}.json")

        # 读取现有的用户偏好文件
        if os.path.exists(user_preferences_file):
            with open(user_preferences_file, "r", encoding="utf-8") as file:
                preferences = json.load(file)
        else:
            preferences = {}

        # 更新或添加 gpt_sovits 偏好
        if "gpt_sovits" not in preferences:
            preferences["gpt_sovits"] = {}
        preferences["gpt_sovits"]["character_name"] = character_name
        preferences["gpt_sovits"]["emotion"] = emotion

        # 保存更新后的用户偏好
        with open(user_preferences_file, "w", encoding="utf-8") as file:
            json.dump(preferences, file, ensure_ascii=False, indent=4)

        # 返回保存成功的信息
        return f"用户 {user_id} 的偏好已保存为：角色：{character_name}，情感：{emotion}"

# import asyncio
#
#
# # 示例用法
# async def main():
#     tts = GPTSovits(service_url="http://127.0.0.1:5000", temp_dir_path="./temp")
#
#     # 获取角色列表并保存到文件
#     characters = await tts.get_character_list(file_path="./temp")
#     print("角色列表:", characters)
#
#     # 生成音频
#     silk_path = await tts.generate_audio("你好，世界！", "Hutao", emotion="default")
#     print("生成的音频路径:", silk_path)
#
#     # 保存用户偏好
#     result = tts.update_user_preference("user1233", "Hutao", "default")
#     print(result)
#
#
# # 运行示例
# asyncio.run(main())
