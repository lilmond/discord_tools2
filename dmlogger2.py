from datetime import datetime
import websocket
import threading
import json
import time
import os

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


class DMLogger(DiscordWebsocket):
    _running = False
    _stopped = threading.Event()

    def __init__(self, token, log_folder_path="./logs/", include_server_messages=False):
        self.log_folder_path = log_folder_path
        self.include_server_messages = include_server_messages
        super().__init__(token)
    
    def initialize(self):
        self._running = True

        if not os.path.exists(self.log_folder_path):
            os.mkdir(self.log_folder_path)

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

        try:
            data = json.loads(data)
        except Exception:
            return
        
        if any([not "t" in data, not "d" in data]): return
        if not data["t"] in ["MESSAGE_CREATE", "MESSAGE_UPDATE", "MESSAGE_DELETE"]: return

        message = data["d"]
        if not message: return

        if not self.include_server_messages:
            if "guild_id" in message: return

        current_date = datetime.now().strftime("%H:%M:%S %Y-%m-%d")
        
        if any([data["t"] == "MESSAGE_CREATE", data["t"] == "MESSAGE_UPDATE"]):
            if not "id" in message: return
            if not "content" in message: return
            if not "channel_id" in message: return
            if not "author" in message: return
            if not "attachments" in message: return

            message_id = message["id"]
            message_content = message["content"]
            channel_id = message["channel_id"]
            author = message["author"]
            attachments = message["attachments"]
            embeds = message["embeds"]

            if not author: return
            if not "username" in author: return
            if not "id" in author: return

            author_username = author["username"]
            author_id = author["id"]
            
            log_text = f"[{current_date}]\n[{data['t'].split('_', 1)[1]}/{channel_id}][{author_id}/{author_username}][{message_id}] {message_content}"

            if attachments:
                log_text += "\n:Attachments:\n"
                for attachment in attachments:
                    if not "url" in attachment: continue
                    log_text += attachment["url"] + "\n"
            
            if embeds:
                log_text += "\n:Embeds:\n"
                for embed in embeds:
                    if not "url" in embed: continue
                    log_text += embed["url"] + "\n"
            
            print(f"{log_text}\n")

            with open(f"{self.log_folder_path}{channel_id}.txt", "a", errors="replace") as file:
                file.write(f"{log_text}\n\n")
                file.close()
        
        elif data["t"] == "MESSAGE_DELETE":
            if not "id" in message: return
            if not "channel_id" in message: return

            message_id = message["id"]
            channel_id = message["channel_id"]

            log_text = f"[{current_date}]\n[DELETE/{channel_id}] {message_id}"

            print(f"{log_text}\n")

            with open(f"{self.log_folder_path}{channel_id}.txt", "a", errors="replace") as file:
                file.write(f"{log_text}\n\n")
                file.close()

    def stop(self):
        self._running = False
        self._websocket.send(json.dumps({"op": 1, "d": None}))
        self._stopped.wait()


def main():
    token = ""
    dmlogger = DMLogger(token)
    threading.Thread(target=dmlogger.initialize, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        dmlogger.stop()
        return

if __name__ == "__main__":
    main()
