import websocket
import json

TOKEN = ""

payload = {
    "op": 2,
    "d": {
        "token": TOKEN,
        "properties": {
            "os": "Windows Device",
            "browser": "Windows Browser",
            "device": "Windows Device"
        },
        "presence": {
            "status": "offline",
            "afk": True
        }
    }
}
payload = json.dumps(payload)

ws = websocket.WebSocket()
ws.connect("wss://gateway.discord.gg/")
ws.send(payload)

while True:
    data = ws.recv()
    try:
        data = json.loads(data)
    except Exception:
        continue
    
    if not data["t"] == "READY": continue
    sessions = data["d"]["sessions"]

    for i, session in enumerate(sessions, 1):
        print(f"{i} : {session}")
    
    ws.close()
    break
