import json
import os

def createConfigFolder():
    if not os.path.exists("Config"):
        os.makedirs("Config")
        createConfigJson()

def createConfigJson():
    if not os.path.exists("Config/config.json"):
        configData = {}
        with open("Config/config.json", "w") as configFile:
            json.dump(configData, configFile, indent=4)

def checkConfigFolder():
    import os
    if os.path.exists("Config"):
        if not os.path.exists("Config/config.json"):
            createConfigJson()
        return True
    else:
        createConfigFolder()
        return False

__all__ = ["checkConfigFolder"]