import scrapy
from manga.settings import *
import sys
import logging
import re
from manga.items import MangaItem

class CmadSpider(scrapy.Spider):
    name = "cmad"
    xpath = {
        "urls": ["http://www.cartoonmad.com/comic/1217.html"],
        "chapter": "//a[contains(., '話')]/@href",  # 默认下载话
        "image_page": "//option[contains(., '頁')]/@value",  
        "image": "//img[contains(@src, 'cartoonmad.com')]/@src",
        "start_index": "73",
    }

    def start_requests(self):
        urls = self.xpath.get("urls")
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        start_index = int(self.xpath.get("start_index"))
        srcs = response.xpath(self.xpath.get("chapter")).extract()
        # hikaru test
        # srcs = ["http://www.cartoonmad.com/comic/109000211098001.html", "http://www.cartoonmad.com/comic/109000221097001.html", "http://www.cartoonmad.com/comic/109000231095001.html"]
        srcs = [response.urljoin(x) for x in srcs]
        for src in srcs:
            yield scrapy.Request(url=src, callback=self.parse_chapter)


    def parse_chapter(self, response):
        srcs = response.xpath(self.xpath.get("image_page")).extract()
        srcs = [response.urljoin(x) for x in srcs]
        for src in srcs:
            yield scrapy.Request(url=src, callback=self.parse_image_page) 

    def parse_image_page(self, response):
        srcs = response.xpath(self.xpath.get("image")).extract()
        self.log(srcs)
        title = response.xpath("//title/text()").extract_first().split("-")
        manga_name = title[0].split(" ")[0]
        chapter_name = title[1].strip()

        logging.info("downloading " + manga_name + ": " + chapter_name)

        item = MangaItem(image_urls=srcs, manga_name=manga_name, chapter_name=chapter_name)
        return item


