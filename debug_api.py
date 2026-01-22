import urllib.request
import urllib.error
import json

url = 'http://localhost:8000/api/recommend/'
# Request maximum items to trigger any potential data issues
data = json.dumps({'limit': 50}).encode('utf-8')
headers = {'Content-Type': 'application/json'}

print(f"Sending request to {url} with limit=50")

try:
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req) as response:
        print("Success!")
        data = json.loads(response.read().decode('utf-8'))
        print(f"Received {len(data['recommendations'])} recommendations")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}:")
    error_body = e.read().decode('utf-8')
    with open('error.log', 'w') as f:
        f.write(error_body)
    print("Error written to error.log")
except Exception as e:
    print(f"Error: {e}")
