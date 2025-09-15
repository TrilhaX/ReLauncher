import json
import os

def createConfigFolder():
    if not os.path.exists("Config"):
        os.makedirs("Config")
        print("Created 'Config' folder.")

def checkConfigFolder():
    createConfigFolder()

__all__ = ["checkConfigFolder"]