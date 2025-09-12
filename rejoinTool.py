from scripts.createFiles import checkConfigFolder
from scripts.manageFiles import loadConfig, checkIfAlrSaved, makeUrConfig
import subprocess

checkConfigFolder()
if checkIfAlrSaved():
    loadDecision = input("Do you want to load the last configuration? (y/n): ").lower()
    if loadDecision == 'y':
        configData = loadConfig()
        idPlayer = configData.get("idPlayer", [])
        clients = configData.get("clients", [])
        clientToPlayer = configData.get("clientToPlayer", {})
        clientToGame = configData.get("clientToGame", {})

        print(configData)
        print("Configuration loaded successfully.")

        for client in clients:
            place_id = clientToGame[client]["placeID"]

            cmd = [
                "adb", "shell",
                "am", "start",
                "-a", "android.intent.action.VIEW",
                "-d", f"roblox://placeId={place_id}",
                "com.roblox.cliena"
            ]

            print(f"Running for {client} -> placeID {place_id}")
            subprocess.run(cmd)

    else:
        makeUrConfig()
else:
    makeUrConfig()