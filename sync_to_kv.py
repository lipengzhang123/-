#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步钉钉AI表格案例数据到 Cloudflare KV
用法: python sync_to_kv.py
前置条件: 
  1. 已安装 wrangler CLI: npm install -g wrangler
  2. 已登录: wrangler login
  3. KV_NAMESPACE_ID 在下方配置
"""

import subprocess
import json
import sys

# ============ 配置区 ============
DWS_EXE = r"C:\Users\22104\.real\.bin\dws\bin\dws.exe"
PYTHON_EXE = r"C:\Users\22104\.real\.bin\python-3.12-windows-x64\python.exe"
AITABLE_BASE_ID = "93NwLYZXWyg41rxYTGlDbaPZJkyEqBQm"
AITABLE_TABLE_ID = "KzrXdgf"
KV_NAMESPACE_ID = "YOUR_KV_NAMESPACE_ID_HERE"  # ← 替换为你的 KV ID
# ================================

def fetch_cases_from_aitable():
    """从钉钉AI表格获取全量案例数据"""
    print("[1/3] 正在从AI表格拉取案例数据...")
    cmd = [
        DWS_EXE, "aitable", "record", "query",
        "--base-id", AITABLE_BASE_ID,
        "--table-id", AITABLE_TABLE_ID,
        "--all", "-f", "json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"[ERROR] dws 命令失败: {result.stderr}")
        sys.exit(1)
    
    data = json.loads(result.stdout)
    records = data.get("records", [])
    print(f"      成功获取 {len(records)} 条案例记录")
    return records

def transform_records(records):
    """将AI表格原始记录转换为前端需要的格式"""
    print("[2/3] 正在转换数据格式...")
    cases = []
    for r in records:
        fields = r.get("fields", {})
        case = {
            "id": r.get("id"),
            "title": fields.get("MS8cFpk", ""),       # Title
            "category": fields.get("yqo08Rp", ""),     # Category
            "summary": fields.get("问题原因字段ID", ""),  # ← 替换为实际字段ID
            "approach": fields.get("YxuDAfu", []),     # Approach (richText)
            "results": fields.get("RraZcE8", []),      # Results
            "company": fields.get("公司字段ID", ""),    # ← 替换
            "level": fields.get("等级字段ID", ""),      # ← 替换
            "date": fields.get("日期字段ID", ""),        # ← 替换
            "cover": fields.get("封面图字段ID", ""),     # ← 替换
            "tags": fields.get("标签字段ID", [])         # ← 替换
        }
        cases.append(case)
    print(f"      转换完成 {len(cases)} 条案例")
    return cases

def upload_to_kv(cases):
    """将案例数据写入 Cloudflare KV"""
    print("[3/3] 正在上传到 Cloudflare KV...")
    cases_json = json.dumps(cases, ensure_ascii=False)
    
    cmd = [
        "wrangler", "kv:key", "put",
        "--namespace-id", KV_NAMESPACE_ID,
        "cases_data",
        cases_json
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"[ERROR] wrangler 上传失败: {result.stderr}")
        sys.exit(1)
    
    print("      ✅ 案例数据已成功写入 KV!")
    print(f"      Key: cases_data")
    print(f"      大小: {len(cases_json)} bytes")

if __name__ == "__main__":
    print("=" * 50)
    print("  AI表格 → Cloudflare KV 同步工具")
    print("=" * 50)
    
    records = fetch_cases_from_aitable()
    cases = transform_records(records)
    upload_to_kv(cases)
    
    print("\n🎉 同步完成! 前端刷新后即可看到最新案例。")
