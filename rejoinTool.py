from scripts.createFiles import checkConfigFolder
from scripts.manageFiles import loadConfig, checkIfAlrSaved, makeUrConfig
from scripts.getInfoPlayer import getInfoPlayer
import subprocess
import time

checkConfigFolder()

if checkIfAlrSaved():
    loadDecision = input("Do you want to load the last configuration? (y/n): ").lower()
    if loadDecision == 'y':
        configData = loadConfig()
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

print(configData)

def runClient(client, place_id):
    cmd = f"am start -a android.intent.action.VIEW -d roblox://placeId={place_id} com.roblox.{client}"
    print(cmd)
    print(f"Running for {client} -> placeID {place_id}")
    subprocess.run(cmd, shell=True)

def main():
    while True:
        for client in clients:
            player_id = clientToPlayer[client]
            playerPresence = getInfoPlayer(player_id)
            status = playerPresence.get("status")
            cdTime = configData.get("cdTime", 10)

            if status == "InGame":
                print(f"{playerPresence['name']} está InGame ({client}).")
            else:
                print(f"{playerPresence['name']} caiu ({status}) -> Reabrindo {client}...")
                place_id = clientToGame[client]["placeID"]
                runClient(client, place_id)
        time.sleep(cdTime)

if __name__ == "__main__":
    main()