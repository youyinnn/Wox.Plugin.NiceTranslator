# -*- coding: utf-8 -*-
import requests
import re
from html.parser import HTMLParser

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
        p1_11_head_pattern = re.compile(r'<div class="p1-11">')
        p1_11_head_rs = p1_11_head_pattern.search(html)
        p1_11_end_pattern = re.compile(r'</div>')
        p1_11_end_rs = p1_11_end_pattern.search(html, p1_11_head_rs.span()[1])

        translate_html = html[p1_11_head_rs.span()[0]: p1_11_end_rs.span()[1]]
        translate_buf = []
        parser.feed(translate_html, translate_buf)
        finalrs.append({
            'title': ''.join(translate_buf).strip(),
            'subtitle': '必应机翻'
        })
        finalrs.append({
            'title': '翻译至中文',
            'subtitle': '百度翻译'
        })
        finalrs.append({
            'title': '翻译至英文',
            'subtitle': '百度翻译'
        })

    return finalrs

if __name__ == '__main__':
    print(search_in_dictionary_bing('I was wondering how to fix that problem'))