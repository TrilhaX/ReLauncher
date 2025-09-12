from scripts.createFiles import checkConfigFolder
from scripts.manageFiles import loadConfig, checkIfAlrSaved, makeUrConfig
from scripts.getInfoPlayer import getInfoPlayer
from scripts.functions import runClient, sendWebhook
import time
lastStatus = {}
checkConfigFolder()

if checkIfAlrSaved():
    loadDecision = input("Do you want to load the last configuration? (y/n): ").lower()
    if loadDecision == 'y':
        configName = input("Type the name of the configuration file (default is config): ") or "config"
        filePath = f"Config/{configName}.json"
        configData = loadConfig(filePath)
        print("Configuration loaded successfully.")
    else:
        configData = makeUrConfig()
        print("New configuration created.")
else:
    configData = makeUrConfig()
    print("New configuration created.")

idPlayer = configData.get("idPlayer", [])
clients = configData.get("clients", [])
clientToPlayer = configData.get("clientToPlayer", {})
clientToGame = configData.get("clientToGame", {})

cdTime = configData.get("cdTime", 10)
webhookURL = configData.get("webhookURL", None)
webhookEnabled = configData.get("webhookEnabled", False)
runSpecificClient = configData.get("runSpecificClient", True)

print("Loaded configuration:", configData)

def main():
    for client in clients:
        lastStatus[client] = None

    while True:
        for client in clients:
            player_id = clientToPlayer.get(client)
            gameInfo = clientToGame.get(client, {})
            place_id = gameInfo.get("placeID")

            if not player_id or not place_id:
                print(f"Missing info for {client}, skipping...")
                continue

            playerPresence = getInfoPlayer(player_id)
            status = playerPresence.get("status", "Offline")
            playerName = playerPresence.get("name", f"Player {player_id}")

            prevStatus = lastStatus.get(client)

            if status != prevStatus:
                if status != "InGame" and prevStatus == "InGame":
                    print(f"{playerName} is offline in ({client}).")
                    if webhookEnabled:
                        sendWebhook(webhookURL, f"{playerName} is offline in ({client})")
                elif status == "InGame" and prevStatus != "InGame":
                    print(f"{playerName} is back in ({client}).")
                    if webhookEnabled:
                        sendWebhook(webhookURL, f"{playerName} is back in ({client})")

            lastStatus[client] = status

            if status == "InGame":
                print(f"{playerName} is InGame ({client}).")
            else:
                if runSpecificClient:
                    print(f"{playerName} is ({status}) -> Reopening {client}...")
                    runClient(client, place_id)
                else:
                    print("Reopening all clients...")
                    for cl in clients:
                        cl_place_id = clientToGame.get(cl, {}).get("placeID")
                        if cl_place_id:
                            runClient(cl, cl_place_id)
                        else:
                            print(f"Missing placeID for {cl}, skipping...")

        time.sleep(cdTime)

if __name__ == "__main__":
    main()