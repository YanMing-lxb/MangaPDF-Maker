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
Date         : 2025-02-03 19:13:19 +0800
LastEditTime : 2025-02-04 18:40:42 +0800
Github       : https://github.com/YanMing-lxb/
FilePath     : /MangaPDF-Maker/src/test.py
Description  : 
 -----------------------------------------------------------------------
'''

import flet as ft

def main(page: ft.Page):
    page.title = "Flet 计数器示例"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    if page.platform == ft.PagePlatform.LINUX or page.platform == ft.PagePlatform.MACOS or page.platform == ft.PagePlatform.WINDOWS:
        page.window.height = 450
        page.window.width = 500
        page.window.center()
    else:
        page.add(ft.TextButton("Material Button"))

    txt_number = ft.TextField(value="0", text_align="right", width=100)

    def minus_click(e):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    def plus_click(e):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()

    page.add(
        ft.Row(
            [
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                txt_number,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

ft.app(target=main)