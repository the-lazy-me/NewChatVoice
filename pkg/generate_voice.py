import requests
import json
import os
import re
import yaml
from plugins.NewChatVoice.pkg.audio_converter import convert_to_silk


def load_config():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(base_path, 'config/config.yml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config, base_path


config, base_path = load_config()

url = config['token']

# 截取token，是url中的token参数，如果不是url，则直接视作token
if 'http' in url:
    token = url.split('=')[1]


def remove_emojis(text):
    # 正则表达式匹配所有表情符号
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def get_character_list(session=None):
    if session is None:
        session = requests.Session()
    url = "https://u95167-bd74-2aef8085.westx.seetacloud.com:8443/flashsummary/voices?language=zh-CN&tag_id=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        characters_list = process_characters(data)
        save_data(os.path.join(base_path, 'data', 'character.json'), characters_list)
    else:
        print(f"Failed to fetch characters: {response.status_code}")


def process_characters(data):
    characters_list = []
    for item in data:
        voice_name = item['voice_name'].split("|")[0]
        character = {
            "voice_name": voice_name,
            "id": item['id'],
            "tags": item['tags'][0]['tag_name'],
        }
        characters_list.append(character)
    return characters_list


def save_data(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='UTF-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_audio_url(text, voice_id, session=None):
    if session is None:
        session = requests.Session()
    url = f"https://u95167-bd74-2aef8085.westx.seetacloud.com:8443/flashsummary/tts?token={token}"
    payload = json.dumps({
        "voice_id": voice_id,
        "text": text,
        "format": "mp3",
        "to_lang": "auto",
        "auto_translate": 0,
        "voice_speed": "0%",
        "speed_factor": 1,
        "rate": "1.0",
        "client_ip": "ACGN",
        "emotion": 1
    })
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    # 打印请求
    response = session.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        json_response = response.json()
        return f"{json_response['url']}:{json_response['port']}/flashsummary/retrieveFileData?stream=True&token={config['token']}&voice_audio_path={json_response['voice_path']}"
    else:
        print(response.text)
        return None


def download_audio(url, save_path):
    try:
        with requests.get(url) as response:
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                print(f"Error downloading audio: {response.status_code}")
                return False
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
        return False


def generate_audio(text, character_id, session=None):
    if session is None:
        session = requests.Session()
    audio_url = get_audio_url(text, character_id, session)
    # 检测text,如果存在表情符号，去除
    text = remove_emojis(text)

    if audio_url:
        file_name = audio_url.split('/')[-1].split('.')[0][:8]
        save_path = os.path.join(base_path, "audio_temp", file_name + '.mp3')
        if download_audio(audio_url, save_path):
            silk_path = convert_to_silk(save_path)
            os.remove(save_path)
            return silk_path
    return None


if __name__ == "__main__":
    get_character_list()
