# -*- coding: utf-8 -*-
import requests
import re

def search_in_dictionary(q):
    finalrs = []
    r = requests.get('http://dict.youdao.com/w/{q}'.format(q = q))
    div = re.compile('<div class="trans-container">')
    divrs = div.search(r.text)
    endul = re.compile('</ul>')
    if (divrs is None):
        return finalrs
    ulrs = endul.search(r.text, divrs.span()[1])
    lst = r.text[divrs.span()[1]:ulrs.span()[1]]
    
    lipairs = re.compile('<li>.*<\/li>')
    lipairsrs = lipairs.findall(lst)
    if (len(lipairsrs) > 0) :
        for i, p in enumerate(lipairsrs):
            lipairsrs[i] = lipairsrs[i][4:-5]
            if (lipairsrs[i].startswith('<a')):
                return finalrs
            finalrs.append(lipairsrs[i])
    else :
        line = []
        ppairs = re.compile('k;">.*<\/span>')
        ppairsrs = ppairs.findall(lst)
        for i, p in enumerate(ppairsrs):
            line.append(lst.find(p))
            ppairsrs[i] = ppairsrs[i][4:-7] + ' '
        apairs = re.compile('on">.*<\/a>')
        apairsrs = apairs.findall(lst)
        for i, p in enumerate(apairsrs):
            pos = lst.find(p)
            apairsrs[i] = apairsrs[i][4:-4]
            for ii, l in enumerate(line):
                if (ii + 1 == len(line)):
                    ppairsrs[ii] = ppairsrs[ii] + apairsrs[i] + '; '
                    break
                if (pos < line[ii + 1]):
                    ppairsrs[ii] = ppairsrs[ii] + apairsrs[i] + '; '
                    break
        for p in ppairsrs:
            finalrs.append(p)
    return finalrs