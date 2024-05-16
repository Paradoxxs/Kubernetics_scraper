import scrapy


class ToScrapeCSSSpider(scrapy.Spider):
    name = "toscrape-css"
    start_urls = [
        'https://www.shellsec.pw/',
    ]

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                'body': quote.css("post_body::text").extract_first(),
                'author': quote.css("largetext::text").extract_first(),
                'timestamp': quote.css("float_left smalltext::text").extract_first()
            }

        next_page_url = response.css("li.next > a::attr(href)").extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))