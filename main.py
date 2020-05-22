# -*- coding: utf-8 -*-
from wox import Wox,WoxAPI
import requests
import re
from html.parser import HTMLParser

import ctypes
from ctypes import wintypes

import http.client
import hashlib
import urllib
import random
import json

appid = 'id'
secretKey = 'key'

httpClient = None
fromLang = 'auto'
target_languages = [
    'zh', 
    'en',
    'jp', 
    'kor' 
]

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
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)
        return result
    except Exception as e:
        print (e)
    finally:
        if httpClient:
            httpClient.close()

def get_translate_with_baidu(q, to):
    if appid is 'id':
        return {
            'title': '请在main.py代码中填写你的APPID和密钥',
            'subtitle': '百度翻译',
            'from': 'a',
            'to': 'b'
        }
    else :
        rs = translate_with_baudi(q, to)
        return {
            'title': rs['trans_result'][0]['dst'],
            'subtitle': '百度翻译: ' + rs['from'] + ' to ' + rs['to'],
            'from': rs['from'].strip(),
            'to': rs['to'].strip()
        }

CF_UNICODETEXT = 13

user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')

OpenClipboard = user32.OpenClipboard
OpenClipboard.argtypes = wintypes.HWND,
OpenClipboard.restype = wintypes.BOOL
CloseClipboard = user32.CloseClipboard
CloseClipboard.restype = wintypes.BOOL
EmptyClipboard = user32.EmptyClipboard
EmptyClipboard.restype = wintypes.BOOL
GetClipboardData = user32.GetClipboardData
GetClipboardData.argtypes = wintypes.UINT,
GetClipboardData.restype = wintypes.HANDLE
SetClipboardData = user32.SetClipboardData
SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
SetClipboardData.restype = wintypes.HANDLE

GlobalLock = kernel32.GlobalLock
GlobalLock.argtypes = wintypes.HGLOBAL,
GlobalLock.restype = wintypes.LPVOID
GlobalUnlock = kernel32.GlobalUnlock
GlobalUnlock.argtypes = wintypes.HGLOBAL,
GlobalUnlock.restype = wintypes.BOOL
GlobalAlloc = kernel32.GlobalAlloc
GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
GlobalAlloc.restype = wintypes.HGLOBAL
GlobalSize = kernel32.GlobalSize
GlobalSize.argtypes = wintypes.HGLOBAL,
GlobalSize.restype = ctypes.c_size_t

GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040

def paste():
    OpenClipboard(None)
    
    handle = GetClipboardData(CF_UNICODETEXT)
    pcontents = GlobalLock(handle)
    size = GlobalSize(handle)
    if pcontents and size:
        raw_data = ctypes.create_string_buffer(size)
        ctypes.memmove(raw_data, pcontents, size)
        text = raw_data.raw.decode('utf-16le').rstrip(u'\0')
    else:
        text = None

    GlobalUnlock(handle)
    CloseClipboard()
    return text

def copy(s):
    data = s.encode('utf-16le')
    OpenClipboard(None)
    EmptyClipboard()
    handle = GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, len(data) + 2)
    pcontents = GlobalLock(handle)
    ctypes.memmove(pcontents, data, len(data))
    GlobalUnlock(handle)
    SetClipboardData(CF_UNICODETEXT, handle)
    CloseClipboard()

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        if len(attrs) > 0:
            if attrs[0][1].startswith('synoid'):
                self.__buf__.append('\nsynoid\n')
            if attrs[0][1].startswith('antoid'):
                self.__buf__.append('\nantoid\n')

    def handle_endtag(self, tag):
        if tag.startswith('li') or tag.startswith('div'):
            self.__buf__.append('\n')

    def handle_data(self, data):
        if len(data) > 0:
            self.__buf__.append(data)

    def feed(self, feed, buf):
        self.__buf__ = buf
        return super().feed(feed)

parser = MyHTMLParser()

def search_in_dictionary_bing(q):
    finalrs = []
    html = requests.get('https://cn.bing.com/dict/search?q={q}'.format(q = q)).text
    hd_area_pattern = re.compile(r'<div class="hd_area">')
    hd_area_rs = hd_area_pattern.search(html)

    if (hd_area_rs is not None):
        ul_head_pattern = re.compile(r'<ul>')
        ul_head_rs = ul_head_pattern.search(html, hd_area_rs.span()[1])
        # dictionary result handle
        if (ul_head_rs.span()[0] - hd_area_rs.span()[1] < 3000):
            ul_end_pattern = re.compile(r'<\/ul>')
            ul_end_rs = ul_end_pattern.search(html, ul_head_rs.span()[1])
            
            list_html = html[ul_head_rs.span()[1]:ul_end_rs.span()[0]]
            buf = []
            parser.feed(list_html, buf)
            buf.insert(0, '\n')
            current = -1
            for i in buf:
                if i is '\n':
                    current = current + 1
                    finalrs.append({
                        'title': '',
                        'subtitle': ''
                    })
                else :
                    if finalrs[current]['subtitle'] is '':
                        finalrs[current]['subtitle'] = i.strip()
                    else :
                        finalrs[current]['title'] = finalrs[current]['title'] + i
        
        # form result hanlde
        hd_if_head_pattern = re.compile(r'<div class="hd_if">')
        hd_if_head_rs = hd_if_head_pattern.search(html, hd_area_rs.span()[1])

        finalrs = finalrs[:-1]
        if hd_if_head_rs is not None:
            hd_if_end_pattern = re.compile(r'</div>')
            hd_if_end_rs = hd_if_end_pattern.search(html, hd_if_head_rs.span()[1])
            form_list_html = html[hd_if_head_rs.span()[0]:hd_if_end_rs.span()[1]]
            form_buf = []
            parser.feed(form_list_html, form_buf)
            finalrs.append({
                'title': ''.join(form_buf).replace('\xa0\xa0', '  ').strip(),
                'subtitle': '其他形式'
            })

        # colid result handle
        wd_div_head_pattern = re.compile(r'<div class="wd_div">')
        wd_div_head_rs = wd_div_head_pattern.search(html, hd_area_rs.span()[1])

        if wd_div_head_rs is not None:
            wd_div_end_pattern = re.compile(r'<div class="df_div">')
            wd_div_end_rs = wd_div_end_pattern.search(html, wd_div_head_rs.span()[1])
            wd_div_html = html[wd_div_head_rs.span()[0]:wd_div_end_rs.span()[0]]
            wd_buf = []
            parser.feed(wd_div_html, wd_buf)
            wd_buf_str = ''.join(wd_buf).replace('同义词', '').replace('搭配', '').replace('反义词', '')
            
            colid_zoom = ''
            antoid_zoom = ''
            synoid_zoom = ''
            split_antoid = wd_buf_str.split('antoid')
            if len(split_antoid) is 2:
                colid_zoom = split_antoid[0]
                split_synoid = split_antoid[1].split('synoid')
                if len(split_synoid) is 2:
                    antoid_zoom = split_synoid[0]
                    synoid_zoom = split_synoid[1]
                else :
                    antoid_zoom = split_antoid[1]
            else:
                split_synoid = wd_buf_str.split('synoid')
                if len(split_synoid) is 2:
                    colid_zoom = split_synoid[0]
                    synoid_zoom = split_synoid[1]
                else :
                    colid_zoom = wd_buf_str
            
            colid_list = list(filter(lambda x: x != '', colid_zoom.split('\n')))
            antoid_list = list(filter(lambda x: x != '', antoid_zoom.split('\n')))
            synoid_list = list(filter(lambda x: x != '', synoid_zoom.split('\n')))

            if len(colid_list) > 0:
                for i, p in enumerate(colid_list):
                    if i % 2 is 0:
                        finalrs.append({
                            'title': "【搭配】：" + colid_list[i + 1].strip().replace(',', '，'),
                            'subtitle': p.strip()
                        })

            if len(antoid_list) > 0:
                for i, p in enumerate(antoid_list):
                    if i % 2 is 0:
                        finalrs.append({
                            'title': "【反义词】：" + antoid_list[i + 1].strip().replace(',', '，'),
                            'subtitle': p.strip()
                        })

            if len(synoid_list) > 0:
                for i, p in enumerate(synoid_list):
                    if i % 2 is 0:
                        finalrs.append({
                            'title': "【同义词】：" + synoid_list[i + 1].strip().replace(',', '，'),
                            'subtitle': p.strip()
                        })
    
    else :
        # 必应机翻
        # p1_11_head_pattern = re.compile(r'<div class="p1-11">')
        # p1_11_head_rs = p1_11_head_pattern.search(html)
        # p1_11_end_pattern = re.compile(r'</div>')
        # p1_11_end_rs = p1_11_end_pattern.search(html, p1_11_head_rs.span()[1])

        # translate_html = html[p1_11_head_rs.span()[0]: p1_11_end_rs.span()[1]]
        # translate_buf = []
        # parser.feed(translate_html, translate_buf)
        # finalrs.append({
        #     'title': ''.join(translate_buf).strip(),
        #     'subtitle': '必应机翻'
        # })

        def wq(target_language):
            return get_translate_with_baidu(q, target_language)

        baidu_tran_rs = list(map(wq, target_languages))
        for tran_rs in baidu_tran_rs:
            if tran_rs['from'] != tran_rs['to']:
                finalrs.append({
                    'title': tran_rs['title'],
                    'subtitle': tran_rs['subtitle']
                })        

    # action: copy result to clipboard
    for i, p in enumerate(finalrs):
        if finalrs[i]['subtitle'] is '必应机翻' or '百度翻译':
            params = [finalrs[i]['title']]
        else :
            params = [finalrs[i]['subtitle'] + ' ' + finalrs[i]['title']]

        finalrs[i]['JsonRPCAction'] = {
            "method": "copy2clipboard",
            #参数必须以数组的形式传过去
            "parameters": params,
        }
    return finalrs

class Main(Wox):

    def query(self, query):
      results = []
      if (len(query) == 0):
        results.append({
            "Title": "Nice Translation",
            "SubTitle": "Please enter word or sentence",
            "IcoPath":"img/app.ico",
        })
      else :
        rs = search_in_dictionary_bing(query)
        for r in rs:
          results.append({
            "Title": r['title'],
            "SubTitle": r['subtitle'],
            "IcoPath":"img/app.ico",
            "JsonRPCAction": r['JsonRPCAction']
          })
      return results
    
    def copy2clipboard(self, t):
        copy(t)


if __name__ == "__main__":
    Main()