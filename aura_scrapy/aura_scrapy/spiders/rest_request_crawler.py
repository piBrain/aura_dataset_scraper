import scrapy
import re
import json
import html2text as h2t
import itertools
import os
import aura_scrapy
import urllib

class RestRequestCrawler(scrapy.Spider):
    name = 'rest_request_crawler'
    regexs = [re.compile(r'(GET|POST|DELETE|PUT\A) ([a-zA-z/:,0-9{}\-.]+)+'), re.compile(r'(GET|DELETE|POST|PUT\A)[,a-zA-Z0-9/\-:{}`. ]+')]
    crawlera_enabled = True
    crawlera_apikey = '4f24252b2cfe4c3cabf35d866e9dca17'
    allowed_schemes = ['http','https']
    allowed_link_substrings = ['dev','developer','developers','api','resources','devcenter','doc','docs','dev-center']

    def __init__(self):
        self.api_data = self.load_api_data()
        self.allowed_regexs = []
        self._seen_domains = {}

    def start_requests(self):
        for api in self.api_data:
            try:
                parse_lambda = lambda response,api_name=api['api_name']: self.docs_parse(response,api_name)
                self._add_to_allowed_domains(api['doc_url'])
                self._add_to_seen_domains(urllib.parse.urlparse(api['doc_url']).netloc,1,0)
                yield scrapy.Request(api['doc_url'], callback=parse_lambda)
            except TypeError:
                print('Empty doc url.')

    def docs_parse(self,response,api_name):
        self._update_domain_seen_count(urllib.parse.urlparse(response.url).netloc)
        
        data_array = self._extract_request_documentation(api_name,response)

        for match_dict in data_array:
            if match_dict is None:
                continue
            yield match_dict

        if not self._can_crawl(urllib.parse.urlparse(response.url).netloc):
            return 

        for url in response.xpath("//a/@href").extract():
            full_url = response.urljoin(url)
            if urllib.parse.urlparse(full_url)[0] not in RestRequestCrawler.allowed_schemes:
                continue
            if not any([x in urllib.parse.urlparse(full_url).netloc for x in RestRequestCrawler.allowed_link_substrings]):
                continue
            parse_lambda = lambda response,api_name=api_name: self.docs_parse(response,api_name)
            yield scrapy.Request(response.urljoin(url),callback=parse_lambda)

    def _can_crawl(self,url):
        if url in self._seen_domains:
            if self._seen_domains[url]['count'] >= 200:
                try:
                    if (self._seen_domains[url]['count'] / self._seen_domains[url]['data'] <= 0.3):
                        del(self._seen_domains[url])
                        return False
                except ZeroDivisionError:
                    print('Caught ZeroDivErr')
                    return False
            return True
        else:
            self._add_to_seen_domains(url,0,0)
            return True

    def _update_domain_seen_count(self,url):
        if url in self._seen_domains:
            self._seen_domains[url]['count'] += 1
        else:
            self._add_to_seen_domains(url,1,0)
        return

    def _update_domain_data_count(self,url):
        if url not in self._seen_domains:
            self._add_to_seen_domains(url,1,1)
            return
        self._seen_domains[url]['data'] += 1
        return

    def _add_to_seen_domains(self,url,initial_count,initial_data_count):
        self._seen_domains[url] = { 'count': initial_count, 'data': initial_data_count }

    def _extract_request_documentation(self,api_name,response):

        data_array = []
        for regex in RestRequestCrawler.regexs:
            for match in re.findall(regex,h2t.html2text(str(response.body))):
                data_array.append(self._clean_scrape_data(match,api_name,response))
            for text in response.xpath("//text()").extract():
                matches = re.findall(regex,text.rstrip())
                if len(matches) > 0:
                    data_array.append(self._clean_scrape_data(matches,api_name,response,text))
        return data_array

    def _clean_scrape_data(self,matched_text,api_name,response,original_text=''):
        if not matched_text:
            return None
        match_list = list(matched_text)
        if not any([type(x) == tuple for x in list(match_list)]):
            return None
        self._update_domain_data_count(urllib.parse.urlparse(response.url).netloc)
        return {
                'api_name': api_name,
                'api_url': response.url,
                'request': match_list,
                'original_text': original_text
        }


    def _add_to_allowed_domains(self,url):
        self._add_to_regexs(url)
        self._refresh_allowed_domains()
        return

    def _remove_from_allowed_domains(self,url):
        self._remove_from_regexs(url)
        self._refresh_allowed_domains()
        return

    def _add_to_regexs(self,url):
        if url == None:
            return
        domain = urllib.parse.urlparse(url).netloc
        self.allowed_regexs.append(r"".join(["(http://)?",domain,"([a-zA-Z0-9/\-])*"]))

    def _remove_from_regexs(self,url):
        domain = urllib.parse.urlparse(url).netloc
        for i,x in enumerate(self.allowed_regexs):
            if r"".join(["(http://)?",domain,"([a-zA-Z0-9/\-])*"]) == x:
                del(self.allowed_regexs[i])
                return
        return

    def _refresh_allowed_domains(self):
        for mw in self.crawler.engine.scraper.spidermw.middlewares:
            if isinstance(mw, scrapy.spidermiddlewares.offsite.OffsiteMiddleware):
                mw.spider_opened(self)

    def load_api_data(self):
        with open(os.path.join(os.path.dirname(aura_scrapy.__file__),'data','api_urls.jl')) as f:
            return [ json.loads(line) for line in f ]
