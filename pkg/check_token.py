import requests
import yaml
import os

# 设置基础路径为当前文件夹的上一级
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 读取yaml文件
with open(os.path.join(base_path, 'config/config.yml'), 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

url = config['token']

# 截取token，是url中的token参数，如果不是url，则直接视作token
if 'http' in url:
    token = url.split('=')[1]


def check_token():
    global token
    url = f"https://u95167-bd74-2aef8085.westx.seetacloud.com:8443/flashsummary/getTokenData?token={token}"

    headers = {
        'Accept': 'application/json',  # Assuming JSON is expected
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return "Token有效,您的会员将于" + response.json()['data']['expiry_date'] + "到期"
    else:
        return response.text
