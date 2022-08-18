# ToDo
# Finish DiscordMessage class
# Finish DiscordEmbed class
# Finish DiscordChannel.create_message method
# Finish DiscordChannel class
# Sleep
# ToDo.sort(key=lambda x: x == "Sleep", reverse=True)

import requests
import base64

class DiscordRequest(object):
    __gateway = "https://discord.com/api/v9"

    def __init__(self, token: str):
        self.token = token
    
    def _request(self, method: str, path: str, payload: dict = None) -> dict:
        http = requests.request(method, f"{self.__gateway}{path}", headers={"Authorization": self.token}, json=payload)

        try:
            return http.json()
        except Exception:
            return http.text
    
    def _param_extract(self, kwargs: dict):
        params = [f'{kwarg}={kwargs[kwarg]}' if i == 0 else f'&{kwarg}={kwargs[kwarg]}' for i, kwarg in enumerate(kwargs)]
        params.sort(key=lambda x: x.startswith("&"))
        params = "".join(params)

        return params


class DiscordMessage(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def set_content(self, content):
        self.content = content


class DiscordEmbed(object):
    def __init__(self):
        pass


class DiscordChannel(DiscordRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_channel(self, channel_id: str):
        return self._request("GET", f"/channels/{channel_id}")
    
    def modify_channel(self, channel_id: str, name: str = None, icon: str = None):
        if icon:
            with open(icon, "rb") as file:
                icon = f"data:image/png;base64,{base64.b64encode(file.read()).decode()}"
                file.close()
        
        return self._request("PATCH", f"/channels/{channel_id}", payload={"name": name, "icon": icon})
    
    def delete_channel(self, channel_id: str):
        return self._request("DELETE", f"/channels/{channel_id}")
    
    def get_channel_messages(self, channel_id: str, **kwargs):
        return self._request("GET", f"/channels/{channel_id}/messages?{self._param_extract(kwargs)}")
    
    def get_channel_message(self, channel_id: str, message_id: str):
        return self._request("GET", f"/channels/{channel_id}/messages/{message_id}")
    
    def create_message(self, channel_id: str, message: DiscordMessage):
        pass


#token = ""
#message = DiscordMessage(content="test")
#print(message.__dict__)
#discord = DiscordChannel(token)
#var = discord.create_message()
#print(var)
