# NewChatVoice插件使用教程

> 但是我没学过python，代码大量依赖于AI生成，难免有不合理不正确之处，反正代码和人有一个能跑就行😋

## NewChatVoice插件介绍

本插件调用了[海豚Ai TTS-Online文本转语音](https://www.ttson.cn/?source=thelazy)的接口，用于将QChatGPT返回的内容转换为多种角色语音

特点：速度快，低价，效果好，支持原神、星铁、日漫1000+个角色、鸣潮、红警、APEX等多种类型的角色音色

当前版本：v1.0

TODO：

- [ ] 支持更多TTS平台，包括在线和本地的，如[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
- [ ] 支持用户单独配置token等鉴权密钥
- [ ] 支持返回更长语音
- [ ] 联动其他插件，如**[Waifu](https://github.com/ElvisChenML/Waifu)**
- [ ] 可能的WebUI配置页面，实现支持在线页面切换

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
# 默认角色，可在对话中指定角色，不指定则为每个用户使用默认角色
character: "派蒙"
# 是否为每个用户默认开启语音功能，默认为False，即不开启，True为默认开启
voice_switch: False

# token，这个是必须的，不然无法使用，获取方式请看文档
token: "填入购买后显示的网站，不能删首尾的双引号"
```

重点关注第三个，token，在汉字提示处填入刚刚复制网址，保存即可

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
