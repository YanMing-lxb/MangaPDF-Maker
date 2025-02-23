import flet as ft
from time import sleep

def main(page: ft.Page):
    # 创建进度条和状态显示容器
    pb = ft.ProgressBar(width=400, value=0)  # 初始值为0，表示静止
    status_text = ft.Text("", color="blue")  # 用于显示任务状态
    status_icon = ft.Text("")  # 用于显示执行状态图标
    start_button = ft.ElevatedButton(text="启动", on_click=lambda e: start_tasks(page, pb, status_text, status_icon))  # 启动按钮
    
    # 页面布局
    page.add(
        ft.Text("多任务进度监控", style="headlineSmall"),
        ft.Row([pb, status_text, status_icon]),
        start_button
    )

def start_tasks(page, pb, status_text, status_icon):
    # 模拟多个子任务
    tasks = [
        ("处理图像", 2),
        ("生成PDF", 3),
        ("上传文件", 1),
        ("清理缓存", 1)
    ]

    total_tasks = len(tasks)

    for index, (task_name, duration) in enumerate(tasks, 1):
        # 更新任务状态
        status_text.value = f"{index}/{total_tasks} - {task_name}"
        page.update()
        
        # 模拟任务执行
        for i in range(0, 101):
            pb.value = i * 0.01
            sleep(duration / 100)
            page.update()
        
        # 重置进度条
        pb.value = 0
        page.update()

    # 所有任务完成后显示完成图标
    status_icon.value = "✅"
    status_icon.color = "green"
    page.update()

ft.app(target=main)