# NewChatVoice插件使用教程

> 但是我没学过python，代码大量依赖于AI生成，难免有不合理不正确之处，反正代码和人有一个能跑就行😋

## NewChatVoice插件介绍

本插件调用了[海豚Ai TTS-Online文本转语音](https://www.ttson.cn/?source=thelazy)的接口，用于将QChatGPT返回的内容转换为多种角色语音

特点：速度快，低价，效果好，支持原神、星铁、日漫1000+个角色、鸣潮、红警、APEX等多种类型的角色音色

TODO：

- [ ] 支持更多TTS平台，包括在线和本地的，如[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] 支持返回更长语音
- [ ] 可能的WebUI配置页面，实现支持在线页面切换

## 版本记录

### NewChatVoice 1.1

* 新增 外部调用接口。

  * 外部调用将使用相同的插件配置文件，但无视voice_switch状态。

  * 接口函数：

    ```python
    async def ncv_tts(self, user_id: str, text: str) -> Voice:
        """
        供外部调用的文字转Voice的接口
    
        Args:
            user_id (str): 会话ID
            text (str): 要转换的文本
    
        Returns:
            Voice: 生成的语音对象
        """
    ```

  * 调用示例：

    ```python
    async def handle_voice_synthesis(self, launcher_id: int, text: str, ctx: EventContext):
        try:
            from plugins.NewChatVoice.main import VoicePlugin, VoiceSynthesisError
        except ImportError as e:
            self.ap.logger.error(f"Failed to import VoicePlugin: {e}")
            return False
    
        ncv = VoicePlugin(self.host)
        try:
            voice = await ncv.ncv_tts(launcher_id, text)
            await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, MessageChain([voice]), False)
            return True
        except VoiceSynthesisError as e:
            self.ap.logger.error(f"{e}")
            return False
    ```

* 优化 配置文件逻辑。

  * 配置将分为 通用配置 “conifg.yaml”，以及会话配置 “config_&#91;会话&#93;.yaml”
  * 会话配置 优先级高于 通用配置

## NewChatVoice插件使用（重要）

配置完成 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get https://github.com/the-lazy-me/NewChatVoice
```
或查看详细的[插件安装说明](https://github.com/RockChinQ/QChatGPT/wiki/5-%E6%8F%92%E4%BB%B6%E4%BD%BF%E7%94%A8)

## token获取（重要）

打开此页面[https://www.ttson.cn/](https://www.ttson.cn/?source=thelazy)

点击升级专业版

付款后，会给出一个链接（**只展示一次，相当重要，记清楚，不然钱就白花了！！！**）

**复制粘贴给出的网址**

## 配置（重要）

打开NewChatVoice的config文件夹下的`config.yaml`，内容如下所示

```yaml
# 语音角色id，可在对话中指定角色，不指定则为使用默认角色（派蒙 430）
character_id: 430
# 是否为每个用户默认开启语音功能，默认为False，即不开启，True为默认开启
voice_switch: False
# 语音传输方式：path/base64，如果遇到消息平台访问权限问题，可尝试切换
voice_type: path
# 语音缓存路径，如果遇到消息平台访问权限问题，可以尝试修改至消息平台有权限访问的目录
temp_dir_path: plugins/NewChatVoice/audio_temp
# token，这个是必须的，不然无法使用，获取方式请看文档
token: 填入购买后显示的网站
```

重点关注：token，在汉字提示处填入刚刚复制网址，保存即可

## 指令（重要）

对话中，发送

- !ncv 开启
- !ncv 关闭
- !ncv 状态
- !ncv 角色列表
- !ncv 切换 <角色id>
- !ncv 帮助

角色列表：

> 飞书云文档：https://s1c65jp249c.feishu.cn/sheets/WoiOsshwfhtUXRt2ZS0cVMCFnLc?from=from_copylink
> 腾讯文档：https://docs.qq.com/sheet/DSFhQT3dUZkpabHVu?tab=BB08J2
> 切换角色请使用id,例如切换角色为流萤(id为2075): !ncv 切换 2075
