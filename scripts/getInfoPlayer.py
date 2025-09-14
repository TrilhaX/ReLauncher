import requests
import json
import time

urlToGetPresence = "https://presence.roblox.com/v1/presence/users"
urlToGetPlayerInfo = "https://users.roblox.com/v1/users/"
urlToGetGameInfo = "https://games.roblox.com/v1/games/multiget-place-details?placeIds="

def getInfoPlayer(userID: int):
    try:
        player_info_url = urlToGetPlayerInfo + str(userID)
        player_info_resp = requests.get(player_info_url)
        player_info_resp.raise_for_status()
        data = player_info_resp.json()
        playerName = data.get("name", "Unknown")
        
        time.sleep(1) 

        headers = {"Content-Type": "application/json"}
        payload = {"userIds": [userID]}
        presence_resp = requests.post(urlToGetPresence, headers=headers, data=json.dumps(payload))
        presence_resp.raise_for_status()
        presenceData = presence_resp.json()
        
        playerPresenceJson = presenceData["userPresences"][0]
        presenceType = playerPresenceJson.get("userPresenceType", 0)
        placeIDFromPresence = playerPresenceJson.get("placeId")
        
        presenceMap = {
            0: "Offline",
            1: "Online",
            2: "InGame",
            3: "InStudio",
            4: "Invisible",
        }
        playerPresence = presenceMap.get(presenceType, "Unknown")
        
        gameData = getGameInfoFromPlace(placeIDFromPresence) if placeIDFromPresence else None
        gameName = gameData.get("name", "Unknown Game") if gameData else None
        
        print("-----------------------------------------")
        print("Player:", playerName)
        print("Status:", playerPresence)
        if gameName:
            print("Game:", gameName)
        print("-----------------------------------------")
        
        return {
            "name": playerName,
            "status": playerPresence,
            "placeID": placeIDFromPresence,
            "gameName": gameName,
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching player info for {userID}: {e}")
        return {"name": f"Player {userID}", "status": "Offline", "placeID": None, "gameName": None}

def getGameInfoFromPlace(placeID: int):
    try:
        time.sleep(1)
        response = requests.get(f"{urlToGetGameInfo}{placeID}")
        response.raise_for_status()
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            placeData = data["data"][0]
            return {
                "name": placeData.get("name", "Unknown Game"),
                "universeId": placeData.get("universeId"),
                "creator": placeData.get("creator", {}).get("name", "Unknown Creator"),
            }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching game info for PlaceID {placeID}: {e}")
        
    return {"name": "Unknown Game", "universeId": None, "creator": None}

__all__ = ["getInfoPlayer"]