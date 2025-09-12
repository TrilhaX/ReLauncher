import requests
import subprocess

def runClient(client, place_id):
    cmd = f"am start -a android.intent.action.VIEW -d roblox://placeId={place_id} com.roblox.{client}"
    print(f"Running command: {cmd}")
    subprocess.run(cmd, shell=True)

def sendWebhook(url, message):
    if not url:
        print("Webhook URL is not defined!")
        return
    try:
        response = requests.post(url, json={"content": message})
        print(f"Webhook sent! Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending webhook: {e}")
        
__all__ = ["runClient", "sendWebhook"]