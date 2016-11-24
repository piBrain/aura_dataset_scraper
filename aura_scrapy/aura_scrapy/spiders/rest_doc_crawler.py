import scrapy
from csv import reader
from IPython import embed
class rest_doc_crawler(scrapy.Spider):

    name = 'rest_doc_crawler'
    allowed_domains = ['http://www.programmableweb.com/api/','http://www.programmableweb.com/apis/']

    ROOT_URL = 'http://www.programmableweb.com'
    
    def __init__(self,path):
        with open(path,'r+') as f:
            self.start_urls = [page for page in reader(f)][0]
            embed()
        

    def parse(self, response):
        partial_urls = response.xpath("//div[@class='view-content']/child::node()/tbody/tr/td[@class='views-field views-field-title col-md-3']/a/@href").extract()

        for partial in partial_urls:
           full_url = ROOT_URL.join(partial)
           yield scrapt.Request(full_url,self.parse_api_page)
        response.urljoin(response.xpath("//div[@class='text-center']/*/li[@class='pager-last']/a/@href").extract_first())
        embed()

    def parse_api_page(self,response):
        embed()
        response.xpath("/")



