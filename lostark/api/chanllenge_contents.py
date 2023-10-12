from PIL import Image, ImageDraw, ImageFont

import os
import glob
import platform
import datetime
import requests
import urllib.request

from util import read_json

from .request import get_dobyss_info, get_doguard_info

global font_dir, title_font, subtitle_font, abyss_font, guardian_font

path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
current_os = "Linux"

if "Linux" in platform.platform():

    font_dir = "/usr/share/fonts/truetype/nanum"
    ttf_files = glob.glob(f"{font_dir}/*.ttf")

    title_font = ImageFont.truetype(ttf_files[-4], size=40)
    subtitle_font = ImageFont.truetype(ttf_files[-4], size=32)
    abyss_font = ImageFont.truetype(ttf_files[-4], size=18)
    guardian_font = ImageFont.truetype(ttf_files[-4], size=18)

elif "Window" in platform.platform():
    current_os = "window"

    title_font = ImageFont.truetype("C:/USERS/DEV2/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/NANUMBARUNGOTHICBOLD.TTF",
                                    size=40)
    subtitle_font = ImageFont.truetype("C:/USERS/DEV2/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/NANUMBARUNGOTHICBOLD.TTF",
                                       size=32)
    abyss_font = ImageFont.truetype("C:/USERS/DEV2/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/NANUMBARUNGOTHICBOLD.TTF",
                                    size=18)
    guardian_font = ImageFont.truetype(
        "C:/USERS/DEV2/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/NANUMBARUNGOTHICBOLD.TTF",
        size=18)


def get_image(name: str):
    name = name.replace(":", "")

    dir = os.path.join(path, 'data')

    if current_os == "Linux":
        if not os.path.isfile(dir + f'/{name}.png'):
            return None

        return Image.open(dir + f'/{name}.png').convert("RGBA")

    else:
        if not os.path.isfile(dir + f'\\{name}.png'):
            return None

        return Image.open(dir + f'\\{name}.png').convert("RGBA")


def get_bg(width, height, color, alpha):
    # background
    bg = Image.new('RGBA', (width, height), color)
    alpha = Image.new("L", bg.size, alpha)
    bg.putalpha(alpha)

    return bg


window_size = (1024, 512)
abyss_icon_size = (268, 116)
guardian_icon_size = (254, 83)

item_color = (50, 50, 50)

background_color = (32, 32, 32)
box_color = (0, 0, 0)

# background_color = (32, 32, 32)
# title_back_color = (0, 0, 0)

font_color = (255, 255, 255)
title_color = (255, 210, 40)
icon_gap = 4  # 아이콘 사이의 공백
content_gap = 32  # 컨텐츠 사이의 공백
max_reward_num = 8
margin = 4


def make_abyss_box(image, name):
    # image
    img = get_image(name)

    if img is None:
        urllib.request.urlretrieve(image, f"{path}/data/{name}.png")
        img = get_image(name)

    # name
    drawable_image = ImageDraw.Draw(img)
    w, h = drawable_image.textsize(name, font=abyss_font)

    crop_x, crop_y = 0, abyss_icon_size[1] - h - margin * 2
    crop_w, crop_h = int(abyss_icon_size[0] / 2), h + margin * 2

    bg = get_bg(crop_w, crop_h, background_color, 255)
    crop_bg = img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))

    crop_bg = Image.blend(crop_bg, bg, 0.6)

    img.paste(crop_bg, (crop_x, crop_y))

    x, y = (crop_w - w) / 2, margin + crop_y
    drawable_image.text((x, y), name, fill=title_color, font=abyss_font)

    return img


def make_abyss_boxes(info):
    width, height = abyss_icon_size[0] + margin * 2, abyss_icon_size[1] * len(info) + margin * (len(info) + 1)
    content = Image.new('RGBA', (width, height), box_color)

    # abyss box
    for i in range(len(info)):
        abyss_box = make_abyss_box(info[i]["Image"], info[i]["Name"])
        x, y = margin, margin + i * (abyss_icon_size[1] + margin)
        content.paste(abyss_box, (x, y))

    return content


def make_abyss_dungeon(info):
    width, height = int(window_size[0] / 2), window_size[1] - content_gap * 4
    content = Image.new('RGBA', (width, height), background_color)

    drawable_image = ImageDraw.Draw(content)

    # subtitle
    subtitle = "도전 어비스 던전"
    _w, _h = drawable_image.textsize(subtitle, font=subtitle_font)
    x, y = (width - _w) / 2, _h / 2
    drawable_image.text((x, y), subtitle, fill=font_color, font=subtitle_font)

    # abyss_boxes
    abyss_boxes = make_abyss_boxes(info)
    size_gap = int((guardian_icon_size[1] * 3 - abyss_icon_size[1] * 2 + margin) / 2)
    x, y = int((width - abyss_icon_size[0]) / 2), _h + content_gap + size_gap
    content.paste(abyss_boxes, (x, y))

    return content


def make_guardian_box(image, name):
    # image
    img = get_image(name)

    if img is None:
        urllib.request.urlretrieve(image, f"{path}/data/{name}.png")
        img = get_image(name)

    bg = get_bg(guardian_icon_size[0], guardian_icon_size[1], background_color, 255)
    img = Image.alpha_composite(bg, img)

    # name
    drawable_image = ImageDraw.Draw(img)
    w, h = drawable_image.textsize(name, font=guardian_font)

    crop_x, crop_y = 0, guardian_icon_size[1] - h - margin * 2
    crop_w, crop_h = int(guardian_icon_size[0] / 2), h + margin * 2

    bg = get_bg(crop_w, crop_h, background_color, 255)
    crop_bg = img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))

    crop_bg = Image.blend(crop_bg, bg, 0.6)

    img.paste(crop_bg, (crop_x, crop_y))

    x, y = (crop_w - w) / 2, margin + crop_y
    drawable_image.text((x, y), name, fill=title_color, font=guardian_font)

    return img


def make_guardian_boxes(info):
    width, height = guardian_icon_size[0] + margin * 2, guardian_icon_size[1] * len(info) + margin * (len(info) + 1)
    content = Image.new('RGBA', (width, height), box_color)

    # abyss box
    for i in range(len(info)):
        guardian_box = make_guardian_box(info[i]["Image"], info[i]["Name"])
        x, y = margin, margin + i * (guardian_icon_size[1] + margin)
        content.paste(guardian_box, (x, y))

    return content


def make_guardian_raid(info):
    width, height = int(window_size[0] / 2), window_size[1] - content_gap * 4
    content = Image.new('RGBA', (width, height), background_color)

    drawable_image = ImageDraw.Draw(content)

    # subtitle
    subtitle = "도전 가디언 토벌"
    _w, _h = drawable_image.textsize(subtitle, font=subtitle_font)
    x, y = (width - _w) / 2, _h / 2
    drawable_image.text((x, y), subtitle, fill=font_color, font=subtitle_font)

    # guardian_boxes
    guardian_boxes = make_guardian_boxes(info["Raids"])
    x, y = int((width - guardian_icon_size[0]) / 2), _h + content_gap
    content.paste(guardian_boxes, (x, y))

    return content


def make_weekly_challenge_contents(authorization):
    content = Image.new('RGBA', window_size, background_color)

    # title
    title = "주간 도전 컨텐츠"
    drawable_image = ImageDraw.Draw(content)
    _w, _h = drawable_image.textsize(title, font=title_font)
    x, y = (window_size[0] - _w) / 2, _h
    drawable_image.text((x, y), title, fill=title_color, font=title_font)

    # 도비스
    abyss_info = get_dobyss_info(authorization)
    abyss_content = make_abyss_dungeon(abyss_info)
    start_x, start_y = 0, _h + content_gap * 2 + margin * 2
    content.paste(abyss_content, (start_x, start_y))

    # 도가토
    guardian_info = get_doguard_info(authorization)
    guardian_content = make_guardian_raid(guardian_info)
    start_x, start_y = int(window_size[0] / 2), _h + content_gap * 2 + margin * 2
    content.paste(guardian_content, (start_x, start_y))

    return content


def get_weekly_challenge_contents(authorization):
    content = make_weekly_challenge_contents(authorization)

    link = f'{path}/result.png'
    content.save(link)

    return link


if __name__ == "__main__":
    api_key = read_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..") + "/data/key.json")["lostark"][
        "api_key"]

    make_weekly_challenge_contents(authorization=f"Bearer {api_key}") \
        .save('img.png')
    #    .show()
