# MangaPDF Maker

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/) [![Flet](https://img.shields.io/badge/Flet-0.27.1-green)](https://flet.dev/) [![License](https://img.shields.io/badge/License-GPL3.0-yellow)](LICENSE)

一款基于Flet框架开发的漫画图片转PDF工具，支持图片自动分割。

## ✨ 功能特性

- 🖼️ 支持JPEG/JPG/PNG/BMP等多种图片格式
- 📑 智能图片批量转换
- 🖼️ 图片预处理（分割图片）
- 🎯 多平台支持（Windows/macOS/Linux）
- 📦 一键打包为独立可执行文件

## 🖥️ 界面操作指南


## 📦 开发指南

### 前置要求

- Python 3.12+
- Flet 0.27.1+
- pypdf 5.3.0+


### 安装步骤

克隆仓库
```bash
git clone https://github.com/YanMing-lxb/MangaPDF-Maker.git
cd MangaPDF-Maker
```

### 🚀 程序打包

#### Windows单文件打包

```bash
python -m nuitka --standalone --onefile --windows-console-mode=hide --windows-icon-from-ico=./src/assets/ico.ico --include-data-dir=./src/assets=assets --company-name="YanMing" --product-name="MangaPDF Maker" --file-version="1.4.1" --product-version="1.4.1" --output-filename="MangaPDF Maker" ./src/main.py
```

#### 使用Flet打包

```bash
flet pack -i ./src/assets/ico.ico -n "MangaPDF Maker" ./src/main.py
```

## 🤝 参与贡献

欢迎通过Issue或Pull Request参与项目改进：

## Fork项目仓库

1. 创建特性分支（git checkout -b feature/AmazingFeature）
2. 提交修改（git commit -m 'Add some AmazingFeature'）
3. 推送到远程分支（git push origin feature/AmazingFeature）
4. 发起Pull Request

## 📄 许可证
本项目采用 GPL3.0 License

## 🌟 致谢
[Flet](https://flet.dev/) - 优秀的跨平台GUI框架
[pypdf](https://github.com/py-pdf/pypdf) - PDF操作库
