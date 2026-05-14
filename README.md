# 📂 文件归类工具

[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个**带图形界面**的智能文件归类工具，帮你快速整理杂乱的文件。不仅支持常规的按文件名、类型、时间归类，还特别优化了**翻译文档**和**同名文件**的整理场景。
<img width="1252" height="1002" alt="stps" src="https://github.com/user-attachments/assets/d766d433-0768-433b-bef5-0519024170b0" />

---

## ✨ 功能特性

- 🗂️ **多种归类依据**
  - 按**文件名**归类（支持模糊匹配、关键词提取）
  - 按**时间窗口**归类（例如按年/月/日自动建立文件夹）
  - 按**文件类型**归类（如 `.pdf`、`.docx`、`.xlxs` 等）

- 📝 **翻译文档专项归类**
  - 自动识别原文件与译文文件（例如 `source.docx` 与 `source_translated.docx`）以开头名称字符数相似为原则。
  - 将译文与原文放入同一目录，或按语言/项目单独归类

- 🔁 **同名文件智能合并**
  - 检测不同目录下**文件名相同**的文件（如多份 `readme.md`）
  - 支持合并到同一文件夹，避免重复散落

- ⏱️ **时间段归类**
  - 按文件的**创建时间**或**修改时间**建立时间树（如 `2025/01/15/`）
  - 自定义时间窗口粒度（小时/天/周/月/年）

- 📦 **双操作模式**
  - **复制**：保留原文件，适合备份式整理
  - **剪切**：移动文件，彻底归类

- 🧪 **预览归类结构**（仅显示目录树，不实际移动文件）

---

## 🚀 快速开始

### 环境要求
- Windows（基于 Python 3.x）
- 或直接使用打包后的 `.exe`（Windows）

### 方式一：EXE 版（推荐普通用户）
1. 从 [Releases](../../releases) 下载最新版 `stepedProgram_corrected.exe`
2. 双击运行，打开图形界面
3. 按下面 **界面使用说明** 操作即可

### 方式二：源码版
```bash
git clone https://github.com/你的用户名/文件归类工具.git
cd 文件归类工具
pip install -r requirements.txt   # 如有依赖
python main.py
