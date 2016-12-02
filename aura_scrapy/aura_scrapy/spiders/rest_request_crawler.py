import scrapy
import re
import json
import html2text as h2t
import IPython as ip
import itertools

class RestRequestCrawler(scrapy.Spider):
    
    name = 'rest_request_crawler'
    data_path = './data/api_urls.jl'
    regexs = [re.compile(r'(GET|POST|DELETE|PUT\A) ([a-zA-z/:,0-9\-.]+)+'), re.compile(r'(GET|DELETE|POST|PUT\A)[,a-zA-Z0-9/\-:. ]+')]


    def __init__(self):
        self.api_data = self.load_api_data()
        self.allowed_regexs = []
        self.last_found_data = 0

    def start_requests(self):
        for api in self.api_data:
            try:
                self.last_found_data = 0
                self.page_depth = 0
                parse_lambda = lambda response,api_name=api['api_name']: self.docs_parse(response,api_name)
                self._update_allowed_domains(api['doc_url'])
                yield scrapy.Request(api['doc_url'], callback=parse_lambda)
            except TypeError:
                print('Empty doc url.')


    def docs_parse(self,response,api_name):

        if self.page_depth > 100:
            return
        self.page_depth+=1
        data_dict = self._extract_request_documentation(api_name,response)

        for match_dict in data_dict['h2t']:
            if match_dict is None:
                continue
            yield match_dict
        for match_dict in data_dict['xpath']:
            if match_dict is None:
                continue
            yield match_dict

        for url in response.xpath("//a/@href").extract():
            parse_lambda = lambda response,api_name=api_name: self.docs_parse(response,api_name)
            yield scrapy.Request(response.urljoin(url),callback=parse_lambda)


    def _extract_request_documentation(self,api_name,response):
        self.last_found_data += 1
        data_dict = {'h2t': [], 'xpath': []}
        for regex in RestRequestCrawler.regexs:
            for matched_text in re.findall(regex,h2t.html2text(str(response.body))):
                self.last_found_data = 0
                data_dict['h2t'].append(self._clean_scrape_data(matched_text,api_name,response))
            for matches in list(itertools.chain.from_iterable([re.findall(regex,text) for text in response.xpath("//text()").extract()])):
                self.last_found_data = 0
                data_dict['xpath'].append(self._clean_scrape_data(matches,api_name,response,'_xpath'))
        return data_dict

    def _clean_scrape_data(self,matched_text,api_name,response,suffix=''):
        if not matched_text:
            return None
        if type(matched_text) is str:
            return None
        return {
                'api_name': api_name+suffix,
                'api_url': response.url,
                'request': list(matched_text)
        }


    def _update_allowed_domains(self,url):
        self._add_to_regexs(url)
        self._refresh_allowed_domains()

    def _add_to_regexs(self,url):
        if url == None:
            return
        domain = url.split('//')[-1].split("/")[0]
        self.allowed_regexs.append(r"".join(["(http://)?",domain,"([a-zA-Z0-9/\-])*"]))

    def _refresh_allowed_domains(self):
        for mw in self.crawler.engine.scraper.spidermw.middlewares:
            if isinstance(mw, scrapy.spidermiddlewares.offsite.OffsiteMiddleware):
                mw.spider_opened(self)

    def load_api_data(self):
        with open(RestRequestCrawler.data_path,'r+') as f:
            return [ json.loads(line) for line in f ]
