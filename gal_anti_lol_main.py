from telegram_api import Galtelegram

def main():
    
    # 텔레그램 봇 인스턴스 생성
    telegram_bot = Galtelegram()

    # 텔레그램 봇 실행
    telegram_bot.tele_on()

if __name__ == "__main__":
    main()