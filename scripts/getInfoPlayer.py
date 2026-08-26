import requests
import json

urlToGetPresence = "https://presence.roblox.com/v1/presence/users"
urlToGetPlayerInfo = "https://users.roblox.com/v1/users/"

def getInfoPlayer(userID: int):
    try:
        player_info_url = urlToGetPlayerInfo + str(userID)

        player_info_resp = requests.get(
            player_info_url,
            timeout=10
        )
        player_info_resp.raise_for_status()

        data = player_info_resp.json()

        playerName = data.get("name", f"Player {userID}")

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "userIds": [int(userID)]
        }

        presence_resp = requests.post(
            urlToGetPresence,
            headers=headers,
            json=payload,
            timeout=10
        )

        presence_resp.raise_for_status()

        presenceData = presence_resp.json()

        userPresences = presenceData.get("userPresences", [])

        if not userPresences:
            return {
                "name": playerName,
                "status": "Offline",
                "placeID": None,
                "gameName": None,
            }

        playerPresenceJson = userPresences[0]

        presenceType = playerPresenceJson.get(
            "userPresenceType",
            0
        )

        placeIDFromPresence = playerPresenceJson.get("placeId")

        presenceMap = {
            0: "Offline",
            1: "Online",
            2: "InGame",
            3: "InStudio",
            4: "Invisible",
        }

        playerPresence = presenceMap.get(
            presenceType,
            "Unknown"
        )

        print("-----------------------------------------")
        print("Player:", playerName)
        print("Status:", playerPresence)

        if placeIDFromPresence:
            print("PlaceID:", placeIDFromPresence)

        print("-----------------------------------------")

        return {
            "name": playerName,
            "status": playerPresence,
            "placeID": placeIDFromPresence,
            "gameName": None,
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching player info for {userID}: {e}")

        return {
            "name": f"Player {userID}",
            "status": "Offline",
            "placeID": None,
            "gameName": None,
        }

    except (ValueError, KeyError, TypeError) as e:
        print(f"Error parsing Roblox response for {userID}: {e}")

        return {
            "name": f"Player {userID}",
            "status": "Offline",
            "placeID": None,
            "gameName": None,
        }


__all__ = ["getInfoPlayer"]