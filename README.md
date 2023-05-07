[中文文档看这里](https://github.com/kagari-bi/UmaChat_WebApi/blob/main/README-ZH.md)

# What is this
This project allows you to build a simple Web application that, when combined with my other repository[UmaChat](https://github.com/kagari-bi/UmaChat), enables you to have conversations with Uma Musume characters.

The VITS inference part is based on https://github.com/Plachtaa/VITS-fast-fine-tuning. Many thanks!

# How to use
1.Clone this repository
```
git clone https://github.com/kagari-bi/UmaChat_WebApi.git
```
2.Create a directory called 'models' in the root of the project, download the model you want from my [HuggingFace repository](https://huggingface.co/gouhuo/Umamusume_Vits_models/tree/main) and unzip it into the 'models' directory

3.Open config_backup.ini, enter your OpenAI account's api_key, Baidu account's appid and key (for translating ChatGPT's response into Japanese and then using VITS for inference), and the proxy address. Save and close it, then rename it to config.ini

4.Install dependencies
```
pip install -r requirements.txt
```
5.Run the Web application
```
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

# A simple example
After running the Web application, you can try using PostRequest.ipynb to understand the format of Post forms and responses

# Advanced usage
Although I expect this project to eventually enable conversations with all Uma Musume characters, I cannot guarantee the timeframe. Therefore, you can add necessary files for your favorite Uma Musume characters in the action_mapping_table and prompt folders. You can also train the corresponding VITS model for each character and place it in the 'models' folder.

I will probably release a video tutorial on this later.

# Current limitations
Currently, emotion recognition in this project is implemented using ChatGPT. However, without binding a payment method, ChatGPT's API can only be called three times per minute. When emotion recognition is involved, each question and answer requires calling the API twice, meaning it takes an average of 40 seconds to perform a single question and answer.

There are three solutions:
1. Use two ChatGPT accounts
2. Reduce the frequency of questions
3. Bind a payment method

I do not recommend the third option personally, as I have not optimized the continuous conversation logic yet. Currently, the dialogue record and question are simply sent together as a request, which can cause a sharp increase in token consumption with the increasing number of dialogue turns, making it expensive.

I haven't come up with a particularly good solution yet. I might implement the emotion recognition part with another large language model in the future, but I can't guarantee that I will definitely do it (I'm quite the procrastinator).

# Contribute to this project
Help bring Uma Musume characters to the desktop pet world (just kidding). In fact, after making the project applicable to your favorite Uma Musume characters in the advanced usage section, you can submit the additional files to this project via pull requests or any other possible methods.
### Benefits of doing this
1. Avoid reinventing the wheel, significantly improving efficiency
2. That's it

# About the proxy address
The proxy address format looks like http://127.0.0.1:1920. The specific method to check the proxy address depends on the software you are using, and you can try searching for relevant keywords to see if you can find answers online.
