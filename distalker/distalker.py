from datetime import datetime
import websocket
import threading
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

class Distalker(DiscordWebsocket):
    _running = False
    _stopped = threading.Event()
    _logfile = None

    def __init__(self, token, target_texts: list):
        self.target_texts = target_texts
        super().__init__(token)
    
    def initialize(self):
        datenow = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        self._logfile = f"./logs/{datenow}.txt"
        self._running = True

        with open(self._logfile, "a") as file:
            file.write(f"This file was created at: {datenow}\n\n")
            file.close()

        while self._running:
            try:
                print("Initializing...")
                super().initialize()
                print("Initialization completed")
                print("\n")
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
    
    def on_data_receive(self, data):
        if len(data) > 10000: return
        
        datenow = datetime.now().strftime('%H:%M:%S %Y-%m-%d')
        log_text = f"[{datenow}]\n{data}\n\n"

        for text in self.target_texts:
            if text in data:
                print(log_text)
                with open(self._logfile, "a", errors="replace") as file:
                    file.write(log_text)
                    file.close()
    
    def stop(self):
        self._running = False
        self._websocket.send(json.dumps({"op": 1, "d": None}))
        self._stopped.wait()

def main():
    token = ""
    target_texts = input("Target Texts: ").split("|")
    distalker = Distalker(token, target_texts)
    threading.Thread(target=distalker.initialize, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        distalker.stop()
        return

if __name__ == "__main__":
    main()
