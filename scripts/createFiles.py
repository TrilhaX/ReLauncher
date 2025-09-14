import json
import os

def createConfigFolder():
    if not os.path.exists("Config"):
        os.makedirs("Config")
        print("Created 'Config' folder.")

def createConfigJson():
    filePath = "Config/config.json"
    if not os.path.exists(filePath):
        with open(filePath, "w") as configFile:
            json.dump({}, configFile, indent=4)
            print("Created 'Config/config.json' file.")

def checkConfigFolder():
    createConfigFolder()
    createConfigJson()

__all__ = ["checkConfigFolder"]