import re

def gameInfo():
    link = input("Enter the Roblox Private Server game link: ")
    matchPlaceID = re.search(r"games/(\d+)", link)
    matchPrivateServerCode = re.search(r"privateServerLinkCode=([a-zA-Z0-9]+)", link)
    if matchPlaceID and matchPrivateServerCode:
        place_id = matchPlaceID.group(1)
        private_server_code = matchPrivateServerCode.group(1)
        return place_id, private_server_code
    else:
        print("Dont Found PlaceID or PrivateServerCode in Link.")

__all__ = ["gameInfo"]