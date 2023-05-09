import requests
import hashlib
import json

# MD5加密函数定义
def MD5(str):
    m1 = hashlib.md5()
    m1.update(str.encode("utf-8"))
    token = m1.hexdigest()
    return token

def translate_baidu(APPID, key, q):
    salt = '143566999992'
    original_langrage = 'zh'
    to_langrage = 'jp'

    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'

    sign = MD5(APPID + q + salt + key)
    para = {"q": q, "from": original_langrage, "to": to_langrage, "appid": APPID, "salt": salt, "sign": sign}


    response = requests.get(url, params=para)
    # 结果中文是Unicode，需要进行解码
    result = response.content.decode('unicode-escape')
    # 反序列化为python对象
    result = json.loads(result)
    # 获取日文
    result = result['trans_result'][0]['dst']
    return result
