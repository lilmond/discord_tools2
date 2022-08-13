import websocket
import threading
import winsound
import requests
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

class DMAlarm(DiscordWebsocket):
    _running = False
    _stopped = threading.Event()
    _alarm_playing = False

    def __init__(self, token, channel_id, notify_user=False):
        self.channel_id = channel_id
        self.notify_user = notify_user
        self._user_id = None
        super().__init__(token)
    
    def initialize(self):
        self._running = True

        self._user_id = self.get_user_id()

        while self._running:
            try:
                print("Initializing...")
                super().initialize()
                print("Initialization completed")
            except Exception:
                print("Initialization error. Retrying...")
                time.sleep(5)
                continue
            while self._running:
                try:
                    data = self.receive_data()
                except Exception:
                    break
                threading.Thread(target=self.on_data_receive, args=[data], daemon=True).start()
        
        self._stopped.set()
    
    def get_user_id(self):
        return requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": self.token}).json()["id"]

    def on_data_receive(self, data):
        if len(data) > 10000: return
        
        try:
            data = json.loads(data)
        except Exception:
            return

        if any([not "t" in data, not "d" in data]): return

        if not data["t"] == "MESSAGE_CREATE": return
        
        message = data["d"]
        if not message: return

        channel_id = message["channel_id"]
        author_id = message["author"]["id"]

        if not channel_id == self.channel_id: return
        if author_id == self._user_id: return

        self.play_alarm()
    
    def play_alarm(self):
        if self._alarm_playing:
            if self.notify_user:
                threading.Thread(target=self.send_notification, args=["Alarm is currently playing..."], daemon=True).start()
            return

        try:
            self._alarm_playing = True
            
            print("Playing alarm...")

            if self.notify_user:
                threading.Thread(target=self.send_notification, args=["Playing alarm..."], daemon=True).start()
            for _ in range(30):
                winsound.PlaySound("alarm.wav", winsound.SND_FILENAME)
        except Exception:
            return
        finally:
            self._alarm_playing = False
    
    def send_notification(self, message):
        requests.post(f"https://discord.com/api/v9/channels/{self.channel_id}/messages", headers={"Authorization": self.token}, json={"content": message})
    
    def stop(self):
        self._running = False
        self._websocket.send(json.dumps({"op": 1, "d": None}))
        self._stopped.wait()

def main():
    token = ""
    channel_id = input("Channel ID: ").strip()
    dmalarm = DMAlarm(token, channel_id, False)
    threading.Thread(target=dmalarm.initialize, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        dmalarm.stop()
        return

if __name__ == "__main__":
    main()
