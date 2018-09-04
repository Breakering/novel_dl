# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

from novel_dl.utility.file_op import write_file, read_file


class NovelDlPipeline(object):
    def process_item(self, item, spider):
        if item["action"] == "save_novel_img":
            novel_file_path = item["novel_file_path"]
            novel_name = os.path.basename(novel_file_path)
            body = item["body"]
            write_file(os.path.join(novel_file_path, "%s.jpg" % novel_name), body, pattern='wb')
        elif item["action"] == "save_novel_detail":
            novel_file_path = item["novel_file_path"]
            chapter = item["chapter"]  # 第几章节
            detail = item["detail"]  # 内容
            os.makedirs(os.path.join(novel_file_path, "chapters"), exist_ok=True)  # 按书来建目录
            write_file(os.path.join(novel_file_path, "chapters", "%s.txt" % chapter), detail)
        return item

    def close_spider(self, spider):
        for novel_type in os.listdir(spider.novel_collect_dir):
            novel_type_dir = os.path.join(spider.novel_collect_dir, novel_type)
            for novel_name in os.listdir(novel_type_dir):
                novel_name_dir = os.path.join(novel_type_dir, novel_name)
                chapters_dir = os.path.join(novel_name_dir, "chapters")
                if os.path.exists(chapters_dir):
                    novel_file_path = os.path.join(novel_name_dir, "%s.txt" % novel_name)
                    if os.path.isfile(novel_file_path):
                        os.remove(novel_file_path)

                    # 加上小说名，作者和简介
                    novel_info_path = os.path.join(novel_name_dir, "%s_info.txt" % novel_name)
                    if os.path.isfile(novel_info_path):
                        write_file(novel_file_path, read_file(novel_info_path), pattern='a')

                    # 将每章内容加入汇总的小说文件里面
                    chapter_file_list = os.listdir(chapters_dir)
                    chapter_file_list.sort()
                    for chapter_file in chapter_file_list:
                        chapter_file_path = os.path.join(chapters_dir, chapter_file)
                        with open(chapter_file_path, "r") as chapter_detail:
                            title_find = False
                            for line in chapter_detail:
                                line = line.lstrip()  # 剔除开头的空格
                                if line.startswith('Chapter'):  # 找到了标题
                                    write_file(novel_file_path, '###start###\n', pattern='a')
                                    write_file(novel_file_path, line, pattern='a')
                                    write_file(novel_file_path, '###end###\n', pattern='a')
                                    title_find = True
                                    continue
                                if title_find:
                                    write_file(novel_file_path, '\t%s' % line, pattern='a')
                                    title_find = False
                                    continue
                                write_file(novel_file_path, line, pattern='a')
