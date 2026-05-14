import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta

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
        root.title("文件归类工具")
        root.geometry("1000x750")  # 增加窗口宽度
        root.resizable(True, True)

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

        # 预览状态
        self.preview_plan = None

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 创建菜单
        self.create_menu()
        
        # 源目录
        frame_src = ttk.LabelFrame(self.root, text="源目录", padding=5)
        frame_src.pack(fill="x", padx=10, pady=5)
        ttk.Entry(frame_src, textvariable=self.source_dir, width=60).pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(frame_src, text="浏览...", command=self.browse_source).pack(side="right")
        ttk.Checkbutton(frame_src, text="包含子目录", variable=self.recursive).pack(side="right", padx=5)

        # 目标目录
        frame_dst = ttk.LabelFrame(self.root, text="目标目录", padding=5)
        frame_dst.pack(fill="x", padx=10, pady=5)
        ttk.Entry(frame_dst, textvariable=self.target_dir, width=60).pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(frame_dst, text="浏览...", command=self.browse_target).pack(side="right")

        # 归类依据
        frame_criteria = ttk.LabelFrame(self.root, text="归类依据", padding=5)
        frame_criteria.pack(fill="x", padx=10, pady=5)

        # 按文件名
        cb_name = ttk.Checkbutton(frame_criteria, text="按文件名归类", variable=self.by_name, command=self.toggle_name_options)
        cb_name.grid(row=0, column=0, sticky="w")
        self.name_frame = ttk.Frame(frame_criteria)
        self.name_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=20)
        self.fuzzy_cb = ttk.Checkbutton(self.name_frame, text="模糊匹配 (取前N个字符)", variable=self.use_fuzzy, command=self.toggle_fuzzy)
        self.fuzzy_cb.pack(anchor="w")
        self.fuzzy_len_frame = ttk.Frame(self.name_frame)
        self.fuzzy_len_frame.pack(anchor="w", padx=20)
        ttk.Label(self.fuzzy_len_frame, text="字符数:").pack(side="left")
        self.fuzzy_spin = ttk.Spinbox(self.fuzzy_len_frame, from_=1, to=50, width=5, textvariable=self.fuzzy_len, state="disabled")
        self.fuzzy_spin.pack(side="left")
        self.name_frame.grid_remove()  # 初始隐藏

        # 按时间
        cb_time = ttk.Checkbutton(frame_criteria, text="按时间窗口归类", variable=self.by_time, command=self.toggle_time_options)
        cb_time.grid(row=0, column=1, sticky="w", padx=80)  # 增加水平间距
        self.time_frame = ttk.Frame(frame_criteria)
        self.time_frame.grid(row=1, column=1, rowspan=2, sticky="w", padx=100)  # 增加水平间距
        
        # 按文件类型
        cb_type = ttk.Checkbutton(frame_criteria, text="按文件类型归类", variable=self.by_type, command=self.toggle_type_options)
        cb_type.grid(row=0, column=2, sticky="w", padx=80)  # 增加水平间距
        ttk.Label(self.time_frame, text="基准时间:").grid(row=0, column=0, sticky="e")
        ttk.Entry(self.time_frame, textvariable=self.time_point, width=25).grid(row=0, column=1, padx=5)
        ttk.Label(self.time_frame, text="(格式: 2026-05-09 10:30:00)").grid(row=0, column=2, sticky="w")
        ttk.Label(self.time_frame, text="时间窗口半径:").grid(row=1, column=0, sticky="e")
        ttk.Spinbox(self.time_frame, from_=1, to=24, textvariable=self.delta_hours, width=5).grid(row=1, column=1, sticky="w")
        ttk.Label(self.time_frame, text="小时").grid(row=1, column=2, sticky="w")
        ttk.Radiobutton(self.time_frame, text="仅按时间", variable=self.combine_mode, value=False).grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(self.time_frame, text="与文件名同时满足", variable=self.combine_mode, value=True).grid(row=3, column=0, columnspan=2, sticky="w")
        self.time_frame.grid_remove()

        # 操作模式
        frame_action = ttk.LabelFrame(self.root, text="操作模式", padding=5)
        frame_action.pack(fill="x", padx=10, pady=5)
        ttk.Radiobutton(frame_action, text="复制 (保留原文件)", variable=self.move_mode, value=False).pack(side="left", padx=10)
        ttk.Radiobutton(frame_action, text="剪切 (移动文件)", variable=self.move_mode, value=True).pack(side="left", padx=10)

        # 按钮栏
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.pack(fill="x", padx=10, pady=5)
        self.preview_btn = ttk.Button(frame_buttons, text="预览归类结构", command=self.preview)
        self.preview_btn.pack(side="left", padx=5)
        self.classify_btn = ttk.Button(frame_buttons, text="开始归类", command=self.start_classify)
        self.classify_btn.pack(side="left", padx=5)

        # 预览区域
        frame_preview = ttk.LabelFrame(self.root, text="预览结果 (仅显示目录结构)", padding=5)
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
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(fill="x", side="bottom", padx=5, pady=2)

    def browse_source(self):
        path = filedialog.askdirectory(title="选择源目录")
        if path:
            self.source_dir.set(path)

    def browse_target(self):
        path = filedialog.askdirectory(title="选择目标根目录")
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
        file_menu.add_command(label="保存预览文本", command=self.save_preview_text)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)

    def show_about(self):
        """显示关于对话框"""
        about_text = """文件归类工具 v1.0

功能特点：
- 按文件名归类（支持模糊匹配）
- 按时间窗口归类
- 按文件类型归类（文档、代码、图片等）
- 复制/移动模式切换
- 预览功能
- 进度显示

使用说明：
1. 选择源目录和目标目录
2. 选择归类方式
3. 预览归类结构
4. 执行归类操作

开发方：Lingoes Family 武哥使用Trae开发
日期：2026年5月"""
        messagebox.showinfo("关于", about_text)

    def save_preview_text(self):
        """保存预览窗口内容到TXT文件"""
        content = self.preview_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("警告", "预览窗口为空，没有内容可保存")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="保存预览文本"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"预览文本已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")

    def toggle_type_options(self):
        """切换按文件类型分类时，自动取消其他分类选项"""
        if self.by_type.get():
            # 选中按类型分类时，取消其他选项
            self.by_name.set(False)
            self.by_time.set(False)
            self.name_frame.grid_remove()
            self.time_frame.grid_remove()
        # 取消选中时无需操作，其他选项可重新选择

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
            messagebox.showwarning("警告", "请选择有效的源目录")
            return
        dst = self.target_dir.get().strip()
        if not dst:
            messagebox.showwarning("警告", "请选择目标根目录")
            return

        args = self.get_classify_args()
        if args is None:
            return
        if not args['by_name'] and not args['by_time'] and not args['by_type']:
            messagebox.showwarning("警告", "请至少选择一种归类依据（文件名、时间或文件类型）")
            return

        # 收集文件
        self.status_var.set("正在收集文件...")
        self.root.update()
        files = collect_files(src, args['recursive'])
        if not files:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "没有找到任何文件。")
            self.status_var.set("预览完成，未找到文件")
            return

        # 生成分类计划
        plan = get_classification_plan(files, args)
        self.preview_plan = plan

        # 显示目录树
        self.preview_text.delete(1.0, tk.END)
        total_files = sum(len(lst) for lst in plan.values())
        
        if args.get('by_type', False):
            # 按文件类型分类
            self.preview_text.insert(tk.END, f"预计将处理 {total_files} 个文件，分类到 {len(plan)} 个文件类型文件夹中。\n\n")
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
            
            self.preview_text.insert(tk.END, f"预计将处理 {total_files} 个文件，分类到 {len(plan)} 个文件夹中。\n")
            self.preview_text.insert(tk.END, f"（已过滤 {len(unclassified_files)} 个单一文件，仅显示2个及以上相似文件的分类）\n\n")
            
        if plan:
            self.preview_text.insert(tk.END, "目标目录结构预览：\n")
            for folder, flist in sorted(plan.items()):
                self.preview_text.insert(tk.END, f"📁 {folder}\n")
                for f in flist[:5]:  # 每个文件夹最多显示5个文件
                    self.preview_text.insert(tk.END, f"    📄 {os.path.basename(f)}\n")
                if len(flist) > 5:
                    self.preview_text.insert(tk.END, f"    ... 及其他 {len(flist)-5} 个文件\n")
                self.preview_text.insert(tk.END, "\n")
        else:
            self.preview_text.insert(tk.END, "没有找到符合条件的分类。\n")
        
        # 显示未归类的单一文件（仅在非类型分类时显示）
        if not args.get('by_type', False) and 'unclassified_files' in locals() and unclassified_files:
            self.preview_text.insert(tk.END, f"\n未归类的单一文件（共 {len(unclassified_files)} 个）：\n")
            for f in sorted(unclassified_files)[:10]:  # 最多显示10个
                self.preview_text.insert(tk.END, f"  ⚪ {os.path.basename(f)}\n")
            if len(unclassified_files) > 10:
                self.preview_text.insert(tk.END, f"  ... 及其他 {len(unclassified_files)-10} 个文件\n")
        
        # 根据分类类型显示不同状态
        if args.get('by_type', False):
            self.status_var.set(f"预览完成，共 {total_files} 个文件将被归类，{len(plan)} 个文件夹（按类型分类）")
        else:
            self.status_var.set(f"预览完成，共 {total_files} 个文件将被归类，{len(plan)} 个文件夹，{len(unclassified_files)} 个单一文件未归类")

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
        if not messagebox.askyesno("确认执行", f"即将{'移动' if self.move_mode.get() else '复制'} {total_files} 个文件。\n继续吗？"):
            return

        # 禁用按钮
        self.preview_btn.config(state="disabled")
        self.classify_btn.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("正在处理文件，请稍候...")
        self.root.update()

        def update_progress(current, total):
            """更新进度条"""
            percentage = (current / total) * 100 if total > 0 else 0
            self.root.after(0, lambda: self.progress_var.set(percentage))
            self.root.after(0, lambda: self.status_var.set(f"正在处理... {current}/{total} ({percentage:.1f}%)"))

        def work():
            try:
                count = execute_plan(self.preview_plan, self.move_mode.get(), progress_callback=update_progress)
                self.root.after(0, lambda: messagebox.showinfo("完成", f"成功处理 {count} 个文件"))
                self.root.after(0, lambda: self.status_var.set(f"完成！处理了 {count} 个文件"))
                self.root.after(0, lambda: self.preview_plan.clear())  # 清除计划
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
                self.root.after(0, lambda: self.status_var.set("处理出错"))
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