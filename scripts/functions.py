import requests
import subprocess
import time

def runClient(client, place_id, privateServerCode=None):
    app_package = f"com.roblox.{client}"
    
    stop_cmd = ["adb", "shell", "am", "force-stop", app_package]
    print(f"Force closing '{app_package}'...")
    subprocess.run(stop_cmd, check=True)
    time.sleep(1)

    if privateServerCode:
        start_cmd = [
            "adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", 
            "-d", f"roblox://placeId={place_id}&linkCode={privateServerCode}", app_package
        ]
    else:
        start_cmd = [
            "adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", 
            "-d", f"roblox://placeId={place_id}", app_package
        ]
        
    print(f"Reopening '{app_package}'...")
    subprocess.run(start_cmd, check=True)

def sendWebhook(url, message):
    if not url:
        print("Webhook URL is not defined!")
        return
    try:
        response = requests.post(url, json={"content": message})
        response.raise_for_status()
        print(f"Webhook sent! Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending webhook: {e}")

__all__ = ["runClient", "sendWebhook"]