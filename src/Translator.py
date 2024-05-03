import base64
import hashlib
import json
import time

import MeCab
import jaconv
import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad, pad
from fake_user_agent import user_agent
from lxml import etree

langdetect_api = 'https://fanyi.baidu.com/langdetect'
DEFAULT_VALUE = 'デフォルト値'
CONTENT_TYPE = 'application/json;charset=UTF-8'


def make_phonetic(text: str) -> dict:
    mecab_tagger = MeCab.Tagger("-chasen")
    phonetic_ = [i for i in mecab_tagger.parse(text).split('\n') if i != '' and i != 'EOS']
    phonetic_dict = {}
    for i in phonetic_:
        i = i.split('\t')[:2]
        check_ = i[-1]
        i[-1] = jaconv.kata2hira(i[-1])  # Katakana to Hiragana 片假名 ====> 平假名
        if check_ == i[0]:
            i[-1] = check_
        if i[0] == i[-1]:
            i[-1] = ''
        phonetic_dict[i[0]] = i[-1]
    return phonetic_dict


def langdetect(ocr_text: str) -> str:
    header = {'user-agent': user_agent(), 'Content-Type': CONTENT_TYPE}
    langdetect_data = {
        'query': ocr_text
    }
    langdetect_post = requests.post(langdetect_api, data=json.dumps(langdetect_data),
                                    headers=header)
    if langdetect_post.status_code == 200 and 'msg' in langdetect_post.json():
        from_lang = langdetect_post.json()['lan']
        return from_lang
    return 'jp'


class BDTranslator:
    """baidu_translator"""
    __translate_api__ = 'https://fanyi.baidu.com/ait/text/translate'

    def __init__(self):
        print(f"<{self.__class__.__name__}>:----------start----------")
        self.__translation_results__ = None
        self.__phonetic__ = {}

    def execute(self, ocr_text=DEFAULT_VALUE, from_lang='jp', to_lang='zh') -> tuple[str, dict, int, str]:
        lang_dict = {"jp": 'jp', 'zh': 'zh'}
        from_lang = lang_dict[from_lang]
        to_lang = lang_dict[to_lang]
        header = {'user-agent': user_agent(), 'Content-Type': CONTENT_TYPE}
        translate_data = {
            "query": ocr_text,
            "from": langdetect(ocr_text) if from_lang == 'auto' else from_lang,
            "to": to_lang,
            "needPhonetic": True
        }
        translate_post = requests.post(BDTranslator.__translate_api__, data=json.dumps(translate_data), headers=header)
        result = [json.loads(i[5:].replace(' ', ''))['data'] for i in translate_post.text.split('\n') if
                  i != '' and i != 'event: message']
        if translate_post.status_code == 200 and len(result) >= 6:  # 6 if Success else 3
            for i in result:
                if i['event'] == 'Translating':
                    self.__translation_results__ = i['list'][0]['dst']
                    print(fr"<{self.__class__.__name__}>Translate_Result: {self.__translation_results__}")
                    self.__phonetic__ = make_phonetic(ocr_text) if from_lang == 'jp' or langdetect(
                        ocr_text) == 'jp' else {}
                    print(fr"<{self.__class__.__name__}>Phonetic: {self.__phonetic__}")
            return self.__translation_results__, self.__phonetic__, translate_post.status_code, 'ok'
        else:
            print(fr'{self.__class__.__name__}error:status_code>{translate_post.status_code}')
            self.__translation_results__ = f'<error>http状态码:{translate_post.status_code}(网络错误或API已失效)'
            return self.__translation_results__, self.__phonetic__, translate_post.status_code, 'err'


class FXTranslator:
    __translate_api__ = 'https://fanyi.pdf365.cn/api/wordTranslateResult'
    __SIGN_KEY__ = 'FOXIT_YEE_TRANSLATE'

    def __init__(self):
        print(f"<{self.__class__.__name__}>:----------start----------")
        self.__translation_results__ = None
        self.__phonetic__ = {}

    def execute(self, ocr_text=DEFAULT_VALUE, from_lang='jp', to_lang='zh') -> tuple[str, dict, int, str]:
        lang_dict = {"jp": 'ja', 'zh': 'zh'}
        from_lang = lang_dict[from_lang]
        to_lang = lang_dict[to_lang]
        t_ = int(time.time())
        str_ = f'{t_:0<13}' + FXTranslator.__SIGN_KEY__
        md5 = hashlib.md5()  # 创建md5加密对象
        md5.update(str_.encode('utf-8'))  # 指定需要加密的字符串
        sign = md5.hexdigest()  # 加密后的字符串

        header = {'user-agent': user_agent(), 'Content-Type': CONTENT_TYPE}
        translate_params = f"""orginL={'auto' if from_lang == 'auto' else from_lang}&targetL={to_lang}&text={ocr_text}&timestamp={t_:0<13}&sign={sign}"""

        translate_post = requests.post(FXTranslator.__translate_api__, headers=header, params=translate_params)
        result = translate_post.json()
        if translate_post.status_code == 200 and 'result' in result:
            self.__translation_results__ = result['result'].replace('\n', '')
            print(fr"<{self.__class__.__name__}>Translate_Result: {self.__translation_results__}")
            self.__phonetic__ = make_phonetic(ocr_text) if from_lang == 'jp' or langdetect(
                ocr_text) == 'jp' else {}
            print(fr"<{self.__class__.__name__}>Phonetic: {self.__phonetic__}")
            return self.__translation_results__, self.__phonetic__, translate_post.status_code, 'ok'
        else:
            print(fr'{self.__class__.__name__}error:status_code>{translate_post.status_code}')
            self.__translation_results__ = f'<error>http状态码:{translate_post.status_code}(网络错误或API已失效)'
            return self.__translation_results__, self.__phonetic__, translate_post.status_code, 'err'


class YDTranslator:
    __translate_api__ = 'https://dict.youdao.com/webtranslate'
    __AESIV__ = "ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4"
    __AESKEY__ = "ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl"
    __SECRETKEY__ = "fsdsogkndfokasodnaso"

    def __init__(self):
        print(f"<{self.__class__.__name__}>:----------start----------")
        self.__translation_results__ = None
        self.__phonetic__ = {}

    def execute(self, ocr_text=DEFAULT_VALUE, from_lang='jp', to_lang='zh') -> tuple[str, dict, int, str]:
        lang_dict = {"jp": 'ja', 'zh': 'zh-CHS'}
        from_lang = lang_dict[from_lang]
        to_lang = lang_dict[to_lang]
        t_ = int(time.time() * 1000)
        str_ = f'client=fanyideskweb&mysticTime={t_}&product=webfanyi&key={YDTranslator.__SECRETKEY__}'
        md5 = hashlib.md5()  # 创建md5加密对象
        md5.update(str_.encode('utf-8'))  # 指定需要加密的字符串
        sign = md5.hexdigest()  # 加密后的字符串

        cookie = requests.get('https://fanyi.youdao.com/index.html', headers={'user-agent': user_agent()})
        header = {
            'user-agent': user_agent(),
            'cookie': f'OUTFOX_SEARCH_USER_ID={cookie.cookies.get_dict()["OUTFOX_SEARCH_USER_ID"]}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Host': 'dict.youdao.com',
            'Referer': 'https://fanyi.youdao.com/'
        }

        translate_params = f'i={ocr_text}&from={from_lang}&to={"" if from_lang == "auto" else to_lang}&dictResult=true&keyid=webfanyi&sign={sign}&client=fanyideskweb&product=webfanyi&appVersion=1.0.0&vendor=web&pointParam=client%2CmysticTime%2Cproduct&mysticTime={t_}&keyfrom=fanyi.web'
        translate_post = requests.post(YDTranslator.__translate_api__, headers=header, params=translate_params)
        decode_iv = hashlib.md5(YDTranslator.__AESIV__.encode(encoding='utf-8')).digest()
        decode_key = hashlib.md5(YDTranslator.__AESKEY__.encode(encoding='utf-8')).digest()
        aes = AES.new(decode_key, AES.MODE_CBC, decode_iv)
        data_new = base64.urlsafe_b64decode(translate_post.text)
        if len(data_new) % 16 != 0:
            data_new = pad(data_new, AES.block_size)
        result = unpad(aes.decrypt(data_new), AES.block_size).decode('utf-8')
        result = json.loads(result)
        if translate_post.status_code == 200 and result['code'] == 0:
            rls = ''
            for i in result["translateResult"][0]:
                rls += i['tgt']
            self.__translation_results__ = rls
            print(fr"<{self.__class__.__name__}>Translate_Result: {self.__translation_results__}")
            self.__phonetic__ = make_phonetic(ocr_text) if from_lang == 'jp' or langdetect(
                ocr_text) == 'jp' else {}
            print(fr"<{self.__class__.__name__}>Phonetic: {self.__phonetic__}")
            return self.__translation_results__, self.__phonetic__, translate_post.status_code, 'ok'
        else:
            print(fr'{self.__class__.__name__}error:status_code>{translate_post.status_code}')
            self.__translation_results__ = f'<error>http状态码:{translate_post.status_code}(网络错误或API已失效)'
            return self.__translation_results__, self.__phonetic__, translate_post.status_code, 'err'


class MiraiTranslator:
    __translate_api__ = 'https://trial.miraitranslate.com/trial/api/translate.php'

    def __init__(self):
        print(f"<{self.__class__.__name__}>:----------start----------")
        self.__translation_results__ = None
        self.__phonetic__ = {}

    def execute(self, ocr_text=DEFAULT_VALUE, from_lang='jp', to_lang='zh') -> tuple[str, dict, int, str]:
        lang_dict = {"jp": 'ja', 'zh': 'zh'}
        from_lang = lang_dict[from_lang]
        to_lang = lang_dict[to_lang]
        header = {'user-agent': user_agent(), 'Content-Type': CONTENT_TYPE}
        tran = requests.get('https://miraitranslate.com/trial/', header)
        cookie = tran.cookies.get_dict()
        html = etree.HTML(tran.text)
        tran = html.xpath(r'/html/head//script[5]/text()')[0].replace('\n', '').replace(' ', '').split('=')[-1][1:-2]

        header['cookie'] = f"translate_session={cookie['translate_session']}"
        translate_data = {
            "input": f"{ocr_text}",
            "source": f"{from_lang}",
            "target": f"{to_lang}",
            "filter_profile": "nmt",
            "tran": f"{tran}",
            "zt": False
        }

        translate_post = requests.post(MiraiTranslator.__translate_api__, headers=header,
                                       data=json.dumps(translate_data))
        result = translate_post.json()
        if translate_post.status_code == 200 and result['status'] == 'success':
            self.__translation_results__ = result["outputs"][0]["output"][0]["translation"]
            print(fr"<{self.__class__.__name__}>Translate_Result: {self.__translation_results__}")
            self.__phonetic__ = make_phonetic(ocr_text) if from_lang == 'jp' or langdetect(
                ocr_text) == 'jp' else {}
            print(fr"<{self.__class__.__name__}>Phonetic: {self.__phonetic__}")
            return self.__translation_results__, self.__phonetic__, translate_post.status_code, 'ok'
        else:
            print(fr'{self.__class__.__name__}error:status_code>{translate_post.status_code}')
            self.__translation_results__ = f'<error>http状态码:{translate_post.status_code} (网络错误或API已失效)'
            return self.__translation_results__, self.__phonetic__, translate_post.status_code, 'err'


def translation_source_selector(index):
    __dict = {
        0: BDTranslator,
        1: FXTranslator,
        2: YDTranslator,
        3: MiraiTranslator,
    }
    return __dict[index]()


__all__ = ['translation_source_selector']
