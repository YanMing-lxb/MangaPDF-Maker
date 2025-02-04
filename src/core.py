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
Date         : 2025-02-03 00:43:28 +0800
LastEditTime : 2025-02-04 12:07:41 +0800
Github       : https://github.com/YanMing-lxb/
FilePath     : /MangaPDF-Maker/src/core.py
Description  : 
 -----------------------------------------------------------------------
'''

import threading
from PIL import Image
from pathlib import Path
import re
from PyPDF2 import PdfReader, PdfWriter
import time
import shutil
import PySimpleGUI as sg


pdf_files = [] # PDF分文件 数组
pic_files = [] # 图片数组
png_num = 0
jpg_num = 0


def progress(current, total, bar_length, elapsed_time):
    # 计算已完成的部分和剩余的部分
    completed = "▋" * round(current / total * bar_length)
    remaining = "▏" * (bar_length - len(completed))
    # 计算进度百分比
    percentage = (current / total) * 100
    # 使用f-string格式化输出
    print(f"\r{percentage:^3.0f}% [{completed}{remaining}] {elapsed_time:.2f}s", end="")


class FileSearcher:
    def __init__(self):
        """
        """

    def search_files_in_subfolders(self, folder_path):
        folder = Path(folder_path)
        files = [str(item) for item in folder.rglob('*') if item.is_dir()]

        # re.findall(r"\d+")会根据正则在指定字符串内查找全部的数字,返回一个列表, "\d+" 表示查找数字
        # 根据文件名的特征取出最后一个数字进行排序即可
        files.sort(key=lambda x: int(re.findall(r"\d+", x)[-1]))  # 更改排序方式为正常排序,如:9,10
        return files

    def search_pdf(self, temp_path):
        folder = Path(temp_path)
        pdf_files = [str(item) for item in folder.rglob('*.pdf')]

        # 根据文件名的特征取出最后一个数字进行排序即可
        pdf_files.sort(key=lambda x: int(re.findall(r"\d+", x)[-1]))  # 更改排序方式为正常排序,如:9,10

        return pdf_files

class PictureProcessing:
    def __init__(self):
        """
        """

    def statistics_picture(self, input_path):  # 分别统计 png 后缀与 jpg 图片的数量
        print("************** 统计 png 后缀与 jpg 后缀图片数量中！ **************")
        png_list = []
        jpg_list = []

        input_path = Path(input_path)
        for file_path in input_path.rglob('*'):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                if suffix == ".png":
                    png_list.append(file_path.name)
                elif suffix == ".jpg":
                    jpg_list.append(file_path.name)
        png_num = len(png_list)
        jpg_num = len(jpg_list)
        print('************** .png 图片数目: ' + str(png_num) + ' 张 **************')
        print('************** .jpg 图片数目: ' + str(jpg_num) + ' 张 **************')
        
        return png_num, jpg_num
    
    def pic_check(self, input_path):  # 检查错误图片
        error_pics = []
        start = time.perf_counter()
        print("************** 检查异常图片中 **************")
        input_path = Path(input_path)
        for file_path in input_path.rglob('*'):
            if file_path.is_file():
                try:
                    suffix = file_path.suffix.lower()
                    if suffix not in ['.zip', '.rar']:
                        Image.open(file_path).close()
                except:
                    error_pics.append(file_path)
        during = time.perf_counter() - start
        print('################################################################')
        if not error_pics:
            print('无异常图片！')
        for pic in error_pics:
            print(f'{pic} 图片异常')
        return error_pics
    
    def delete_error_pics(self, error_pics):  # 删除错误图片
        start = time.perf_counter()
        for i, pic in enumerate(error_pics, 1):
            pic.unlink()
            during = time.perf_counter() - start
            progress(i, len(error_pics), 50, during)

    def modify_suffix(self, input_path, less_suffixes, more_suffix):  # 将文件夹下所有少数后缀图片 转为多数后缀
        start = time.perf_counter()
        input_path = Path(input_path)
        for file_path in input_path.rglob('*'):
            if file_path.is_file():
                if file_path.suffix.lower() == less_suffixes:
                    new_file_path = file_path.with_suffix(more_suffix)
                    file_path.rename(new_file_path)
        during = time.perf_counter() - start
        progress(len(list(input_path.rglob('*'))), len(list(input_path.rglob('*'))), 50, during)

    def split_picture(self, pic_files, temp_path, more_suffix, right_to_left):  # 分割图片并改变阅读顺序
        start = time.perf_counter()
        temp_path = Path(temp_path)
        if not temp_path.exists():  # 判断要保存到的文件夹是否存在
            temp_path.mkdir()  # 创建 temp_path 文件夹
        print("************** 分割并改变阅读顺序中 **************")
        for path in pic_files:
            path = Path(path)
            file_name = path.name  # 获取文件路径中的文件名
            file_path = temp_path / file_name  # 组合成新的子文件夹地址的路径
            newdir = temp_path / file_name  # 组合成新的子文件夹地址的路径
            if not newdir.exists():  # 如果新的子文件夹不存在，创建新的子文件夹
                newdir.mkdir()
            for z, file in enumerate(path.rglob('*' + more_suffix), 1):  # 循环路径下所有指定后缀文件
                filepath = file
                img = Image.open(filepath)  # 打开该文件
                size = img.size  # 获取该文件尺寸信息
                # 准备将图片横向切割成2张小图片
                weight = size[0] // 2
                height = size[1]

                for i in range(2):
                    box = (weight * i, 0, weight * (i + 1), height)
                    region = img.crop(box)  # 让该 box 形成图片
                    if right_to_left:
                        if i == 1:
                            region.save(newdir / f'_{2 * z - 1:03d}{more_suffix}')
                        else:
                            region.save(newdir / f'_{2 * z:03d}{more_suffix}')
                    else:
                        if i == 1:
                            region.save(newdir / f'_{2 * z:03d}{more_suffix}')
                        else:
                            region.save(newdir / f'_{2 * z - 1:03d}{more_suffix}')
                img.close()  # 关闭已打开的图片，防止占用内存
        during = time.perf_counter() - start
        progress(len(pic_files), len(pic_files), 50, during)

class PdfProcessing:
    def __init__(self):
        """
        """

    def convert_pdf(self, temp_path, pic_files, more_suffix):  # 将每个文件转为pdf
        start = time.perf_counter()
        x = 0
        print("************** 将图片转为pdf文档中 **************")

        for pic_folder in pic_files:
            file_name = Path(pic_folder).stem
            image_list = []
            more_suffix_files = []

            for pic_folder_path in Path(pic_folder).rglob('*'):
                if pic_folder_path.is_file() and pic_folder_path.suffix.lower() in more_suffix:
                    more_suffix_files.append(pic_folder_path)  # 构建多数后缀图片的路径并添加至more_suffix_files数组中

            more_suffix_files.sort(key=lambda file: int(re.findall(r"\d+", file.name)[-1]))  # 更改排序方式为正常排序,如:9,10

            for i in more_suffix_files:  # 在该数组中遍历
                with i.open('rb') as op:  # 打开该图片
                    image = Image.open(op)  # 用Image库代开
                    im = image.convert('RGB')  # 转换为RGB数据
                    image_list.append(im)

            with more_suffix_files[0].open('rb') as op:  # 设置封面图片
                image = Image.open(op)
                im = image.convert('RGB')
                del (image_list[0])  # 为防止第一张图片重复
                output_pdf_path = Path(temp_path) / f"{file_name}.pdf"
                im.save(output_pdf_path, save_all=True, append_images=image_list)  # 保存文件为pdf 名称为子文件夹名称
                image_list.clear()

            # 此处为进度条显示
            x = x + 1
            during = time.perf_counter() - start
            progress(x, int(len(pic_files)), 50, during)

    def merge_pdf(self, pdf_files, output_path, finally_file_name):  # 合并pdf
        start = time.perf_counter()
        x = 0
        print("************** 合并pdf文档中 **************")
        bookmark_num = [0, ]
        output = PdfWriter()
        output_pages = 0
        merged_pdf_path = Path(output_path) / f"{finally_file_name}.pdf"

        for pdf_file in pdf_files:
            # 读取源pdf文件
            with Path(pdf_file).open("rb") as f:
                input = PdfReader(f)

                # 如果pdf文件已经加密，必须首先解密才能使用pyPdf
                if input.is_encrypted:
                    input.decrypt("map")
                # 获得源pdf文件中页面总数
                page_count = len(input.pages)
                output_pages += page_count

                bookmark_num.append(output_pages)

                # 分别将page添加到输出output中
                for i_page in range(0, page_count):
                    output.add_page(input.pages[i_page])

        # 保存合并后的PDF文件内容到文件中
        with merged_pdf_path.open('wb') as output_stream:
            output.write(output_stream)

        x = x + 1
        during = time.perf_counter() - start
        # progress(x, int(len(pic_files)), 50, during)

        return bookmark_num

    def add_bookmark(self, output_path, bookmark_num, finally_file_name):  # 添加目录
        print("开始为PDF文件添加目录！")
        book = PdfReader(Path(output_path) / f"{finally_file_name}.pdf")
        pdf = PdfWriter()
        pdf.clone_document_from_reader(book)

        # 添加书签
        # 注意：页数是从0开始的，中文要用unicode字符串，否则会出现乱码
        # 如果这里的页码超过文档的最大页数，会报IndexError异常

        for i in range(len(pic_files)):
            # 使用 bookmark_num[i+1] 作为每个文件的开始页码，因为 bookmark_num[0] 是 0
            pdf.add_outline_item(u'第' + str(i + 1) + '话', int(bookmark_num[i + 1] - 1))

        # 保存修改后的PDF文件内容到文件中
        # 注意：这里必须用二进制的'wb'模式来写文件，否则写到文件中的内容都为乱码
        modified_pdf_path = Path(output_path) / f"{finally_file_name}.pdf"
        with modified_pdf_path.open('wb') as fout:
            pdf.write(fout)

        print("已为PDF文件添加目录！")


def all_run(input_path, output_path, temp_path, less_suffixes, more_suffix, s_pic, right_to_left, finally_file_name):
    try:
        time1 = time.time()
        fs = FileSearcher()
        pic_files = fs.search_files_in_subfolders(input_path)
        
        pp = PictureProcessing()
        pp.modify_suffix(input_path, less_suffixes, more_suffix)

        if s_pic:
            pp.split_picture(pic_files, temp_path, more_suffix, right_to_left)
            pic_files = fs.search_files_in_subfolders(temp_path)
        else:
            if not Path(temp_path).exists():
                Path(temp_path).mkdir()

        pdfp = PdfProcessing()
        pdfp.convert_pdf(temp_path, pic_files, more_suffix)
        pdf_files = fs.search_pdf(temp_path)
        bookmark_num = pdfp.merge_pdf(pdf_files, output_path, finally_file_name)
        pdfp.add_bookmark(output_path, bookmark_num, finally_file_name)
        
        shutil.rmtree(temp_path)
        time2 = time.time()
        current_time = time2 - time1
        file_name = Path(input_path).name
        print("************** " + file_name + ".pdf 已生成 **************")
        print("************** 总共耗时" + str(int(current_time // 60 // 60)) + " 小时  " + str(
            int(current_time // 60 % 60)) + " 分钟  " + str(
            round(current_time % 60)) + " 秒 **************")
        
    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
    except PermissionError as e:
        print(f"权限错误: {e}")
    except Exception as e:
        print(f"发生了一个错误: {e}")
    finally:
        # 确保临时文件夹在任何情况下都被删除
        if Path(temp_path).exists():
            try:
                shutil.rmtree(temp_path)
            except Exception as e:
                print(f"删除临时文件夹时发生错误: {e}")



# conda create -n 虚拟环境名字 python==3.6 #创建虚拟环境
# conda activate 虚拟环境名字 #激活虚拟环境
# conda deactivate #退出虚拟环境
# conda remove -n aotu--all  # 删除虚拟环境
# (picture_pdf) D:\Users\lixue>cd D:\Desktop\python小工具
# Pyinstaller -F -w -i ico.ico 图片转PDF工具_V1.3.py
# python -m pysimplegui-exemaker.pysimplegui-exemaker # 打包程序
