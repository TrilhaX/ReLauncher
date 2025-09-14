from scripts.createFiles import checkConfigFolder
from scripts.manageFiles import loadConfig, checkIfAlrSaved, makeUrConfig
from scripts.getInfoPlayer import getInfoPlayer
from scripts.functions import runClient, sendWebhook
import time
import sys

lastStatus = {}

def load_or_create_config():
    checkConfigFolder()
    if checkIfAlrSaved():
        loadDecision = input("Do you want to load the last configuration? (y/n): ").lower()
        if loadDecision == 'y':
            configName = input("Type the name of the configuration file (default is config): ") or "config"
            filePath = f"Config/{configName}.json"
            configData = loadConfig(filePath)
            if configData:
                print("Configuration loaded successfully.")
                return configData
            else:
                print("An error occurred loading the file. Creating a new configuration.")
                return makeUrConfig()
        else:
            return makeUrConfig()
    else:
        return makeUrConfig()

def main():
    configData = load_or_create_config()
    
    clients = configData.get("clients", [])
    clientToPlayer = configData.get("clientToPlayer", {})
    clientToGame = configData.get("clientToGame", {})
    cdTime = configData.get("cdTime", 10)
    webhookURL = configData.get("webhookURL", None)
    webhookEnabled = configData.get("webhookEnabled", False)

    if not clients:
        print("No clients configured. Please run the configuration again.")
        sys.exit()

    for client in clients:
        lastStatus[client] = None
        
    print("Starting monitoring. Press Ctrl+C to exit.")
    
    while True:
        try:
            for client in clients:
                player_id = clientToPlayer.get(client)
                gameInfo = clientToGame.get(client, {})
                place_id = gameInfo.get("placeID")
                privateServerCode = gameInfo.get("privateServerCode")

                if not player_id or not place_id:
                    print(f"Missing information for '{client}'. Skipping...")
                    continue

                playerPresence = getInfoPlayer(player_id)
                status = playerPresence.get("status", "Offline")
                playerName = playerPresence.get("name", f"Player {player_id}")
                prevStatus = lastStatus.get(client)

                if status != prevStatus:
                    if status != "InGame" and prevStatus == "InGame":
                        print(f"'{playerName}' is now offline for '{client}'.")
                        if webhookEnabled and webhookURL:
                            sendWebhook(webhookURL, f"'{playerName}' is now offline in '{client}'.")
                    elif status == "InGame" and prevStatus != "InGame":
                        print(f"'{playerName}' is now InGame for '{client}'.")
                        if webhookEnabled and webhookURL:
                            sendWebhook(webhookURL, f"'{playerName}' is now InGame in '{client}'.")

                lastStatus[client] = status
                
                if status == "InGame":
                    print(f"'{playerName}' is InGame for '{client}'.")
                else:
                    print(f"'{playerName}' is currently '{status}'. Reopening client '{client}'...")
                    runClient(client, place_id, privateServerCode)

            time.sleep(cdTime)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            break
        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
            time.sleep(cdTime)

if __name__ == "__main__":
    main()