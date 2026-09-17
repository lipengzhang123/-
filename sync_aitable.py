#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI表格 → 本地JSON 同步脚本（自动更新网页）
用法：双击运行或命令行执行 python sync_aitable.py
输出：同目录下的 cases.json + 自动更新 category.html
"""

import subprocess
import json
import os
import sys
import re

# ========== 配置区 ==========
BASE_ID = "93NwLYZXWyg41rxYTGlDbaPZJkyEqBQm"
TABLE_ID = "KzrXdgf"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cases.json")
DWS_PATH = r"C:\Users\22104\.real\.bin\dws\bin\dws.exe"

FIELD_MAP = {
    "title": "MS8cFpk",
    "category": "yqo08Rp",
    "company": "HaEWw6Q",
    "level": "noJlzRG",
    "date": "320X8MN",
    "tags": "bXPiAq4",
    "cover": "QhNdlR8",
    "summary": "J7G36oG",
    "approach": "DB1cta3",
    "results": "RraZcE8"
}

CATEGORY_MAP = {
    "yield": "良率改善",
    "substitute": "材料替代",
    "reduce": "用量降低",
    "headcount": "人数优化",
    "hours": "工时优化",
    "utilities": "水电气",
    "auxiliary": "辅料",
    "spare_parts": "备件",
    "indirect_staff": "间接人员"
}


def run_dws(args):
    """执行 dws 命令并返回 JSON 解析结果"""
    cmd = [DWS_PATH] + args + ["--format", "json"]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        if result.returncode != 0:
            # stderr 也用 UTF-8 解码
            err_msg = result.stderr.decode("utf-8", errors="replace").strip()
            print(f"[错误] dws 命令失败: {err_msg}")
            return None
        # stdout 用 UTF-8 解码（dws 输出 UTF-8，Windows 默认 GBK 会乱码）
        stdout_text = result.stdout.decode("utf-8", errors="replace")
        return json.loads(stdout_text)
    except subprocess.TimeoutExpired:
        print("[错误] dws 命令超时")
        return None
    except json.JSONDecodeError as e:
        print(f"[错误] JSON 解析失败: {e}")
        return None


def fetch_all_records():
    """拉取 AI 表格所有记录"""
    print("  正在拉取全部记录...")
    data = run_dws([
        "aitable", "record", "query",
        "--base-id", BASE_ID,
        "--table-id", TABLE_ID,
        "--limit", "100"
    ])
    if not data:
        return None
    records = data.get("data", {}).get("records", [])
    print(f"  共获取 {len(records)} 条记录")
    return records


def parse_markdown_list(md_obj):
    """解析 markdown 列表为纯文本数组"""
    if not md_obj or not isinstance(md_obj, dict) or "markdown" not in md_obj:
        return []
    lines = md_obj["markdown"].split("\n")
    items = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        cleaned = stripped.lstrip("0123456789")
        cleaned = cleaned.lstrip(".)-*• \t")
        if cleaned:
            items.append(cleaned)
    return items


def parse_results(md_obj):
    """解析成果数据 markdown 为结构化数组"""
    if not md_obj or not isinstance(md_obj, dict) or "markdown" not in md_obj:
        return []
    text = md_obj["markdown"].strip()
    if text.startswith("•"):
        text = text[1:].strip()
    results = []
    parts = text.split("•")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        match = re.search(r'([\d\.]+[%‰万万元元ttmmsshh]|¥[\d\.]+万?|[0-9]+→[0-9]+[a-zA-Z]*|\d+\.\d+|达标|0)', part)
        if match:
            num = match.group(1).strip()
            label = part[:match.start()].strip()
            if not label:
                label = part.replace(num, "").strip()
            results.append({"num": num, "label": label})
        else:
            results.append({"num": "", "label": part})
    return results


def parse_tags(tags_arr):
    """解析标签数组"""
    if not tags_arr:
        return []
    return [t.get("name", t) if isinstance(t, dict) else str(t) for t in tags_arr]


def convert_record(rec, record_id):
    """将 AI 表格记录转换为网页 CASES 格式"""
    cells = rec.get("cells", {})

    category_code = ""
    cat_field = cells.get(FIELD_MAP["category"])
    if isinstance(cat_field, dict):
        category_code = cat_field.get("name", "")
    elif isinstance(cat_field, str):
        category_code = cat_field

    level_val = ""
    level_field = cells.get(FIELD_MAP["level"])
    if isinstance(level_field, dict):
        level_val = level_field.get("name", "")
    elif isinstance(level_field, str):
        level_val = level_field

    date_raw = cells.get(FIELD_MAP["date"], "")
    date_short = date_raw[:7] if date_raw and len(date_raw) >= 7 else date_raw

    # 清理所有可能导致JS语法错误的字符
    def sanitize_text(text):
        if not text:
            return ""
        text = str(text)
        # 替换中文引号为英文引号
        text = text.replace('\u201c', '"').replace('\u201d', '"')
        # 移除换行符和回车符
        text = text.replace("\n", " ").replace("\r", "")
        # 转义反斜杠
        text = text.replace("\\", "\\\\")
        return text

    return {
        "id": record_id,
        "title": sanitize_text(cells.get(FIELD_MAP["title"], "")),
        "category": category_code,
        "categoryName": CATEGORY_MAP.get(category_code, category_code),
        "company": sanitize_text(cells.get(FIELD_MAP["company"], "")),
        "level": sanitize_text(level_val),
        "date": date_short,
        "tags": parse_tags(cells.get(FIELD_MAP["tags"])),
        "cover": cells.get(FIELD_MAP["cover"], ""),
        "images": [],
        "summary": sanitize_text((cells.get(FIELD_MAP["summary"], {}).get("markdown", "") if isinstance(cells.get(FIELD_MAP["summary"]), dict) else "")),
        "approach": [sanitize_text(item) for item in parse_markdown_list(cells.get(FIELD_MAP["approach"]))],
        "results": parse_results(cells.get(FIELD_MAP["results"]))
    }


def update_html_cases(html_path, cases):
    """将 CASES 数据写入 HTML 文件"""
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 紧凑格式（去掉外层[]，因为HTML中已有 var CASES = [...]）
    cases_json_compact = json.dumps(cases, ensure_ascii=False, separators=(",", ":"))[1:-1]

    # 替换 var CASES = [...] 部分
    pattern = r'(var CASES = \[)[\s\S]*?(\];)'
    replacement = rf'\1{cases_json_compact}\2'
    new_html = re.sub(pattern, replacement, html_content)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_html)


def main():
    print("=" * 50)
    print("  AI表格 → 本地JSON 同步工具（自动更新网页）")
    print("=" * 50)
    print(f"Base ID:   {BASE_ID}")
    print(f"Table ID:  {TABLE_ID}")
    print(f"输出文件:  {OUTPUT_FILE}")
    print("-" * 50)

    print("[1/4] 正在从 AI 表格拉取数据...")
    records = fetch_all_records()

    if records is None:
        print("[失败] 无法获取 AI 表格数据，请确认：")
        print("  1. 已安装 dws CLI 工具")
        print("  2. 已登录钉钉客户端")
        print("  3. Base ID / Table ID 正确")
        sys.exit(1)

    if not records:
        print("[警告] AI 表格中暂无记录")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"[完成] 已生成空文件: {OUTPUT_FILE}")
        return

    print(f"[2/4] 共获取 {len(records)} 条记录，正在转换...")

    cases = []
    for idx, rec in enumerate(records, start=1):
        case = convert_record(rec, idx)
        cases.append(case)

    print(f"[3/4] 正在写入 {OUTPUT_FILE} ...")
    # 如果文件被占用，跳过 JSON 写入，仅更新 HTML
    json_written = False
    if os.path.exists(OUTPUT_FILE):
        try:
            os.remove(OUTPUT_FILE)
            json_written = True
        except PermissionError:
            print(f"  [警告] {OUTPUT_FILE} 被浏览器占用，跳过 JSON 写入，仅更新 HTML")
    if json_written or not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(cases, f, ensure_ascii=False, indent=2)
        json_written = True

    # 自动更新 HTML + js/data.js
    html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "category.html")
    data_js_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "js", "data.js")

    if os.path.exists(html_file):
        print(f"[4/5] 正在更新 {html_file} ...")
        update_html_cases(html_file, cases)
        print(f"  ✓ category.html 数据已更新")
    else:
        print(f"[跳过] 未找到 {html_file}")

    if os.path.exists(data_js_file):
        print(f"[5/5] 正在更新 {data_js_file} ...")
        
        # 读取现有的 CATEGORY_MAP 部分（文件开头到 const CASES = [ 之前）
        with open(data_js_file, "r", encoding="utf-8") as f:
            js_content = f.read()
        
        start_marker = "const CASES = ["
        start_idx = js_content.find(start_marker)
        if start_idx == -1:
            start_marker = "var CASES = ["
            start_idx = js_content.find(start_marker)
        
        if start_idx != -1:
            # 提取 CATEGORY_MAP 部分（从文件开头到 const CASES = [ 之前）
            header = js_content[:start_idx]
            
            # 生成新的 CASES 数组
            cases_json = json.dumps(cases, ensure_ascii=False, indent=4)
            
            # 重建文件：header + const CASES = [...] 
            new_js = header + "const CASES = " + cases_json + ";\n"
            
            with open(data_js_file, "w", encoding="utf-8") as f:
                f.write(new_js)
            print(f"  ✓ js/data.js 数据已更新（首页将显示最新计数）")
        else:
            print(f"  [警告] 未找到 CASES 数组声明")
    else:
        print(f"[跳过] 未找到 {data_js_file}")

    print("-" * 50)
    print(f"[成功] 同步完成！共 {len(cases)} 条案例")
    print(f"  JSON 文件: {OUTPUT_FILE}")
    print(f"  文件大小: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")
    if os.path.exists(html_file):
        print(f"  ✓ 网页已自动更新，双击打开即可看到最新数据")
    print("=" * 50)
    print("提示: 在 AI 表格中新增/修改案例后，重新运行本脚本即可同步到网页")


if __name__ == "__main__":
    main()
