import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from rhinebeckbank.items import Article


class RhinebeckbankSpider(scrapy.Spider):
    name = 'rhinebeckbank'
    start_urls = ['https://www.rhinebeckbank.com/Newsworthy/blog']

    def parse(self, response):
        links = response.xpath('//a[@class="button wsc_pi_button wsc_readmore"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('(//div[@class="posts-paging"]/a[@class="wsc_tag"])[last()]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="wsc_info_date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="wsc_pi_body"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
