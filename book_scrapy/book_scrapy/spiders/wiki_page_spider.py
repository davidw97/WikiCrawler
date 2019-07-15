from scrapy.spiders import Spider
from ..items import BookItem, AuthorItem
import re


class WikiPageSpider(Spider):
    """
    Spider to get basic information about a book from a wikipedia article
    """
    name = 'WikiPageSpider'

    start_urls = ["file:///home/david/Desktop/James%20A.%20Michener%20-%20Wikipedia.html"]

    def parse(self, response):
        author = AuthorItem()

        table_rows = response.css('table.infobox.vcard').xpath('./tbody/tr')

        # url (For reference and to prevent duplicates)
        author['url'] = response.url

        # Title
        author['name'] = response.xpath('string(//h1[@id="firstHeading"])').get()

        # Place unknown values into a list
        unknown = []

        # Details from infobox
        for tr in table_rows:
            # Get main image from the article, if it exists
            if tr.xpath('./td/a[@class="image"]/@href'):
                author['image'] = tr.xpath('./td/a[@class="image"]/@href').get()
            else:
                data = tr.xpath('string(./td)').get()
                title = tr.xpath('./th/text()').get()

                try:
                    if title is not None:
                        new_title = re.sub(r' ', '_', title.lower())
                        author[new_title] = data
                except (AttributeError, KeyError):
                    unknown.append(data)

        # Description from top section in article
        author['description'] = "".join([
            p.xpath('string()').get()
            for p in response.xpath('//*[@id="toc"]/preceding-sibling::p')
        ])

        author['unknown'] = unknown

        yield author
