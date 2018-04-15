# -*- coding: utf-8 -*-
import scrapy

from scrapy.http import Request
from urllib import parse
from scrapy.selector import Selector

from items import ShixisengJobItem,ShixisengJobItemLoader
from utils.common import get_md5

class ShixisengSpider(scrapy.Spider):
    name = 'shixiseng'
    allowed_domains = ['www.shixiseng.com']
    start_urls = ['https://www.shixiseng.com/interns/']

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
        """
        res = Selector(response)

        #解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_nodes = res.css(".info1 .name-box a")
        for post_node in post_nodes:
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin('https://www.shixiseng.com', post_url),  callback=self.parse_detail)

        #提取下一页并交给scrapy进行下载
        next_url = res.xpath('//*[@id="pagebar"]/ul/li[9]/a/@href').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin('https://www.shixiseng.com', next_url), callback=self.parse)

    def parse_detail(self, response):
        item_loader = ShixisengJobItemLoader(item=ShixisengJobItem(), response=response)
        item_loader.add_xpath("job_name", "/html/body/div[1]/div[2]/div[1]/div[1]/text()")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_xpath("salary", "/html/body/div[1]/div[2]/div[1]/div[3]/span[1]/text()")
        item_loader.add_xpath("job_city", "/html/body/div[1]/div[2]/div[1]/div[3]/span[2]/text()")
        item_loader.add_xpath("work_day", "/html/body/div[1]/div[2]/div[1]/div[3]/span[4]/text()")
        item_loader.add_xpath("degree_need", "/html/body/div[1]/div[2]/div[1]/div[3]/span[3]/text()")

        item_loader.add_xpath("publish_time", "//*[@class='job_date ']/span[1]/text()")
        item_loader.add_xpath("job_advantage", "/html/body/div[1]/div[2]/div[1]/div[4]/text()")
        item_loader.add_xpath("job_desc", "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]")
        item_loader.add_xpath("job_addr", "/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/div[5]/span[1]/text()")

        item_loader.add_xpath("company_url", "/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/a/@href")
        item_loader.add_xpath("company_name", "/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/text()")

        job_item = item_loader.load_item()

        return job_item