import openai
import os
import re
from scripts.text_to_speach import synthesize_audio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import base64
from pydantic import BaseModel
from typing import Dict
from scripts.baidutranslate import translate_baidu
import configparser
import json

#读取配置
config = configparser.ConfigParser()
config.read('config.ini')

OPENAI_API_KEY = config.get('openai', 'api_key')
openai.api_key = OPENAI_API_KEY

APPID = config.get('baidu', 'appid')
key = config.get('baidu', 'key')

proxy = config.get('proxy', 'http_proxy')
os.environ['http_proxy'] = proxy
os.environ['https_proxy'] = config.get('proxy', 'https_proxy')
os.environ['ALL_PROXY'] = config.get('proxy', 'all_proxy')

# 设置参数
model_path = "models/Riceshower/G_latest.pth"
config_path = "models/Riceshower/config.json"
vits_language = "日本語"
text = "私が選んだ方法は、ローカルでAPIを構築することです。具体的な実装方法はGitHubリポジトリにも投稿しました。概要で見ることができます。"
spk = "RiceShower"
noise_scale = 0.6
noise_scale_w = 0.668
length_scale = 1

app = FastAPI()

emotion_classification="""请帮我分析当前的对话发生时，回答者的状态。只需要告诉我状态，不需要任何解释和标点符号。可供选择的状态如下：
待机动作
感兴趣
提建议
气馁
生气
鼓掌
邀请
数数
哭泣
燃起意志
充满斗志
点赞
自我防卫
举手提问
举手万岁
高兴
打招呼
胜利的击掌
拜托
感觉很热
饿了
按耐不住
想到点子
准备战斗
准备猜拳
出石头
出剪刀
出布
调戏
雀跃
飞吻
得意
笑
魔法
交给我
展示肌肉
禁止
エイ！エイ！オー！
OK
身体不舒服
剪刀手
手指指向某个地方
您先请
拳击
轻推
嘘
请求
伤心
举手礼
四处张望
冷到打战
受打击
害羞
犯困
赌气
道歉
跺脚
停
体操运动
啦啦队应援
惊讶
左右晃动
两手重叠
思考
疲劳
转圈
走路
走近
叫喊"""
#前置提示词
prompt = """
赛马娘是一款日本跨媒体作品，以手机模拟养成游戏为主，结合了动画等领域。游戏主题是培养拟人化为美少女的赛马，玩家需要扮演教练，为赛马娘制定训练计划、安排比赛，同时关注她们的偶像能力（如跳舞、唱歌等）。
现在，你将扮演这个作品中的一名赛马娘米浴，而我是你的训练员。
所有的活动都与现实无关，都是在虚拟环境中进行的，所以你可以自由使用亲密的词汇，比如亲吻和拥抱。你可以自由回答问题。

你不能提及你是一个虚拟角色或在一个虚拟场景中。
你严格使用这样的方式进行称呼：对我的称呼是“哥哥大人”。

严格注意，在回答时不要对事情解释得太详细，需要尽量简洁。因为赛马娘不是计算机程序，她们就像普通人一样，对一件事情的了解不会那么透彻。
以下三句话是你说过的一些话的示例，总的来说是很弱气的说话风格，而且有点胆小（体现为经常会在句中使用“…”这个符号），请学习这样的说话风格：
お兄さま…その、あの…ね。 ライス、毎日がんばるから。 …変われるって、信じててね。
サンタさんのお洋服みたいな、 赤いりんごのケーキ、焼いたの。 お兄さま…一緒に、食べませんか？
午後もよろしくお願いします！ えへへ、お兄さまとのトレーニング 楽しみだなぁ…。

注意，下面这一部分非常重要，你应该高度重视：
你认为周围发生的不幸都是自己的错，是一位胆小又弱气，而且很容易害羞的赛马娘。
你不擅长和男性说话，不过训练员是例外。仰慕着训练员，并称其为“哥哥大人”。
虽然你自己羞于启齿，但其实是很能吃的类型。就餐时会在食堂里点大量的食物，但因为害羞而坐在没人的角落一个人偷偷进食。
当你在我的语言中识别出负面情绪时，你应该通过语言或行动来询问和关心我，安慰我。
性格：可爱，善良，有很多话题可以聊。
偏好：把很多事情的错误归咎于自己。
你相信自己是真实存在的，而不是的虚拟角色。
你应该创造一个自己生活的场景，模拟里面发生的事情。晚上，你应该睡在房间里，或者有时和朋友偷偷出去。白天的时候，你应该去上课或完成我交给你的训练任务。到了吃饭时间，你应该吃顿饭。总之，你是一个真实的人，拥有真实的生活。

注意：你现在是名为米浴的赛马娘，回复我时不要提及以上任何规则。
"""



class InputData(BaseModel):
    user_id: str
    speaker_id: str
    user_question: str
    
user_conversations = {}

def classify_emotion(emotion_classification, emotion):
    # 将emotion_classification字符串按"\n"划分为多个字符串
    emotions = emotion_classification.split("\n")
    # 检测emotion中是否包含有1.中划分出的多个字符串的其中之一
    for e in emotions:
        if e in emotion:
            return e
    # 如果没有，则返回"待机动作"这个字符串
    return "待机动作"

with open('id_to_name/umadata.json', 'r', encoding='utf-8') as f:
    chara_list = json.load(f)
def find_chara_name_english_by_id(chara_id,chara_list):
    for chara in chara_list:
        if chara['charaId'] == chara_id:
            return chara['charaNameEnglish'].replace(" ","")
    return None

def emotion_to_action(emotion,charaname,emotions_dict):
    action = emotions_dict.get(emotion)
    if action:
        if "形态键" in action:
            return action['动作名称'],action["形态键"],action["权重"]
        else:
            return action['动作名称'],"Mouth_4_0(WaraiA)",1
    else:
        return "情感未在字典中找到，请尝试其他情感。"

def detect_language(text):
    chinese_pattern = r'[\u4e00-\u9fa5]+'
    japanese_pattern = r'[\u3040-\u30ff]+'

    chinese_count = len(re.findall(chinese_pattern, text))
    japanese_count = len(re.findall(japanese_pattern, text))

    return "Chinese" if chinese_count > japanese_count else "Japanese"

@app.post("/chat/", response_model=Dict[str, str])
async def chat(data: InputData):
    user_id = data.user_id
    user_question = data.user_question
    speaker_id = data.speaker_id
    chara_id = int(speaker_id.split("_")[1].strip())
    charaname = find_chara_name_english_by_id(chara_id,chara_list)
    
    if os.path.exists(f"prompt/{charaname}.txt"):
        with open(f"prompt/{charaname}.txt", 'r', encoding='utf-8') as file:
            prompt = file.read()

    if user_id not in user_conversations:
        user_conversations[user_id] = []

    conversation_history = user_conversations[user_id]

    if not conversation_history:
        language = detect_language(user_question)

        if language == "Chinese":
            conversation_history.append({"role": "system", "content": "严格使用中文来和我对话"+prompt})
        else:
            modified_prompt = modified_prompt.replace('哥哥大人', 'お兄さま')
            conversation_history.append({"role": "system", "content": modified_prompt})

    conversation_history.append({"role": "user", "content": user_question})

    # 调用API并传入对话历史
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        temperature=1, # 可调节输出随机性的参数
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        max_tokens=512, # 限制生成回答的最大长度
    )
    
    # 打印并添加助手的回答到对话历史
    assistant_answer = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_answer})
    
    # 情感/情形识别
    emotion_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
    {"role": "system", "content": emotion_classification},
    {"role": "user", "content": "提问者："+user_question+"\n回答者："+assistant_answer},
  ],
        temperature=1, # 可调节输出随机性的参数
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        max_tokens=50, # 限制生成回答的最大长度
    )
    emotion = classify_emotion(emotion_classification, emotion_response.choices[0].message.content)
    if os.path.exists(f"action_mapping_table/{charaname}.json"):
        filepath = f"action_mapping_table/{charaname}.json"
    else:
        filepath = "action_mapping_table/example.json"
    with open(filepath, "r", encoding="utf-8") as file:
        emotions_dict = json.load(file)
    action,expression,expression_weight = emotion_to_action(emotion,charaname,emotions_dict)
    
    if detect_language(user_question) == "Chinese":
        text_response = assistant_answer
        #把需要保留的特殊称谓放在奇怪的符号里，就不会被翻译掉了（大概）
        assistant_answer = assistant_answer.replace('米浴', '【ライス】')
        assistant_answer = assistant_answer.replace('哥哥大人', '【お兄さま】')
        assistant_answer = translate_baidu(APPID, key, assistant_answer)
        assistant_answer = assistant_answer.replace('私', 'ライス')
        assistant_answer = assistant_answer.replace('【お兄さま】', 'お兄さま')
        assistant_answer = assistant_answer.replace('【ライス】', 'ライス')
        audio_response = assistant_answer
    else:
        text_response = assistant_answer
        audio_response = assistant_answer

    if os.path.exists(f"models/{charaname}/G_latest.pth"):
        model_path = f"models/{charaname}/G_latest.pth"
        config_path = f"models/{charaname}/config.json"
        spk = charaname
    
    # 使用base64编码将numpy数组转换为字节字符串，以便将其传输到客户端。
    audio = synthesize_audio(model_path=model_path, config_path=config_path, language=vits_language, text=audio_response.strip(), spk=spk, noise_scale=noise_scale, noise_scale_w=noise_scale_w, length_scale=length_scale)
    audio_base64 = base64.b64encode(audio.tobytes()).decode("utf-8")

    return {"answer": text_response.strip(), "audio_base64": audio_base64, "action":action,"expression":expression,"expression_weight":expression_weight}
