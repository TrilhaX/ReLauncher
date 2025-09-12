import requests
import json
from scripts.checklinks import gameInfo

urlToGetPresence = "https://presence.roblox.com/v1/presence/users"
urlToGetPlayerInfo = "https://users.roblox.com/v1/users/"
urlToGetGameInfo = "https://games.roblox.com/v1/games/multiget-place-details?placeIds="

def getInfoPlayer(userID: int):
    headers = {"Content-Type": "application/json"}
    payload = {"userIds": [userID]}
    allURLToPlayerInfo = urlToGetPlayerInfo + str(userID)
    response = requests.get(allURLToPlayerInfo)
    data = response.json()
    playerName = data.get("name", "Unknown")
    resp = requests.post(urlToGetPresence, headers=headers, data=json.dumps(payload))
    respData = resp.json()
    playerPresenceJson = respData["userPresences"][0]
    presenceType = playerPresenceJson["userPresenceType"]
    placeIDFromPresence = playerPresenceJson.get("placeId")

    presenceMap = {
        0: "Offline",
        1: "Online",
        2: "InGame",
        3: "InStudio",
        4: "Invisible"
    }
    playerPresence = presenceMap.get(presenceType, "Unknown")
    placeIDToUse = placeIDFromPresence

    gameData = getGameInfoFromPlace(placeIDToUse) if placeIDToUse else None

    print("-----------------------------------------")
    print("Player:", playerName)
    print("Status:", playerPresence)
    if gameData:
        print("Game Name:", gameData["name"])
    print("-----------------------------------------")
    return {
        "name": playerName,
        "status": playerPresence,
    }

def getGameInfoFromPlace(placeID: int):
    response = requests.get(f"{urlToGetGameInfo}{placeID}")
    if response.status_code != 200:
        return {"name": "Unknown Game", "universeId": None, "creator": None}

    data = response.json()
    if "data" in data and len(data["data"]) > 0:
        placeData = data["data"][0]
        print(placeData)
        return {
            "name": placeData.get("name", "Unknown Game"),
            "universeId": placeData.get("universeId"),
            "creator": placeData.get("creator", {}).get("name", "Unknown Creator")
        }
    return {"name": "Unknown Game", "universeId": None, "creator": None}

__all__ = ["getInfoPlayer"]
