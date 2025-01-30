# coding:utf-8
import threading
from PIL import Image
import os
from os.path import join
from os import walk
import re
from PyPDF2 import PdfFileReader, PdfFileWriter
import time
import sys
import importlib

importlib.reload(sys)
import shutil
import PySimpleGUI as sg

out_root_file = "D:/"
FileList = []   # 子文件 数组
pdf_files = [] # PDF分文件 数组
Error_picture = [] # 错误图片 数组



def progress(num,all_num,long,dur): # 进度条 子程序 num已运行 all_num总共运行 long总显示长度 dur已进行时长
    finsh = "▋" * round(num/all_num*long)
    need_do = "▏" * round((all_num-num)/all_num*long)
    progress = (num / int(all_num)) * 100
    print("\r{:^3.0f}%[{}->{}]{:.2f}s\n".format(progress, finsh, need_do,dur), end="")


# 搜索所有子文件夹
def search_subfolders(Root_File, list):
    list.clear() # 清空 list 数组
    for root, dirs, files in os.walk(Root_File):
        for item in dirs:
            list.append(Root_File + '/' + item)

            # re.findall(r"\d+")会根据正则在指定字符串内查找全部的数字,返回一个列表, "\d+" 表示查找数字
            # 根据文件名的特征取出最后一个数字进行排序即可
            list.sort(key=lambda x: int(re.findall(r"\d+", x)[-1]))  # 更改排序方式为正常排序,如:9,10


def statistics_picture(): # 分别统计 png后缀与jpg图片的数量
    global png_num
    global jpg_num
    print("************** 统计png后缀与jpg后缀图片数量中！ **************")
    png_list = []
    jpg_list = []
    FileList.clear()

    for root, dirs, files in os.walk(picture_path):
        for file in files:
            filePath = root + '/' + file
            protion = os.path.splitext(filePath)
            if protion[1].lower() == ".png":
                png_list.append(file)
            elif protion[1].lower() == ".jpg":
                jpg_list.append(file)
        FileList.append(root)
    png_num = len(png_list)
    jpg_num = len(jpg_list)
    print('************** .png图片数目: ' + str(png_num) + '张 **************')
    print('************** .jpg图片数目: ' + str(jpg_num) + '张 **************')


def modify_suffix():  # 将文件夹下所有少数后缀图片 转为多数后缀
    start = time.perf_counter()
    x = 0
    print("************** 修改异常后缀中 **************")
    for root, dirs, files in os.walk(picture_path):
        for file in files:
            filePath = root + '/' + file
            protion = os.path.splitext(filePath)
            if protion[1].lower() == Few_suffixes:
                newFilePath = protion[0] + Majority_suffix
                os.rename(filePath, newFilePath)

        x = x + 1
        during = time.perf_counter() - start
        progress(x, (int(len(FileList))+1), 50, during)


def Split_picture(): # 分割图片并改变阅读顺序
    start = time.perf_counter()
    x = 0
    if (os.path.exists(root_file) == False): # 判断要保存到的文件是属否存在
        os.mkdir(root_file) # 创建 Root_file文件夹
    print("************** 分割并改变阅读顺序中 **************")
    for i in FileList:
        z = 0
        path = i
        listdir = os.listdir(path) # 打开path路径
        file_name = os.path.basename(path) # 获取文件路径中的文件名
        file_path = root_file + "/" + file_name # 组合成新的子文件夹地址的路径
        newdir = os.path.join(root_file, file_name)  # 组合成新的子文件夹地址的路径 与上一行等同作用 将数组组合成地址
        if (os.path.exists(newdir) == False): # 如果新的子文件夹不存在，创建新的子文件夹
            os.mkdir(newdir)
        for i in listdir: # 循环lisdir文件夹下所有文件
            z = z + 1
            if Majority_suffix in i:  # 如果后缀存在与文件名i中
                filepath = os.path.join(path, i) # 组合成该文件的地址
                img = Image.open(filepath) # 打开该文件
                size = img.size # 获取该文件尺寸信息
                # 准备将图片横向切割成2张小图片
                weight = int(size[0] // 2)
                height = int(size[1])

                for i in range(2):
                    box = (weight * i, 0, weight * (i + 1), height)
                    region = img.crop(box) # 让该box形成图片

                    if Right_to_left == True: # 如果要改变阅读顺序，则执行以下
                        if (i) == 1:
                            region.save(file_path + '/_{:0>3d}'.format(2 * z - 1)+Majority_suffix)
                        else:
                            region.save(file_path + '/_{:0>3d}'.format(2 * z)+Majority_suffix)
                    else:
                        if (i) == 1:
                            region.save(file_path + '/_{:0>3d}'.format(2 * z)+Majority_suffix)
                        else:
                            region.save(file_path + '/_{:0>3d}'.format(2 * z - 1)+Majority_suffix)
                img.close() # 关闭已打开的图片，防止占用内存

        x = x + 1
        during = time.perf_counter() - start
        progress(x, int(len(FileList)), 50, during)


def convert_pdf():  # 将每个文件转为pdf
    start = time.perf_counter()
    x = 0
    print("************** 将图片转为pdf文档中 **************")

    for i in FileList:
        file_name = os.path.basename(i)
        imagelist = []
        Majority_suffix_files = []
        for root, dirs, files in walk(i): # 获取该路径下的所有 root dirs 文件夹
            for i in files:
                if i.lower().endswith(Majority_suffix):
                    Majority_suffix_files.append(join(root, i)) # 构建多数后缀图片的路径并添加至Majority_suffix_files数组中
                    Majority_suffix_files.sort(key=lambda x: int(re.findall(r"\d+", x)[-1]))  # 更改排序方式为正常排序,如:9,10

        for i in Majority_suffix_files: # 在该数组中遍历
            op = open(i, 'rb') # 打开该图片
            image = Image.open(op) # 用Image库代开
            im = image.convert('RGB') # 转换为RGB数据
            imagelist.append(im)
            op.close() # 关闭已打开的图片，防止占用内存

        op = open(Majority_suffix_files[0], 'rb')
        image=Image.open(op) # 设置封面图片
        im = image.convert('RGB')
        del (imagelist[0]) # 为防止第一张图片重复
        im.save(root_file + '/' + file_name + ".pdf", save_all=True,
                append_images=imagelist)  # 保存文件为pdf 名称为子文件夹名称
        imagelist.clear()

        # 此处为进度条显示
        x = x + 1
        during = time.perf_counter() - start
        progress(x, int(len(FileList)), 50, during)


def search_pdf():  # 搜索pdf文件
    pdf_files.clear()
    for root, dirs, files in walk(root_file):
        for i in files:
            if i.lower().endswith('.pdf'):  # 不区分大小写后缀
                pdf_files.append(join(root, i))
                pdf_files.sort(key=lambda x: int(re.findall(r"\d+", x)[-1]))  # 更改排序方式为正常排序,如:9,10
    print("搜索PDF文件！")


def merge_pdf():  # 合并pdf
    start = time.perf_counter()
    x = 0
    print("************** 合并pdf文档中 **************")
    global Bookmark_num
    Bookmark_num = [0, ]
    output = PdfFileWriter()
    outputPages = 0
    for i in pdf_files:
        # 读取源pdf文件
        with open(i, "rb") as f:
            input = PdfFileReader(f)

            # 如果pdf文件已经加密，必须首先解密才能使用pyPdf
            if input.isEncrypted == True:
                input.decrypt("map")
            # 获得源pdf文件中页面总数
            pageCount = input.getNumPages()
            outputPages += pageCount

            Bookmark_num.append(outputPages)

            # 分别将page添加到输出output中
            for iPage in range(0, pageCount):
                output.addPage(input.getPage(iPage))

            # 输出保存pdf
            outputStream = open(output_file_name + '/' + finally_file_name + '.pdf', "wb")
            output.write(outputStream)
            outputStream.close()
        x = x + 1
        during = time.perf_counter() - start
        progress(x, int(len(FileList)), 50, during)


def add_bookmark():  # 添加目录
    print("开始为PDF文件添加目录！")
    book = PdfFileReader(output_file_name + '/' + finally_file_name + '.pdf')
    pdf = PdfFileWriter()
    pdf.cloneDocumentFromReader(book)

    # 添加书签
    # 注意：页数是从0开始的，中文要用unicode字符串，否则会出现乱码
    # 如果这里的页码超过文档的最大页数，会报IndexError异常

    for i in range(len(FileList)):
        pdf.addBookmark(u'第' + str(i + 1) + '话', int(Bookmark_num[i]))

    # 保存修改后的PDF文件内容到文件中
    # 注意：这里必须用二进制的'wb'模式来写文件，否则写到文件中的内容都为乱码
    with open(output_file_name + '/' + finally_file_name + '.pdf', 'wb') as fout:
        pdf.write(fout)

    print("已为PDF文件添加目录！")

'''
# 分割 pdf 函数定义
def splitPDF(out_num):
    input_pdf = output_file_name + '/' + finally_file_name + '.pdf'
    for i in range(out_num):
        with open(input_pdf, 'rb') as open_pdf, open(finally_file_name+'第'+str(i)+'本.pdf', 'wb') as write_pdf:

            pdfReader = PdfFileReader(open_pdf)
            page_num = pdfReader.getNumPages()
            split_site = page_num/out_num
            pdfWriter = PdfFileWriter()
            for j in range(i*split_site, (i+1)*split_site):
                page = pdfReader.getPage(j)
                pdfWriter.addPage(page)

            pdfWriter.write(write_pdf)
'''

def delete():
    shutil.rmtree(root_file)
    print("已删除多余文件！")

def picture_dele():
    start = time.perf_counter()
    x = 0
    for i in Error_picture:
        os.remove(i)
        x = x + 1
        during = time.perf_counter() - start
        progress(x, int(len(Error_picture)), 50, during)
    Error_picture.clear()

def Chick():  # 检查错误图片
    x = 0
    start = time.perf_counter()
    print("************** 检查异常图片中 **************")
    for root, dirs, files in os.walk(picture_path):
        for file in files:
            filePath = root + '/' + file
            try:
                protion = os.path.splitext(filePath)
                if protion[1].lower() != '.zip':
                    if protion[1].lower() != '.rar':
                        Image.open(filePath).close()


            except:
                Error_picture.append(filePath)
        x = x + 1
        during =time.perf_counter()-start
        progress(x, int(len(FileList)),50,during)
    print('################################################################')
    if Error_picture == []:
        print('无异常图片！')
    for i in Error_picture:
        print(str(i)+'图片异常')






def all_run():
    time1 = time.time()
    search_subfolders(picture_path, FileList)
    modify_suffix()

    if S_picture == True:
        Split_picture()
        search_subfolders(root_file, FileList)
    else:
        if (os.path.exists(root_file) == False):
            os.mkdir(root_file)

    convert_pdf()
    search_pdf()
    merge_pdf()
    add_bookmark()
    delete()
    time2 = time.time()
    current_time = time2 - time1
    file_name = os.path.basename(picture_path)
    print("************** " + file_name + ".pdf 已生成 **************")
    print("************** 总共耗时" + str(int(current_time // 60 // 60)) + " 小时  " + str(
        int(current_time // 60 % 60)) + " 分钟  " + str(
        round(current_time % 60)) + " 秒 **************")
    for i in range(2):
        print('////////////////////////////////////////////////////////////////////////////////////////////////////////////////')
        print('----------------------------------------------------------------------------------------------------------------')
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

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
                    sg.FolderBrowse(button_text="浏览文件夹", initial_folder=out_root_file, key='-root_Button-',
                                    pad=((10, 20), (20, 0)))],

                [
                    sg.Text('输出路径：', size=(10, 1), pad=((20, 0), (4, 20))),
                    sg.In(key='-输出路径-', disabled=False, tooltip='最终生成的pdf保存位置', size=(41, 1), pad=((0, 10), (4, 20))),
                    sg.FolderBrowse(button_text="浏览文件夹", initial_folder=out_root_file, key='-output_Button-',
                                    pad=((10, 20), (4, 20)))],
                JGXZ_layout], relief="raised", border_width=2, pad=((0, 10), (10, 10)))]
    ]

    layout = [all_layout]

    # 3) 创建窗口
    window = sg.Window('PDF文件制作工具 V1.3 by YanMing', layout, icon='ico.ico',finalize=True)

    # 4) 事件循环
    while True:
        global Few_suffixes
        global Majority_suffix
        global picture_path
        global file_walk
        global finally_file_name
        global output_file_name
        global S_picture
        global Right_to_left
        global root_file

        event, values = window.read()  # 窗口的读取，有两个返回值(1.事件  2.值)
        if event == None:  # 窗口关闭事件
            break

        if event == '-检查-':
            global png_num
            global jpg_num

            picture_path = values['-图片总文件所在位置-']
            statistics_picture()
            if png_num < jpg_num:
                window['-少数后缀-'].update('.png')
                window['-多数后缀-'].update('.jpg')
            else:
                window['-多数后缀-'].update('.png')
                window['-少数后缀-'].update('.jpg')
            print('########## 已更改参数设置中的文本框！ ##########')
            Chick()
            window['-运行-'].update(disabled=False)
            window['-删除异常图片-'].update(disabled=False)
            png_num = 0
            jpg_num = 0



        if event == '-删除异常图片-':
            try:
                picture_dele()
                print("已删除所有异常文件！请进行下一步“运行”")
            except:
                print('没有异常文件！请进行下一步“运行”')

        if event == '-运行-':
            window['-运行-'].update(disabled=True)

            S_picture = False
            Right_to_left = False

            Few_suffixes = values['-少数后缀-']
            Majority_suffix = values['-多数后缀-']
            picture_path = values['-图片总文件所在位置-']
            output_file_name = values['-输出路径-']
            if values['-分割图片-'] == True:
                S_picture = True
            else:
                S_picture = False
            if values['-从右到左-'] == True:
                Right_to_left = True
            else:
                Right_to_left = False
            finally_file_name = os.path.basename(picture_path)
            root_file = output_file_name + '/' + finally_file_name+'临时文件'
            threading.Thread(target=all_run, daemon=True, ).start()
            window['-删除失败文件夹-'].update(disabled=False)
            window['-删除异常图片-'].update(disabled=True)

        if event == '-删除失败文件夹-':
            window['-运行-'].update(disabled=True)
            window['-删除异常图片-'].update(disabled=True)
            window['-删除失败文件夹-'].update(disabled=True)
            try:
                delete()
                print("########### 已删除失败文件！ ###########")
            except:
                print("########### 文件删除失败！需手动删除！ ###########")


            # 5) 关闭窗口
    window.close()


GUI()
# conda create -n 虚拟环境名字 python==3.6 #创建虚拟环境
# conda activate 虚拟环境名字 #激活虚拟环境
# conda deactivate #退出虚拟环境
# conda remove -n aotu--all  # 删除虚拟环境
# (picture_pdf) D:\Users\lixue>cd D:\Desktop\python小工具
# Pyinstaller -F -w -i ico.ico 图片转PDF工具_V1.3.py
# python -m pysimplegui-exemaker.pysimplegui-exemaker # 打包程序
