from scripts.getInfoPlayer import getInfoPlayer
from scripts.createFiles import checkConfigFolder
from scripts.manageFiles import saveConfig, loadConfig, resetConfigFile, checkIfAlrSaved, makeUrConfig

checkConfigFolder()
if checkIfAlrSaved():
    loadDecision = input("Do you want to load the last configuration? (y/n): ").lower()
    if loadDecision == 'y':
        configData = loadConfig()
        idPlayer = configData.get("idPlayer", [])
        clients = configData.get("clients", [])
        clientToPlayer = configData.get("clientToPlayer", {})
    else:
        makeUrConfig()
else:
    makeUrConfig()

print(idPlayer)
print(clients)
print(clientToPlayer)