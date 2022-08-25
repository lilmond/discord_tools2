import requests

TOKEN = ""

headers = {
    "Authorization": TOKEN,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
    "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiRGV2aWNlIEkgdXNlIHRvIHdhdGNoIFBvcm5IdWIiLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJicm93c2VyX3VzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTAzLjAuNTA2MC4xMTQgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwMy4wLjUwNjAuMTE0Iiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE0MzU5MiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
}

sessions_request = requests.get("https://discord.com/api/v9/auth/sessions", headers=headers).json()

if "message" in sessions_request:
    print(f"Error: {sessions_request['message']}")
    exit()

if not "user_sessions" in sessions_request:
    print("Error: Unable to get user sessions")
    exit()

sessions = sessions_request["user_sessions"]

print("\n\n")
for session in sessions:
    client_info = session["client_info"]
    id_hash = session["id_hash"]
    approx_last_used_time = session["approx_last_used_time"]
    os = client_info["os"]
    platform = client_info["platform"]
    location = client_info["location"]

    print(f"ID Hash: {id_hash}\nTime: {approx_last_used_time}\nOS: {os}\nPlatform: {platform}\nLocation: {location}\n\n")
