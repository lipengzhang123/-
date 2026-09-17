#!/usr/bin/env python3
"""从钉钉AI表格同步案例数据到网页端"""
import json, re, subprocess, sys, os, shutil
from datetime import datetime

BASE_ID = "93NwLYZXWyg41rxYTGlDbaPZJkyEqBQm"
TABLE_ID = "KzrXdgf"

FIELD_MAP = {
    "title": "MS8cFpk", "category_id": "yqo08Rp", "company": "HaEWw6Q",
    "level_id": "noJlzRG", "date": "320X8MN", "tags": "bXPiAq4",
    "cover": "QhNdlR8", "summary": "J7G36oG", "approach": "YxuDAfu", "results": "RraZcE8"
}

CATEGORY_CODE_MAP = {
    "bJdSTtzMUW": "yield", "e6sP6sLGsf": "substitute", "Tirvo6R5pZ": "reduce",
    "sjo1yrAhRv": "headcount", "2qPo9wD43L": "hours", "aZGSARYjqt": "utilities",
    "tlSppxad6o": "auxiliary", "Uo44qZUI1A": "spare_parts", "BWGbmRyWxV": "indirect_staff"
}

CATEGORY_NAME_MAP = {
    "yield": "良率改善", "substitute": "材料替代", "reduce": "用量降低",
    "headcount": "人数优化", "hours": "工时优化", "utilities": "水电气",
    "auxiliary": "辅料", "spare_parts": "备件", "indirect_staff": "间接人员"
}

def fetch_aitable_data():
    print("正在从AI表格获取数据...")
    # 优先使用已知绝对路径（批处理双击时PATH不含dws）
    dws_path = r"C:\Users\22104\.real\.bin\dws\bin\dws.exe"
    if not os.path.exists(dws_path):
        dws_path = shutil.which("dws")
    if not dws_path:
        print("找不到 dws 命令，请确认已安装钉钉悟空CLI工具")
        return None
    cmd = [dws_path, "aitable", "record", "query", "--base-id", BASE_ID, "--table-id", TABLE_ID, "--all", "-f", "json"]
    try:
        # 关键修复：用 encoding='utf-8' 避免 GBK 解码错误
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=60)
        if result.returncode != 0:
            print(f"dws命令执行失败: {result.stderr}")
            return None
        output_lines = result.stdout.strip().split('\n')
        json_start_idx = next((i for i, line in enumerate(output_lines) if line.strip().startswith('{')), 0)
        json_str = '\n'.join(output_lines[json_start_idx:])
        data = json.loads(json_str)
        records = data.get("data", {}).get("records", [])
        print(f"成功获取 {len(records)} 条记录")
        return records
    except subprocess.TimeoutExpired:
        print("查询超时（60秒）")
        return None
    except Exception as e:
        print(f"未知错误: {e}")
        return None

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

def format_date(date_str):
    if not date_str: return ""
    try:
        return datetime.fromisoformat(date_str.replace('+08:00', '+0800')).strftime("%Y-%m")
    except:
        match = re.match(r'(\d{4}-\d{2})', date_str)
        return match.group(1) if match else date_str

def transform_record(record, index):
    cells = record.get("cells", {})
    category_id = cells.get(FIELD_MAP["category_id"], {}).get("id", "")
    category_code = CATEGORY_CODE_MAP.get(category_id, "yield")
    tags_data = cells.get(FIELD_MAP["tags"], [])
    tags = [tag.get("name", "") for tag in tags_data if isinstance(tag, dict)]
    approach_markdown = cells.get(FIELD_MAP["approach"], {}).get("markdown", "")
    results_markdown = cells.get(FIELD_MAP["results"], {}).get("markdown", "")
    summary = cells.get(FIELD_MAP["summary"], {}).get("markdown", "").strip()
    return {
        "id": index + 1,
        "title": cells.get(FIELD_MAP["title"], ""),
        "category": category_code,
        "categoryName": CATEGORY_NAME_MAP.get(category_code, "良率改善"),
        "company": cells.get(FIELD_MAP["company"], ""),
        "level": cells.get(FIELD_MAP["level_id"], {}).get("name", ""),
        "date": format_date(cells.get(FIELD_MAP["date"], "")),
        "tags": tags,
        "cover": cells.get(FIELD_MAP["cover"], ""),
        "images": [],
        "summary": summary,
        "approach": parse_markdown_list(approach_markdown),
        "results": parse_results(results_markdown)
    }

def update_file(filepath, cases):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        cases_match = re.search(r'(?:var |const )CASES = (\[.*?\]);', content, re.DOTALL)
        if not cases_match:
            print(f"无法找到CASES定义: {filepath}")
            return False
        new_json = json.dumps(cases, ensure_ascii=False, indent=4)
        new_content = content[:cases_match.start(1)] + new_json + content[cases_match.end(1):]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"已更新 {filepath} ({len(cases)} 条案例)")
        return True
    except Exception as e:
        print(f"更新失败 {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("华工科技精益改善案例 - AI表格同步工具")
    print("=" * 60)
    records = fetch_aitable_data()
    if not records:
        print("\n数据获取失败，同步中止")
        sys.exit(1)
    print("\n正在转换数据格式...")
    cases = [transform_record(r, i) for i, r in enumerate(records)]
    print(f"成功转换 {len(cases)} 条案例")
    print("\n正在更新前端文件...")
    success = sum([update_file(r"D:\ruanjian\wukong\js\data.js", cases), update_file(r"D:\ruanjian\wukong\category.html", cases)])
    print()
    print("=" * 60)
    if success == 2:
        print("同步完成！请刷新浏览器查看最新效果。")
        print(f"   - 共 {len(cases)} 条案例")
        print(f"   - 已更新 data.js 和 category.html")
    else:
        print(f"部分更新失败（{success}/2 成功）")
    print("=" * 60)

if __name__ == "__main__":
    main()
