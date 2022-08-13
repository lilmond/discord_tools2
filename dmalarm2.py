import multiprocessing
import websocket
import threading
import requests
import winsound
import json
import time

class DiscordWebsocket(object):
    _gateway = "wss://gateway.discord.gg/"
    _active = False

    def __init__(self, token):
        self.token = token
        self._websocket = None
    
    def initialize(self):
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": "Windows",
                    "$browser": "Windows Browser",
                    "$device": "Windows Device"
                },
                "presence": {
                    "status": "offline"
                }
            }
        }
        payload = json.dumps(payload)
        
        ws = websocket.WebSocket()
        ws.connect(self._gateway)
        ws.send(payload)

        self._websocket = ws
        self._active = True

        threading.Thread(target=self._keepalive, args=[ws], daemon=True).start()

        return ws
    
    def _keepalive(self, ws):
        payload = {
            "op": 1,
            "d": None
        }
        payload = json.dumps(payload)

        while self._active:
            try:
                time.sleep(10)
                ws.send(payload)
            except Exception:
                return
    
    def receive_data(self):
        return self._websocket.recv()
    
    def close(self):
        self._active = False
        self._websocket.send(json.dumps({"op": 1, "d": None}))
        self._websocket.close()


def dmalarm(token, channel_id):
    def _get_my_id():
        return requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token}).json()["id"]

    def _on_message(message):
        if not message["channel_id"] == channel_id: return
        if message["author"]["id"] == my_id: return
        
        while True:
            winsound.PlaySound("alarm.wav", winsound.SND_FILENAME)

    def _on_data(data):
        if len(data) > 10000: return

        try:
            data = json.loads(data)
        except Exception:
            return

        if not "t" in data: return
        if not data["t"] == "MESSAGE_CREATE": return

        threading.Thread(target=_on_message, args=[data["d"]], daemon=True).start()

    my_id = _get_my_id()
    while True:
        try:
            discord_ws = DiscordWebsocket(token)
            discord_ws.initialize()
        except Exception:
            time.sleep(5)
            continue
        while True:
            try:
                data = discord_ws.receive_data()
            except Exception:
                break
            threading.Thread(target=_on_data, args=[data], daemon=True).start()

def main():
    try:
        channel_id = input("Channel ID: ").strip()
    except KeyboardInterrupt:
        return
    token = ""

    paused = False

    try:
        while True:
            if not paused:
                input("-> Press enter to initialize")
            else:
                paused = False
            proc_dmalarm = multiprocessing.Process(target=dmalarm, args=[token, channel_id], daemon=True)
            proc_dmalarm.start()
            print("<- Process started")
            while True:
                full_command = input("-> ")
                args = []
                try:
                    command, args = full_command.split(" ", 1)
                    args = args.split(" ")
                except Exception:
                    command = full_command.strip()
                command = command.lower()

                if command == "stop":
                    if not proc_dmalarm.is_alive():
                        print("<- Process is not alive")
                    else:
                        try:
                            proc_dmalarm.terminate()
                            print("<- Proccess terminated")
                        except Exception:
                            print("<- Unable to terminate process")
                    break
                
                elif command == "exit":
                    try:
                        proc_dmalarm.terminate()
                    except Exception:
                        pass
                    return
                
                elif command == "pause":
                    try:
                        minute = int(args[0]) * 60
                    except Exception:
                        print(f"<- Error. Example: {command} [MINUTE(S)]")
                        continue

                    try:
                        proc_dmalarm.terminate()
                        print(f"<- Process terminated")
                    except Exception:
                        print("<- Unable to terminate process")

                    print(f"<- Sleeping for {minute} seconds...")
                    time.sleep(minute)
                    paused = True
                    break

    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    main()
