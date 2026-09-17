import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "精益改善案例平台建设计划"

# 表头
headers = ["周次", "时间范围", "核心事项", "负责人", "备注"]
ws.append(headers)

# 基于当前对话实际内容的8周计划
data = [
    ("W37", "09.07-09.13", 
     "①确认平台技术选型：原生HTML/CSS/JS静态站点 + GitHub Pages部署\n②定稿制造成本三级分类体系（直接材料/直接人工/制造费用共9个子类）\n输出案例数据字段规范（标题/分类/公司/带级/日期/标签/封面图/实拍图/简介/改善思路/落地成果）", "", ""),
    ("W38", "09.14-09.20", 
     "①完成index.html页面结构搭建（导航栏/轮播Banner/分类卡片/案例网格/详情弹窗/页脚）\n②完成css/style.css样式开发（响应式断点：Desktop/Tablet/Mobile）\n③完成js/data.js数据结构定义与CATEGORY_MAP映射表", "", ""),
    ("W39", "09.21-09.27", 
     "完成js/main.js交互逻辑（轮播自动播放/分类筛选/案例渲染/详情弹窗/返回顶部）\n②录入12条示例案例数据并验证分类切换功能\n③本地浏览器测试全端适配效果", "", "4天工作日"),
    ("W40", "09.28-10.04", 
     "设计钉钉AI表格案例管理模板（字段对齐data.js结构）\n②编写数据转换脚本（钉钉表格→JSON→data.js格式）\n③配置GitHub Actions定时同步工作流（每6小时拉取钉钉数据并推送）", "", "3天工作日（含国庆）"),
    ("W41", "10.05-10.11", 
     "①完成GitHub仓库初始化与SSH密钥配置\n②首次git push部署至GitHub Pages\n③验证线上地址https://lipengzhang123.github.io/-/可正常访问", "", "3天工作日"),
    ("W42", "10.12-10.18", 
     "收集各分子公司真实案例素材（封面图/实拍图/文字描述）\n批量替换Unsplash占位图为真实项目照片\n③优化图片加载性能（lazy loading + WebP格式）", "", ""),
    ("W43", "10.19-10.25", 
     "①组织精益带级人员内测，收集分类准确性/筛选体验/弹窗展示问题\n②修复BUG并优化交互细节（计数badge/筛选高亮/滚动定位）\n③补充平台使用指南文档（如何新增案例/如何修改分类/如何部署更新）", "", ""),
    ("W44", "10.26-11.01", 
     "完成全量案例数据导入与最终校验\n②输出《平台运维手册》《案例投稿规范》《钉钉同步操作指南》\n③正式上线启用，通知各分子公司精益负责人开始使用", "", "")
]

for row in data:
    ws.append(row)

# 设置列宽
ws.column_dimensions['A'].width = 8
ws.column_dimensions['B'].width = 14
ws.column_dimensions['C'].width = 70
ws.column_dimensions['D'].width = 12
ws.column_dimensions['E'].width = 14

# 表头样式
header_font = Font(bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="0052CC", end_color="0052CC", fill_type="solid")
header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)

for col in range(1, len(headers)+1):
    cell = ws.cell(row=1, column=col)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_alignment
    cell.border = thin_border

# 数据行样式
data_alignment = Alignment(vertical="top", wrap_text=True)
alt_fill = PatternFill(start_color="E6F0FF", end_color="E6F0FF", fill_type="solid")

for row_idx in range(2, len(data)+2):
    for col in range(1, len(headers)+1):
        cell = ws.cell(row=row_idx, column=col)
        cell.alignment = data_alignment
        cell.border = thin_border
        if row_idx % 2 == 0:
            cell.fill = alt_fill

# 保存
output_path = r"C:\Users\22104\Desktop\精益改善案例平台建设计划.xlsx"
wb.save(output_path)
print(f"已生成: {output_path}")
