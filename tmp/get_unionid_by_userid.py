import urllib.request
import json
import sys

APP_KEY = "dingtdwofoowl7hxbjd7"
APP_SECRET = "FvEzquXDKa3UvaL9TYSntDhYzI5p0ulyjo_OPqDM1V6iNQ6J2EJ3aeiE0KHhlQrx"
USER_ID = "145705"  # 从成员管理页面看到的

# Step 1: Get token
print("Getting token...")
token_url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
data = json.dumps({"appKey": APP_KEY, "appSecret": APP_SECRET}).encode('utf-8')
req = urllib.request.Request(token_url, data=data, method='POST')
req.add_header('Content-Type', 'application/json')

with urllib.request.urlopen(req, timeout=10) as response:
    token_data = json.loads(response.read().decode('utf-8'))

access_token = token_data['accessToken']
print(f"Token OK")

# Step 2: Get user info by userId using topapi/v2/user/get
print(f"\nGetting user info for userId={USER_ID}...")
user_url = f"https://oapi.dingtalk.com/topapi/v2/user/get?access_token={access_token}"
payload = json.dumps({"userid": USER_ID}).encode('utf-8')
req = urllib.request.Request(user_url, data=payload, method='POST')
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        user_data = json.loads(response.read().decode('utf-8'))
        
        if user_data.get('errcode') == 0:
            result = user_data.get('result', {})
            print(f"\nUser info:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            union_id = result.get('unionid', '')
            if union_id:
                print(f"\n✅ unionId = {union_id}")
                print(f"\n请把下面的值复制到 sync_from_aitable.py 的 OPERATOR_ID 变量中：")
                print(f'OPERATOR_ID = "{union_id}"')
            else:
                print("\n unionId not found in response!")
        else:
            print(f"\n❌ Error: {user_data.get('errmsg')}")
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"HTTP {e.code}: {error_body}")
