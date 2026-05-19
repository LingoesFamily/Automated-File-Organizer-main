import os
import sys
import subprocess
import shutil
import threading
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta

# ====================== 多语言支持 ======================
# 当前语言设置
CURRENT_LANG = "zh"  # "zh" 或 "en"

# 语言字典
LANG_DICT = {
    "zh": {
        # 主窗口标题
        "title": "文件归类工具",
        
        # 源目录区域
        "source_dir": "源目录",
        "browse": "浏览...",
        "include_subdirs": "包含子目录",
        
        # 目标目录区域
        "target_dir": "目标目录",
        
        # 归类依据区域
        "classification_criteria": "归类依据",
        "by_filename": "按文件名归类",
        "fuzzy_match": "模糊匹配 (取前N个字符)",
        "chars": "字符数:",
        "by_time_window": "按时间窗口归类",
        "by_file_type": "按文件类型归类",
        "base_time": "基准时间:",
        "time_format": "(格式: 2026-05-09 10:30:00)",
        "time_window_radius": "时间窗口半径:",
        "hours": "小时",
        "time_only": "仅按时间",
        "combine_with_name": "与文件名同时满足",
        
        # 过滤模式区域
        "filter_mode": "过滤模式",
        "use_filter": "使用过滤模式",
        "regex_mode": "正则表达式",
        "wildcard_mode": "通配符",
        "regex_pattern": "正则表达式:",
        "wildcard_pattern": "通配符模式:",
        "include_match": "包含匹配",
        "exclude_match": "排除匹配",
        "select_template": "选择模板",
        
        # 操作模式区域
        "action_mode": "操作模式",
        "copy_mode": "复制 (保留原文件)",
        "move_mode": "剪切 (移动文件)",
        
        # 按钮
        "preview": "预览归类结构",
        "classify": "开始归类",
        
        # 预览区域
        "preview_results": "预览结果 (仅显示目录结构)",
        
        # 状态消息
        "ready": "就绪",
        "collecting_files": "正在收集文件...",
        "preview_complete_no_files": "预览完成，未找到文件",
        "preview_complete_no_matches": "预览完成，无匹配文件",
        "processing": "正在处理文件，请稍候...",
        "processing_progress": "正在处理... {current}/{total} ({percentage}%)",
        "complete": "完成",
        "complete_message": "成功处理 {count} 个文件",
        "complete_status": "完成！处理了 {count} 个文件",
        "error_status": "处理出错",
        
        # 预览文本
        "filter_by": "已通过",
        "matching_files": "匹配文件，",
        "before_filter": "过滤前 ",
        "files": "个文件",
        "after_filter": "，过滤后 ",
        "preview_type_info": "预计将处理 {total} 个文件，分类到 {folders} 个文件类型文件夹中。\n\n",
        "preview_name_info": "预计将处理 {total} 个文件，分类到 {folders} 个文件夹中。\n",
        "preview_single_files": "（已过滤 {count} 个单一文件，仅显示2个及以上相似文件的分类）\n\n",
        "target_structure": "目标目录结构预览：",
        "and_other": "... 及其他 {count} 个文件\n",
        "no_matches_found": "没有找到符合条件的分类。",
        "unclassified_files": "未归类的单一文件（共 {count} 个）：\n",
        "preview_complete_type": "预览完成，共 {total} 个文件将被归类，{folders} 个文件夹（按类型分类）",
        "preview_complete_other": "预览完成，共 {total} 个文件将被归类，{folders} 个文件夹，{unclassified} 个单一文件未归类",
        "include": "包含",
        "exclude": "排除",
        "regex": "正则表达式",
        "wildcard": "通配符",
        "copy": "复制",
        "move": "移动",
        
        # 对话框消息
        "warning": "警告",
        "error_title": "错误",
        "information": "信息",
        "confirm": "确认执行",
        "please_select_source": "请选择有效的源目录",
        "please_select_target": "请选择目标根目录",
        "select_criteria": "请至少选择一种归类依据（文件名、时间或文件类型）",
        "invalid_regex": "无效的正则表达式: {error}",
        "filter_error": "过滤模式错误: {error}",
        "confirm_action": "即将{action} {count} 个文件。\n继续吗？",
        "warning_empty_preview": "预览窗口为空，没有内容可保存",
        "save_success": "预览文本已保存到:\n{path}",
        "save_error": "保存失败: {error}",
        "no_files_found": "没有找到任何文件。",
        "no_matches_after_filter": "过滤后没有找到匹配的文件。",
        
        # 菜单
        "file": "文件",
        "save_preview": "保存预览文本",
        "exit": "退出",
        "help": "帮助",
        "about": "关于",
        "language": "语言",
        "chinese": "中文",
        "english": "English",
        "theme": "主题",
        "light_theme": "明亮",
        "dark_theme": "暗黑",
        "system_theme": "随系统",
        "restore_default_theme": "还原默认主题",
        "custom_bg_image": "自定义背景图片",
        "set_opacity": "设置透明度",
        
        # 主题相关消息
        "theme_changed": "主题已更改为：{theme}",
        "theme_restored": "已还原为默认主题",
        "select_bg_image": "选择背景图片",
        "bg_image_selected": "背景图片已设置",
        "set_opacity": "设置透明度",
        "opacity_label": "透明度：",
        "apply": "应用",
        "opacity_set": "透明度已设置",
        
        # 主题名称
        "light": "明亮",
        "dark": "暗黑",
        "system": "随系统",
        
        # 关于对话框
        "about_title": "文件归类工具 v1.2",
        "features": "功能特点：",
        "feature_name_match": "- 按文件名归类（支持模糊匹配）",
        "feature_time_match": "- 按时间窗口归类",
        "feature_type_match": "- 按文件类型归类（文档、代码、图片等）",
        "feature_filter": "- 过滤模式（正则表达式 / 通配符）",
        "feature_copy_move": "- 复制/移动模式切换",
        "feature_preview": "- 预览功能",
        "feature_progress": "- 进度显示",
        "feature_theme": "- 主题系统（明亮/暗黑/随系统）",
        "feature_custom_bg": "- 自定义背景图片和透明度",
        "wildcard_support": "通配符模式支持：",
        "wildcard_star": "- * : 匹配任意数量的任意字符（如：*me.jpg）",
        "wildcard_question": "- ? : 匹配单个任意字符（如：file?.txt）",
        "wildcard_brackets": "- [] : 匹配字符集中的任意一个字符（如：file[0-9].txt）",
        "wildcard_exclude": "- [!] : 匹配不在字符集中的任意字符（如：file[!0-9].txt）",
        "regex_templates": "正则表达式模板：",
        "templates_list": "- 图片文件名、视频文件名、文档文件名\n- 表格文件、演示文稿、压缩文件\n- 代码文件、音频文件、日期格式\n- 数字序列、邮箱地址、手机号码、IP地址、版本号",
        "usage": "使用说明：",
        "usage_step1": "1. 选择源目录和目标目录",
        "usage_step2": "2. 选择归类方式（可配合过滤模式）",
        "usage_step3": "3. 预览归类结构",
        "usage_step4": "4. 执行归类操作",
        "developer": "开发方：Lingoes Family 武哥使用Trae开发",
        "date": "日期：2026年5月",
        
        # 模板对话框
        "select_template_title": "选择正则表达式模板",
        "double_click_to_select": "双击选择模板，或复制模板内容到输入框",
        "close": "关闭",
        
        # 正则表达式模板名称
        "template_images": "图片文件名",
        "template_videos": "视频文件名",
        "template_documents": "文档文件名",
        "template_spreadsheets": "表格文件",
        "template_presentations": "演示文稿",
        "template_archives": "压缩文件",
        "template_code": "代码文件",
        "template_audio": "音频文件",
        "template_date": "日期格式",
        "template_numbers": "数字序列",
        "template_keyword": "包含关键词",
        "template_email": "邮箱地址",
        "template_phone": "手机号码",
        "template_ip": "IP地址",
        "template_version": "版本号",
    },
    "en": {
        # 主窗口标题
        "title": "File Organizer",
        
        # 源目录区域
        "source_dir": "Source Directory",
        "browse": "Browse...",
        "include_subdirs": "Include Subdirectories",
        
        # 目标目录区域
        "target_dir": "Target Directory",
        
        # 归类依据区域
        "classification_criteria": "Classification Criteria",
        "by_filename": "Classify by Filename",
        "fuzzy_match": "Fuzzy Match (first N characters)",
        "chars": "Characters:",
        "by_time_window": "Classify by Time Window",
        "by_file_type": "Classify by File Type",
        "base_time": "Base Time:",
        "time_format": "(Format: 2026-05-09 10:30:00)",
        "time_window_radius": "Time Window Radius:",
        "hours": "hours",
        "time_only": "Time Only",
        "combine_with_name": "Combine with Filename",
        
        # 过滤模式区域
        "filter_mode": "Filter Mode",
        "use_filter": "Use Filter",
        "regex_mode": "Regular Expression",
        "wildcard_mode": "Wildcard",
        "regex_pattern": "Regex Pattern:",
        "wildcard_pattern": "Wildcard Pattern:",
        "include_match": "Include Match",
        "exclude_match": "Exclude Match",
        "select_template": "Select Template",
        
        # 操作模式区域
        "action_mode": "Action Mode",
        "copy_mode": "Copy (Keep Original)",
        "move_mode": "Move (Cut)",
        
        # 按钮
        "preview": "Preview Structure",
        "classify": "Start Classification",
        
        # 预览区域
        "preview_results": "Preview Results (Directory Structure Only)",
        
        # 状态消息
        "ready": "Ready",
        "collecting_files": "Collecting files...",
        "preview_complete_no_files": "Preview complete, no files found",
        "preview_complete_no_matches": "Preview complete, no matches",
        "processing": "Processing files, please wait...",
        "processing_progress": "Processing... {current}/{total} ({percentage}%)",
        "complete": "Complete",
        "complete_message": "Successfully processed {count} files",
        "complete_status": "Completed! Processed {count} files",
        "error_status": "Error processing",
        
        # 预览文本
        "filter_by": "Filtered by ",
        "matching_files": " matching files, ",
        "before_filter": "",
        "files": " files",
        "after_filter": ", ",
        "preview_type_info": "Will process {total} files into {folders} file type folders.\n\n",
        "preview_name_info": "Will process {total} files into {folders} folders.\n",
        "preview_single_files": "(Filtered {count} single files, only showing categories with 2+ similar files)\n\n",
        "target_structure": "Target Directory Structure Preview:",
        "and_other": "... and {count} more files\n",
        "no_matches_found": "No matching categories found.",
        "unclassified_files": "Unclassified single files ({count} total):\n",
        "preview_complete_type": "Preview complete, {total} files will be classified into {folders} folders (by type)",
        "preview_complete_other": "Preview complete, {total} files will be classified into {folders} folders, {unclassified} single files unclassified",
        "include": "include",
        "exclude": "exclude",
        "regex": "Regex",
        "wildcard": "Wildcard",
        "copy": "copy",
        "move": "move",
        
        # 对话框消息
        "warning": "Warning",
        "error_title": "Error",
        "information": "Information",
        "confirm": "Confirm Execution",
        "please_select_source": "Please select a valid source directory",
        "please_select_target": "Please select a target directory",
        "select_criteria": "Please select at least one classification criteria (Filename, Time, or File Type)",
        "invalid_regex": "Invalid regular expression: {error}",
        "filter_error": "Filter error: {error}",
        "confirm_action": "About to {action} {count} files.\nContinue?",
        "warning_empty_preview": "Preview window is empty, nothing to save",
        "save_success": "Preview text saved to:\n{path}",
        "save_error": "Save failed: {error}",
        "no_files_found": "No files found.",
        "no_matches_after_filter": "No matching files found after filtering.",
        
        # 菜单
        "file": "File",
        "save_preview": "Save Preview",
        "exit": "Exit",
        "help": "Help",
        "about": "About",
        "language": "Language",
        "chinese": "中文",
        "english": "English",
        "theme": "Theme",
        "light_theme": "Light",
        "dark_theme": "Dark",
        "system_theme": "System",
        "restore_default_theme": "Restore Default Theme",
        "custom_bg_image": "Custom Background Image",
        "set_opacity": "Set Opacity",
        
        # 主题相关消息
        "theme_changed": "Theme changed to: {theme}",
        "theme_restored": "Theme restored to default",
        "select_bg_image": "Select Background Image",
        "bg_image_selected": "Background image set",
        "opacity_label": "Opacity:",
        "apply": "Apply",
        "opacity_set": "Opacity set",
        
        # 主题名称
        "light": "Light",
        "dark": "Dark",
        "system": "System",
        
        # 关于对话框
        "about_title": "File Organizer v1.2",
        "features": "Features:",
        "feature_name_match": "- Classify by filename (supports fuzzy match)",
        "feature_time_match": "- Classify by time window",
        "feature_type_match": "- Classify by file type (documents, code, images, etc.)",
        "feature_filter": "- Filter modes (Regex / Wildcard)",
        "feature_copy_move": "- Copy/Move mode toggle",
        "feature_preview": "- Preview function",
        "feature_progress": "- Progress display",
        "feature_theme": "- Theme system (Light/Dark/System)",
        "feature_custom_bg": "- Custom background image and opacity",
        "wildcard_support": "Wildcard Support:",
        "wildcard_star": "- * : Match any number of characters (e.g.: *me.jpg)",
        "wildcard_question": "- ? : Match single character (e.g.: file?.txt)",
        "wildcard_brackets": "- [] : Match any character in set (e.g.: file[0-9].txt)",
        "wildcard_exclude": "- [!] : Match any character not in set (e.g.: file[!0-9].txt)",
        "regex_templates": "Regex Templates:",
        "templates_list": "- Image files, Video files, Document files\n- Spreadsheets, Presentations, Archives\n- Code files, Audio files, Date formats\n- Number sequences, Email addresses, Phone numbers, IP addresses, Version numbers",
        "usage": "Usage Instructions:",
        "usage_step1": "1. Select source and target directories",
        "usage_step2": "2. Select classification criteria (can combine with filter)",
        "usage_step3": "3. Preview classification structure",
        "usage_step4": "4. Execute classification",
        "developer": "Developer: Lingoes Family (Developed with Trae)",
        "date": "Date: May 2026",
        
        # 模板对话框
        "select_template_title": "Select Regex Template",
        "double_click_to_select": "Double-click to select template, or copy content to input box",
        "close": "Close",
        
        # 正则表达式模板名称
        "template_images": "Image Files",
        "template_videos": "Video Files",
        "template_documents": "Document Files",
        "template_spreadsheets": "Spreadsheets",
        "template_presentations": "Presentations",
        "template_archives": "Archives",
        "template_code": "Code Files",
        "template_audio": "Audio Files",
        "template_date": "Date Format",
        "template_numbers": "Number Sequence",
        "template_keyword": "Contains Keyword",
        "template_email": "Email Address",
        "template_phone": "Phone Number",
        "template_ip": "IP Address",
        "template_version": "Version Number",
    }
}

def _(key):
    """翻译函数"""
    return LANG_DICT[CURRENT_LANG].get(key, key)

# ====================== 配置文件管理 ======================
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.ini")

def load_settings():
    """加载配置文件"""
    settings = {
        "language": "zh",
        "theme": "system",
        "custom_bg_image": "",
        "bg_opacity": 0.3
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in settings:
                            if key == "bg_opacity":
                                settings[key] = float(value)
                            else:
                                settings[key] = value
        except Exception:
            pass
    return settings

def save_settings_to_file(settings):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            for key, value in settings.items():
                f.write(f"{key}={value}\n")
    except Exception:
        pass

# 加载配置
config = load_settings()
CURRENT_LANG = config["language"]

# ====================== 主题定义 ======================
THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "frame_bg": "#f0f0f0",
        "button_bg": "#e0e0e0",
        "button_fg": "#000000"
    },
    "dark": {
        "bg": "#2d2d2d",
        "fg": "#ffffff",
        "frame_bg": "#3d3d3d",
        "button_bg": "#4d4d4d",
        "button_fg": "#ffffff"
    }
}

def get_system_theme():
    """获取系统主题（简化版本）"""
    try:
        # Windows系统检测
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        winreg.CloseKey(key)
        return "light" if value == 1 else "dark"
    except:
        return "light"

# ====================== 正则表达式模板 ======================
# 常用正则表达式模板
REGEX_TEMPLATES = {
    "图片文件名": r".*\.(jpg|jpeg|png|gif|bmp|tiff|svg|webp|raw|heic)$",
    "视频文件名": r".*\.(mp4|mkv|avi|mov|wmv|flv|webm|m4v|mpeg|mpg)$",
    "文档文件名": r".*\.(doc|docx|docm|pdf|txt|md|rtf|odt)$",
    "表格文件": r".*\.(xls|xlsx|xlsm|xlsb|csv)$",
    "演示文稿": r".*\.(ppt|pptx|pptm|pps|ppsx)$",
    "压缩文件": r".*\.(zip|rar|7z|tar|gz|bz2|xz)$",
    "代码文件": r".*\.(py|java|cpp|c|h|js|ts|html|css|go|rs)$",
    "音频文件": r".*\.(mp3|wav|ogg|flac|aac|m4a)$",
    "日期格式": r".*(\d{4}-\d{2}-\d{2}|\d{8}).*",
    "数字序列": r".*(\d{3,}).*",
    "包含关键词": r".*keyword.*",
    "邮箱地址": r".*@.*\..*",
    "手机号码": r".*1[3-9]\d{9}.*",
    "IP地址": r".*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*",
    "版本号": r".*v?\d+\.\d+(\.\d+)?.*"
}

def match_regex_pattern(filename, pattern):
    """使用正则表达式匹配文件名"""
    try:
        return re.match(pattern, filename, re.IGNORECASE) is not None
    except re.error:
        return False

def filter_files_by_regex(files, regex_pattern):
    """根据正则表达式过滤文件列表"""
    if not regex_pattern:
        return files
    try:
        compiled = re.compile(regex_pattern, re.IGNORECASE)
        return [f for f in files if compiled.search(os.path.basename(f))]
    except re.error:
        return files

def validate_regex(pattern):
    """验证正则表达式是否有效"""
    try:
        re.compile(pattern)
        return True, None
    except re.error as e:
        return False, str(e)

# ====================== 通配符模式支持 ======================
def wildcard_to_regex(wildcard_pattern):
    """
    将通配符模式转换为正则表达式
    支持的通配符:
    - * : 匹配任意数量的任意字符（包括零个）
    - ? : 匹配单个任意字符
    - [] : 匹配字符集中的任意一个字符
    - [!] : 匹配不在字符集中的任意字符
    """
    if not wildcard_pattern:
        return ""
    
    # 转义正则表达式特殊字符（除了通配符）
    special_chars = '.^$+{}()|\\'
    result = []
    i = 0
    while i < len(wildcard_pattern):
        char = wildcard_pattern[i]
        
        if char == '*':
            result.append('.*')
            i += 1
        elif char == '?':
            result.append('.')
            i += 1
        elif char == '[':
            # 处理字符集
            result.append('[')
            i += 1
            if i < len(wildcard_pattern) and wildcard_pattern[i] == '!':
                result.append('^')
                i += 1
            while i < len(wildcard_pattern) and wildcard_pattern[i] != ']':
                result.append(wildcard_pattern[i])
                i += 1
            if i < len(wildcard_pattern) and wildcard_pattern[i] == ']':
                result.append(']')
                i += 1
        elif char in special_chars:
            result.append('\\')
            result.append(char)
            i += 1
        else:
            result.append(char)
            i += 1
    
    return ''.join(result)

def match_wildcard_pattern(filename, wildcard_pattern):
    """使用通配符模式匹配文件名"""
    if not wildcard_pattern:
        return True
    regex_pattern = wildcard_to_regex(wildcard_pattern)
    try:
        return re.match(regex_pattern, filename, re.IGNORECASE) is not None
    except re.error:
        return False

# ====================== 文件处理核心逻辑 ======================
def parse_time_window(time_str, delta_hours):
    """解析时间字符串，返回起止时间"""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %H", "%Y-%m-%d"):
        try:
            base_time = datetime.strptime(time_str, fmt)
            if fmt == "%Y-%m-%d":
                base_time = base_time.replace(hour=0, minute=0, second=0)
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"无法解析时间: {time_str}")
    start_time = base_time - timedelta(hours=delta_hours)
    end_time = base_time + timedelta(hours=delta_hours)
    return start_time, end_time

def sanitize_folder_name(name):
    """清理文件夹名称，移除Windows非法字符"""
    invalid_chars = '<>:"/\\|?*'
    for c in invalid_chars:
        name = name.replace(c, '_')
    # 移除末尾的空格和点
    return name.rstrip('. ').strip()

def get_file_group_by_name(filename, fuzzy_len):
    """根据文件名（不含扩展名）返回分组关键词"""
    base = os.path.splitext(filename)[0]
    if fuzzy_len > 0:
        return sanitize_folder_name(base[:fuzzy_len])
    else:
        return sanitize_folder_name(base)

def get_file_group_by_time(filepath, start_time, end_time):
    """返回时间窗口标签或None"""
    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
    if start_time <= mtime <= end_time:
        return start_time.strftime("%Y%m%d_%H%M") + "_to_" + end_time.strftime("%Y%m%d_%H%M")
    return None

# 文件类型分类映射
FILE_TYPE_GROUPS = {
    # 文档类
    "documents": [".doc", ".docx", ".docm", ".dot", ".dotx",
                  ".xls", ".xlsx", ".xlsm", ".xlsb", ".csv",
                  ".ppt", ".pptx", ".pptm", ".pps", ".ppsx",
                  ".pdf", ".txt", ".rtf", ".md", ".odt"],
    
    # 编程类
    "code": [".py", ".java", ".cpp", ".c", ".h", ".hpp",
             ".js", ".jsx", ".ts", ".tsx", ".html", ".css",
             ".xml", ".json", ".yaml", ".yml", ".ini", ".cfg",
             ".sh", ".bat", ".ps1", ".go", ".rs", ".rb"],
    
    # 图片类
    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff",
               ".svg", ".webp", ".ico", ".raw", ".heic"],
    
    # 视频类
    "videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv",
               ".webm", ".m4v", ".mpeg", ".mpg"],
    
    # 音频类
    "audio": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a",
              ".wma", ".opus"],
    
    # 压缩类
    "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2",
                 ".xz", ".cab", ".iso"],
    
    # 可执行文件
    "executables": [".exe", ".msi", ".dll", ".bat", ".cmd"],
    
    # 数据库
    "databases": [".db", ".sqlite", ".mdb", ".accdb", ".sql"],
    
    # 其他
    "other": []  # 默认分类
}

def get_file_group_by_type(filename):
    """根据文件扩展名返回类型分类"""
    ext = os.path.splitext(filename)[1].lower()
    for group_name, extensions in FILE_TYPE_GROUPS.items():
        if ext in extensions:
            return group_name
    return "other"

def collect_files(src_dir, recursive):
    """收集所有文件路径"""
    files = []
    if recursive:
        for root, _, filenames in os.walk(src_dir):
            for f in filenames:
                files.append(os.path.join(root, f))
    else:
        for item in os.listdir(src_dir):
            full = os.path.join(src_dir, item)
            if os.path.isfile(full):
                files.append(full)
    return files

def safe_copy(src, dst_dir):
    """复制文件并自动处理重名"""
    os.makedirs(dst_dir, exist_ok=True)
    dst_path = os.path.join(dst_dir, os.path.basename(src))
    counter = 1
    while os.path.exists(dst_path):
        name, ext = os.path.splitext(os.path.basename(src))
        dst_path = os.path.join(dst_dir, f"{name}_{counter}{ext}")
        counter += 1
    shutil.copy2(src, dst_path)
    return dst_path

def safe_move(src, dst_dir):
    """移动文件并自动处理重名"""
    os.makedirs(dst_dir, exist_ok=True)
    dst_path = os.path.join(dst_dir, os.path.basename(src))
    counter = 1
    while os.path.exists(dst_path):
        name, ext = os.path.splitext(os.path.basename(src))
        dst_path = os.path.join(dst_dir, f"{name}_{counter}{ext}")
        counter += 1
    shutil.move(src, dst_path)
    return dst_path

def get_classification_plan(files, args):
    """
    返回一个字典：{目标文件夹路径: [源文件路径列表]}
    args 包含:
        by_name (bool)
        fuzzy_len (int)
        by_time (bool)
        by_type (bool)
        start_time (datetime) / end_time (datetime) / time_label (str)
        target_root (str)
        mode_combine (bool) -- 若为True则需同时满足两个条件
    """
    plan = {}
    for filepath in files:
        target_subdir = None

        if args.get('by_type', False):
            # 按文件类型分类（单独使用，不与其他方式混合）
            type_key = get_file_group_by_type(os.path.basename(filepath))
            target_subdir = os.path.join(args['target_root'], "by_type", type_key)
        elif args['by_name'] and args['by_time'] and args['mode_combine']:
            # 同时满足名称和时间条件
            name_key = get_file_group_by_name(os.path.basename(filepath), args['fuzzy_len'])
            time_key = get_file_group_by_time(filepath, args['start_time'], args['end_time'])
            if time_key:
                target_subdir = os.path.join(args['target_root'], args['time_label'], name_key)
        elif args['by_name'] and not args['by_time']:
            name_key = get_file_group_by_name(os.path.basename(filepath), args['fuzzy_len'])
            target_subdir = os.path.join(args['target_root'], "by_name", name_key)
        elif args['by_time'] and not args['by_name']:
            time_key = get_file_group_by_time(filepath, args['start_time'], args['end_time'])
            if time_key:
                target_subdir = os.path.join(args['target_root'], "by_time", time_key)

        if target_subdir:
            plan.setdefault(target_subdir, []).append(filepath)
    
    # 按文件类型分类时不过滤（所有类型都显示），其他方式过滤掉只有1个文件的分类
    if args.get('by_type', False):
        return plan
    else:
        filtered_plan = {k: v for k, v in plan.items() if len(v) >= 2}
        return filtered_plan

def execute_plan(plan, move, progress_callback=None):
    """实际复制或移动文件
    progress_callback: 可选的回调函数，接收 (current, total) 参数
    """
    count = 0
    total_files = sum(len(lst) for lst in plan.values())
    processed = 0
    
    for dst_dir, src_files in plan.items():
        # 确保目标目录存在
        os.makedirs(dst_dir, exist_ok=True)
        for src in src_files:
            # 检查源文件是否存在
            if not os.path.isfile(src):
                print(f"警告：源文件不存在，跳过: {src}")
                processed += 1
                if progress_callback:
                    progress_callback(processed, total_files)
                continue
            if move:
                safe_move(src, dst_dir)
            else:
                safe_copy(src, dst_dir)
            count += 1
            processed += 1
            if progress_callback:
                progress_callback(processed, total_files)
    return count

# ====================== GUI 界面 ======================
class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        root.title(_("title"))
        root.geometry("1000x750")  # 增加窗口宽度
        root.resizable(True, True)

        # 配置相关
        self.config = config.copy()
        self.current_theme = self.config["theme"]
        self.custom_bg_image = self.config["custom_bg_image"]
        self.bg_opacity = self.config["bg_opacity"]
        
        # 背景图片标签
        self.bg_label = None

        # 变量
        self.source_dir = tk.StringVar()
        self.target_dir = tk.StringVar()
        self.recursive = tk.BooleanVar(value=True)
        self.move_mode = tk.BooleanVar(value=False)  # False=复制, True=移动

        self.by_name = tk.BooleanVar(value=False)
        self.fuzzy_len = tk.IntVar(value=0)
        self.use_fuzzy = tk.BooleanVar(value=False)

        self.by_time = tk.BooleanVar(value=False)
        self.time_point = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.delta_hours = tk.IntVar(value=2)
        self.combine_mode = tk.BooleanVar(value=True)  # 同时满足两个条件
        
        self.by_type = tk.BooleanVar(value=False)  # 按文件类型分类

        # 正则表达式/通配符相关变量
        self.use_regex = tk.BooleanVar(value=False)  # 是否使用正则表达式/通配符过滤
        self.regex_pattern = tk.StringVar(value="")  # 过滤模式
        self.regex_match_type = tk.StringVar(value="include")  # include=包含匹配, exclude=排除匹配
        self.pattern_mode = tk.StringVar(value="regex")  # regex=正则表达式, wildcard=通配符模式
        
        # 预览状态
        self.preview_plan = None

        # 创建界面
        self.apply_theme()
        self.create_widgets()

    def create_widgets(self):
        # 创建菜单
        self.create_menu()
        
        # 源目录
        frame_src = ttk.LabelFrame(self.root, text=_(("source_dir")), padding=5)
        frame_src.pack(fill="x", padx=10, pady=5)
        ttk.Entry(frame_src, textvariable=self.source_dir, width=60).pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(frame_src, text=_(("browse")), command=self.browse_source).pack(side="right")
        ttk.Checkbutton(frame_src, text=_(("include_subdirs")), variable=self.recursive).pack(side="right", padx=5)

        # 目标目录
        frame_dst = ttk.LabelFrame(self.root, text=_(("target_dir")), padding=5)
        frame_dst.pack(fill="x", padx=10, pady=5)
        ttk.Entry(frame_dst, textvariable=self.target_dir, width=60).pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(frame_dst, text=_(("browse")), command=self.browse_target).pack(side="right")

        # 归类依据
        frame_criteria = ttk.LabelFrame(self.root, text=_(("classification_criteria")), padding=5)
        frame_criteria.pack(fill="x", padx=10, pady=5)

        # 按文件名
        cb_name = ttk.Checkbutton(frame_criteria, text=_(("by_filename")), variable=self.by_name, command=self.toggle_name_options)
        cb_name.grid(row=0, column=0, sticky="w")
        self.name_frame = ttk.Frame(frame_criteria)
        self.name_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=20)
        self.fuzzy_cb = ttk.Checkbutton(self.name_frame, text=_(("fuzzy_match")), variable=self.use_fuzzy, command=self.toggle_fuzzy)
        self.fuzzy_cb.pack(anchor="w")
        self.fuzzy_len_frame = ttk.Frame(self.name_frame)
        self.fuzzy_len_frame.pack(anchor="w", padx=20)
        ttk.Label(self.fuzzy_len_frame, text=_(("chars"))).pack(side="left")
        self.fuzzy_spin = ttk.Spinbox(self.fuzzy_len_frame, from_=1, to=50, width=5, textvariable=self.fuzzy_len, state="disabled")
        self.fuzzy_spin.pack(side="left")
        self.name_frame.grid_remove()  # 初始隐藏

        # 按时间
        cb_time = ttk.Checkbutton(frame_criteria, text=_(("by_time_window")), variable=self.by_time, command=self.toggle_time_options)
        cb_time.grid(row=0, column=1, sticky="w", padx=80)  # 增加水平间距
        self.time_frame = ttk.Frame(frame_criteria)
        self.time_frame.grid(row=1, column=1, rowspan=2, sticky="w", padx=100)  # 增加水平间距
        
        # 按文件类型
        cb_type = ttk.Checkbutton(frame_criteria, text=_(("by_file_type")), variable=self.by_type, command=self.toggle_type_options)
        cb_type.grid(row=0, column=2, sticky="w", padx=80)  # 增加水平间距
        ttk.Label(self.time_frame, text=_(("base_time"))).grid(row=0, column=0, sticky="e")
        ttk.Entry(self.time_frame, textvariable=self.time_point, width=25).grid(row=0, column=1, padx=5)
        ttk.Label(self.time_frame, text=_(("time_format"))).grid(row=0, column=2, sticky="w")
        ttk.Label(self.time_frame, text=_(("time_window_radius"))).grid(row=1, column=0, sticky="e")
        ttk.Spinbox(self.time_frame, from_=1, to=24, textvariable=self.delta_hours, width=5).grid(row=1, column=1, sticky="w")
        ttk.Label(self.time_frame, text=_(("hours"))).grid(row=1, column=2, sticky="w")
        ttk.Radiobutton(self.time_frame, text=_(("time_only")), variable=self.combine_mode, value=False).grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(self.time_frame, text=_(("combine_with_name")), variable=self.combine_mode, value=True).grid(row=3, column=0, columnspan=2, sticky="w")
        self.time_frame.grid_remove()

        # 过滤模式（正则表达式/通配符）
        frame_regex = ttk.LabelFrame(self.root, text=_(("filter_mode")), padding=5)
        frame_regex.pack(fill="x", padx=10, pady=5)
        
        self.regex_cb = ttk.Checkbutton(frame_regex, text=_(("use_filter")), variable=self.use_regex, command=self.toggle_regex_options)
        self.regex_cb.pack(side="left")
        
        self.regex_frame = ttk.Frame(frame_regex)
        self.regex_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        # 模式选择：正则表达式 / 通配符
        ttk.Radiobutton(self.regex_frame, text=_(("regex_mode")), variable=self.pattern_mode, value="regex", command=self.update_pattern_label).pack(side="left", padx=5)
        ttk.Radiobutton(self.regex_frame, text=_(("wildcard_mode")), variable=self.pattern_mode, value="wildcard", command=self.update_pattern_label).pack(side="left", padx=5)
        
        # 模式输入框
        self.pattern_label = ttk.Label(self.regex_frame, text=_(("regex_pattern")))
        self.pattern_label.pack(side="left")
        self.regex_entry = ttk.Entry(self.regex_frame, textvariable=self.regex_pattern, width=40)
        self.regex_entry.pack(side="left", padx=5)
        
        # 匹配类型选择
        ttk.Radiobutton(self.regex_frame, text=_(("include_match")), variable=self.regex_match_type, value="include").pack(side="left", padx=5)
        ttk.Radiobutton(self.regex_frame, text=_(("exclude_match")), variable=self.regex_match_type, value="exclude").pack(side="left", padx=5)
        
        # 模板按钮
        self.regex_template_btn = ttk.Button(self.regex_frame, text=_(("select_template")), command=self.show_regex_templates)
        self.regex_template_btn.pack(side="left", padx=5)
        
        # 验证状态
        self.regex_status = ttk.Label(self.regex_frame, text="", foreground="green")
        self.regex_status.pack(side="left", padx=5)
        
        # 绑定验证
        self.regex_pattern.trace_add("write", self.validate_pattern_input)
        
        self.regex_frame.pack_forget()  # 初始隐藏

        # 操作模式
        frame_action = ttk.LabelFrame(self.root, text=_(("action_mode")), padding=5)
        frame_action.pack(fill="x", padx=10, pady=5)
        ttk.Radiobutton(frame_action, text=_(("copy_mode")), variable=self.move_mode, value=False).pack(side="left", padx=10)
        ttk.Radiobutton(frame_action, text=_(("move_mode")), variable=self.move_mode, value=True).pack(side="left", padx=10)

        # 按钮栏
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.pack(fill="x", padx=10, pady=5)
        self.preview_btn = ttk.Button(frame_buttons, text=_(("preview")), command=self.preview)
        self.preview_btn.pack(side="left", padx=5)
        self.classify_btn = ttk.Button(frame_buttons, text=_(("classify")), command=self.start_classify)
        self.classify_btn.pack(side="left", padx=5)

        # 预览区域
        frame_preview = ttk.LabelFrame(self.root, text=_(("preview_results")), padding=5)
        frame_preview.pack(fill="both", expand=True, padx=10, pady=5)
        self.preview_text = tk.Text(frame_preview, wrap="none", height=15)  # 不换行
        scroll_y = ttk.Scrollbar(frame_preview, command=self.preview_text.yview)
        scroll_x = ttk.Scrollbar(frame_preview, command=self.preview_text.xview, orient="horizontal")
        self.preview_text.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.preview_text.pack(side="top", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        # 进度条
        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(fill="x", side="bottom", padx=5, pady=2)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", side="top")
        
        # 状态栏
        self.status_var = tk.StringVar(value=_(("ready")))
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(fill="x", side="bottom", padx=5, pady=2)

    def browse_source(self):
        path = filedialog.askdirectory(title=_(("source_dir")))
        if path:
            self.source_dir.set(path)

    def browse_target(self):
        path = filedialog.askdirectory(title=_(("target_dir")))
        if path:
            self.target_dir.set(path)

    def toggle_name_options(self):
        if self.by_name.get():
            self.name_frame.grid()
        else:
            self.name_frame.grid_remove()

    def toggle_fuzzy(self):
        if self.use_fuzzy.get():
            self.fuzzy_spin.config(state="normal")
        else:
            self.fuzzy_spin.config(state="disabled")
            self.fuzzy_len.set(0)

    def toggle_time_options(self):
        if self.by_time.get():
            self.time_frame.grid()
        else:
            self.time_frame.grid_remove()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=_(("save_preview")), command=self.save_preview_text)
        file_menu.add_separator()
        file_menu.add_command(label=_(("exit")), command=self.root.quit)
        menubar.add_cascade(label=_(("file")), menu=file_menu)
        
        # 主题子菜单
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label=_(("light_theme")), command=lambda: self.change_theme("light"))
        theme_menu.add_command(label=_(("dark_theme")), command=lambda: self.change_theme("dark"))
        theme_menu.add_command(label=_(("system_theme")), command=lambda: self.change_theme("system"))
        theme_menu.add_separator()
        theme_menu.add_command(label=_(("restore_default_theme")), command=self.restore_default_theme)
        theme_menu.add_separator()
        theme_menu.add_command(label=_(("custom_bg_image")), command=self.select_custom_background)
        theme_menu.add_command(label=_(("set_opacity")), command=self.set_bg_opacity)
        
        # 语言子菜单
        lang_menu = tk.Menu(menubar, tearoff=0)
        lang_menu.add_command(label=_(("chinese")), command=lambda: self.change_language("zh"))
        lang_menu.add_command(label=_(("english")), command=lambda: self.change_language("en"))
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=_(("about")), command=self.show_about)
        help_menu.add_separator()
        help_menu.add_cascade(label=_(("theme")), menu=theme_menu)
        help_menu.add_separator()
        help_menu.add_cascade(label=_(("language")), menu=lang_menu)
        menubar.add_cascade(label=_(("help")), menu=help_menu)
        
        self.root.config(menu=menubar)

    def change_language(self, lang):
        """切换语言"""
        global CURRENT_LANG
        CURRENT_LANG = lang
        # 保存语言设置到配置文件
        self.save_settings()
        messagebox.showinfo(_("information"), _("language") + ": " + _("chinese" if lang == "zh" else "english"))
        # 使用 subprocess 重启应用，避免窗口闪烁问题
        python = sys.executable
        self.root.destroy()
        subprocess.Popen([python] + sys.argv)
        sys.exit(0)

    def save_settings(self):
        """保存配置到文件"""
        self.config["language"] = CURRENT_LANG
        self.config["theme"] = self.current_theme
        self.config["custom_bg_image"] = self.custom_bg_image
        self.config["bg_opacity"] = self.bg_opacity
        save_settings_to_file(self.config)

    def apply_theme(self):
        """应用主题"""
        theme_name = self.current_theme
        if theme_name == "system":
            theme_name = get_system_theme()
        
        if theme_name in THEMES:
            theme = THEMES[theme_name]
            self.root.config(bg=theme["bg"])
            
            # 更新ttk样式
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('.', 
                          background=theme["frame_bg"],
                          foreground=theme["fg"],
                          fieldbackground=theme["bg"])
            style.configure('TLabel', background=theme["frame_bg"], foreground=theme["fg"])
            style.configure('TButton', background=theme["button_bg"], foreground=theme["button_fg"])
            style.configure('TLabelframe', background=theme["bg"], foreground=theme["fg"])
            style.configure('TLabelframe.Label', background=theme["bg"], foreground=theme["fg"])
            style.configure('TCheckbutton', background=theme["frame_bg"], foreground=theme["fg"])
            style.configure('TRadiobutton', background=theme["frame_bg"], foreground=theme["fg"])
            style.configure('TProgressbar', background=theme["button_bg"])
            
            # 更新预览文本框样式（tk.Text组件需要单独设置）
            if hasattr(self, 'preview_text') and self.preview_text:
                self.preview_text.config(bg=theme["frame_bg"], fg=theme["fg"])
            
            # 更新菜单背景
            self.root.config(menu=None)
            
        # 应用自定义背景图片
        self.apply_custom_background()

    def apply_custom_background(self):
        """应用自定义背景图片"""
        # 移除旧的背景标签
        if self.bg_label:
            self.bg_label.destroy()
            self.bg_label = None
            
        if self.custom_bg_image and os.path.exists(self.custom_bg_image):
            try:
                from PIL import Image, ImageTk
                # 获取当前窗口大小
                window_width = self.root.winfo_width()
                window_height = self.root.winfo_height()
                
                # 如果窗口还没完全初始化，使用默认大小
                if window_width <= 1 or window_height <= 1:
                    window_width = 1000
                    window_height = 750
                
                # 打开图片
                image = Image.open(self.custom_bg_image)
                
                # 计算缩放比例 - 覆盖整个窗口
                scale = max(window_width / image.width, window_height / image.height)
                new_width = int(image.width * scale)
                new_height = int(image.height * scale)
                
                # 缩放图片
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 创建透明图片
                image = image.convert("RGBA")
                alpha = int(255 * self.bg_opacity)
                image.putalpha(alpha)
                
                self.bg_photo = ImageTk.PhotoImage(image)
                
                # 创建背景标签 - 使用place放置在整个窗口
                self.bg_label = tk.Label(self.root, image=self.bg_photo)
                self.bg_label.place(x=0, y=0, width=new_width, height=new_height)
                self.bg_label.lower()  # 置于底层
                
                # 更新所有组件的背景为透明
                self.root.config(bg='')
                
                # 设置ttk样式使框架透明
                style = ttk.Style()
                style.configure('TLabelframe', background='', foreground='black')
                style.configure('TLabelframe.Label', background='', foreground='black')
                
            except Exception as e:
                print(f"Failed to load background image: {e}")
        else:
            # 如果没有自定义背景，恢复默认背景色
            self.root.config(bg=self.get_current_theme_bg())
            
    def get_current_theme_bg(self):
        """获取当前主题的背景色"""
        theme_name = self.current_theme
        if theme_name == "system":
            theme_name = get_system_theme()
        if theme_name in THEMES:
            return THEMES[theme_name]["bg"]
        return "#ffffff"

    def change_theme(self, theme):
        """切换主题"""
        self.current_theme = theme
        self.save_settings()
        self.apply_theme()
        messagebox.showinfo(_("information"), _("theme_changed").format(theme=_(theme)))

    def restore_default_theme(self):
        """还原默认主题（系统主题）并清除自定义背景"""
        self.current_theme = "system"
        self.custom_bg_image = ""
        self.bg_opacity = 0.3
        # 移除背景图片
        if self.bg_label:
            self.bg_label.destroy()
            self.bg_label = None
        # 恢复默认样式
        self.apply_theme()
        self.save_settings()
        messagebox.showinfo(_("information"), _("theme_restored"))

    def select_custom_background(self):
        """选择自定义背景图片"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All Files", "*.*")],
            title=_(("select_bg_image"))
        )
        if file_path:
            self.custom_bg_image = file_path
            self.apply_custom_background()
            self.save_settings()
            messagebox.showinfo(_("information"), _("bg_image_selected"))

    def set_bg_opacity(self):
        """设置背景透明度"""
        opacity_win = tk.Toplevel(self.root)
        opacity_win.title(_("set_opacity"))
        opacity_win.geometry("300x150")
        opacity_win.resizable(False, False)
        
        ttk.Label(opacity_win, text=_(("opacity_label"))).pack(pady=10)
        
        opacity_var = tk.DoubleVar(value=self.bg_opacity * 100)
        ttk.Scale(opacity_win, from_=0, to=100, variable=opacity_var, orient="horizontal").pack(fill="x", padx=20, pady=5)
        
        def apply_opacity():
            self.bg_opacity = opacity_var.get() / 100
            self.apply_custom_background()
            self.save_settings()
            opacity_win.destroy()
            messagebox.showinfo(_("information"), _("opacity_set"))
        
        ttk.Button(opacity_win, text=_(("apply")), command=apply_opacity).pack(pady=10)

    def show_about(self):
        """显示关于对话框"""
        about_text = f"""{_("about_title")}

{_("features")}
{_("feature_name_match")}
{_("feature_time_match")}
{_("feature_type_match")}
{_("feature_filter")}
{_("feature_copy_move")}
{_("feature_preview")}
{_("feature_progress")}
{_("feature_theme")}
{_("feature_custom_bg")}

{_("wildcard_support")}
{_("wildcard_star")}
{_("wildcard_question")}
{_("wildcard_brackets")}
{_("wildcard_exclude")}

{_("regex_templates")}
{_("templates_list")}

{_("usage")}
{_("usage_step1")}
{_("usage_step2")}
{_("usage_step3")}
{_("usage_step4")}

{_("developer")}
{_("date")}"""
        messagebox.showinfo(_("about"), about_text)

    def save_preview_text(self):
        """保存预览文本"""
        content = self.preview_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning(_("warning"), _("warning_empty_preview"))
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("*.txt", "*.txt"), ("*.*", "*.*")],
            title=_(("save_preview"))
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo(_("information"), _("save_success").format(path=file_path))
            except Exception as e:
                messagebox.showerror(_("error_title"), _("save_error").format(error=str(e)))

    def toggle_type_options(self):
        """切换按文件类型分类时，自动取消其他分类选项"""
        if self.by_type.get():
            # 选中按类型分类时，取消其他选项
            self.by_name.set(False)
            self.by_time.set(False)
            self.name_frame.grid_remove()
            self.time_frame.grid_remove()
        # 取消选中时无需操作，其他选项可重新选择

    def toggle_regex_options(self):
        """切换正则表达式选项的显示/隐藏"""
        if self.use_regex.get():
            self.regex_frame.pack(side="left", fill="x", expand=True, padx=10)
        else:
            self.regex_frame.pack_forget()

    def update_pattern_label(self):
        """更新输入框标签，根据当前模式显示不同文字"""
        if self.pattern_mode.get() == "regex":
            self.pattern_label.config(text=_(("regex_pattern")))
        else:
            self.pattern_label.config(text=_(("wildcard_pattern")))

    def validate_pattern_input(self, *args):
        """验证输入的模式是否有效"""
        pattern = self.regex_pattern.get().strip()
        if not pattern:
            self.regex_status.config(text="", foreground="green")
            return
        
        if self.pattern_mode.get() == "regex":
            # 验证正则表达式
            valid, error = validate_regex(pattern)
            if valid:
                self.regex_status.config(text="✓ OK", foreground="green")
            else:
                self.regex_status.config(text=f"✗ {error}", foreground="red")
        else:
            # 通配符模式始终有效（简单模式）
            self.regex_status.config(text="✓ OK", foreground="green")

    def show_regex_templates(self):
        """显示正则表达式模板选择对话框"""
        template_win = tk.Toplevel(self.root)
        template_win.title(_("select_template_title"))
        template_win.geometry("600x400")
        template_win.resizable(True, True)
        
        # 创建列表框显示模板
        listbox = tk.Listbox(template_win, width=80, height=15)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 获取模板名称的翻译
        template_names = {
            "图片文件名": _("template_images"),
            "视频文件名": _("template_videos"),
            "文档文件名": _("template_documents"),
            "表格文件": _("template_spreadsheets"),
            "演示文稿": _("template_presentations"),
            "压缩文件": _("template_archives"),
            "代码文件": _("template_code"),
            "音频文件": _("template_audio"),
            "日期格式": _("template_date"),
            "数字序列": _("template_numbers"),
            "包含关键词": _("template_keyword"),
            "邮箱地址": _("template_email"),
            "手机号码": _("template_phone"),
            "IP地址": _("template_ip"),
            "版本号": _("template_version"),
        }
        
        for name, pattern in REGEX_TEMPLATES.items():
            translated_name = template_names.get(name, name)
            listbox.insert(tk.END, f"{translated_name}: {pattern}")
        
        # 双击选择模板
        def select_template(event):
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                template_name = list(list(REGEX_TEMPLATES.keys())[index])
                template_pattern = REGEX_TEMPLATES[template_name]
                self.regex_pattern.set(template_pattern)
                template_win.destroy()
        
        listbox.bind("<Double-1>", select_template)
        
        # 添加说明标签
        ttk.Label(template_win, text=_(("double_click_to_select"))).pack(pady=5)
        
        # 关闭按钮
        ttk.Button(template_win, text=_(("close")), command=template_win.destroy).pack(pady=5)

    def get_classify_args(self):
        """从界面提取参数，返回字典"""
        args = {
            'by_name': self.by_name.get(),
            'by_time': self.by_time.get(),
            'by_type': self.by_type.get(),
            'target_root': self.target_dir.get().strip(),
            'move': self.move_mode.get(),
            'recursive': self.recursive.get(),
            'fuzzy_len': self.fuzzy_len.get() if self.use_fuzzy.get() else 0,
            'mode_combine': self.combine_mode.get() if (self.by_name.get() and self.by_time.get()) else False,
            # 过滤模式相关参数
            'use_regex': self.use_regex.get(),
            'regex_pattern': self.regex_pattern.get().strip(),
            'regex_match_type': self.regex_match_type.get(),
            'pattern_mode': self.pattern_mode.get(),  # regex 或 wildcard
        }
        # 时间相关
        if args['by_time']:
            try:
                start, end = parse_time_window(self.time_point.get().strip(), self.delta_hours.get())
                args['start_time'] = start
                args['end_time'] = end
                args['time_label'] = start.strftime("%Y%m%d_%H%M") + "_to_" + end.strftime("%Y%m%d_%H%M")
            except Exception as e:
                messagebox.showerror("时间解析错误", str(e))
                return None
        return args

    def preview(self):
        """生成预览计划并显示目录树"""
        # 检查基本路径
        src = self.source_dir.get().strip()
        if not os.path.isdir(src):
            messagebox.showwarning(_("warning"), _("please_select_source"))
            return
        dst = self.target_dir.get().strip()
        if not dst:
            messagebox.showwarning(_("warning"), _("please_select_target"))
            return

        args = self.get_classify_args()
        if args is None:
            return
        if not args['by_name'] and not args['by_time'] and not args['by_type']:
            messagebox.showwarning(_("warning"), _("select_criteria"))
            return

        # 收集文件
        self.status_var.set(_("collecting_files"))
        self.root.update()
        files = collect_files(src, args['recursive'])
        if not files:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, _("no_files_found"))
            self.status_var.set(_("preview_complete_no_files"))
            return

        # 应用过滤模式（正则表达式或通配符）
        original_count = len(files)
        if args.get('use_regex', False) and args.get('regex_pattern'):
            pattern = args['regex_pattern']
            match_type = args['regex_match_type']
            pattern_mode = args.get('pattern_mode', 'regex')
            
            try:
                if pattern_mode == 'regex':
                    # 正则表达式模式
                    valid, error = validate_regex(pattern)
                    if not valid:
                        messagebox.showerror(_("error_title"), _("invalid_regex").format(error=error))
                        return
                    compiled = re.compile(pattern, re.IGNORECASE)
                    if match_type == 'include':
                        files = [f for f in files if compiled.search(os.path.basename(f))]
                    else:
                        files = [f for f in files if not compiled.search(os.path.basename(f))]
                else:
                    # 通配符模式
                    regex_pattern = wildcard_to_regex(pattern)
                    compiled = re.compile(regex_pattern, re.IGNORECASE)
                    if match_type == 'include':
                        files = [f for f in files if compiled.match(os.path.basename(f))]
                    else:
                        files = [f for f in files if not compiled.match(os.path.basename(f))]
            except re.error as e:
                messagebox.showerror(_("error_title"), _("filter_error").format(error=str(e)))
                return
        
        if not files:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, _("no_matches_after_filter"))
            self.status_var.set(_("preview_complete_no_matches"))
            return

        # 生成分类计划
        plan = get_classification_plan(files, args)
        self.preview_plan = plan
        
        # 记录过滤信息
        self.filtered_count = original_count - len(files)

        # 显示目录树
        self.preview_text.delete(1.0, tk.END)
        total_files = sum(len(lst) for lst in plan.values())
        
        # 显示过滤模式信息
        if args.get('use_regex', False) and args.get('regex_pattern'):
            mode_name = _("regex") if args.get('pattern_mode') == 'regex' else _("wildcard")
            filter_info = f"{_(('filter_by'))}{mode_name} {_(('include') if args['regex_match_type'] == 'include' else 'exclude')}{_(('matching_files'))}"
            filter_info += f"{_(('before_filter'))}{original_count} {_(('files'))}{_(('after_filter'))}{len(files)} {_(('files'))}"
            self.preview_text.insert(tk.END, f"{filter_info}\n\n")
        
        if args.get('by_type', False):
            # 按文件类型分类
            self.preview_text.insert(tk.END, _("preview_type_info").format(total=total_files, folders=len(plan)))
        else:
            # 按名称或时间分类
            # 计算所有文件和未归类文件
            all_files_set = set(files)
            
            # 计算已归类的文件
            classified_files = set()
            for flist in plan.values():
                classified_files.update(flist)
            
            # 计算未归类的单一文件
            unclassified_files = all_files_set - classified_files
            
            self.preview_text.insert(tk.END, _("preview_name_info").format(total=total_files, folders=len(plan)))
            self.preview_text.insert(tk.END, _("preview_single_files").format(count=len(unclassified_files)))
            
        if plan:
            self.preview_text.insert(tk.END, _("target_structure") + "\n")
            for folder, flist in sorted(plan.items()):
                self.preview_text.insert(tk.END, f"📁 {folder}\n")
                for f in flist[:5]:  # 每个文件夹最多显示5个文件
                    self.preview_text.insert(tk.END, f"    📄 {os.path.basename(f)}\n")
                if len(flist) > 5:
                    self.preview_text.insert(tk.END, _("and_other").format(count=len(flist)-5))
                self.preview_text.insert(tk.END, "\n")
        else:
            self.preview_text.insert(tk.END, _("no_matches_found") + "\n")
        
        # 显示未归类的单一文件（仅在非类型分类时显示）
        if not args.get('by_type', False) and 'unclassified_files' in locals() and unclassified_files:
            self.preview_text.insert(tk.END, _("unclassified_files").format(count=len(unclassified_files)))
            for f in sorted(unclassified_files)[:10]:  # 最多显示10个
                self.preview_text.insert(tk.END, f"  ⚪ {os.path.basename(f)}\n")
            if len(unclassified_files) > 10:
                self.preview_text.insert(tk.END, _("and_other").format(count=len(unclassified_files)-10))
        
        # 根据分类类型显示不同状态
        if args.get('by_type', False):
            self.status_var.set(_("preview_complete_type").format(total=total_files, folders=len(plan)))
        else:
            self.status_var.set(_("preview_complete_other").format(total=total_files, folders=len(plan), unclassified=len(unclassified_files)))

    def start_classify(self):
        """执行归类（在子线程中运行，避免界面冻结）"""
        # 先检查预览是否存在且有效？或者重新生成计划
        if self.preview_plan is None:
            # 如果用户没有预览，自动执行预览并获取计划
            self.preview()
            if self.preview_plan is None:
                return

        # 确认执行
        total_files = sum(len(lst) for lst in self.preview_plan.values())
        action = _("move") if self.move_mode.get() else _("copy")
        if not messagebox.askyesno(_("confirm"), _("confirm_action").format(action=action, count=total_files)):
            return

        # 禁用按钮
        self.preview_btn.config(state="disabled")
        self.classify_btn.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set(_("processing"))
        self.root.update()

        def update_progress(current, total):
            """更新进度条"""
            percentage = (current / total) * 100 if total > 0 else 0
            self.root.after(0, lambda: self.progress_var.set(percentage))
            self.root.after(0, lambda: self.status_var.set(_("processing_progress").format(current=current, total=total, percentage=f"{percentage:.1f}")))

        def work():
            try:
                count = execute_plan(self.preview_plan, self.move_mode.get(), progress_callback=update_progress)
                self.root.after(0, lambda: messagebox.showinfo(_("complete"), _("complete_message").format(count=count)))
                self.root.after(0, lambda: self.status_var.set(_("complete_status").format(count=count)))
                self.root.after(0, lambda: self.preview_plan.clear())  # 清除计划
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(_("error_title"), str(e)))
                self.root.after(0, lambda: self.status_var.set(_("error_status")))
            finally:
                # 重新启用按钮
                self.root.after(0, lambda: self.preview_btn.config(state="normal"))
                self.root.after(0, lambda: self.classify_btn.config(state="normal"))

        threading.Thread(target=work, daemon=True).start()

# ====================== 主程序 ======================
if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerGUI(root)
    root.mainloop()