import datetime
import os.path
import time
import os

import tweepy

from util import read_json
from lostark import get_adventure_island, get_weekly_challenge_contents


class TwitterBot:
    def __init__(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        self.data = read_json(path + "/data/key.json")["twitter"]
        self.lostark = read_json(path + "/data/key.json")["lostark"]

        self.daily_message = [
            "\n".join([" 월요일 컨텐츠>", "- 카오스 게이트", "- 모험섬"]),
            "\n".join([" 화요일 컨텐츠>", "- 필드보스", "- 유령선", "- 모험섬"]),
            "\n".join([" 로요일 컨텐츠>", "- 모험섬", "- 툴루비크 전장"]),
            "\n".join([" 목요일 컨텐츠>", "- 카오스 게이트", "- 유령선", "- 모험섬"]),
            "\n".join([" 금요일 컨텐츠>", "- 필드보스", "- 모험섬"]),
            "\n".join([" 토요일 컨텐츠>", "- 카오스 게이트", "- 유령선", "- 모험섬(오전/오후)", "- 툴루비크 전장"]),
            "\n".join([" 일요일 컨텐츠>", "- 카오스 게이트", "- 필드보스", "- 모험섬(오전/오후)", "- 툴루비크 전장"]),
        ]

    def run(self):
        while True:
            time.sleep(1)

            now = datetime.datetime.now()

            if now.hour == 8 and now.minute == 0 and now.second == 0:
                self.upload_infoes()

    def test(self):
        self.upload_infoes(test=True)

    def get_client(self):
        client = tweepy.Client(
            consumer_key=self.data["api_key"],
            consumer_secret=self.data["api_key_secret"],
            access_token=self.data["access_token"],
            access_token_secret=self.data["access_token_secret"]
        )
        return client

    def get_api(self):
        auth = tweepy.OAuthHandler(
            consumer_key=self.data["api_key"],
            consumer_secret=self.data["api_key_secret"]
        )

        auth.set_access_token(
            key=self.data["access_token"],
            secret=self.data["access_token_secret"]
        )

        return tweepy.API(auth)

    def get_daily_contents_message(self, day):
        return self.daily_message[day]

    def get_weekly_contents_message(self):
        media = get_weekly_challenge_contents("Bearer " + self.lostark["api_key"])
        message = "주간 도전 컨텐츠 안내>"

        return media, message

    def get_adventure_island_infoes(self):
        media = get_adventure_island("Bearer " + self.lostark["api_key"])

        return media

    def upload_infoes(self, test=False):
        now = datetime.datetime.now()
        day = now.weekday()

        client = self.get_client()

        # 일간 정보
        message = now.strftime('%Y-%m-%d') + self.get_daily_contents_message(day) + "\n\n등장하는 모험섬 정보>"
        media = self.get_adventure_island_infoes()

        response = self.post_with_image(client, message, media, None)

        # 수요일이면 추가의 정보를 업로드함
        if day == 2 or test:
            media, message = self.get_weekly_contents_message()
            _ = self.post_with_image(client, message, media, response)

    def post_with_image(self, client, message, image_path, reply_id=None):
        api = self.get_api()
        media = api.media_upload(image_path)

        response = client.create_tweet(
            text=message,
            media_ids=[media.media_id],
            in_reply_to_tweet_id=reply_id
        )

        print(response.data)
        print(f"다음의 내용을 트윗합니다.\n{message}, {media.media_id}")

        return response.data["id"]
