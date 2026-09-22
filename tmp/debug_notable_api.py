import urllib.request, json

APP_KEY = "dingtdwofoowl7hxbjd7"
APP_SECRET = "FvEzquXDKa3UvaL9TYSntDhYzI5p0ulyjo_OPqDM1V6iNQ6J2EJ3aeiE0KHhlQrx"
BASE_ID = "93NwLYZXWyg41rxYTGlDbaPZJkyEqBQm"
TABLE_ID = "KzrXdgf"
OPERATOR_ID = "sfjtIP0upiP4bP9XMMQpN6giEiE"

# Get token
token_url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
data = json.dumps({"appKey": APP_KEY, "appSecret": APP_SECRET}).encode('utf-8')
req = urllib.request.Request(token_url, data=data, method='POST')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req, timeout=10) as response:
    token_data = json.loads(response.read().decode('utf-8'))
access_token = token_data['accessToken']
print(f"Token OK")

# Fetch records with debug output
url = f"https://api.dingtalk.com/v1.0/notable/bases/{BASE_ID}/sheets/{TABLE_ID}/records?operatorId={OPERATOR_ID}"
print(f"\nURL: {url}")
req = urllib.request.Request(url)
req.add_header('x-acs-dingtalk-access-token', access_token)

try:
    with urllib.request.urlopen(req, timeout=15) as response:
        raw = response.read().decode('utf-8')
        print(f"\nRaw response (first 2000 chars):\n{raw[:2000]}")
        
        data = json.loads(raw)
        print(f"\nTop-level keys: {list(data.keys())}")
        
        result = data.get('result', {})
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
        
        records = result.get('records', []) if isinstance(result, dict) else None
        print(f"Records count: {len(records) if records else 'N/A'}")
        
        if records:
            print(f"\nFirst record keys: {list(records[0].keys()) if records else 'empty'}")
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"HTTP {e.code}: {error_body}")
