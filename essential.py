#api 사용을 위한 key 불러오기
import os

class GalTokens:
    #텔레그램 관련 토큰
    tele_token = os.environ.get('JUREN_TELE_TOKEN')
    chat_id_path = 'chat_id.json'
    user_list_path = 'user_list.json'
    
    lol_api_key = os.environ.get('LOL_API_KEY')
    
import json

class GalJasons:
    # JSON -> Dictionary
    def json_to_dict(file_name):
        with open(file_name) as file:
            return json.load(file) # json을 dictionary로 변환

    # Dictionary -> JSON
    def dict_to_json(dict, file_name):
        with open(file_name, 'w') as file:
            json.dump(dict, file, ensure_ascii = False)