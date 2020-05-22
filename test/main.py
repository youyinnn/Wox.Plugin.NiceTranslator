import ydict
import ytrans


def get(text):
    rs = ydict.search_in_dictionary(text)
    if (len(rs) == 0):
        return ytrans.translate(text)
    else :
        return rs

if __name__ == '__main__':
    print(get('我'))
    print(get('hello'))
    print(get('今天天气真不错.'))
    print(get('I want to see you.'))