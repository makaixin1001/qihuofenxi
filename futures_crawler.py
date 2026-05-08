from playwright.sync_api import sync_playwright
import json

# 东方财富期货行情页面（真实页面）
URL = "https://quote.eastmoney.com/center/gridlist.html#futures"

# 1. 用 Playwright 爬取实时期货数据
def get_futures_data():
    with sync_playwright() as p:
        # 启动无头浏览器（后台运行，不弹出窗口）
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        )
        
        print("正在访问东方财富期货行情...")
        page.goto(URL, timeout=60000)
        page.wait_for_selector(".table-body", timeout=20000)
        
        # 提取页面数据
        rows = page.query_selector_all(".table-body tr")
        data_list = []
        
        for row in rows[:50]:  # 取前50条
            cols = row.query_selector_all("td")
            if len(cols) < 8:
                continue
            
            item = {
                "f12": cols[1].inner_text().strip(),  # 代码
                "f14": cols[2].inner_text().strip(),  # 名称
                "f2": cols[3].inner_text().strip(),   # 最新价
                "f3": cols[4].inner_text().strip(),   # 涨跌幅
                "f4": cols[4].inner_text().strip().replace("%", ""),  # 涨跌幅数值
                "f5": cols[6].inner_text().strip(),   # 成交量
                "f22": cols[7].inner_text().strip(),  # 持仓量
                "f15": cols[8].inner_text().strip(),  # 最高
                "f16": cols[9].inner_text().strip(),  # 最低
            }
            data_list.append(item)
        
        browser.close()
        print(f"✅ 成功获取 {len(data_list)} 条实时期货数据")
        return data_list

# 2. 生成可部署 GitHub 的静态 HTML
def generate_html(data):
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>期货实时行情</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        body {{ font-family: 'Noto Sans SC', sans-serif; }}
        .positive {{ color: #ef4444; font-weight:600; }}
        .negative {{ color: #22c55e; font-weight:600; }}
    </style>
</head>
<body class="bg-slate-50">
    <div class="max-w-7xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold mb-4">期货实时行情</h1>
        <p class="text-green-600 mb-6">✅ 实时数据由 Playwright 爬取 | 刷新时间：{json.dumps(json.JSONEncoder().encode({"time": __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')})).strip('"')}</p>
        
        <div class="bg-white rounded-2xl border overflow-hidden">
            <table class="w-full text-sm">
                <thead>
                    <tr class="bg-slate-100">
                        <th class="px-4 py-3 text-left">代码</th>
                        <th class="px-4 py-3 text-left">名称</th>
                        <th class="px-4 py-3 text-right">最新价</th>
                        <th class="px-4 py-3 text-right">涨跌幅</th>
                        <th class="px-4 py-3 text-right">成交量</th>
                        <th class="px-4 py-3 text-right">持仓量</th>
                    </tr>
                </thead>
                <tbody>
    '''
    
    for item in data:
        change = str(item['f4']).replace("%", "")
        try:
            change_class = "positive" if float(change) > 0 else "negative" if float(change) < 0 else ""
        except:
            change_class = ""
        
        html += f'''
                    <tr class="border-b hover:bg-slate-50">
                        <td class="px-4 py-3 font-mono">{item['f12']}</td>
                        <td class="px-4 py-3">{item['f14']}</td>
                        <td class="px-4 py-3 text-right font-semibold">{item['f2']}</td>
                        <td class="px-4 py-3 text-right {change_class}">{item['f3']}</td>
                        <td class="px-4 py-3 text-right">{item['f5']}</td>
                        <td class="px-4 py-3 text-right">{item['f22']}</td>
                    </tr>
        '''
    
    html += '''
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>'''
    
    # 保存为 index.html（可直接上传 GitHub）
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ 已生成 index.html，可上传 GitHub Pages！")

# 3. 主程序
if __name__ == "__main__":
    data = get_futures_data()
    generate_html(data)
