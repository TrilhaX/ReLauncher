import json
import os
idPlayer = []
clients = []
clientToPlayer = {}

def saveConfig(data, filePath="Config/config.json"):
    with open(filePath, "w") as configFile:
        json.dump(data, configFile, indent=4)
        
def loadConfig(filePath="Config/config.json"):
    if not os.path.exists(filePath):
        return {}
    with open(filePath, "r") as configFile:
        return json.load(configFile)
    
def resetConfigFile(filePath="Config/config.json"):
    if os.path.exists(filePath):
        os.remove(filePath)
    with open(filePath, "w") as configFile:
        json.dump({}, configFile, indent=4)
        
def checkIfAlrSaved(filePath="Config/config.json"):
    return os.path.exists(filePath) and os.path.getsize(filePath) > 2

def makeUrConfig():
    resetConfigFile()
    rbxQuant = int(input("How many roblox do u want open?: "))
    for i in range(rbxQuant):
        idPlayer.append(int(input(f"Type the id of the player {i + 1}: ")))
        clients.append(input(f"Type the name (after the final dot) of the client {i + 1} (ex: cliena): "))
        clientToPlayer[clients[i]] = idPlayer[i]  
        
    configDecision = input("Do you want to save this configuration? (y/n): ").lower()
    if configDecision == 'y':
        configData = {
            "idPlayer": idPlayer,
            "clients": clients,
            "clientToPlayer": clientToPlayer
        }
        saveConfig(configData)

__all__ = ["saveConfig", "loadConfig"]