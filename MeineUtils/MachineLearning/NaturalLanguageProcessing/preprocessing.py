import re
import json
import emot
from textsearch import TextSearch
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize

from MeineUtils.General import path_join

class TextPreProcessing():
    def __init__(self, text):
        self.text = text
        self.punctuations = ['!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']

    def sentence_tokenize(self):
        return sent_tokenize(self.text)
    
    def word_tokenize(self):
        return word_tokenize(self.text)
    
    def lowercase(self):
        return self.text.lower()

    def expand_contractions(self, lang='english'):
        contractions_dict = json.load(open(advanced_path_join(['corpus', 'contractions', f'contractions-{lang}.json'])))
        ts_basic = TextSearch("insensitive", "norm")
        ts_basic.add(contractions_dict)
        self.text = ts_basic.replace(self.text)
        return self
    
    def remove_html(self):
        self.text = re.compile('<.*?>').sub(r' ', self.text)
        return self
        
    def remove_urls(self):
        self.text = re.compile(r'https?://\S+|www\.\S+').sub(r' ', self.text)
        return self

    def remove_unwanted_chars(self, unwanted_chars=None, rule=None, count=0, flags=0):
        if unwanted_chars:
            for token in unwanted_chars:
                self.text = self.text.replace(token, "")
        if rule:
            self.text = re.sub(pattern=rule,
                               repl=' ',
                               string=self.text,
                               count=count,
                               flags=flags)
        return self

    def remove_punctuations(self, exclude=None):
        return self.remove_unwanted_chars(unwanted_chars=self.punctuations if exclude==None else [p for p in self.punctuations if p not in exclude])

    def remove_special_characters(self):
        return self.remove_unwanted_chars(rule=
                                                '[^'
                                                u'a-z'
                                                u'A-z'
                                                u'0-9'
                                                u'\s]')

    def remove_emoji(self):
        return self.remove_unwanted_chars(rule=
                                                "["
                                                u"\U0001F600-\U0001F64F"  # emoticons
                                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                                u"\U00002500-\U00002BEF"  # chinese char
                                                u"\U00002702-\U000027B0"
                                                u"\U00002702-\U000027B0"
                                                u"\U000024C2-\U0001F251"
                                                u"\U0001f926-\U0001f937"
                                                u"\U00010000-\U0010ffff"
                                                u"\u2640-\u2642"
                                                u"\u2600-\u2B55"
                                                u"\u200d"
                                                u"\u23cf"
                                                u"\u23e9"
                                                u"\u231a"
                                                u"\ufe0f"  # dingbats
                                                u"\u3030"
                                                "]+", 
                                          flags=re.UNICODE)
        
    def remove_stopwords(self, lang='english'):
        assert lang in ['english', 'vietnamese']
        STOPWORDS = set([line.replace('\n', '').strip() for line in open(advanced_path_join(['corpus' ,'stopwords', f'stopwords-{lang}.txt']), 'r').readlines()])
        self.text = " ".join([word for word in str(self.text).split() if word not in STOPWORDS])
        return self

    def convert_emoticons(self):
        dict_emoticons = dict(zip(emot.emot().emoticons(self.text)['value'], emot.emot().emoticons(self.text)['mean']))
        res_emoticons =  dict(sorted(dict_emoticons.items(), key = lambda kv:len(kv[1]), reverse=True))
        for emoticon, mean in res_emoticons.items():
            self.text = self.text.replace(emoticon, mean)
        return self

    def convert_emojis(self):
        for emoji, mean in zip(emot.emot().emoji(self.text)['value'], emot.emot().emoji(self.text)['mean']):
            self.text = self.text.replace(emoji, mean.replace(":", ""))
        return self

    def fix_format(self):
        self.text = " ".join(self.text.split()) 
        fix_spaces = re.compile(r'\s*([?!.,]+(?:\s+[?!.,]+)*)\s*')
        self.text = fix_spaces.sub(lambda x: "{} ".format(x.group(1).replace(" ", "")), self.text).strip()

        return self

    def get_text(self):
        return self.text