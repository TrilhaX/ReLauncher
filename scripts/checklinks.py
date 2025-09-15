import re

def gameInfo():
    link = input("Enter the Roblox game or private server link: ")
    matchPlaceID = re.search(r"games/(\d+)", link)
    matchPrivateServerCode = re.search(r"privateServerLinkCode=([a-zA-Z0-9]+)", link)
    
    place_id = matchPlaceID.group(1) if matchPlaceID else None
    private_server_code = matchPrivateServerCode.group(1) if matchPrivateServerCode else None

    if not place_id:
        print("PlaceID not found in the link.")
    
    return place_id, private_server_code

__all__ = ["gameInfo"]