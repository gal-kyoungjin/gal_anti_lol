##Essential 함수들
from essential import GalTokens
from essential import GalJasons

##비동기 관련 함수
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

##텔레그램 관련 함수
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from lol_api import Gallol
 
class Galtelegram:    
    def __init__(self):
        #가장 최근 chat_id 불러오기
        self.current_chat_id = GalJasons.json_to_dict(GalTokens.chat_id_path)

        #telegram api load
        self.app = Application.builder().token(GalTokens.tele_token).build()
        
        #스케줄러 생성
        self.scheduler = AsyncIOScheduler(timezone='Asia/Seoul')
        
        self.lol = Gallol()
                
        
    async def lol_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        msg = ""
        msg += "롤 경보기 채팅방 설정"+ "\n"
        msg += "도움말: /lol"+ "\n"
        msg += "추가: /add 닉네임 태그라인"+ "\n"
        msg += "삭제: /delete 닉네임 태그라인"+ "\n"
        msg += "사용자 목록: /user"+ "\n"
        self.current_chat_id = update.effective_message.chat_id
        GalJasons.dict_to_json(self.current_chat_id, GalTokens.chat_id_path)

        await context.bot.send_message(chat_id = update.effective_message.chat_id, text=msg, parse_mode='HTML')

    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        args = context.args
        if len(args) != 2:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="올바른 형식: /add <닉네임> <태그라인>"
            )
            return

        nickname, tagline = args
        result = self.lol.add_user(nickname, tagline)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result
        )
        
    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        args = context.args
        if len(args) != 2:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="올바른 형식: /delete <닉네임> <태그라인>"
            )
            return

        nickname, tagline = args
        result = self.lol.delete_user(nickname, tagline)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result
        )
        
    async def user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_list = self.lol.user_list
        if user_list['user_count'] == 0:
            message = "현재 등록된 사용자가 없습니다."
        else:
            message = "현재 등록된 사용자 목록:\n"
            for user in user_list['users']:
                message += f"- {user['nickname']}#{user['tagLine']}\n"
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
    
    async def run_every_minute(self):
        # 10분마다 실행할 작업 구현
        user_count, alarm_list = await self.lol.update_last_match()
        
        for i in range(user_count):
            if alarm_list[i] == 1:
                user = self.lol.user_list['users'][i]
                message = f"{user['nickname']}님이 새로운 게임을 플레이했습니다!"
                
                await self.app.bot.send_message(chat_id = self.current_chat_id, text=message, parse_mode='HTML')
         
    def tele_on(self):
        """Run bot."""
        # Create the Application and pass it your bot's token.
        
        self.app.add_handler(CommandHandler("lol", self.lol_command))
        self.app.add_handler(CommandHandler("add", self.add_command))  # 새로운 핸들러 추가
        self.app.add_handler(CommandHandler("delete", self.delete_command))  # 새로운 핸들러 추가
        self.app.add_handler(CommandHandler("user", self.user_command))  # 새로운 핸들러 추가
        
        #30분마다 실행
        
        
        self.scheduler.add_job(self.run_every_minute, 'cron', minute='*', id='every_1_min')
        self.scheduler.start()
        
         # 애플리케이션을 초기화하고 시작
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)