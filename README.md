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
你可以通过添加

# 目前的缺陷
当前此仓库的情感识别是利用ChatGPT实现的，但在不绑定支付方式的情况下，ChatGPT的API一分钟只能调用三次，而加入了情感识别的情况下，一次问答需要调用两次API，也就是平均要40s才能进行一次问答。
解决方法有三个：
1. 使用两个ChatGPT的账号
2. 降低提问的频率
3. 绑定支付方式

个人不太推荐第三种方法，因为我目前还没优化连续对话的逻辑，只是单纯把对话记录和问题一起作为请求发送了，这会导致随着当前对话轮数的增加，单次问答的Token消耗急剧上升，总之就是很费钱。
目前没有想到特别好的解决办法，或许今后我有可能会把情感识别的部分用另外的大型语言模型实现，但我不保证我一定会弄（老鸽子了属于是）

# 关于代理地址
代理地址的形式形如http://127.0.0.1:1920 ,具体的查看方法根据使用软件的不同也有所不同，可以尝试搜索相关关键词，看网上能不能找到答案
