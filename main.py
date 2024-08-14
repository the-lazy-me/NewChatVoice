import json
import os
import base64

from mirai import *
from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *
from pkg.command import entities
from pkg.command.operator import CommandOperator, operator_class
from .pkg.ncv import NCV

# 定义命令常量
CMD_ON = "开启"
CMD_OFF = "关闭"
CMD_STATUS = "状态"
CMD_LIST = "角色列表"
CMD_PROVIDER = "平台"
CMD_CHARACTER = "角色"
CMD_HELP = "帮助"
SUPPORTED_PROVIDERS = ["acgn_ttson", "gpt_sovits"]


@operator_class(name="ncv", help="获取帮助请输入：！ncv 帮助", privilege=1)
class SwitchVoicePlugin(CommandOperator):
    def __init__(self, host: APIHost):
        super().__init__(host)
        self.ncv = NCV()

    async def enable_voice(self, sender_id):
        provider_name = self.ncv.load_user_preference(sender_id)["provider"]
        await self.ncv.update_voice_switch(sender_id, True)
        return f"为用户{sender_id}开启语音合成，当前TTS平台为：{provider_name}"

    async def disable_voice(self, sender_id):
        provider_name = self.ncv.load_user_preference(sender_id)["provider"]
        await self.ncv.update_voice_switch(sender_id, False)
        return f"为用户{sender_id}关闭语音合成，当前TTS平台为：{provider_name}"

    async def check_status(self, sender_id):
        user_prefer = self.ncv.load_user_preference(sender_id)
        provider = user_prefer["provider"]
        character_name = user_prefer[provider]["character_name"]
        return_text = (f"用户{sender_id}的当前语音合成状态为：\n"
                       f"语音合成开关状态为：{'开启' if user_prefer['voice_switch'] else '关闭'}\n"
                       f"使用的TTS平台为：{provider}\n"
                       f"使用的角色为：{character_name}")
        if provider == "gpt_sovits":
            emotion = user_prefer[provider]["emotion"]
            return_text += f"\n使用的情感为：{emotion}"
        return return_text

    async def list_characters(self, sender_id):
        provider_name = self.ncv.load_user_preference(sender_id)["provider"]
        if provider_name == "acgn_ttson":
            return_text = (
                f"当前TTS平台为：{provider_name}，角色列表：\n"
                "当前角色较多，请查看云文档：\n"
                "飞书云文档：https://s1c65jp249c.feishu.cn/sheets/WoiOsshwfhtUXRt2ZS0cVMCFnLc?from=from_copylink  \n"
                "腾讯文档：https://docs.qq.com/sheet/DSFhQT3dUZkpabHVu?tab=BB08J2  \n"
                "切换角色使用对应角色的id，例如切换角色为流萤(id为2075): \n !ncv 角色 2075"
            )
        elif provider_name == "gpt_sovits":
            data = await self.ncv.get_character_list(provider_name)
            character_list = ""
            for name, emotions in data.items():
                emotions_str = ",".join(emotions)
                character_list += f"{name}：{emotions_str}\n"
            return_text = (f"当前TTS平台：{provider_name}\n"
                           "角色列表：\n"
                           f"{character_list}\n"
                           "切换角色使用对应角色的名称和情感，例如切换角色为胡桃，情感为default: \n"
                           f"!ncv 角色 Hutao default"
                           )
        return return_text

    async def switch_provider(self, sender_id, provider_name: str):
        self.ncv.update_user_provider(sender_id, provider_name)
        return f"为用户{sender_id}切换TTS平台为：{provider_name}"

    async def switch_character(self, sender_id, character_info: str):
        provider_name = self.ncv.load_user_preference(sender_id)["provider"]
        if provider_name == "acgn_ttson":
            character_id = character_info["character_id"]
            response = await self.ncv.update_character_config(sender_id, provider_name, {"character_id": character_id})

        elif provider_name == "gpt_sovits":
            character_name = character_info["character_name"]
            emotion = character_info["emotion"]
            response = await self.ncv.update_character_config(sender_id, provider_name,
                                                              {"character_name": character_name, "emotion": emotion})
        return response

    async def execute(self, context: entities.ExecuteContext) -> typing.AsyncGenerator[entities.CommandReturn, None]:
        sender_id = int(context.query.sender_id)
        command = context.crt_params[0]
        if command in [CMD_ON, "on"]:
            result = await self.enable_voice(sender_id)
        elif command in [CMD_OFF, "off"]:
            result = await self.disable_voice(sender_id)
        elif command in [CMD_STATUS, "status"]:
            result = await self.check_status(sender_id)
        elif command in [CMD_LIST, "list"]:
            result = await self.list_characters(sender_id)
        elif command in [CMD_PROVIDER, "provider"]:
            if len(context.crt_params) < 2:
                result = "请指定TTS平台名称：acgn_ttson或gpt_sovits"
            elif context.crt_params[1] not in SUPPORTED_PROVIDERS:
                result = f"无效的TTS平台名称：{context.crt_params[1]}，当前支持的TTS平台有：acgn_ttson, gpt_sovits"
            else:
                result = await self.switch_provider(sender_id, context.crt_params[1])
        elif command in [CMD_CHARACTER, "character"]:
            if len(context.crt_params) < 2:
                result = ("请指定角色信息，例如：\n"
                          "acgn_ttson使用!ncv 角色 2075 "
                          "gpt_sovits使用!ncv 角色 Hutao default"
                          )
            else:
                provider = self.ncv.load_user_preference(sender_id)["provider"]
                if provider == "acgn_ttson":
                    character_id = context.crt_params[1]
                    result = await self.switch_character(sender_id, {"character_id": character_id})
                elif provider == "gpt_sovits":
                    character_name = context.crt_params[1]
                    emotion = context.crt_params[2]
                    result = await self.switch_character(sender_id,
                                                         {"character_name": character_name, "emotion": emotion})

        elif command in [CMD_HELP, "help"]:
            result = (
                "NewChatVoice语音合成插件,一个可以生成多种音色的语音对话插件 \n"
                "支持的指令有：\n"
                "1. 为当前用户开启语音：\n"
                "!ncv 开启  或  !ncv on\n"
                "\n"
                "2. 为当前用户关闭语音：\n"
                "!ncv 关闭  或  !ncv off\n"
                "\n"
                "3. 查看当前用户语音合成状态：\n"
                "!ncv 状态  或  !ncv status\n"
                "\n"
                "4.查看当前TTS平台的角色列表：\n"
                "!ncv 角色列表  或  !ncv list\n"
                "\n"
                "5. 切换TTS平台：\n"
                "!ncv 平台 <TTS平台名称>  或  !ncv provider <TTS平台名称>\n"
                "\n"
                "6. 切换当前TTS平台的角色：\n"
                "!ncv 角色 <角色信息>  或  !ncv character <角色信息>\n"
                "\n"
                "7. 查看NewChatVoice插件的帮助：\n"
                "!ncv 帮助  或  !ncv help\n"
                "\n"
                "8. 详细教程：https://github.com/the-lazy-me/NewChatVoice/tree/master"
            )
        else:
            result = '无效指令，请输入"!ncv 帮助"查看帮助'
        yield entities.CommandReturn(text=result)


@register(name="NewChatVoice", description="一个可以生成多种音色的语音对话插件", version="2.2", author="the-lazy-me")
class VoicePlugin(BasePlugin):
    def __init__(self, host: APIHost):
        super().__init__(host)
        self.ncv = NCV()
        self.voiceWithText = False
        global_config = self._load_global_config()
        self.voiceWithText = global_config.get('voiceWithText', False)
        temp_dir_path = global_config.get('temp_dir_path', 'temp/')
        self._clear_temp_dir(temp_dir_path)

    def _load_global_config(self):
        try:
            with open("data/plugins/NewChatVoice/config/global_config.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"加载全局配置文件时出错: {e}")
            return {}

    def _clear_temp_dir(self, temp_dir_path: str):
        try:
            if not os.path.exists(temp_dir_path):
                os.makedirs(temp_dir_path)
            else:
                for file in os.listdir(temp_dir_path):
                    os.remove(os.path.join(temp_dir_path, file))
        except Exception as e:
            print(f"清理临时目录时出错: {e}")

    @handler(NormalMessageResponded)
    async def text_to_voice(self, ctx: EventContext):
        user_prefer = self.ncv.load_user_preference(ctx.event.sender_id)
        if not user_prefer["voice_switch"]:
            return

        ctx.prevent_default()
        target_type = str(ctx.event.query.launcher_type).split('.')[-1].lower()
        sender_id = ctx.event.sender_id
        group_id = ctx.event.launcher_id
        text = ctx.event.response_text

        if target_type == "person":
            receiver_id = sender_id
            single_audio_path = await self.ncv.no_split_generate_audio(sender_id, text)
            if single_audio_path:
                # print(single_audio_path)
                # base64编码
                with open(single_audio_path, "rb") as f:
                    base64_audio = base64.b64encode(f.read()).decode()
                await ctx.send_message(target_type, receiver_id, [Voice(base64=base64_audio)])
            # await ctx.send_message(target_type, receiver_id, [Voice(path=str(single_audio_path))])
        elif target_type == "group":
            receiver_id = group_id
            audio_paths = await self.ncv.auto_split_generate_audio(sender_id, text)
            if audio_paths:
                for audio_path in audio_paths:
                    # base64编码
                    with open(audio_path, "rb") as f:
                        base64_audio = base64.b64encode(f.read()).decode()
                    await ctx.send_message(target_type, receiver_id, [Voice(base64=base64_audio)])
                    # await ctx.send_message(target_type, receiver_id, [Voice(path=str(audio_path))])
            if self.voiceWithText:
                await ctx.send_message(target_type, receiver_id, [Plain(text)])

    def __del__(self):
        pass
