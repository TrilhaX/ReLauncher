from scripts.createFiles import checkConfigFolder
from scripts.manageFiles import loadConfig, checkIfAlrSaved, makeUrConfig
import subprocess

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

for client in clients:
    place_id = clientToGame[client]["placeID"]
    cmd = f"am start -a android.intent.action.VIEW -d roblox://placeId={place_id} com.roblox.{client}"
    print(cmd)
    print(f"Running for {client} -> placeID {place_id}")
    subprocess.run(cmd, shell=True)