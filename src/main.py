import json
import requests
import threading
import flet as ft
from pathlib import Path
from core import PictureProcessing, all_run

current_version = "v1.4.1"  # 版本号变量


async def get_latest_version():
    try:
        # 基础配置
        repo_owner = "YanMing-lxb"
        repo_name = "MangaPDF-Maker"
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}

        # 第一阶段：尝试获取最新release
        release_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        release_response = requests.get(release_url, headers=headers, timeout=10)

        # 处理成功响应
        if release_response.status_code == 200:
            release_data = release_response.json()
            if "tag_name" in release_data:
                return release_data["tag_name"]
            print("Release存在但缺少tag_name字段")

        # 处理404响应（没有release时尝试获取tags）
        elif release_response.status_code == 404:
            tags_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/tags"
            tags_response = requests.get(tags_url, headers=headers, timeout=10)

            if tags_response.status_code == 200:
                tags_data = tags_response.json()
                if tags_data:
                    return tags_data[0].get("name", current_version)
                print("仓库存在但没有可用标签")

            print(f"标签请求失败: {tags_response.status_code}")

        # 处理其他错误状态码
        else:
            print(f"Release请求失败: {release_response.status_code}")
            print(f"响应内容: {release_response.text[:200]}")

        return current_version

    except requests.exceptions.RequestException as re:
        print(f"网络请求异常: {str(re)}")
    except json.JSONDecodeError:
        print("响应内容JSON解析失败")
    except Exception as e:
        print(f"意外错误: {str(e)}")

    return current_version


def main(page: ft.Page):
    if page.platform == ft.PagePlatform.LINUX or page.platform == ft.PagePlatform.MACOS or page.platform == ft.PagePlatform.WINDOWS:
        if page.platform == ft.PagePlatform.WINDOWS:
            page.window.icon = "logo.ico"  # 窗口图标
        page.window.height = 500
        page.window.width = 500
        page.window.center()
    else:
        page.add(ft.TextButton("Material Button"))
    page.title = "MangaPDF Maker"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.SYSTEM
    pp = PictureProcessing()

    class GuiAction:

        def __init__(self, ProgressBar):
            self.ProgressBar = ProgressBar
            self.error_pics = []

        def handle_dismissal(self, e):
            page.close(drawer)

        def handle_change(self, e):
            page.close(drawer)

        def handle_delete(self, yes):
            page.close(dlg_delete_error_pics)
            delete_error_status = self.ProgressBar['delete_error']['status']
            if yes:
                pp.delete_error_pics(self.error_pics)
                delete_error_status.value = "成功删除异常文件 ✅"
                page.update()

        def open_github(self, e):
            page.launch_url("https://github.com/YanMing-lxb/MangaPDF-Maker")

        async def check_update(self, e):
            latest_version = await get_latest_version()
            if latest_version != current_version:
                print(latest_version)
                dlg_update.content.controls[0].value = f"最新版本 {latest_version} 可用！"  # 更新文本内容
                page.open(dlg_update)

        def theme_changed(self, e):
            page.theme_mode = (ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT)
            ib_theme.label = ("浅色主题" if page.theme_mode == ft.ThemeMode.LIGHT else "暗色主题")
            e.control.selected = not e.control.selected
            e.control.update()
            page.update()

        def pick_files_result(self, e: ft.FilePickerResultEvent):
            if e.path:
                tt_selected_directory.value = e.path
                eb_check_pic.disabled = False
                page.update()
            else:
                tt_selected_directory.value = "已取消！"
            tt_selected_directory.update()

        def eb_check_pic_click(self, e):
            eb_delete_error_pics.disabled = False
            eb_run.disabled = False
            pb = self.ProgressBar['check']['pb']
            status = self.ProgressBar['check']['status']
            delete_error_status = self.ProgressBar['delete_error']['status']
            input_path = tt_selected_directory.value

            status.value = "1/2 - 统计图片"
            page.update()
            most_suffix, other_suffixes = pp.statistics_picture(page, pb, input_path)

            tf_more_suffix.value = most_suffix
            tf_other_suffix.value = other_suffixes

            page.update()

            status.value = "2/2 - 错误检查"
            page.update()
            self.error_pics = pp.pic_check(page, pb, input_path)
            if self.error_pics:
                # 将 WindowsPath 对象转换为字符串
                error_pics_str = [str(path) for path in self.error_pics]
                tt_error_pics.value = '\n'.join(error_pics_str)  # 使用转换后的字符串列表
                delete_error_status.value = "存在异常文件，请点击 <删除异常>"
                page.open(dlg_error_pics)

            # 所有任务完成后显示完成图标
            status.value = "✅"
            status.color = "green"
            page.update()

        def eb_run_click(self, e):
            pb = self.ProgressBar['run']['pb']
            status = self.ProgressBar['run']['status']

            s_pics = sw_slip_pic.value

            total_task = 7 if s_pics else 5
            status.value = f"1/{total_task} - 准备工作"
            page.update()

            right_to_left = sw_right_to_left.value
            input_path = tt_selected_directory.value
            output_path = Path(input_path + "-build")
            output_path.mkdir(exist_ok=True)
            if sw_output_name.value:
                finally_file_name = tf_output_name.value
            else:
                finally_file_name = Path(input_path).name
            self.temp_path = output_path / (finally_file_name + '-temp')
            more_suffix = tf_more_suffix.value
            other_suffix = tf_other_suffix.value

            print('输入路径：', input_path)
            print('输出路径：', output_path)
            print('临时路径：', self.temp_path)
            print('最终文件名：', finally_file_name)
            print('切割图片：', s_pics)
            print('从右到左：', right_to_left)
            print('多数图片后缀：', more_suffix)
            print('少数图片后缀：', other_suffix)
            print('开始生成 PDF 文件！')

            threading.Thread(
                target=all_run,
                daemon=True,
                args=(
                    page,
                    pb,
                    status,
                    str(input_path),
                    str(output_path),
                    str(self.temp_path),
                    other_suffix,
                    more_suffix,
                    s_pics,
                    right_to_left,
                    finally_file_name,
                ),
            ).start()

            eb_delete_error_pics.disabled = True
            eb_run.disabled = True
            page.update()

    tt_logo = ft.Text(
        "MangaPDF Maker",
        size=24,
        color=ft.Colors.WHITE,
        weight=ft.FontWeight.BOLD,
        italic=True,
    )
    tt_error_pics = ft.Text("")

    pb_check = ft.ProgressBar(width=250, value=0)  # 初始值为0，表示静止
    pb_run = ft.ProgressBar(width=250, value=0)  # 初始值为0，表示静止
    check_status = ft.Text("", color="blue")  # 用于显示任务状态
    run_status = ft.Text("", color="blue")
    delete_error_status = ft.Text("没有待删除文件", color="blue")
    ProgressBar = {'check': {'pb': pb_check, 'status': check_status}, 'run': {'pb': pb_run, 'status': run_status}, 'delete_error': {'status': delete_error_status}}
    ga = GuiAction(ProgressBar)

    sw_slip_pic = ft.Switch(label="切割图片", value=False, label_position=ft.LabelPosition.LEFT)
    sw_right_to_left = ft.Switch(label="从右到左", value=False, label_position=ft.LabelPosition.LEFT)
    sw_output_name = ft.Switch(label="指定名称", value=False, on_change=lambda e: (setattr(tf_output_name, 'disabled', not sw_output_name.value), page.update()), label_position=ft.LabelPosition.LEFT)

    tf_more_suffix = ft.TextField(label="多数图片后缀", dense=True, adaptive=True)
    tf_other_suffix = ft.TextField(label="少数图片后缀", dense=True, adaptive=True)
    tf_output_name = ft.TextField(label="输出文件名称", dense=True, adaptive=True, disabled=True, expand=True)

    eb_check_pic = ft.ElevatedButton(text="检查图片", icon='fact_check', on_click=ga.eb_check_pic_click, adaptive=True, disabled=True)
    eb_delete_error_pics = ft.ElevatedButton(text="删除异常", icon="cleaning_services", on_click=lambda e: page.open(dlg_delete_error_pics), adaptive=True, disabled=True)
    eb_run = ft.ElevatedButton(text="生成文件", icon="directions_run", on_click=ga.eb_run_click, adaptive=True, disabled=True)
    pick_files_dialog = ft.FilePicker(on_result=ga.pick_files_result)
    eb_input_path = ft.ElevatedButton(text="输入路径", icon=ft.Icons.UPLOAD_FILE, on_click=lambda _: pick_files_dialog.get_directory_path(initial_directory=Path.home(), dialog_title="选择图片所在文件夹"), adaptive=True)
    drawer = ft.NavigationDrawer(
        on_dismiss=ga.handle_dismissal,
        on_change=ga.handle_change,
        controls=[
            ft.ListTile(
                leading=ft.Icon(ft.Icons.CODE),  # 修改点1
                title=ft.Text("项目主页"),
                on_click=ga.open_github),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.UPDATE),  # 修改点2
                title=ft.Text("检查更新"),
                on_click=ga.check_update),
            ft.Divider(),
            ft.ListTile(title=ft.Text(f"当前版本: {current_version}"))
        ])
    ib_menu = ft.IconButton(icon=ft.Icons.MENU, on_click=lambda e: page.open(drawer))
    ib_theme = ft.IconButton(icon=ft.Icons.LIGHT_MODE, selected_icon=ft.Icons.MODE_NIGHT, selected=False, on_click=ga.theme_changed, tooltip="切换主题")

    tt_selected_directory = ft.Text(max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)  # 显示选中的目录路径

    dlg_error_pics = ft.AlertDialog(
        title=ft.Text("异常图片"),
        content=tt_error_pics,
    )
    dlg_update = ft.AlertDialog(title=ft.Text("发现新版本"),
                                content=ft.Column(
                                    [ft.Text("发现新版本！"), ft.TextButton("前往GitHub下载", icon=ft.Icons.OPEN_IN_BROWSER, on_click=lambda e: page.launch_url("https://github.com/YanMing-lxb/MangaPDF-Maker/releases"))], tight=True),
                                actions=[ft.TextButton("确定", on_click=lambda e: page.close(dlg_update))])
    dlg_delete_error_pics = ft.AlertDialog(
        modal=True,
        title=ft.Text("删除异常"),
        content=ft.Text("请确认是否清除异常？注意此操作不可恢复！"),
        actions=[
            ft.TextButton("Yes", on_click=lambda e: ga.handle_delete(True)),
            ft.TextButton("No", on_click=lambda e: ga.handle_delete(False)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    col_input_path = ft.Row([eb_input_path, tt_selected_directory])

    col_pic_operation = ft.Column([
        sw_slip_pic,
        sw_right_to_left,
    ])
    col_pic_suffix = ft.Column([
        tf_more_suffix,
        tf_other_suffix,
    ], expand=True)

    row_output_name = ft.Row([sw_output_name, tf_output_name], expand=True)
    row_pic_operation = ft.Row([col_pic_operation, col_pic_suffix])
    col_operation = ft.Column([
        tt_logo,
        row_pic_operation,
        row_output_name,
        col_input_path,
    ])

    row_check = ft.Row([eb_check_pic, pb_check, check_status])
    row_delete = ft.Row([eb_delete_error_pics, delete_error_status])
    row_run = ft.Row([eb_run, pb_run, run_status])
    col_button = ft.Column([row_check, row_delete, row_run])

    page.overlay.append(pick_files_dialog)
    page.add(ft.Row(
        [ib_menu, ft.Container(expand=True), ib_theme],
        alignment=ft.MainAxisAlignment.CENTER,
    ))

    page.add(
        ft.Column([
            ft.Container(
                content=col_operation,
                margin=0,
                padding=10,
                expand=True,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.GREEN_200,
                blend_mode=ft.BlendMode.MULTIPLY,
                blur=ft.Blur(10, 0, ft.BlurTileMode.MIRROR),
                # gradient=ft.LinearGradient(
                #     begin=ft.alignment.top_center,
                #     end=ft.alignment.bottom_center,
                #     colors=[ft.Colors.BLUE, ft.Colors.YELLOW],
                # ),
                adaptive=True,
            ),
            col_button,
        ]))


ft.app(target=main)
