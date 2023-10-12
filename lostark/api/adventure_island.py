import os
import platform
import datetime

from PIL import Image, ImageDraw, ImageFont
import requests

from lostark.api.api import get_island_info

path = os.path.join(os.path.dirname(os.path.abspath(__file__)))

test = False

# if test:
#     title_font = ImageFont.truetype("C:/USERS/DEV2/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/NANUMBARUNGOTHICBOLD.TTF",
#                                     size=40)
#     time_font = ImageFont.truetype("C:/USERS/DEV2/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/NANUMBARUNGOTHIC.TTF", size=32)
#     island_font = ImageFont.truetype("C:/USERS/DEV2/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/NANUMBARUNGOTHIC.TTF",
#                                      size=28)
#     island_type_font = ImageFont.truetype(
#         "C:/USERS/DEV2/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/NANUMBARUNGOTHICBOLD.TTF",
#         size=28)

if "Window" in platform.platform():
    title_font = ImageFont.truetype(path + "/font/NANUMBARUNGOTHICBOLD.TTF", size=40)
    time_font = ImageFont.truetype(path + "/font/NANUMBARUNGOTHIC.TTF", size=32)
    island_font = ImageFont.truetype(path + "/font/NANUMBARUNGOTHIC.TTF", size=28)
    island_type_font = ImageFont.truetype(path + "/font/NANUMBARUNGOTHICBOLD.TTF", size=28)
elif "Linux" in platform.platform():
    import glob

    font_dir = "/usr/share/fonts/truetype/nanum"
    ttf_files = glob.glob(f"{font_dir}/*.ttf")

    title_font = ImageFont.truetype(ttf_files[-4], size=40)
    time_font = ImageFont.truetype(ttf_files[-1], size=32)
    island_font = ImageFont.truetype(ttf_files[-1], size=28)
    island_type_font = ImageFont.truetype(ttf_files[-4], size=28)


def filter_data(auth):
    data = get_island_info(auth)

    today_island = []

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    for island in data:
        start_times = island["StartTimes"]

        if start_times is None:
            continue

        # 오늘의 모험섬인지 확인
        for start_time in start_times:
            words = start_time.split("T")
            if words[0] == today:
                today_island.append({
                    "name": island["ContentsName"],
                    "icon": island["ContentsIcon"],
                    "time": words[1].split(":")[0]  ## hour
                })
                break

        # 오늘의 모험섬 보상인지 확인
        reward_items = island["RewardItems"]

        if reward_items is None:
            continue

        for reward_item in reward_items:
            # 공통 보상 제외
            ignore_item = ["인연의 돌"]
            if reward_item["Name"] in ignore_item:
                continue

            # 기본 보상 제외
            if reward_item["StartTimes"] is not None:
                exception = False
                exception_reward = ["비밀지도", "모험물", "수호", "풍요"]

                for reward in exception_reward:
                    if reward in reward_item["Name"]:
                        exception = True

                if exception:
                    if "reward" not in today_island[len(today_island) - 1].keys():
                        today_island[len(today_island) - 1]["reward"] = []

                    today_island[len(today_island) - 1]["reward"].append({
                        "name": reward_item["Name"],
                        "icon": reward_item["Icon"],
                        "grade": reward_item["Grade"]
                    })

            if reward_item["StartTimes"] is not None:
                start_times = reward_item["StartTimes"]

                for start_time in start_times:
                    words = start_time.split("T")
                    if words[0] == today:
                        if "reward" not in today_island[len(today_island) - 1].keys():
                            today_island[len(today_island) - 1]["reward"] = []

                        today_island[len(today_island) - 1]["reward"].append({
                            "name": reward_item["Name"],
                            "icon": reward_item["Icon"],
                            "grade": reward_item["Grade"]
                        })
                        break

    return today_island


def get_image(icon: str):
    return Image.open(requests.get(icon, stream=True).raw)


# 일반 고급 희귀 영웅 전설 유물 고대 에스더
# 회색 초록 파랑 보라 금색 빨강 하양 하늘색
grade_color = {
    "일반": (78, 80, 77),
    "고급": (56, 74, 34),
    "희귀": (15, 49, 74),
    "영웅": (65, 28, 79),
    "전설": (115, 78, 25),
    "유물": (164, 69, 15),
    "고대": (248, 228, 178),
    "에스더": (122, 245, 247)
}


def get_item_color(grade: str):
    if grade in grade_color.keys():
        return grade_color[grade]
    else:
        return grade_color["일반"]


window_size = (1024, 512)
icon_size = (64, 64)

item_color = (50, 50, 50)

background_color = (0, 0, 0)
title_back_color = (32, 32, 32)

# background_color = (32, 32, 32)
# title_back_color = (0, 0, 0)

font_color = (255, 255, 255)
title_color = (255, 210, 40)
icon_gap = 4  # 아이콘 사이의 공백
content_gap = 32  # 컨텐츠 사이의 공백
max_reward_num = 8
margin = 4


def make_rewards_box(rewards):
    width, height = icon_size[0] * len(rewards) + icon_gap * (len(rewards) - 1), icon_size[1]
    reward_box_size = (width, height)
    reward_box = Image.new('RGBA', reward_box_size, background_color)

    for i in range(len(rewards)):
        reward = rewards[i]

        grade = reward["grade"]
        icon = reward["icon"]

        reward_back = Image.new('RGBA', icon_size, get_item_color(grade))

        reward_image = get_image(icon)
        reward_image = reward_image.resize(icon_size)

        start_x, start_y = (icon_size[0] + icon_gap) * i, 0
        reward_image = Image.alpha_composite(reward_back, reward_image)
        reward_box.paste(reward_image, (start_x, start_y), reward_image)

    return reward_box


def make_island_box(item):
    width, height = 1024 - icon_size[0] * 2 + margin * 2, icon_size[1] + margin * 2
    island_box = Image.new('RGBA', (width, height), background_color)

    # island
    island = item["name"]
    island_image = get_image(item["icon"])
    island_image = island_image.resize(icon_size)

    island_box.paste(island_image, (margin, margin))

    drawable_image = ImageDraw.Draw(island_box)

    # text ( island_type )
    island_type = "섬"

    rewards = item["reward"]
    for reward in rewards:
        if reward["name"] == "골드":
            island_type = "골드섬"
            break

        elif reward["name"] == "대양의 주화 상자":
            island_type = "주화섬"
            break

        elif "카드 팩" in reward["name"]:
            island_type = "카드섬"
            break

        elif "실링" in reward["name"]:
            island_type = "실링섬"
            break

    _w, _h = drawable_image.textsize(island_type, font=island_type_font)
    x, y = icon_size[0] + icon_gap * 4 + margin, (height - _h) / 2
    drawable_image.text((x, y), island_type, fill=title_color, font=island_type_font)

    # text ( island_name )
    w, h = drawable_image.textsize(island, font=island_font)
    x, y = x + _w + icon_gap * 3, (height - h) / 2
    drawable_image.text((x, y), island, fill=font_color, font=island_font)

    # reward
    rewards_box = make_rewards_box(rewards)
    start_x, start_y = width - icon_size[0] * len(rewards) - icon_gap * (len(rewards) - 1) - margin, margin
    island_box.paste(rewards_box, (start_x, start_y), rewards_box)

    return island_box


def make_island_boxes(island_rewards_infoes):
    width, height = 1024 - icon_size[0] * 2 + margin * 2, icon_size[1] * 3 + content_gap * 2 + margin * 6
    island_boxes = Image.new('RGBA', (width, height))

    for i in range(len(island_rewards_infoes)):
        item = island_rewards_infoes[i]

        island_box = make_island_box(item)
        start_x, start_y = 0, (icon_size[1] + content_gap) * i
        island_boxes.paste(island_box, (start_x, start_y), island_box)

    return island_boxes


def make_island_content(island_rewards_infoes, time_text):
    width, height = 1024 - icon_size[0] * 2 + margin * 2, icon_size[1] * 3 + content_gap * 2 + icon_size[
        1] * 2 + margin * 6
    island_content = Image.new('RGBA', (width, height))

    # text
    drawable_image = ImageDraw.Draw(island_content)
    w, h = drawable_image.textsize(time_text, font=time_font)
    x, y = (width - w) / 2, h / 2
    drawable_image.text((x, y), time_text, fill=font_color, font=time_font)

    # image
    island_boxes = make_island_boxes(island_rewards_infoes)
    start_x, start_y = 0, icon_size[1] + content_gap
    island_content.paste(island_boxes, (start_x, start_y), island_boxes)

    return island_content


def make_daily_adventure_island(island_rewards_infoes, date_text):
    daily_adventure_island = None

    if len(island_rewards_infoes) == 6:
        daily_adventure_island_content = Image.new('RGBA', (window_size[0], window_size[1] * 2), title_back_color)

        # title
        drawable_image = ImageDraw.Draw(daily_adventure_island_content)
        w, h = drawable_image.textsize(date_text, font=title_font)
        x, y = (window_size[0] - w) / 2, h
        drawable_image.text((x, y), date_text, fill=title_color, font=title_font)

        group1 = list(filter(lambda e: e["time"] == '09', island_rewards_infoes))
        island_content_1 = make_island_content(group1, "09:00/11:00/13:00")
        start_x, start_y = icon_size[0] - margin, icon_size[1] + content_gap
        daily_adventure_island_content.paste(island_content_1, (start_x, start_y), island_content_1)

        group2 = list(filter(lambda e: e["time"] == '19', island_rewards_infoes))
        island_content_2 = make_island_content(group2, "19:00/21:00/23:00")
        start_x, start_y = icon_size[0] - margin, icon_size[1] * 7 + content_gap * 4
        daily_adventure_island_content.paste(island_content_2, (start_x, start_y), island_content_2)

    else:
        daily_adventure_island_content = Image.new('RGBA', window_size, title_back_color)

        # title
        drawable_image = ImageDraw.Draw(daily_adventure_island_content)
        w, h = drawable_image.textsize(date_text, font=title_font)
        x, y = (window_size[0] - w) / 2, h
        drawable_image.text((x, y), date_text, fill=title_color, font=title_font)

        island_content = make_island_content(island_rewards_infoes, "11:00/13:00/19:00/21:00/23:00")
        start_x, start_y = icon_size[0] - margin, icon_size[1] + content_gap
        daily_adventure_island_content.paste(island_content, (start_x, start_y), island_content)

    return daily_adventure_island_content


def get_adventure_island(auth):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    link = f'/home/itjeong/2023_Dedenne-Bot_v2/result/today/{date}.png'

    if not os.path.isfile(link):
        island_info = filter_data(auth)

        image = make_daily_adventure_island(island_info, f"{date} 모험섬 일정")
        # link = f'./adventure_island/data/today/{date}.png'
        # link = f'D:/{date}.png'
        image.save(link)

    return link


if __name__ == "__main__":
    link = get_adventure_island(
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyIsImtpZCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyJ9.eyJpc3MiOiJodHRwczovL2x1ZHkuZ2FtZS5vbnN0b3ZlLmNvbSIsImF1ZCI6Imh0dHBzOi8vbHVkeS5nYW1lLm9uc3RvdmUuY29tL3Jlc291cmNlcyIsImNsaWVudF9pZCI6IjEwMDAwMDAwMDAwMDA1MTMifQ.KJSweBbQpwz7OcYwY_Fc9FJDmSBL_8y0KqNXKq3KMC6vIgy-Cmsfzi7klAyjIJLGRB2SeW9sq--QbafkIHBeWUVD7jROy8mhLvKlr8vLnGJ5IePGriBtC6IB-Ma6Wr1w4Upa0jwBDE7eRwk6FPX21wrXnalqk-MpYpTBmPp1MmcaNVCoxZliMRsNtfrFrQE0RnceerNsBAoj6blyIt7wH9IB5dHTzLYEDVXBA6rQeS8gBzYzcKC4yWDcHSas6es_JqCykp-w9HdaT20YXZW0te3knRl2VZ3oOsVmCmCoPk3cSHaqaleesmabKnuWPd7sT6FCvdKeuhfCNvMNAze9nA")

    # image = get_adventure_island(
    #     island=["하모니 섬", "죽음의 협곡", "고요한 안식의 섬", "하모니 섬", "죽음의 협곡", "고요한 안식의 섬"],
    #     reward=["카드", "실링", "골드", "카드", "실링", "골드"],
    #     double=False
    # )

    # image.show()
    # make_daily_adventure_island([
    #     ["스노우팡 아일랜드", ["전설 ~ 고급 카드 팩", "영혼의 잎사귀", "인연의 돌", "실링"], ["전설", "고급", "희귀", "일반"]],
    #     ["기회의 섬", ["전설 ~ 고급 카드 팩", "영혼의 잎사귀", "인연의 돌", "해적 주화", "실링"], ["전설", "고급", "희귀", "일반", "일반"]],
    #     ["스노우팡 아일랜드", ["전설 ~ 고급 카드 팩", "영혼의 잎사귀", "인연의 돌", "해적 주화", "실링"], ["전설", "고급", "희귀", "일반", "일반"]]
    # ], "2023-03-11 모험섬 일정") \
    #     .save("D:/평일_테스트1.png")
    # .show()

    # make_daily_adventure_island([
    #     ["스노우팡 아일랜드", ["전설 ~ 고급 카드 팩", "영혼의 잎사귀", "인연의 돌", "실링"], ["전설", "고급", "희귀", "일반"]],
    #     ["기회의 섬", ["전설 ~ 고급 카드 팩", "영혼의 잎사귀", "인연의 돌", "해적 주화", "실링"], ["전설", "고급", "희귀", "일반", "일반"]],
    #     ["스노우팡 아일랜드", ["전설 ~ 고급 카드 팩", "영혼의 잎사귀", "인연의 돌", "해적 주화", "실링"], ["전설", "고급", "희귀", "일반", "일반"]],
    #     ["스노우팡 아일랜드", ["전설 ~ 고급 카드 팩", "영혼의 잎사귀", "인연의 돌", "실링"], ["전설", "고급", "희귀", "일반"]],
    #     ["기회의 섬", ["전설 ~ 고급 카드 팩", "영혼의 잎사귀", "인연의 돌", "해적 주화", "실링"], ["전설", "고급", "희귀", "일반", "일반"]],
    #     ["스노우팡 아일랜드", ["전설 ~ 고급 카드 팩", "영혼의 잎사귀", "인연의 돌", "해적 주화", "실링"], ["전설", "영웅", "희귀", "고급", "일반"]],
    # ], "2023-03-11 모험섬 일정") \
    #     .save("D:/주말_테스트1.png")
    # .show()
