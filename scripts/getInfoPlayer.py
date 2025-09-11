import requests
import json

urlToGetPresence = "https://presence.roblox.com/v1/presence/users"
urlToGetPlayerInfo = "https://users.roblox.com/v1/users/"
urlToGetGameInfo = "https://games.roblox.com/v1/games?universeIds="

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
    universeID = playerPresenceJson.get("universeId", 1962086868)

    presenceMap = {
        0: "Offline",
        1: "Online",
        2: "InGame",
        3: "InStudio",
        4: "Invisible"
    }

    playerPresence = presenceMap.get(presenceType, "Unknown")
    gameInfo = getGameInfo(universeID)

    print("-----------------------------------------")
    print("Player:", playerName)
    print("Status:", playerPresence)
    print("Game:", gameInfo)
    print("-----------------------------------------")

def getGameInfo(universeIDAtual: int):
    print(universeIDAtual)
    allUrlGame = urlToGetGameInfo + str(universeIDAtual)
    response = requests.get(allUrlGame)
    respJson = response.json()
    if "data" in respJson and len(respJson["data"]) > 0:
        data = respJson["data"][0]
        return data.get("name", "Unknown Game")
    return "Unknown Game"

__all__ = ["getInfoPlayer"]