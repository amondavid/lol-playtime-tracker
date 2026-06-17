from urllib.parse import quote
import requests
from database import get_setting


VALID_ACCOUNT_REGIONS = {"americas", "asia", "europe", "sea"}


class RiotApiError(Exception):
    pass


def get_required_setting(key):
    value = get_setting(key)

    if value is None:
        raise RiotApiError(f"Missing required setting: {key}")

    value = value.strip()

    if not value:
        raise RiotApiError(f"Missing required setting: {key}")

    return value


def get_account_by_riot_id():
    riot_id = get_required_setting("riot_id")
    tagline = get_required_setting("tagline")
    region = get_required_setting("region").lower()
    api_key = get_required_setting("api_key")

    if region not in VALID_ACCOUNT_REGIONS:
        raise RiotApiError(
            f"Invalid region '{region}'. Use one of: americas, asia, europe, sea."
        )

    encoded_riot_id = quote(riot_id)
    encoded_tagline = quote(tagline)

    url = (
        f"https://{region}.api.riotgames.com"
        f"/riot/account/v1/accounts/by-riot-id/"
        f"{encoded_riot_id}/{encoded_tagline}"
    )

    response = requests.get(
        url,
        headers={"X-Riot-Token": api_key},
        timeout=10,
    )

    if response.status_code != 200:
        raise RiotApiError(
            f"Riot API request failed with status {response.status_code}: "
            f"{response.text}"
        )

    data = response.json()

    return {
        "puuid": data["puuid"],
        "game_name": data["gameName"],
        "tagline": data["tagLine"],
    }

def get_recent_match_ids(count=10):
    account_data = get_account_by_riot_id()
    puuid = account_data["puuid"]

    region = get_required_setting("region").lower()
    api_key = get_required_setting("api_key")

    url = (
        f"https://{region}.api.riotgames.com"
        f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
    )

    response = requests.get(
        url,
        headers={"X-Riot-Token": api_key},
        params={
            "start": 0,
            "count": count,
        },
        timeout=10,
    )

    if response.status_code != 200:
        raise RiotApiError(
            f"Riot API request failed with status {response.status_code}: "
            f"{response.text}"
        )

    return response.json()