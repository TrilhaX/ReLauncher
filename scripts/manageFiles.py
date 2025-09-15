import json
import os
from scripts.checklinks import gameInfo

def saveConfig(data, filePath="Config/config.json"):
    try:
        with open(filePath, "w") as configFile:
            json.dump(data, configFile, indent=4)
        print(f"Configuration saved to '{filePath}' successfully.")
    except Exception as e:
        print(f"Error saving configuration: {e}")

def loadConfig(filePath):
    try:
        with open(filePath, "r") as configFile:
            return json.load(configFile)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading configuration: {e}")
        return {}
    
def checkIfAlrSaved(folderPath="Config/"):
    if not os.path.exists(folderPath):
        return False
    json_files = [f for f in os.listdir(folderPath) 
                if f.endswith(".json") and os.path.getsize(os.path.join(folderPath, f)) > 0]
    return len(json_files) > 0

def makeUrConfig():
    configData = {
        "clients": [],
        "clientToPlayer": {},
        "clientToGame": {},
        "cdTime": 10,
        "runSpecificClient": True,
        "webhookEnabled": False,
        "webhookURL": None,
    }

    try:
        rbxQuant_input = input("How many Roblox clients do you want to open?: ")
        rbxQuant = int(rbxQuant_input)
        
        for i in range(rbxQuant):
            player_id_input = input(f"Enter the ID of player {i + 1}: ")
            client_name = input(f"Enter the name of client {i + 1} (like 'client', 'cliena', 'clienb'): ")
            
            if not player_id_input.isdigit() or not client_name:
                print("Invalid input. Skipping this client.")
                continue

            player_id = int(player_id_input)
            
            configData["clients"].append(client_name)
            configData["clientToPlayer"][client_name] = player_id
            
            psDecision = input(f"Do you want to use a private server link for '{client_name}'? (y/n, default is n): ").lower()
            
            placeID, privateServerLinkCode = gameInfo()
            
            if placeID:
                if psDecision == 'y':
                    configData["clientToGame"][client_name] = {
                        "placeID": placeID,
                        "privateServerCode": privateServerLinkCode
                    }
                else:
                    placeID = int(input("Send the PlaceID of game: "))
                    configData["clientToGame"][client_name] = {
                        "placeID": placeID,
                        "privateServerCode": None
                    }
            else:
                print("Could not get game info. Skipping game configuration for this client.")
                
        cdTime_input = input("Cooldown time (in seconds) to check if the player is in game (default is 10): ") or "10"
        configData["cdTime"] = int(cdTime_input)

        webhookDecision = input("Do you want to enable webhook notifications? (y/n, default is n): ").lower()
        if webhookDecision == 'y':
            configData["webhookEnabled"] = True
            webhookURL = input("Type your webhook URL: ")
            configData["webhookURL"] = webhookURL
        
        configDecision = input("Do you want to save this configuration? (y/n): ").lower()
        if configDecision == 'y':
            nameOfConfig = input("Type the name of the configuration file (default is 'config'): ") or "config"
            saveConfig(configData, filePath=f"Config/{nameOfConfig}.json")

    except ValueError:
        print("Invalid input. Please ensure you enter a number for the quantity of clients and cooldown time.")
    except Exception as e:
        print(f"An error occurred during configuration creation: {e}")
        
    return configData
    
def resetConfigFile(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)
    with open(filePath, "w") as configFile:
        json.dump({}, configFile, indent=4)

__all__ = ["saveConfig", "loadConfig", "resetConfigFile", "checkIfAlrSaved", "makeUrConfig"]