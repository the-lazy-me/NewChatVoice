import os
import yaml
import json
import requests
from mirai import *

from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *
from pkg.command import entities
from pkg.command.operator import CommandOperator, operator_class
import typing

from plugins.NewChatVoice.pkg.generate_voice import generate_audio,get_character_list
from plugins.NewChatVoice.pkg.user_prefer import get_preference, change_preference
from plugins.NewChatVoice.pkg.check_token import check_token


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.yml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}


def load_character_dict():
    character_path = os.path.join(os.path.dirname(__file__), 'data/character.json')
    # 如果没有character.json文件或者内容为空，则获取角色数据
    if not os.path.exists(character_path) or os.path.getsize(character_path) == 0:
        get_character_list()
    try:
        with open(character_path, 'r', encoding='UTF-8') as file:
            character_list = json.load(file)
            return {str(ch['id']): ch for ch in character_list}
    except Exception as e:
        print(f"Error loading characters: {e}")
        return {}


def load_user_preference(user_id):
    user_preference = get_preference(str(user_id))
    if not user_preference:
        default_preference = {
            "switch": config['voice_switch'],
            "provider": "haitunAI",
            "detail": {
                "voice_id": int(default_character_id),
                "voice_name": config['character']
            }
        }
        change_preference(user_id, default_preference)
        return default_preference
    return user_preference


config = load_config()
character_dict = load_character_dict()
if character_dict=={}:
    get_character_list()
default_voice_switch = config.get('voice_switch', True)
default_character = config.get('character', 'default_character')
default_character_id = None
for char_id, char_info in character_dict.items():
    if char_info['voice_name'] == default_character:
        default_character_id = char_id
        break


@operator_class(name="ncv", help="获取帮助请输入：！ncv 帮助", privilege=1)
class SwitchVoicePlugin(CommandOperator):

    def __init__(self, host: APIHost):
        super().__init__(host)
        self.voice_enabled = config.get('voice_switch', True)
        self.character = config.get('character', 'default_character')
        self.session = requests.Session()

    async def enable_voice(self, user_id):
        change_preference(str(user_id), {"switch": True})
        return f"为用户{user_id}开启语音合成"

    async def disable_voice(self, user_id):
        change_preference(str(user_id), {"switch": False})
        return f"为用户{user_id}关闭语音合成"

    async def check_status(self, user_id):
        user_preference = load_user_preference(user_id)
        return f"用户{user_id}的当前语音合成状态为：{user_preference['switch']}，使用角色为：{user_preference['detail']['voice_name']}"

    async def list_characters(self):
        return_text = "当前角色较多，请查看云文档：\n" \
                      "飞书云文档：https://s1c65jp249c.feishu.cn/sheets/WoiOsshwfhtUXRt2ZS0cVMCFnLc?from=from_copylink  \n" \
                      "腾讯文档：https://docs.qq.com/sheet/DSFhQT3dUZkpabHVu?tab=BB08J2  \n" \
                      "切换角色请使用id,例如切换角色为流萤(id为2075): !ncv 切换 2075"
        return return_text

    async def switch_character(self, user_id, character_id):
        character_info = character_dict.get(str(character_id))
        if character_info:
            change_preference(str(user_id),
                              {"detail": {"voice_id": int(character_id), "voice_name": character_info['voice_name']}})
            return f"为用户{user_id}切换语音合成角色为：{character_info['voice_name']}"
        else:
            return "未找到指定的角色"

    async def execute(self, context: entities.ExecuteContext) -> typing.AsyncGenerator[entities.CommandReturn, None]:
        user_id = context.query.sender_id
        command = context.crt_params[0]
        if command == "开启":
            result = await self.enable_voice(user_id)
        elif command == "关闭":
            result = await self.disable_voice(user_id)
        elif command == "状态":
            result = await self.check_status(user_id)
        elif command == "角色列表":
            result = await self.list_characters()
        elif command == "切换":
            if len(context.crt_params) < 2:
                result = "请指定角色id"
            else:
                result = await self.switch_character(user_id, context.crt_params[1])
        elif command == "帮助":
            result = "NewChatVoice语音合成插件,一个可以生成多种音色的语音对话插件 \n" \
                     "支持的指令有：\n" \
                     "!ncv 开启\n" \
                     "!ncv 关闭\n" \
                     "!ncv 状态\n" \
                     "!ncv 角色列表\n" \
                     "!ncv 切换 <角色id>\n" \
                     "!ncv 帮助"

        else:
            result = "无效指令，请输入\"!ncv 帮助\"查看帮助"
        yield entities.CommandReturn(text=result)


@register(name="NewChatVoice", description="一个可以生成多种音色的语音对话插件", version="1.0", author="the-lazy-me")
class VoicePlugin(BasePlugin):
    def __init__(self, host: APIHost):
        super().__init__(host)
        self.session = requests.Session()
        os.makedirs(os.path.join(os.path.dirname(__file__), "audio_temp"), exist_ok=True)
        audio_temp_path = os.path.join(os.path.dirname(__file__), "audio_temp")
        for file in os.listdir(audio_temp_path):
            os.remove(os.path.join(audio_temp_path, file))

        # 检查data下是否有preference.json文件，没有则创建，并写入{}
        current_dir = os.path.dirname(os.path.abspath(__file__))
        preference_path = os.path.join(current_dir, 'data', 'preference.json')
        if not os.path.exists(preference_path):
            with open(preference_path, 'w', encoding='utf-8') as file:
                file.write('{}')


    async def initialize(self):
        result = check_token()
        self.ap.logger.info("NewChatVoice插件提示：" + result)

    @handler(PersonMessageReceived)
    async def check_user(self, ctx: EventContext):
        user = ctx.event.sender_id
        user_preference = load_user_preference(user)
        # 如果用户没有设置偏好，则设置默认偏好
        if not user_preference:
            default_preference = {
                "switch": default_voice_switch,
                "provider": "haitunAI",
                "detail": {
                    "voice_id": int(default_character_id),
                    "voice_name": default_character
                }
            }
            change_preference(user, default_preference)

    @handler(NormalMessageResponded)
    async def text_to_voice(self, ctx: EventContext):
        user = ctx.event.sender_id
        res_text = ctx.event.response_text
        user_preference = load_user_preference(user)
        if user_preference['switch']:
            voice_path = generate_audio(res_text, user_preference['detail']['voice_id'], self.session)
            if voice_path:
                ctx.add_return("reply", [Voice(path=str(voice_path))])
