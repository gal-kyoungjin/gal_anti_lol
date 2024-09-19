import requests
from urllib import parse # 한글

from essential import GalTokens
from essential import GalJasons

class Gallol:    
    def __init__(self):

        self.api_key = GalTokens.lol_api_key
        
        self.request_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com"
        }
        
        self.user_list = GalJasons.json_to_dict(GalTokens.user_list_path)
        
        self.init_uuid()
        self.init_last_match()
    
    def get_last_match(self, puuid):

        url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1&api_key={self.api_key}"
        matchInfo = requests.get(url, headers = self.request_headers).json();
        
        return matchInfo
    
    def get_uuid(self, user_nickname, user_tagline):

        encodedName = parse.quote(user_nickname)
        url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encodedName}/{user_tagline}?api_key={self.api_key}"
        player_id = requests.get(url, headers=self.request_headers).json()
       
        return player_id['puuid']
    
    def init_uuid(self):

        for i in range(self.user_list['user_count']):
            user = self.user_list['users'][i]
            new_puuid = self.get_uuid(user['nickname'], user['tagLine'])
            self.user_list['users'][i]['puuid'] = new_puuid
    
        # JSON 파일 업데이트
        GalJasons.dict_to_json(self.user_list, GalTokens.user_list_path)
        
    def init_last_match(self):

        for i in range(self.user_list['user_count']):
            user = self.user_list['users'][i]
            new_last_match_id = self.get_last_match(user['puuid'])
            self.user_list['users'][i]['last_match_id'] = new_last_match_id
    
        # JSON 파일 업데이트
        GalJasons.dict_to_json(self.user_list, GalTokens.user_list_path)

    async def update_last_match(self):
        alarm_list = [0] * self.user_list['user_count']
        
        for i in range(self.user_list['user_count']):
            user = self.user_list['users'][i]
            new_last_match_id = self.get_last_match(user['puuid'])
            
            if new_last_match_id != user['last_match_id']:
                alarm_list[i] = 1  # 다른 경우 alarm_list를 1로 변경
            
            self.user_list['users'][i]['last_match_id'] = new_last_match_id
            
        print(alarm_list)
        # JSON 파일 업데이트
        GalJasons.dict_to_json(self.user_list, GalTokens.user_list_path)
        
        return self.user_list['user_count'], alarm_list