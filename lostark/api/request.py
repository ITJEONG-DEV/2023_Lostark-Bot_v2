import requests
import json

main_url = "https://developer-lostark.game.onstove.com"


def get_GET_headers(auth):
    return {'accept': 'application/json', 'authorization': auth}


def get_POST_headers(auth):
    return {'accept': 'application/json', 'authorization': auth, 'Content-Type': 'application/json'}


def get_events(auth):
    request_url = main_url + "/news/events"

    response = requests.get(request_url, headers=get_GET_headers(auth), verify=False)

    return response.json()


def get_notices(type, auth):
    request_url = main_url + f"/news/notices/"

    response = requests.get(request_url, headers=get_GET_headers(auth), verify=False)

    return response.json()


def get_dobyss_info(auth):
    request_url = main_url + "/gamecontents/challenge-abyss-dungeons"

    response = requests.get(request_url, headers=get_GET_headers(auth), verify=False)

    return response.json()


def get_doguard_info(auth):
    request_url = main_url + "/gamecontents/challenge-guardian-raids"

    response = requests.get(request_url, headers=get_GET_headers(auth), verify=False)

    return response.json()


def get_island_info(auth):
    request_url = main_url + "/gamecontents/calendar"

    response = requests.get(request_url, headers=get_GET_headers(auth), verify=False)

    island = []

    for item in response.json():
        if item["CategoryName"] == "모험 섬":
            island.append(item)

    return island
