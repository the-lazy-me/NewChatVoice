import os
import shutil
import typing
import base64
from mirai import *

from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *
from pkg.command import entities
from pkg.command.operator import CommandOperator, operator_class
from plugins.NewChatVoice.pkg.voice import VoiceBase
from plugins.NewChatVoice.pkg.user_prefer import UserPreference


user_prefer: typing.Dict[str, UserPreference] = {}


@operator_class(name="ncv", help="获取帮助请输入：！ncv 帮助", privilege=1)
class SwitchVoicePlugin(CommandOperator):

    def __init__(self, host: APIHost):
        super().__init__(host)
        global user_prefer

    async def enable_voice(self, user_id):
        await user_prefer[user_id].change_preference({"voice_switch": True})
        return f"为用户{user_id}开启语音合成"

    async def disable_voice(self, user_id):
        await user_prefer[user_id].change_preference({"voice_switch": False})
        return f"为用户{user_id}关闭语音合成"

    async def check_status(self, user_id):
        return f"用户{user_id}的当前语音合成状态为：{user_prefer[user_id].voice_switch}，使用角色为：{user_prefer[user_id].get_character_by_id()}"

    async def list_characters(self):
        return_text = (
            "当前角色较多，请查看云文档：\n"
            "飞书云文档：https://s1c65jp249c.feishu.cn/sheets/WoiOsshwfhtUXRt2ZS0cVMCFnLc?from=from_copylink  \n"
            "腾讯文档：https://docs.qq.com/sheet/DSFhQT3dUZkpabHVu?tab=BB08J2  \n"
            "切换角色可使用名称或id,例如切换角色为流萤(id为2075): !ncv 切换 2075"
        )
        return return_text

    async def switch_character(self, user_id, character_id: str):
        info = await user_prefer[user_id].get_character_info(character_id)
        if info:
            await user_prefer[user_id].change_preference({"character_id": info["id"]})
            return f"为用户{user_id}切换语音合成角色为：{info['voice_name']}"
        else:
            return "未找到指定的角色"

    async def execute(self, context: entities.ExecuteContext) -> typing.AsyncGenerator[entities.CommandReturn, None]:
        user_id = context.query.launcher_id
        command = context.crt_params[0]
        if user_id not in user_prefer:
            user_prefer[user_id] = UserPreference(user_id)
            await user_prefer[user_id].load_config()

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
            result = "NewChatVoice语音合成插件,一个可以生成多种音色的语音对话插件 \n" "支持的指令有：\n" "!ncv 开启\n" "!ncv 关闭\n" "!ncv 状态\n" "!ncv 角色列表\n" "!ncv 切换 <角色id>\n" "!ncv 帮助"

        else:
            result = '无效指令，请输入"!ncv 帮助"查看帮助'
        yield entities.CommandReturn(text=result)


class VoiceSynthesisError(Exception):

    def __init__(self, message: str = None):
        super().__init__("语音合成错误: " + (message if message else "未知错误"))


@register(name="NewChatVoice", description="一个可以生成多种音色的语音对话插件", version="1.1", author="the-lazy-me")
class VoicePlugin(BasePlugin):
    def __init__(self, host: APIHost):
        super().__init__(host)
        global user_prefer
        self.ap = host.ap
        self.voice = None
        self._ensure_required_files_exist()

    async def initialize(self):
        user_prefer["default"] = UserPreference()
        self.voice = VoiceBase(user_prefer["default"].temp_dir_path)

        # 如果没有character.json文件或者内容为空，则获取角色数据
        character_path = user_prefer["default"].character_path
        if not os.path.exists(character_path) or os.path.getsize(character_path) == 0:
            await self.voice.get_character_list(character_path)

        # 需要character_list已经下载完成
        await user_prefer["default"].load_config()

        self.voice.set_token(user_prefer["default"].token)
        result = await self.voice.check_token()
        self.ap.logger.info("NewChatVoice插件提示：" + result)

        # 删除缓存目录并重新创建
        temp_dir_path = user_prefer["default"].temp_dir_path
        if os.path.exists(temp_dir_path):
            shutil.rmtree(temp_dir_path)
        os.makedirs(temp_dir_path)

    def _ensure_required_files_exist(self):
        directories = ["plugins/NewChatVoice/data/", "plugins/NewChatVoice/config"]

        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.ap.logger.info(f"Directory created: {directory}")
            self._set_permissions_recursively(directory)

    def _set_permissions_recursively(self, path, mode=0o777):
        for root, dirs, files in os.walk(path):
            for dirname in dirs:
                os.chmod(os.path.join(root, dirname), mode)
            for filename in files:
                os.chmod(os.path.join(root, filename), mode)

    @handler(NormalMessageResponded)
    async def text_to_voice(self, ctx: EventContext):
        user_id = ctx.event.launcher_id
        if user_id not in user_prefer:
            user_prefer[user_id] = UserPreference(user_id)
            await user_prefer[user_id].load_config()
        if user_prefer[user_id].voice_switch:
            voice = await self._get_voice(user_id, ctx.event.response_text)
            ctx.add_return("reply", [voice])

    async def ncv_tts(self, user_id: str, text: str) -> Voice:
        """
        供外部调用的文字转Voice的接口

        Args:
            user_id (str): 会话ID
            text (str): 要转换的文本

        Returns:
            Voice: 生成的语音对象
        """
        return await self._get_voice(user_id, text, True)

    async def _get_voice(self, user_id: str, text: str, is_api: bool = False) -> Voice:
        """
        将文本转换为语音

        Args:
            user_id (str): 会话ID
            text (str): 要转换的文本

        Returns:
            Voice: 生成的语音对象

        Raises:
            VoiceSynthesisError: 如果语音生成失败或者API调用失败
        """
        try:
            if not self.voice:
                await self.initialize()
            if user_id not in user_prefer:
                user_prefer[user_id] = UserPreference(user_id)
                await user_prefer[user_id].load_config()
            if is_api or user_prefer[user_id].voice_switch:
                voice_path = await self.voice.generate_audio(text, user_prefer[user_id].character_id)
                if os.path.exists(voice_path):
                    if user_prefer[user_id].voice_type == "base64":
                        with open(voice_path, "rb") as audio_file:
                            audio_data = audio_file.read()
                            base64_silk = base64.b64encode(audio_data).decode("utf-8")
                            return Voice(base64=base64_silk)
                    else:
                        return Voice(path=str(voice_path))
                else:
                    raise VoiceSynthesisError("语音生成失败")
            else:
                raise VoiceSynthesisError("语音合成未开启")
        except Exception as e:
            raise VoiceSynthesisError(f"API调用失败: {e}")
