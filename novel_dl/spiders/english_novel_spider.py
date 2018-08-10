#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Breakering"
# Date: 18-8-10
import json
import os
import re

import scrapy

from novel_dl.utility.file_op import write_file, read_file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class EnglishNovelSpider(scrapy.Spider):
    name = "english_novel_spider"
    start_urls = [
        "http://www.wuxiaworld.co/all/",
    ]
    novel_collect_dir = os.path.join(BASE_DIR, "novel_collect")

    @staticmethod
    def get_href(a):
        return a.css("::attr(href)").extract_first()

    def parse(self, response):
        all_novel_a_tag_list = response.css("div.novellist3 a")
        for a in all_novel_a_tag_list:
            yield response.follow(self.get_href(a), callback=self.parse_novel_info)

    def parse_novel_info(self, response):
        novel_type = response.css("div.con_top::text")[1].re("  > (\w+).*")[0]  # 小说类型
        os.makedirs(os.path.join(BASE_DIR, "novel_collect", novel_type), exist_ok=True)  # 确保该类型的小说路径存在
        novel_name = response.css("div#info h1::text").extract_first()  # 小说名称
        novel_author = response.css("div#info p::text")[0].re("Author：(.*)")[0]  # 小说作者
        novel_update_time = response.css("div#info p")[2].css("::text")[0].re("UpdateTime：(.*)")[0]  # 小说更新时间
        novel_updates = response.css("div#info p")[3].css("a::text").extract_first()  # 小说最近更新章节
        novel_intro = "\n".join(response.css("div#intro::text").extract())  # 小说介绍
        english_novel_json_file = os.path.join(BASE_DIR, "db", "english_novel.json")  # 用来去重或者更新小说
        if not os.path.exists(english_novel_json_file):
            write_file(english_novel_json_file, json.dumps({}))
        else:
            english_novel_dict = json.loads(read_file(english_novel_json_file))
            if novel_name in english_novel_dict:  # 如果之前已经爬取过该小说了
                if english_novel_dict[novel_name]["novel_updates"] == novel_updates:  # 上次爬取的和本次爬取的一致，则跳过
                    return
                else:  # 不一致，说明更新了新内容，需要添加
                    pass
            else:  # 该小说没有爬取过
                english_novel_dict[novel_name] = {
                    "novel_type": novel_type,
                    "novel_author": novel_author,
                    "novel_update_time": novel_update_time,
                    "novel_updates": novel_updates,
                }
                write_file(english_novel_json_file, json.dumps(english_novel_dict))
                novel_file_path = os.path.join(BASE_DIR, "novel_collect", novel_type, novel_name)
                os.makedirs(novel_file_path, exist_ok=True)
                write_file(
                    os.path.join(novel_file_path, "%s_info.txt" % novel_name),
                    "{novel_name}\nAuthor:{novel_author}\nIntro:{novel_intro}".format(
                        novel_name=novel_name, novel_author=novel_author, novel_intro=novel_intro,
                    )
                )
                novel_img_src = response.css("div#fmimg img::attr(src)").extract_first()
                yield response.follow(
                    novel_img_src, callback=lambda response, novel_file_path=novel_file_path:
                    self.save_novel_img(response, novel_file_path)
                )  # 存储小说对应的图片

                for a in response.css("div#list dd a"):  # 存储小说内容
                    yield response.follow(
                        self.get_href(a), callback=lambda response, novel_file_path=novel_file_path:
                        self.save_novel_detail(response, novel_file_path)
                    )

    @staticmethod
    def save_novel_img(response, novel_file_path):
        yield {
            "action": "save_novel_img",
            "novel_file_path": novel_file_path,
            "body": response.body
        }

    @staticmethod
    def save_novel_detail(response, novel_file_path):
        yield {
            "action": "save_novel_detail",
            "novel_file_path": novel_file_path,
            "chapter": re.findall("(\d+).*", response.url)[0],
            "detail": "\n".join(response.css("div#content::text").extract())
        }
