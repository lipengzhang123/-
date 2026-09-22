#!/usr/bin/env python3
"""从钉钉AI表格同步案例数据到静态JSON文件"""
import json, re, sys, os
from datetime import datetime
from collections import Counter
import urllib.request

APP_KEY = "dingtdwofoowl7hxbjd7"
APP_SECRET = "FvEzquXDKa3UvaL9TYSntDhYzI5p0ulyjo_OPqDM1V6iNQ6J2EJ3aeiE0KHhlQrx"
BASE_ID = "93NwLYZXWyg41rxYTGlDbaPZJkyEqBQm"
TABLE_ID = "KzrXdgf"
OUTPUT_FILE = "data/cases.json"
OPERATOR_ID = "sfjtIP0upiP4bP9XMMQpN6giEiE"

CATEGORY_CODE_MAP = {
    "yield": "yield", "substitute": "substitute", "reduce": "reduce",
    "headcount": "headcount", "hours": "hours", "utilities": "utilities",
    "auxiliary": "auxiliary", "spare_parts": "spare_parts", "indirect_staff": "indirect_staff"
}

CATEGORY_NAME_MAP = {
    "yield": "良率改善", "substitute": "材料替代", "reduce": "用量降低",
    "headcount": "人数优化", "hours": "工时优化", "utilities": "水电气",
    "auxiliary": "辅料", "spare_parts": "备件", "indirect_staff": "间接人员"
}

def get_access_token():
    token_url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    data = json.dumps({"appKey": APP_KEY, "appSecret": APP_SECRET}).encode('utf-8')
    req = urllib.request.Request(token_url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=10) as response:
        token_data = json.loads(response.read().decode('utf-8'))
    if 'accessToken' not in token_data:
        raise Exception(f"获取token失败: {token_data}")
    return token_data['accessToken']

def fetch_records(access_token):
    """拉取所有记录（支持分页）"""
    all_records = []
    next_token = None
    
    while True:
        url = f"https://api.dingtalk.com/v1.0/notable/bases/{BASE_ID}/sheets/{TABLE_ID}/records?operatorId={OPERATOR_ID}"
        if next_token:
            url += f"&nextToken={next_token}"
        
        req = urllib.request.Request(url)
        req.add_header('x-acs-dingtalk-access-token', access_token)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        records = data.get('records', [])
        all_records.extend(records)
        
        # 检查是否有更多页
        has_more = data.get('hasMore', False)
        next_token = data.get('nextToken')
        
        if not has_more or not next_token:
            break
    
    return all_records

def parse_markdown_list(text):
    if not text: return []
    paragraphs = re.split(r'\n\s*\n', text.strip())
    items = []
    for para in paragraphs:
        para = para.strip()
        if not para: continue
        if para.startswith('• ') or para.startswith('- '):
            items.append(para[2:].strip())
        else:
            items.append(para)
    return items

def parse_results(text):
    if not text: return []
    items = [item.strip() for item in re.split(r'•\s*', text.strip()) if item.strip()]
    results = []
    for item in items:
        match = re.match(r'^([^\d]*?)\s*([\d][\d.%万→\-]*)\s*(.*?)$', item)
        if match:
            label = f"{match.group(1).strip()} {match.group(3).strip()}".strip()
            results.append({"num": match.group(2).strip(), "label": label or match.group(2).strip()})
        else:
            results.append({"num": item, "label": ""})
    return results

def format_date(timestamp_ms):
    """将毫秒时间戳转为 YYYY-MM 格式"""
    if not timestamp_ms: return ""
    try:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%Y-%m")
    except:
        return ""

def transform_record(record, index):
    fields = record.get("fields", {})
    
    # 提取各字段（使用中文列名）
    title = fields.get("标题", "")
    category_code = fields.get("分类代码", {}).get("name", "yield")
    company = fields.get("公司名称", "")
    level_name = fields.get("等级", {}).get("name", "")
    date_timestamp = fields.get("日期", 0)
    tags_data = fields.get("标签", [])
    cover = fields.get("封面图URL", "")
    summary_md = fields.get("问题原因", {}).get("markdown", "").strip()
    approach_md = fields.get("问题解决思路与措施", {}).get("markdown", "")
    results_md = fields.get("项目成果", {}).get("markdown", "")
    
    tags = [tag.get("name", "") for tag in tags_data if isinstance(tag, dict)]
    
    return {
        "id": index + 1,
        "title": title,
        "category": CATEGORY_CODE_MAP.get(category_code, "yield"),
        "categoryName": CATEGORY_NAME_MAP.get(category_code, "良率改善"),
        "company": company,
        "level": level_name,
        "date": format_date(date_timestamp),
        "tags": tags,
        "cover": cover,
        "images": [],
        "summary": summary_md,
        "approach": parse_markdown_list(approach_md),
        "results": parse_results(results_md)
    }

def main():
    print("=" * 60)
    print("华工科技精益改善案例 - AI表格同步工具")
    print("=" * 60)
    
    print("\n[1/3] 获取access_token...")
    try:
        access_token = get_access_token()
        print("✅ Token获取成功")
    except Exception as e:
        print(f"❌ Token获取失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("\n[2/3] 从AI表格拉取数据...")
    try:
        records = fetch_records(access_token)
        print(f"✅ 获取到 {len(records)} 条记录")
    except Exception as e:
        print(f"❌ 数据拉取失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not records:
        print("未获取到任何记录", file=sys.stderr)
        sys.exit(1)
    
    print("\n[3/3] 转换数据格式并保存到JSON...")
    cases = [transform_record(r, i) for i, r in enumerate(records)]
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    output = {
        "errcode": 0,
        "data": cases,
        "total": len(cases),
        "page": 1,
        "size": len(cases),
        "syncTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 成功保存 {len(cases)} 条案例到 {OUTPUT_FILE}")
    print(f"\n 分类统计:")
    category_counts = Counter(c['categoryName'] for c in cases)
    for cat, count in sorted(category_counts.items()):
        print(f"   - {cat}: {count} 条")
    
    print("\n" + "=" * 60)
    print("同步完成！下一步：")
    print("1. git add data/cases.json && git commit -m 'sync cases' && git push")
    print("2. 等待GitHub Pages构建完成")
    print("3. 在钉钉中刷新页面查看效果")
    print("=" * 60)

if __name__ == "__main__":
    main()
