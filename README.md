# 这是什么
这个项目可以构建一个简单的Web应用程序，与我的另一个仓库[UmaChat](https://github.com/kagari-bi/UmaChat)结合，可以与马娘进行对话。

VITS推理部分基于https://github.com/Plachtaa/VITS-fast-fine-tuning ，非常感谢。

# 如何使用
1.克隆此仓库
```
git clone https://github.com/kagari-bi/UmaChat_WebApi.git
```
2.在该项目的根目录下创建一个名为models的目录，从我的[HuggingFace仓库](https://huggingface.co/gouhuo/Umamusume_Vits_models/tree/main)下载你想要的模型，并将其解压到models目录中

3.打开config_backup.ini，输入你的OpenAI账户的api_key、百度账户的appid和key（用于将Chatgpt的回应翻译成日语，然后使用vits进行推理），以及代理地址等。保存并关闭，然后将其重命名为config.ini

4.安装依赖项
```
pip install -r requirements.txt
```
5.运行Web应用程序
```
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

# 一个简单的示例
在运行Web应用程序后，你可以尝试使用PostRequest.ipynb来了解Post表单和响应的格式

# 进阶用法
虽然我预期是让此项目最终能够实现与全马娘的对话，但时间上无法保证。因此，你可以为自己喜欢的马娘在action_mapping_table、prompt这两个文件夹中自己追加必要的文件。并且训练对应马娘的vits模型，放到models里面。

具体做法我在之后应该会出一期视频教程。

# 目前的缺陷
当前此项目的情感识别是利用ChatGPT实现的，但在不绑定支付方式的情况下，ChatGPT的API一分钟只能调用三次，而加入了情感识别的情况下，一次问答需要调用两次API，也就是平均要40s才能进行一次问答。

解决方法有三个：
1. 使用两个ChatGPT的账号
2. 降低提问的频率
3. 绑定支付方式

个人不太推荐第三种方法，因为我目前还没优化连续对话的逻辑，只是单纯把对话记录和问题一起作为请求发送了，这会导致随着当前对话轮数的增加，单次问答的Token消耗急剧上升，总之就是很费钱。

目前没有想到特别好的解决办法，或许今后我有可能会把情感识别的部分用另外的大型语言模型实现，但我不保证我一定会弄（老鸽子了属于是）

# 为这个项目出一份力
为全马娘桌宠化出一份力（大雾）。事实上，在进阶用法部分让该项目也能适用于你喜欢的马娘之后，你可以通过pull requests或其他任何可能的方法，将你追加的文件提交到此项目中。
### 这样做有什么好处
1. 避免重复造轮子，效率大幅提高
2. 没了

# 关于代理地址
代理地址的形式形如http://127.0.0.1:1920 ,具体的查看方法根据使用软件的不同也有所不同，可以尝试搜索相关关键词，看网上能不能找到答案
