from flask import Flask, jsonify
import requests
import random
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOMAINS = [
    "https://push2delay.eastmoney.com/api/qt/clist/get",
    "https://push2.eastmoney.com/api/qt/clist/get",
    "https://36.push2.eastmoney.com/api/qt/clist/get",
]

def get_headers():
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    ]
    return {
        "User-Agent": random.choice(ua_list),
        "Referer": "https://quote.eastmoney.com/center/gridlist.html?type=futures",
        "Origin": "https://quote.eastmoney.com",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

@app.route('/futures', methods=['GET'])
def get_futures():
    params = {
        "np": "1", "fltt": "2", "invt": "2",
        "fields": "f12,f14,f2,f3,f4,f5,f6,f15,f16,f17,f18,f22,f23",
        "fs": "m:113,m:114,m:115,m:116,m:117,m:118,m:119,m:120,m:121,m:122,m:123,m:124,m:125,m:126,m:127,m:128,m:129,m:130,m:131,m:132,m:133,m:134,m:135,m:136,m:137,m:138,m:139,m:140,m:141,m:142",
        "ut": "bd1d9ddb040897e8b1a2a5c0a5a2f5d4",
    }

    for attempt in range(4):
        for base_url in DOMAINS:
            try:
                headers = get_headers()
                resp = requests.get(base_url, params=params, headers=headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("data") and data["data"].get("diff"):
                        items = data["data"]["diff"]
                        result = {
                            "status": "success",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "raw_data": data,
                            "summary": {
                                "涨幅前5": sorted(items, key=lambda x: float(x.get("f4", 0)), reverse=True)[:5],
                                "跌幅前5": sorted(items, key=lambda x: float(x.get("f4", 0)))[:5],
                                "持仓前5": sorted(items, key=lambda x: float(x.get("f22", 0)), reverse=True)[:5],
                                "成交前5": sorted(items, key=lambda x: float(x.get("f5", 0)), reverse=True)[:5],
                            }
                        }
                        return jsonify(result)
            except:
                continue
        time.sleep(1.5)

    return jsonify({"status": "failed", "error": "EastMoney blocked after retries", "data": None}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
