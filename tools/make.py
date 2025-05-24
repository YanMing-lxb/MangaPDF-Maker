

import subprocess
import re
import sys
from pathlib import Path
from rich.console import Console

console = Console()

def _run_command(command, check=True):
    try:
        subprocess.run(command, check=check)
    except subprocess.CalledProcessError as e:
        console.log(f"执行命令时出错: {e}")
        sys.exit(1)

def _get_version():
    version_file = Path('src/version.py')
    if not version_file.exists():
        raise FileNotFoundError(f"文件 {version_file} 不存在")
    
    with open(version_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", content)
    if not version_match:
        raise ValueError(f"无法在 {version_file} 中找到 __version__ 变量")
    
    return version_match.group(1)


def upload():
    version = _get_version()
    tag_name = f"v{version}"
    
    # 创建标签
    _run_command(['git', 'tag', tag_name])
    console.log(f"创建标签: {tag_name}")
    
    # 推送标签
    _run_command(['git', 'push', 'origin', tag_name])
    console.log(f"推送标签: {tag_name}")

    console.log("成功上传标签和推送到远程仓库，发布到 github")

def main():
    targets = {
        'upload': upload,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in targets:
        console.log(f"用法: {sys.argv[0]} <目标>")
        console.log("可用目标:", ', '.join(targets.keys()))
        sys.exit(1)

    target = sys.argv[1]
    try:
        targets[target]()
    except subprocess.CalledProcessError as e:
        console.log(f"执行命令时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
