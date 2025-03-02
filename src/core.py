
from PIL import Image
from pathlib import Path
import re
from pypdf import PdfReader, PdfWriter
import time
import shutil

pdf_files = []  # PDF分文件 数组
pic_files = []  # 图片数组
png_num = 0
jpg_num = 0


class FileSearcher:

    def __init__(self):
        """
        """

    def search_files_in_subfolders(self, page, pb, folder_path):
        folder = Path(folder_path)
        files = list(folder.rglob('*'))  # 获取所有文件和文件夹
        total_files = len(files)  # 总文件数
        dir_files = []  # 用于存储符合条件的文件夹路径
        for index, item in enumerate(files, 1):  # 遍历文件，index 从 1 开始
            if item.is_dir():
                dir_files.append(str(item))

            # 更新进度条
            pb.value = index / total_files  # 计算当前进度
            page.update()  # 更新页面

        # re.findall(r"\d+")会根据正则在指定字符串内查找全部的数字,返回一个列表, "\d+" 表示查找数字
        # 根据文件名的特征取出最后一个数字进行排序
        dir_files.sort(key=lambda x: int(re.findall(r"\d+", x)[-1]))  # 更改排序方式为正常排序,如:9,10
        return dir_files

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

    def statistics_picture(self, page, pb, input_path):  # 统计图片后缀数量
        suffix_count = {}  # 用于存储后缀及其数量的字典

        input_path = Path(input_path)
        files = list(input_path.rglob('*'))  # 获取所有文件列表
        total_files = len(files)  # 总文件数
        for index, file_path in enumerate(files, 1):  # 遍历文件，index 从 1 开始
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                if suffix in suffix_count:
                    suffix_count[suffix] += 1
                else:
                    suffix_count[suffix] = 1

            # 更新进度条
            pb.value = index / total_files  # 计算当前进度
            page.update()  # 更新页面

        # 找到数量最多的后缀
        most_suffix = max(suffix_count, key=suffix_count.get) if suffix_count else None
        # 其他后缀及其数量
        other_suffixes = [suffix for suffix in suffix_count.keys() if suffix != most_suffix]

        # 返回结果字典
        return most_suffix, other_suffixes

    def pic_check(self, page, pb, input_path):  # 检查错误图片
        # 重置进度条
        pb.value = 0
        page.update()
        error_pics = []

        input_path = Path(input_path)

        files = list(input_path.rglob('*'))  # 获取所有文件列表
        total_files = len(files)  # 总文件数

        for index, file_path in enumerate(files, 1):  # 遍历文件，index 从 1 开始
            if file_path.is_file():
                try:
                    suffix = file_path.suffix.lower()
                    if suffix not in ['.zip', '.rar']:
                        Image.open(file_path).close()
                except:
                    error_pics.append(file_path)
            # 更新进度条
            pb.value = index / total_files  # 计算当前进度
            page.update()  # 更新页面
        return error_pics

    def delete_error_pics(self, error_pics):  # 删除错误图片
        for i, pic in enumerate(error_pics, 1):
            pic.unlink()

    def modify_suffix(self, page, pb, input_path, other_suffixes, more_suffix):  # 将文件夹下所有少数后缀图片 转为多数后缀
        input_path = Path(input_path)
        files = list(input_path.rglob('*'))  # 获取所有文件列表
        total_files = len(files)  # 总文件数
        for index, file_path in enumerate(files, 1):  # 遍历文件，index 从 1 开始
            if file_path.is_file() and file_path.suffix.lower() in other_suffixes:
                # 将文件后缀改为 more_suffix 中的第一个元素
                new_file_path = file_path.with_suffix(more_suffix[0])
                file_path.rename(new_file_path)

            # 更新进度条
            pb.value = index / total_files  # 计算当前进度
            page.update()  # 更新页面

    def split_picture(self, page, pb, pic_files, temp_path, more_suffix, right_to_left):  # 分割图片并改变阅读顺序
        temp_path = Path(temp_path)
        temp_path.mkdir(parents=True, exist_ok=True)
        print("************** 分割并改变阅读顺序中 **************")

        # 计算总文件数
        total_files = sum(len(list(Path(path).rglob('*' + more_suffix))) for path in pic_files)
        processed_files = 0  # 已处理的文件数
        for path in pic_files:
            path = Path(path)
            file_name = path.name  # 获取文件路径中的文件名
            newdir = temp_path / file_name  # 组合成新的子文件夹地址的路径
            newdir.mkdir(parents=True, exist_ok=True)

            # 获取当前文件夹下的所有指定后缀文件
            files = list(path.rglob('*' + more_suffix))
            for z, file in enumerate(files, 1):  # 循环路径下所有指定后缀文件
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

                # 更新进度条
                processed_files += 1
                pb.value = processed_files / total_files  # 计算当前进度
                page.update()  # 更新页面


class PdfProcessing:

    def __init__(self):
        """
        """

    def convert_pdf(self, page, pb, input_path, temp_path, pic_subfolders, more_suffix):  # 将每个文件转为pdf
        start = time.perf_counter()
        total_files = len(pic_subfolders)  # 总文件数
        processed_files = 0  # 已处理的文件数
        print("************** 图片转为pdf文档 **************")
        print("图片文件路径：", pic_subfolders)
        print("图片文件后缀：", more_suffix)
        if pic_subfolders: # 如果文件夹下存在子文件夹才执行
            for pic_folder in pic_subfolders:
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

                # 更新进度条
                processed_files += 1
                pb.value = processed_files / total_files  # 计算当前进度
                page.update()  # 更新页面
        else:
            file_name = Path(input_path).stem
            image_list = []
            more_suffix_files = []

            for pic_folder_path in Path(input_path).rglob('*'):
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

        during = time.perf_counter() - start

    def merge_pdf(self, page, pb, pdf_files, output_path, finally_file_name):  # 合并pdf
        print("************** 合并pdf文档中 **************")
        bookmark_num = [0]
        output = PdfWriter()
        output_pages = 0
        merged_pdf_path = Path(output_path) / f"{finally_file_name}.pdf"
        total_files = len(pdf_files)  # 总文件数
        processed_files = 0  # 已处理的文件数

        if len(pdf_files) == 1:
            pass
        else:
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

                # 更新进度条
                processed_files += 1
                pb.value = processed_files / total_files  # 计算当前进度
                page.update()  # 更新页面

            # 保存合并后的PDF文件内容到文件中
            with merged_pdf_path.open('wb') as output_stream:
                output.write(output_stream)

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


def all_run(page, pb, status, input_path, output_path, temp_path, other_suffixes, more_suffix, s_pics, right_to_left, finally_file_name):
    try:
        total_task = 6 if s_pics else 4
        time1 = time.time()
        fs = FileSearcher()
        task_index = 2
        status.value = f"{task_index+1}/{total_task} - 搜索文件夹"
        page.update()
        pic_files = fs.search_files_in_subfolders(page, pb, input_path)

        status.value = f"{task_index+1}/{total_task} - 修改后缀"
        page.update()
        pp = PictureProcessing()
        pp.modify_suffix(page, pb, input_path, other_suffixes, more_suffix)

        if s_pics:
            status.value = f"{task_index+1}/{total_task} - 分割图片"
            page.update()
            pp.split_picture(page, pb, pic_files, temp_path, more_suffix, right_to_left)
            status.value = f"{task_index+1}/{total_task} - 重新搜索"
            page.update()
            pic_files = fs.search_files_in_subfolders(page, pb, temp_path)
        else:
            Path(temp_path).mkdir(parents=True, exist_ok=True)

        pdfp = PdfProcessing()
        status.value = f"{task_index+1}/{total_task} - 转换PDF"
        page.update()
        pdfp.convert_pdf(page, pb, input_path, temp_path, pic_files, more_suffix)
        pdf_files = fs.search_pdf(temp_path)
        status.value = f"{task_index+1}/{total_task} - 合并PDF"
        page.update()
        bookmark_num = pdfp.merge_pdf(page, pb, pdf_files, output_path, finally_file_name)
        # pdfp.add_bookmark(output_path, bookmark_num, finally_file_name)

        shutil.rmtree(temp_path)
        time2 = time.time()
        current_time = time2 - time1
        file_name = Path(input_path).name
        print("************** " + file_name + ".pdf 已生成 **************")
        print("************** 总共耗时" + str(int(current_time // 60 // 60)) + " 小时  " + str(int(current_time // 60 % 60)) + " 分钟  " + str(round(current_time % 60)) + " 秒 **************")

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
        status.value = "✅"
        status.color = "green"
        page.update()


# conda create -n 虚拟环境名字 python==3.6 #创建虚拟环境
# conda activate 虚拟环境名字 #激活虚拟环境
# conda deactivate #退出虚拟环境
# conda remove -n aotu--all  # 删除虚拟环境
# (picture_pdf) D:\Users\lixue>cd D:\Desktop\python小工具
# Pyinstaller -F -w -i ico.ico 图片转PDF工具_V1.3.py
# python -m pysimplegui-exemaker.pysimplegui-exemaker # 打包程序
