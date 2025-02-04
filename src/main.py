'''
 =======================================================================
 ·······································································
 ·······································································
 ····Y88b···d88P················888b·····d888·d8b·······················
 ·····Y88b·d88P·················8888b···d8888·Y8P·······················
 ······Y88o88P··················88888b·d88888···························
 ·······Y888P··8888b···88888b···888Y88888P888·888·88888b·····d88b·······
 ········888······"88b·888·"88b·888·Y888P·888·888·888·"88b·d88P"88b·····
 ········888···d888888·888··888·888··Y8P··888·888·888··888·888··888·····
 ········888··888··888·888··888·888···"···888·888·888··888·Y88b·888·····
 ········888··"Y888888·888··888·888·······888·888·888··888··"Y88888·····
 ·······························································888·····
 ··························································Y8b·d88P·····
 ···························································"Y88P"······
 ·······································································
 =======================================================================

 -----------------------------------------------------------------------
Author       : 焱铭
Date         : 2025-02-03 14:32:59 +0800
LastEditTime : 2025-02-04 15:27:32 +0800
Github       : https://github.com/YanMing-lxb/
FilePath     : /MangaPDF-Maker/src/main.py
Description  : 
 -----------------------------------------------------------------------
'''

import threading
import flet as ft
from pathlib import Path
from core import PictureProcessing, all_run


def main(page: ft.Page):
    pp = PictureProcessing()

    page.title = "MangaPDF Maker"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.SYSTEM
    if page.platform == ft.PagePlatform.LINUX or page.platform == ft.PagePlatform.MACOS or page.platform == ft.PagePlatform.WINDOWS:
        page.window.height = 450
        page.window.width = 500
        page.window.center()
    else:
        page.add(ft.TextButton("Material Button"))

    class GuiAction:

        def __init__(self):
            self.error_pics = []

        def handle_dismissal(self, e):
            page.close(drawer)

        def handle_change(self, e):
            page.close(drawer)

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

            input_path = tt_selected_directory.value
            png_num, jpg_num = pp.statistics_picture(input_path)

            if png_num < jpg_num:
                tf_more_suffix.value = '.jpg'
                tf_less_suffix.value = '.png'
            else:
                tf_more_suffix.value = '.png'
                tf_less_suffix.value = '.jpg'

            page.update()
            print('########## 已更改参数设置中的文本框！ ##########')
            self.error_pics = pp.pic_check(input_path)

        def eb_delete_error_pics_click(self, e):
            pp.delete_error_pics(self.error_pics)

        def eb_run_click(self, e):
            s_pics = sw_slip_pic.value
            right_to_left = sw_right_to_left.value
            input_path = tt_selected_directory.value
            output_path = Path(input_path + "-output")
            output_path.mkdir(exist_ok=True)
            if sw_output_name.value:
                finally_file_name = tf_output_name.value
            else:
                finally_file_name = Path(input_path).name
            self.temp_path = output_path / (finally_file_name + '-temp')
            more_suffix = tf_more_suffix.value
            less_suffix = tf_less_suffix.value

            print('输入路径：', input_path)
            print('输出路径：', output_path)
            print('临时路径：', self.temp_path)
            print('最终文件名：', finally_file_name)
            print('切割图片：', s_pics)
            print('从右到左：', right_to_left)
            print('多数图片后缀：', more_suffix)
            print('少数图片后缀：', less_suffix)
            print('开始生成 PDF 文件！')

            threading.Thread(
                target=all_run,
                daemon=True,
                args=(
                    str(input_path),
                    str(output_path),
                    str(self.temp_path),
                    less_suffix,
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

    ga = GuiAction()

    sw_slip_pic = ft.Switch(label="切割图片", value=False, label_position=ft.LabelPosition.LEFT)
    sw_right_to_left = ft.Switch(label="从右到左", value=False, label_position=ft.LabelPosition.LEFT)
    sw_output_name = ft.Switch(label="指定名称", value=False, label_position=ft.LabelPosition.LEFT)

    tf_more_suffix = ft.TextField(label="多数图片后缀", dense=True, adaptive=True)
    tf_less_suffix = ft.TextField(label="少数图片后缀", dense=True, adaptive=True)
    tf_output_name = ft.TextField(label="输出文件名称", dense=True, adaptive=True)

    eb_check_pic = ft.ElevatedButton(text="检查图片", icon='fact_check', on_click=ga.eb_check_pic_click, adaptive=True, disabled=True)
    eb_delete_error_pics = ft.ElevatedButton(text="删除异常", icon="cleaning_services", on_click=ga.eb_delete_error_pics_click, adaptive=True, disabled=True)
    eb_run = ft.ElevatedButton(text="处理文件", icon="directions_run", on_click=ga.eb_run_click, adaptive=True, disabled=True)
    pick_files_dialog = ft.FilePicker(on_result=ga.pick_files_result)
    eb_input_path = ft.ElevatedButton(text="输入路径", icon=ft.Icons.UPLOAD_FILE, on_click=lambda _: pick_files_dialog.get_directory_path(initial_directory=Path.home(), dialog_title="选择图片所在文件夹"), adaptive=True)
    drawer = ft.NavigationDrawer(on_dismiss=ga.handle_dismissal, on_change=ga.handle_change, controls=[])
    ib_menu = ft.IconButton(icon=ft.Icons.MENU, on_click=lambda e: page.open(drawer))
    ib_theme = ft.IconButton(icon=ft.Icons.LIGHT_MODE, selected_icon=ft.Icons.MODE_NIGHT, selected=False, on_click=ga.theme_changed, tooltip="切换主题")

    tt_selected_directory = ft.Text(max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)  # 显示选中的目录路径

    col_input_path = ft.Row([eb_input_path, tt_selected_directory])

    col_pic_operation = ft.Column([sw_slip_pic,sw_right_to_left,])
    col_pic_suffix = ft.Column([tf_more_suffix,tf_less_suffix,], expand=True)

    row_output_name = ft.Row([sw_output_name, tf_output_name], expand=True)
    row_pic_operation = ft.Row([col_pic_operation, col_pic_suffix])
    col_operation = ft.Column([
        tt_logo,
        row_pic_operation,
        row_output_name,
        col_input_path,
    ])

    row_check = ft.Row([eb_check_pic, ft.Placeholder(fallback_height=20, expand=True)])
    row_delete = ft.Row([eb_delete_error_pics, ft.Placeholder(fallback_height=20, expand=True)])
    row_run = ft.Row([eb_run, ft.Placeholder(fallback_height=20, expand=True)])
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
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[ft.Colors.BLUE, ft.Colors.YELLOW],
                ),
                adaptive=True,
            ),
            col_button,
        ]))


ft.app(target=main)
