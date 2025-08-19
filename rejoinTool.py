import requests
import json
urlToGetPresence = "https://presence.roblox.com/v1/presence/users"
urlToGetPlayerInfo = "https://users.roblox.com/v1/users/"
urlToGetGameInfo = "https://games.roblox.com/v1/games?universeIds="

def getInfoPlayer(userID):
    headers = {'Content-Type': 'application/json'}
    payload = {"userIds": [userID]}
    allURLToPlayerInfo = urlToGetPlayerInfo + str(userID)
    response = requests.get(allURLToPlayerInfo)
    data = response.json()

    resp = requests.post(urlToGetPresence, headers=headers, data=json.dumps(payload))
    playerName = data["name"]
    respData = resp.json()
    playerPresenceJson = respData["userPresences"][0]
    presenceType = playerPresenceJson['userPresenceType']
    universeID = playerPresenceJson["universeId"] or 1962086868

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
    print(playerName)
    print(playerPresence)
    print(gameInfo)
    print("-----------------------------------------")

def getGameInfo(universeIDAtual):
    allUrlGame = urlToGetGameInfo + str(universeIDAtual)
    response = requests.get(allUrlGame)
    respJson = response.json()
    data = respJson["data"][0]
    nameGame = data["name"]
    return nameGame

getInfoPlayer(156)