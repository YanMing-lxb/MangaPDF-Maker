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
Date         : 2025-01-30 22:16:15 +0800
LastEditTime : 2025-02-03 00:44:27 +0800
Github       : https://github.com/YanMing-lxb/
FilePath     : /MangaPDF-Maker/src/__main__.py
Description  : 
 -----------------------------------------------------------------------
'''

import shutil
import threading
import PySimpleGUI as sg
from pathlib import Path
from core import PictureProcessing, all_run
out_temp_path = "D:/"

def GUI():
    sg.theme('SystemDefaultForReal')

    JGXZ_layout = [
        sg.Frame('运行状态',
                 [
                     [sg.Output(size=(64, 20), key='-state_print-', pad=((0, 0), 10), background_color='black',
                                text_color='green')],
                 ], relief="raised", border_width=2, pad=((20, 20), (0, 15)), )]

    all_layout = [
        [
            sg.Frame('参数设置', [

                [
                    sg.Text('是否分割图片：', size=(12, 1), pad=((20, 0), (20, 10))),
                    sg.Radio('是', 1, default=False, enable_events=True, key='-分割图片-', pad=((0, 5), (20, 10))),
                    sg.Radio('否', 1, default=True, enable_events=True, key='-不分割图片-', pad=((0, 20), (20, 10)))],
                [
                    sg.Text('更改阅读顺序：', size=(12, 1), pad=((20, 0), 10)),
                    sg.Radio('是', 2, default=False, enable_events=True, key='-从右到左-', pad=((0, 5), 10)),
                    sg.Radio('否', 2, default=True, enable_events=True, key='-从左到右-', pad=((0, 20), 10))],
                [
                    sg.Text('图片少数后缀：', size=(12, 1), pad=((20, 0), (45, 10))),
                    sg.In(default_text='.jpg', key='-少数后缀-', size=(10, 1), pad=((10, 0), (45, 10)),
                          justification='center')],
                [
                    sg.Text('图片多数后缀：', size=(12, 1), pad=((20, 0), 10)),
                    sg.In(default_text='.png', key='-多数后缀-', size=(10, 1), pad=((10, 0), 10), justification='center')],

                [sg.Button('检查', key='-检查-', size=(20, 1), pad=((30, 0), (125, 10)))],
                [sg.Button('删除异常图片', key='-删除异常图片-', disabled=True, size=(20, 1), pad=((30, 0), (10, 10)))],
                [sg.Button('运行', key='-运行-', disabled=True, size=(20, 1), pad=((30, 0), (10, 10)))],
                [sg.Button('删除失败文件夹', key='-删除失败文件夹-', disabled=True, size=(20, 1), pad=((30, 0), (10, 20)))]

            ], relief="raised", border_width=2, pad=((10, 10), (10, 10))),
            sg.Frame('路径及显示', [
                [
                    sg.Text('输入路径：', size=(10, 1), pad=((20, 0), (20, 0))),
                    sg.In(key='-图片总文件所在位置-', disabled=False, tooltip='图片总文件夹所在位置', size=(41, 1),
                          pad=((0, 10), (20, 0))),
                    sg.FolderBrowse(button_text="浏览文件夹", initial_folder=out_temp_path, key='-root_Button-',
                                    pad=((10, 20), (20, 0)))],

                [
                    sg.Text('输出路径：', size=(10, 1), pad=((20, 0), (4, 20))),
                    sg.In(key='-输出路径-', disabled=False, tooltip='最终生成的pdf保存位置', size=(41, 1), pad=((0, 10), (4, 20))),
                    sg.FolderBrowse(button_text="浏览文件夹", initial_folder=out_temp_path, key='-output_Button-',
                                    pad=((10, 20), (4, 20)))],
                JGXZ_layout], relief="raised", border_width=2, pad=((0, 10), (10, 10)))]
    ]

    layout = [all_layout]

    # 3) 创建窗口
    window = sg.Window('PDF文件制作工具 V1.3 by YanMing', layout, icon='ico.ico',finalize=True)

    # 4) 事件循环
    while True:
        event, values = window.read()  # 窗口的读取，有两个返回值(1.事件  2.值)
        if event == None:  # 窗口关闭事件
            break

        if event == '-检查-':
            input_path = values['-图片总文件所在位置-']
            pp = PictureProcessing()

            png_num, jpg_num=pp.statistics_picture(input_path)
            if png_num < jpg_num:
                window['-少数后缀-'].update('.png')
                window['-多数后缀-'].update('.jpg')
            else:
                window['-多数后缀-'].update('.png')
                window['-少数后缀-'].update('.jpg')
            print('########## 已更改参数设置中的文本框！ ##########')
            error_pics = pp.pic_check(input_path)
            window['-运行-'].update(disabled=False)
            window['-删除异常图片-'].update(disabled=False)


        if event == '-删除异常图片-':
            try:
                pp.delete_error_pics(error_pics)
                print("已删除所有异常文件！请进行下一步“运行”")
            except:
                print('没有异常文件！请进行下一步“运行”')

        if event == '-运行-':
            window['-运行-'].update(disabled=True)

            s_pic = False
            right_to_left = False

            less_suffixes = values['-少数后缀-']
            more_suffix = values['-多数后缀-']
            input_path = Path(values['-图片总文件所在位置-'])
            output_path = Path(values['-输出路径-'])
            if values['-分割图片-'] == True:
                s_pic = True
            else:
                s_pic = False
            if values['-从右到左-'] == True:
                right_to_left = True
            else:
                right_to_left = False
            finally_file_name = input_path.name
            temp_path = output_path / (finally_file_name + '临时文件')
            threading.Thread(target=all_run, daemon=True, args=(str(input_path), str(output_path), str(temp_path), less_suffixes, more_suffix, s_pic, right_to_left, finally_file_name)).start()
            window['-删除失败文件夹-'].update(disabled=False)
            window['-删除异常图片-'].update(disabled=True)

        if event == '-删除失败文件夹-':
            window['-运行-'].update(disabled=True)
            window['-删除异常图片-'].update(disabled=True)
            window['-删除失败文件夹-'].update(disabled=True)
            try:
                shutil.rmtree(temp_path)
                print("########### 已删除失败文件！ ###########")
            except:
                print("########### 文件删除失败！需手动删除！ ###########")


            # 5) 关闭窗口
    window.close()


GUI()