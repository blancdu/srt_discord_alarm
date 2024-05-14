import os
import SRT
from requests.exceptions import ConnectionError
import schedule
import time
from discord import SyncWebhook
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
SRT_ID = os.getenv("SRT_ID", "")
SRT_PW = os.getenv("SRT_PW", "")

def main():
    def get_srt():
        return SRT.SRT(
            srt_id=SRT_ID,
            srt_pw=SRT_PW,
            verbose=True
        )
    srt = get_srt()
    webhook = SyncWebhook.from_url(DISCORD_WEBHOOK_URL)
    if not all([DISCORD_WEBHOOK_URL, SRT_ID, SRT_PW]):
        print(".env 확인 필요")
        return
    
    dep = '부산'
    arr = '수서'
    date = '20240526'
    _time = '154000'
    time_limit = '201000'
    available_only = False
        
    train_available = defaultdict(lambda: '매진')

    def job():
        nonlocal srt
        try:
            print(time.strftime("%Y-%m-%d %H:%M:%S"))
            results = srt.search_train(
                dep=dep,
                arr=arr,
                date=date,
                time=_time,
                time_limit=time_limit,
                available_only=available_only
                )
        except ConnectionError:
            print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} | 커넥션이 끊어져서 새로 연결합니다.')
            srt = get_srt()
            results = srt.search_train(
                dep=dep,
                arr=arr,
                date=date,
                time=_time,
                time_limit=time_limit,
                available_only=available_only
                )
        msg = ""
        for result in results:
            train, other = result.dump().split(' 특실 ')
            general_seat = other.split(', 예약대기')[0].split(' 일반실 ')[1]
            if train_available[train] != general_seat:
                msg += f'{train} : {general_seat}\n'
                train_available[train] = general_seat
        if msg:
            msg = "변경사항 알림\n" + msg + "\n\n[SRT플레이 바로가기](https://srtplay.com/ticket/reservation)"
            print(msg)
            webhook.send(msg)

    schedule.every(5).seconds.do(job)
    print("알림시작")
    while True:
        schedule.run_pending()
        time.sleep(1)


main()