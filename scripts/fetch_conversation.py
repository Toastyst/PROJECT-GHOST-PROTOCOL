import urllib.request
import json

url = "https://chat.deepseek.com/share/sj6xg3ugojxo6bpeju"
try:
    with urllib.request.urlopen(url) as response:
        data = response.read().decode('utf-8')
        print(data)
except Exception as e:
    print(f"Error: {e}")