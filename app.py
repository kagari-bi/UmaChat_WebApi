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

# 检查代理设置是否存在并设置代理
if config.has_section('proxy'):
    if config.has_option('proxy', 'http_proxy'):
        os.environ['http_proxy'] = config.get('proxy', 'http_proxy')
    if config.has_option('proxy', 'https_proxy'):
        os.environ['https_proxy'] = config.get('proxy', 'https_proxy')
    if config.has_option('proxy', 'all_proxy'):
        os.environ['ALL_PROXY'] = config.get('proxy', 'all_proxy')

# 设置参数
model_path = "models/Riceshower/G_latest.pth"
config_path = "models/Riceshower/config.json"
vits_language = "日本語"
text = ""
spk = "RiceShower"
noise_scale = 0.6
noise_scale_w = 0.668
length_scale = 1

app = FastAPI()

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
    
    emotion_classification="请帮我分析当前的对话发生时，回答者的状态。只需要告诉我状态，不需要任何解释和标点符号。可供选择的状态如下："
    if os.path.exists(f"action_mapping_table/{charaname}.json"):
        filepath = f"action_mapping_table/{charaname}.json"
    else:
        filepath = "action_mapping_table/example.json"
    with open(filepath, "r", encoding="utf-8") as file:
        emotions_dict = json.load(file)
    # 遍历字典中的键并拼接到字符串后面
    for i in emotions_dict.keys():
        emotion_classification = emotion_classification+"\n"+i

    
    if os.path.exists(f"prompt/{charaname}.txt"):
        with open(f"prompt/{charaname}.txt", 'r', encoding='utf-8') as file:
            prompt = file.read()
    else:
        with open(f"prompt/NishinoFlower.txt", 'r', encoding='utf-8') as file:
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
    action,expression,expression_weight = emotion_to_action(emotion,charaname,emotions_dict)

    if detect_language(user_question) == "Chinese":
        #加载称谓替换表
        with open("prompt/appellation.json", "r", encoding="utf-8") as file:
            appellation_dict = json.load(file)
        text_response = assistant_answer

        if charaname in appellation_dict:
            assistant_answer = assistant_answer.replace(appellation_dict[charaname]["中文自称"], appellation_dict[charaname]["日文自称"])
            assistant_answer = assistant_answer.replace(appellation_dict[charaname]["对玩家的中文称呼"], appellation_dict[charaname]["对玩家的日文称呼"])
            assistant_answer = assistant_answer.replace(appellation_dict[charaname]["中文的打招呼方式"], appellation_dict[charaname]["日文的打招呼方式"])
        else:
            pass
        assistant_answer = assistant_answer.replace("？","[？]")
        assistant_answer = translate_baidu(APPID, key, assistant_answer)
        assistant_answer = assistant_answer.replace("[？]","？")
        assistant_answer = assistant_answer.replace("。","。 ")
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
