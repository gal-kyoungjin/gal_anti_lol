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
       
        response = requests.get(url, headers=self.request_headers)
        
        if response.status_code == 200:
            player_id = response.json()
            return player_id.get('puuid')
        else:
            return None  # API 호출 실패 시 None 반환
    
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
        
    def add_user(self, nickname, tagline):
        # 이미 존재하는 사용자인지 확인
        for user in self.user_list['users']:
            if user['nickname'] == nickname and user['tagLine'] == tagline:
                print(f"사용자 '{nickname}#{tagline}'는 이미 존재합니다.")
                return

        # 새 사용자의 UUID 가져오기
        new_puuid = self.get_uuid(nickname, tagline)
        
        if new_puuid is None:
            return f"사용자 '{nickname}#{tagline}'의 UUID를 가져오는 데 실패했습니다. 닉네임과 태그라인을 확인해주세요."
        
        # 새 사용자의 마지막 매치 ID 가져오기
        new_last_match_id = self.get_last_match(new_puuid)
        
        # 새 사용자 정보 생성
        new_user = {
            "nickname": nickname,
            "tagLine": tagline,
            "puuid": new_puuid,
            "last_match_id": new_last_match_id
        }
        
        # user_list에 새 사용자 추가
        self.user_list['users'].append(new_user)
        self.user_list['user_count'] += 1
        
        # JSON 파일 업데이트
        GalJasons.dict_to_json(self.user_list, GalTokens.user_list_path)
        
        return f"사용자 '{nickname}#{tagline}'가 성공적으로 추가되었습니다."

    def delete_user(self, nickname, tagline):
        # 삭제할 사용자 찾기
        user_to_delete = None
        for user in self.user_list['users']:
            if user['nickname'] == nickname and user['tagLine'] == tagline:
                user_to_delete = user
                break
        
        if user_to_delete:
            # 사용자 제거
            self.user_list['users'].remove(user_to_delete)
            self.user_list['user_count'] -= 1
            
            # JSON 파일 업데이트
            GalJasons.dict_to_json(self.user_list, GalTokens.user_list_path)
            
            return f"사용자 '{nickname}#{tagline}'가 성공적으로 삭제되었습니다."
        else:
            return f"사용자 '{nickname}#{tagline}'를 찾을 수 없습니다."
    
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