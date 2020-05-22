#百度通用翻译API,不包含词典、tts语音合成等资源，如有相关需求请联系translate_api@baidu.com
# coding=utf-8

import http.client
import hashlib
import urllib
import random
import json

appid = 'id'  # 填写你的appid
secretKey = 'key'  # 填写你的密钥
httpClient = None
fromLang = 'auto'   #原文语种

def translate_with_baudi(q, to):

    myurl = '/api/trans/vip/translate'
    toLang = to   #译文语种
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
    salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        return result

    except Exception as e:
        print (e)
    finally:
        if httpClient:
            httpClient.close()



if __name__ == '__main__':
    print(translate_with_baudi('I was wondering how to fix that problem', 'zh'))
    print(translate_with_baudi('我在想如何解决这个问题', 'en'))
    print(translate_with_baudi('我在想如何解决这个问题', 'zh'))