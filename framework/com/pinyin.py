# -*- coding:utf-8 -*-
import os.path

class Pinyin(object):
    def __init__(self):
        self.word_dict = {}
        dict_data = os.path.dirname(os.path.abspath(__file__))+'/pinyin.data'
        if not os.path.exists(dict_data):
            raise IOError("NotFoundFile")

        with file(dict_data) as f_obj:
            for f_line in f_obj.readlines():
                try:
                    line = f_line.split('    ')
                    self.word_dict[line[0]] = line[1]
                except:
                    line = f_line.split('   ')
                    self.word_dict[line[0]] = line[1]

    def hanzi2pinyin(self, string=""):
        result = []
        if not isinstance(string, unicode):
            string = string.decode("utf-8")
        
        for char in string:
            key = '%X' % ord(char)
            chr = self.word_dict.get(key, char)
            if key in self.word_dict: chr = chr.split()[0][:-1].lower()
            result.append(chr)

        return result

    def pinyin(self, string="", split=""):
        result = self.hanzi2pinyin(string=string)
        return split.join(result)
