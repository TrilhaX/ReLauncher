from scripts.createFiles import checkConfigFolder
from scripts.manageFiles import loadConfig, checkIfAlrSaved, makeUrConfig

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
    else:
        makeUrConfig()
else:
    makeUrConfig()