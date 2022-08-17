from queue import Queue
import threading
import requests
import time
import os

class DiscordAPI(object):
    _url = "https://discord.com/api/v9"

    def __init__(self, token):
        self.token = token
    
    def _request(self, method, path, payload=None):
        url = f"{self._url}{path}"

        http = requests.request(method, url, headers={"Authorization": self.token}, json=payload)

        try:
            return http.json()
        except Exception:
            return http.text
        
    def search_files(self, channel_id, target_type="file", offset=0, limit=25):
        return self._request("GET", f"/channels/{channel_id}/messages/search?has={target_type}&offset={offset}&limit={limit}")

DOWNLOAD_PATH = "./Downloads/"

download_queue = Queue()

def downloader_thread():
    if not os.path.exists(DOWNLOAD_PATH):
        os.mkdir(DOWNLOAD_PATH)

    taken_filenames = []

    while True:
        download_info = download_queue.get()
        if type(download_info) == str: return
        subfolder = download_info[0]
        download_url = download_info[2]

        subfolder1, subfolder2 = subfolder.split("/", 1)
        if not os.path.exists(os.path.join(DOWNLOAD_PATH, subfolder1)):
            os.mkdir(os.path.join(DOWNLOAD_PATH, subfolder1))

        output_folder = os.path.join(DOWNLOAD_PATH, subfolder)
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        filename = download_info[1].split(".")
        file_extension = filename.pop(-1)
        filename = ".".join(filename)
        full_filename = f"{filename}.{file_extension}"

        if full_filename in os.listdir(output_folder) or full_filename in taken_filenames:
            iter_number = 0
            while True:
                full_filename = f"{filename}_{iter_number}.{file_extension}"
                iter_number += 1
                if full_filename in os.listdir(output_folder) or full_filename in taken_filenames: continue
                break

        taken_filenames.append(full_filename)

        full_filepath = os.path.join(output_folder, full_filename)

        while True:
            time.sleep(0.1)
            if threading.active_count() > 26: continue
            threading.Thread(target=download_file, args=[download_url, full_filepath], daemon=False).start()
            break
        

def download_file(url, output_path):
    print(f"Downloading {url}")
    
    with requests.get(url, stream=True) as http:
        http.raise_for_status()
        with open(output_path, "wb") as file:
            for chunk in http.iter_content(8192):
                file.write(chunk)

def main():
    token = ""
    channel_id = input("Channel ID: ").strip()
    discord = DiscordAPI(token)

    threading.Thread(target=downloader_thread, daemon=False).start()

    offset = 0

    while True:
        try:
            try:
                fetch = discord.search_files(channel_id, offset=offset)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)
                continue
            
            if "message" in fetch:
                print(f"Error: {fetch['message']}", end=" ")
                if "retry_after" in fetch:
                    print(f"Pausing for {fetch['retry_after']} seconds...")
                    time.sleep(fetch["retry_after"])
                    continue
                print("Retrying in 5 seconds...")
                time.sleep(5)
                continue

            if not "messages" in fetch: continue
            messages = fetch["messages"]

            for messages2 in messages:
                for message in messages2:
                    author_id = message["author"]["id"]
                    attachments = message["attachments"]
                    
                    for attachment in attachments:
                        filename = attachment["filename"]
                        url = attachment["url"]
                        download_info = (f"{channel_id}/{author_id}", filename, url)
                        download_queue.put(download_info)
            
            offset += 25
            print(f"Messages Length: {len(messages)}")
            if len(messages) < 25:
                break

        except KeyboardInterrupt:
            break
    
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    download_queue.queue.clear()
    download_queue.put("quitlife")


if __name__ == "__main__":
    main()
