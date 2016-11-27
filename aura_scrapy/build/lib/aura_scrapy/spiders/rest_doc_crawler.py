import scrapy
from csv import reader
class RestDocCrawler(scrapy.Spider):

    name = 'rest_doc_crawler'
    # allowed_domains = ['http://www.programmableweb.com/api/','http://www.programmableweb.com/apis/']
    allowed_regex = r'(http://)?www.programmableweb.com([a-zA-Z0-9\/\-])*'

    ROOT_URL = 'http://www.programmableweb.com'

    START_PAGES = ['http://www.programmableweb.com/category/all/apis?page=1']

    def __init__(self):
            self.start_urls = RestDocCrawler.START_PAGES

    def parse(self, response):
        partial_urls = response.xpath("//div[@class='view-content']/child::node()/tbody/tr/td[@class='views-field views-field-title col-md-3']/a/@href").extract() 
        for partial in partial_urls:
           full_url = ''.join([RestDocCrawler.ROOT_URL,partial])
           yield scrapy.Request(full_url, self.parse_api_page)
        next_page = response.urljoin(response.xpath("//div[@class='text-center']/*/li[@class='pager-last']/a/@href").extract_first())
        yield scrapy.Request(next_page,self.parse)

    def parse_api_page(self,response):
        doc_url = response.xpath("//div[@class='tab-pane fade in active']/div/div/div/label[text()[contains(.,'Docs Home Page URL')]]/following-sibling::span/a/@href").extract_first()
        yield {
                'api_name': response.url.split('/')[-1],
                'doc_url': doc_url
        }


