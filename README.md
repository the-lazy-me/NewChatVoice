# NewChatVoice插件使用教程

> 我没学过python，代码大量依赖于AI生成，难免有不合理不正确之处，反正代码和人有一个能跑就行😋

## 插件介绍

NewChatVoice，一个可以调用多个TTS服务平台的[QChatGPT](https://github.com/RockChinQ/QChatGPT)插件，用于将LLM返回的文本转为你喜欢的语音

当前支持以下TTS服务平台：
1. [TTS-Online原神免费文本转语音](https://acgn.ttson.cn/)（在使用中，本插件称之为`acgn_ttson`）
2. [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)（在使用中本插件称之为`gpt_sovits`）

TODO：

- [x] 支持[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] 支持[海豚AI 海豚配音 TTS Online](https://www.ttson.cn/?source=thelazy)
- [ ] 支持[fish-speech](https://github.com/fishaudio/fish-speech)
- [ ] 支持[ChatTTS](https://github.com/2noise/ChatTTS)
- [x] 支持返回更长语音，长文本自动切分，分开发送
- [ ] 可能的WebUI配置页面，实现支持在线页面切换

</details>

## 插件安装

配置完成 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get https://github.com/the-lazy-me/NewChatVoice.git
```



## 插件配置

### acgn_ttson的token获取

如果不使用在线语音则可跳过

打开此页面[https://www.ttson.cn/](https://www.ttson.cn/?source=thelazy)

点击升级专业版

付款后，会给出一个链接（**只展示一次，相当重要，记清楚，不然钱就白花了！！！**）

**复制粘贴给出的网址**

### GPT-SoVITS推理整合包

如果不使用本地语音则可跳过

整合包来源：B站UP主：[箱庭XTer](https://space.bilibili.com/66633770)制作的基于[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)开发的 推理特化的 前后端项目[GPT-soVITS-Inference](https://www.yuque.com/xter/zibxlp/kkicvpiogcou5lgp)

推理整合包下载路径：[参考原教程的整合包下载部分](https://www.yuque.com/xter/zibxlp/nqi871glgxfy717e#K8NQm)

下载，解压，打开`0 一键启动脚本`文件夹，然后双击打开里面的`5 启动后端程序.bat`

等待1分钟之内，可以看到如下提示就说明可以了

```bash
INFO:     Started server process [15276]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

> **GPT-SoVITS推理整合包，仅限Windows**
>
> 其他平台，参考[原教程](https://www.yuque.com/xter/zibxlp/nqi871glgxfy717e#s54wm)

### 配置文件

> 请注意，所有的配置文件和用户数据，默认都在QChatGPT目录下的`data/plugins/NewChatVoice`中

打开`data/plugins/NewChatVoice`的config文件夹下的`global_config.json`，内容如下所示

```json
{
  "provider": "acgn_ttson",
  "max_characters": 300,
  "voiceWithText": false,
  "temp_dir_path": "data/plugins/NewChatVoice/temp",
  "data_dir_path": "data/plugins/NewChatVoice/data",
  "acgn_ttson": {
    "character_id": 430,
    "token": "填入购买后给出的网址"
  },
  "gpt_sovits": {
    "url": "http://127.0.0.1:5000",
    "character_name": "Hutao",
    "emotion": "default",
    "batch_size": 1,
    "speed": 1.0,
    "save_temp": true
  }
}

```

默认情况下，你需要修改的只有

`token`，将`填入购买后给出的网址`这句话，替换为你上面购买后复制的`链接`

以下是参数解释

- `provider`: 默认使用的TTS服务提供商，可以使用的是 `acgn_ttson`和`gpt_sovits`
- `max_characters`: 单个音频消息中最多包含的字符，超过即切分
- `voiceWithText`: 设置回复语音消息时，是否连同文本一起回复
- `temp_dir_path`: 临时文件存储路径。在合成过程中生成的语音文件将存储在这个目录中，每次运行主程序会清空
- `data_dir_path`: 数据文件存储路径。生成的用户偏好配置将存储在这个目录中
- `acgn_ttson`: 
  - `character_id`: 指定要使用的角色ID。这里设置为430(派蒙)
  - `token`: 需要替换为你购买后提供的链接或令牌，用于身份验证
- `gpt_sovits`: 
  - `url`:默认本地服务器 `http://127.0.0.1:5000`
  - `character_name`: 角色文件夹名称，注意大小写、全半角、语言。默认设置为 Hutao
  - `emotion`: 角色情感，需为角色实际支持的情感，否则将调用默认情感。默认设置为 default
  - `batch_size`: 一次性几个batch，电脑牛逼一些可以开大点，会加速很多，整数，默认为1
  - `speed`: 语速，默认为1.0
  - `save_temp`: 是否保存临时文件，为true时，后端会保存生成的音频，下次相同请求会直接返回该数据，默认为true


## 插件指令

对话中，发送

1. 为当前用户开启语音：
`!ncv` 开启  或  `!ncv on`

2. 为当前用户关闭语音：
`!ncv 关闭`  或  `!ncv off`

3. 查看当前用户语音合成状态：
`!ncv 状态`  或  `!ncv status`

4. 查看当前TTS平台的角色列表：
`!ncv 角色列表`  或  `!ncv list`

5. 切换TTS平台：
`!ncv 平台 <TTS平台名称>`  或  `!ncv provider <TTS平台名称>`

6. 切换当前TTS平台的角色：
`!ncv 角色 <角色>`  或  `!ncv character <角色>`

7. 查看NewChatVoice插件的帮助：
`!ncv 帮助`  或  `!ncv help`

acgn_ttson角色列表：

> 飞书云文档：https://s1c65jp249c.feishu.cn/sheets/WoiOsshwfhtUXRt2ZS0cVMCFnLc?from=from_copylink
> 
> 腾讯文档：https://docs.qq.com/sheet/DSFhQT3dUZkpabHVu?tab=BB08J2
> 
> 切换角色请使用id,例如切换角色为流萤(id为2075): !ncv 切换 2075

## Q&A:
- acgn_ttson是什么
  - 答：这里的`acgn_ttson`是指这个站点[https://acgn.ttson.cn](https://acgn.ttson.cn)，一个在线生成二次元语音的，支持超多角色，生成速度快，生成效果好，使用成本低

- gpt_sovits是什么
  - 这里的`gpt_sovits`是指GPT-SoVITS，这是[花儿不哭](https://space.bilibili.com/5760446/)大佬研发的低成本AI音色克隆软件。目前只有TTS（文字转语音）功能，将来会更新变声功能。（2024-08-08摘录自[GPT-SoVITS指南](https://www.yuque.com/baicaigongchang1145haoyuangong/ib3g1e)）
  - 特点：本地部署，自由度高，但是生成速度慢，使用成本高

- 我应该选什么
  - 为更好的体验，建议使用acgn_ttson，为了更高自由度，选择gpt_sovits

- 报错：ImportError：DLL load failed while importing _silkv3：找不到指定的模块
  - 在[这里](https://aka.ms/vs/17/release/vc_redist.x64.exe)下载最新版本的 **C++ Redistributable**
- 报错：{"detail":"未注册的用户，请联系管理员"}
  - 没有填写acgn_ttson的token，如果不需要，则可以无视，这时建议把`global_config.json`的`provider`改为`gpt_sovits`，不然一直报这个


## 版本记录

<details> 
  <summary>更新摘要：</summary> 

### NewChatVoice 2.2

优化可能有的诸多问题

### NewChatVoice 2.1

- 群聊中自动切割长文本，以多个音频分别返回，私聊中单个音频直接返回（不得已而为之）
- 优化自动切分逻辑
- 修改外部调用接口

```python
async def ncv_outside_interface(self, sender_id: str, text: str, split: bool) -> Voice:
    """
    供外部调用的文字转Voice的接口
    Args:
        sender_id (str): 会话ID
        text (str): 要转换的文本
        split (bool): 是否分割文本
    Returns:
        Voice: 生成的语音silk文件路径(如果split为True则以列表返回多个路径)
    """
    if split:
        audio_paths = await self.ncv.auto_split_generate_audio(sender_id, text)
        if audio_paths:
            return audio_paths
    else:
        audio_path = await self.ncv.no_split_generate_audio(sender_id, text)
        return audio_path
```

### NewChatVoice 2.0

- 新增对gpt_sovits的支持
- 支持长文本自动切分，以多个音频消息发送
- 修改所有配置文件为json格式
- 修改外部调用接口

```python
async def ncv_outsid_interface(self, sender_id: str, text: str) -> Voice:
    """
    供外部调用的文字转Voice的接口

    Args:
        sender_id (str): 会话ID
        text (str): 要转换的文本

    Returns:
        Voice: 生成的语音silk文件列表
    """
```

### NewChatVoice 1.2

- 修改配置文件位置，为了避免升级时被删除，过程文件及配置文件目录移至插件目录外：“QChatGPT\data\plugins\NewChatVoice\”。

### NewChatVoice 1.1

- 新增外部调用接口。

    - 外部调用将使用相同的插件配置文件，但无视voice_switch状态。
    - 接口函数：

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

    - 调用示例：

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

- 优化配置文件逻辑。

    - 配置将分为通用配置“config.yaml”，以及会话配置“config_[会话].yaml”
    - 会话配置优先级高于通用配置
