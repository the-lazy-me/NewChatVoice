import json
import os

from mirai import *
from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *
from pkg.command import entities
from pkg.command.operator import CommandOperator, operator_class
from plugins.NewChatVoice.pkg.ncv import NCV


#
@operator_class(name="ncv", help="获取帮助请输入：！ncv 帮助", privilege=1)
class SwitchVoicePlugin(CommandOperator):

    def __init__(self, host: APIHost):
        super().__init__(host)
        self.ncv = NCV()

    async def enable_voice(self, sender_id):
        provider_name = self.ncv.load_user_preference(sender_id)["provider"]
        await self.ncv.updata_voice_switch(sender_id, True)
        return f"为用户{sender_id}开启语音合成，当前TTS平台为：{provider_name}"

    async def disable_voice(self, sender_id):
        provider_name = self.ncv.load_user_preference(sender_id)["provider"]
        await self.ncv.updata_voice_switch(sender_id, False)
        return f"为用户{sender_id}关闭语音合成，当前TTS平台为：{provider_name}"

    async def check_status(self, sender_id):
        user_prefer = self.ncv.load_user_preference(sender_id)
        provider = user_prefer["provider"]
        character_name = user_prefer[provider]["character_name"]
        return_text = (f"用户{sender_id}的当前语音合成状态为：\n"
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
                f"当前提供者为：{provider_name}，角色列表：\n"
                "当前角色较多，请查看云文档：\n"
                "飞书云文档：https://s1c65jp249c.feishu.cn/sheets/WoiOsshwfhtUXRt2ZS0cVMCFnLc?from=from_copylink  \n"
                "腾讯文档：https://docs.qq.com/sheet/DSFhQT3dUZkpabHVu?tab=BB08J2  \n"
                "切换角色使用对应角色的id，例如切换角色为流萤(id为2075): !ncv 角色 2075"
            )
        elif provider_name == "gpt_sovits":
            character_list = self.ncv.get_character_list(provider_name)
            return_text = f"当前提供者为：{provider_name}，角色列表：\n" + "\n".join(character_list)
        return return_text

    async def switch_provider(self, sender_id, provider_name: str):
        self.ncv.update_user_provider(sender_id, provider_name)
        return f"为用户{sender_id}切换语音合成提供者为：{provider_name}"

    async def switch_character(self, sender_id, character_info: str):
        provider_name = self.ncv.load_user_preference(sender_id)["provider"]
        if provider_name == "acgn_ttson":
            character_id = character_info["character_id"]
            resonse = await self.ncv.update_character_config(sender_id, provider_name, {"character_id": character_id})

        elif provider_name == "gpt_sovits":
            character_name = character_info["character_name"]
            emotion = character_info["emotion"]
            resonse = await self.ncv.update_character_config(sender_id, provider_name,
                                                             {"character_name": character_name, "emotion": emotion})
        return resonse

    async def execute(self, context: entities.ExecuteContext) -> typing.AsyncGenerator[entities.CommandReturn, None]:
        sender_id = int(context.query.sender_id)
        command = context.crt_params[0]
        if command == "开启" or command == "on":
            result = await self.enable_voice(sender_id)
        elif command == "关闭" or command == "off":
            result = await self.disable_voice(sender_id)
        elif command == "状态" or command == "status":
            result = await self.check_status(sender_id)
        elif command == "角色列表" or command == "list":
            result = await self.list_characters(sender_id)
        elif command == "平台" or command == "provider":
            if len(context.crt_params) < 2:
                result = "请指定TTS平台名称，acgn_ttson或gpt_sovits"
            elif context.crt_params[1] not in ["acgn_ttson", "gpt_sovits"]:
                result = f"无效的TTS平台名称：{context.crt_params[1]}，当前支持的TTS平台有：acgn_ttson, gpt_sovits"
            else:
                result = await self.switch_provider(sender_id, context.crt_params[1])
        elif command == "角色" or command == "character":
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

        elif command == "帮助" or command == "help":
            result = (
                "NewChatVoice语音合成插件,一个可以生成多种音色的语音对话插件 \n"
                "支持的指令有：\n"
                "1. 为当前用户开启语音：\n"
                "!ncv 开启  或  !ncv off\n"
                "\n"
                "2. 为当前用户关闭语音：\n"
                "!ncv 关闭  或  !ncv on\n"
                "\n"
                "3. 查看当前用户语音合成状态：\n"
                "!ncv 状态  或  !ncv status\n"
                "\n"
                "4. 查看当前TTS平台的角色列表：\n"
                "!ncv 角色列表  或  !ncv list\n"
                "\n"
                "5. 切换TTS平台：\n"
                "!ncv 切换提供者 <TTS平台名称>  或  !ncv provider <TTS平台名称>\n"
                "\n"
                "6. 切换当前TTS平台的角色：\n"
                "!ncv 角色 <角色信息>  或  !ncv character <角色信息>\n"
                "\n"
                "7. 查看详细帮助：https://github.com/the-lazy-me/NewChatVoice\n"
            )
        else:
            result = '无效指令，请输入"!ncv 帮助"查看帮助'
        yield entities.CommandReturn(text=result)


@register(name="NewChatVoice", description="一个可以生成多种音色的语音对话插件", version="2.0", author="the-lazy-me")
class VoicePlugin(BasePlugin):
    def __init__(self, host: APIHost):
        super().__init__(host)
        self.ncv = NCV()
        self.voiceWithText = False
        # 加载全局配置文件
        global_config = _load_global_config()
        self.voiceWithText = global_config['voiceWithText']
        # 清空音频临时文件
        temp_dir_path = global_config['temp_dir_path']
        _clear_temp_dir(temp_dir_path)

    async def ncv_outsid_interface(self, sender_id: str, text: str) -> Voice:
        """
        供外部调用的文字转Voice的接口

        Args:
            sender_id (str): 会话ID
            text (str): 要转换的文本

        Returns:
            Voice: 生成的语音silk文件列表
        """
        audio_paths = await self.ncv.generate_audio(sender_id, text)
        if audio_paths:
            return audio_paths
        return None

    @handler(NormalMessageResponded)
    async def text_to_voice(self, ctx: EventContext):
        # 禁止默认回复行为
        ctx.prevent_default()

        launcher_type = str(ctx.event.query.launcher_type)
        target_type = (launcher_type).split('.')[-1].lower()
        sender_id = ctx.event.sender_id
        group_id = ctx.event.launcher_id
        text = ctx.event.response_text
        audio_paths = await self.ncv.generate_audio(sender_id, text)
        if audio_paths:
            # print(audio_paths)
            # 遍历生成的音频文件路径
            for audio_path in audio_paths:
                if target_type == "group":
                    # 发送语音消息
                    await ctx.send_message(target_type, group_id, [Voice(path=str(audio_path))])
                    if self.voiceWithText:
                        print("发送文本消息")
                        # 发送文本消息
                        await ctx.send_message(target_type, group_id, [Plain(text=text)])
                elif target_type == "person":
                    # 发送语音消息
                    await ctx.send_message(target_type, sender_id, [Voice(path=str(audio_path))])
                    if self.voiceWithText:
                        # 发送文本消息
                        await ctx.send_message(target_type, sender_id, [Plain(text=text)])

    # 插件卸载时触发
    def __del__(self):
        pass


def _load_global_config():
    global_config = {}
    try:
        with open("data/plugins/NewChatVoice/config/global_config.json", "r", encoding="utf-8") as file:
            global_config = json.load(file)
    except Exception as e:
        print(f"Error loading global config: {e}")
    return global_config


def _clear_temp_dir(temp_dir_path: str):
    if not os.path.exists(temp_dir_path):
        os.makedirs(temp_dir_path)
    else:
        for file in os.listdir(temp_dir_path):
            os.remove(os.path.join(temp_dir_path, file))
