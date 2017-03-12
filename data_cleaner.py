import datetime
import iso8601
import argparse
import shlex
import re
import json
import logging
import urllib.parse as urlparse
import boto3
from contextlib import contextmanager

class DataCleaner():
    def __init__(self):
        self.row_cache = []
        self.cleaner_cases = {
            'simple': self._simple_case,
            'curl': self._curl_format_case,
            'potential_garbage' : self._potential_garbage_case
        }
        self.row_count = 0
        self.garbage_regex = re.compile(r'((request*.{0,3})|(^.{0,10}$))')
        self.s3_client = boto3.resource('s3')

    def process_row(self,row):
        self.row_count += 1
        row_results = self.cleaner_cases[self._get_row_type(row)](row)
        if not row_results:
            return
        self.row_cache.append(row_results)
        if len(self.row_cache) >= 5000:
            self.flush_row_cache()

    def _simple_case(self,row):
        requests = row['request']
        if len(requests) >= 2 and type(requests[0]) == list:
            return [ { 'api_url': row['api_url'], 'method': request[0], 'parsed_request': ' '.join([urlparse.urljoin(row['api_url'],request[1])]), 'arguments': { 'data': '' } } for request in requests ]
        else:
            return { 'api_url': row['api_url'], 'method': requests[0][0], 'parsed_request': ' '.join([urlparse.urljoin(row['api_url'],requests[0][1])]), 'arguments': { 'data': '' } }

    def _curl_format_case(self,row):
        parsed_result = CurlParser().parse_curl(row['original_text'],row['api_url'])
        if not parsed_result:
            return None
        return parsed_result

    def _get_row_type(self,row):
        if 'curl' in row['original_text'] or 'CURL' in row['original_text']:
            return 'curl'
        if len(row['request']) > 1:
            if any([self.garbage_regex.match(x) for x in row['request'][0]]):
                del(row['request'][0])
            return self._get_row_type(row)
        if any([self.garbage_regex.match(x) for x in row['request'][0]][1:]):
            return 'potential_garbage'
        return 'simple'

    def _potential_garbage_case(self,row):
        potential_valid_cases = []
        for x in row['request']:
            if len(x[1]) <= 8:
                continue
            if '/' not in x[1]:
                continue
            if x[0] == x[1]:
                continue
            potential_valid_cases.append(x)
        if not potential_valid_cases:
            return
        return self._simple_case( { 'api_url': row['api_url'],'request': potential_valid_cases } )

    @contextmanager
    def _s3_assist(self):
        self.s3_client.create_bucket(Bucket='pibrain.dev.general')
        key = ''.join(['datasets/cleaned.data/clean_data_',str(datetime.datetime.utcnow().isoformat())])
        s3_object = self.s3_client.Object('pibrain.dev.general',key)
        yield s3_object

    def flush_row_cache(self):
        with self._s3_assist() as key:
            rows_string = ''.join([''.join([json.dumps(x),'\n']) for x in self.row_cache])
            key.put(Body=rows_string)
        del(self.row_cache)
        self.row_cache = []
        return

class ArgumentParserError(Exception): pass

class CleanerArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

class CurlParser():
    def __init__(self):
        self.parser = CleanerArgumentParser(argument_default='')
        self.parser.add_argument('command')
        self.parser.add_argument('url', nargs='?')
        self.parser.add_argument('--append')
        self.parser.add_argument('--compressed', action='store_true')
        self.parser.add_argument('-A', '--user-agent')
        self.parser.add_argument('--anyauth')
        self.parser.add_argument('-b', '--cookie')
        self.parser.add_argument('-B', '--use-ascii')
        self.parser.add_argument('--basic')
        self.parser.add_argument('-c', '--cookie-jar')
        self.parser.add_argument('--ciphers')
        self.parser.add_argument('--connect-timeout')
        self.parser.add_argument('-d', '--data')
        self.parser.add_argument('-D', '--dump-header')
        self.parser.add_argument('--data-ascii')
        self.parser.add_argument('--data-binary')
        self.parser.add_argument('--data-raw')
        self.parser.add_argument('--data-urlencode',nargs='?')
        self.parser.add_argument('--dns-interface')
        self.parser.add_argument('--dns-ipv4-addr')
        self.parser.add_argument('--dns-ipv6-addr')
        self.parser.add_argument('--dns-servers')
        self.parser.add_argument('-e', '--referer')
        self.parser.add_argument('-E', '--cert')
        self.parser.add_argument('--engine')
        self.parser.add_argument('--environment')
        self.parser.add_argument('--egd-file')
        self.parser.add_argument('--expect100-timeout')
        self.parser.add_argument('--cert-type')
        self.parser.add_argument('--cacert')
        self.parser.add_argument('--capath')
        self.parser.add_argument('--pinnedpubkey')
        self.parser.add_argument('--cert-status')
        self.parser.add_argument('-F', '-f','--form', action='append', default=[], nargs='?')
        self.parser.add_argument('--form-string')
        self.parser.add_argument('-g', '--globoff')
        self.parser.add_argument('-G', '--get')
        self.parser.add_argument('-H', '--header', nargs='?', action='append', default=[])
        self.parser.add_argument('--hostpubmd5')
        self.parser.add_argument('--ignore-content-length')
        self.parser.add_argument('-i', '--include', action='store_true')
        self.parser.add_argument('-I', '--head')
        self.parser.add_argument('--interface')
        self.parser.add_argument('-j', '--junk-session-cookies')
        self.parser.add_argument('-J', '--remote-header-name')
        self.parser.add_argument('-k', '--insecure', action='store_true')
        self.parser.add_argument('-K', '--config')
        self.parser.add_argument('--keepalive-time')
        self.parser.add_argument('--key')
        self.parser.add_argument('--key-type')
        self.parser.add_argument('--krb')
        self.parser.add_argument('--krb4')
        self.parser.add_argument('-l', '--list-only')
        self.parser.add_argument('-L', '--location')
        self.parser.add_argument('--libcurl')
        self.parser.add_argument('--limit-rate')
        self.parser.add_argument('--local-port')
        self.parser.add_argument('--location-trusted')
        self.parser.add_argument('-m', '--max-time')
        self.parser.add_argument('--login-options')
        self.parser.add_argument('--max-redirs')
        self.parser.add_argument('--metalink')
        self.parser.add_argument('-n', '--netrc')
        self.parser.add_argument('-N', '--no-buffer')
        self.parser.add_argument('--netrc-file')
        self.parser.add_argument('--netrc-optional')
        self.parser.add_argument('--negotiate')
        self.parser.add_argument('--no-keepalive')
        self.parser.add_argument('--no-sessionid')
        self.parser.add_argument('--noproxy')
        self.parser.add_argument('--connect-to')
        self.parser.add_argument('--ntlm')
        self.parser.add_argument('--ntlm-wb')
        self.parser.add_argument('-o', '--output')
        self.parser.add_argument('-O', '--remote-name')
        self.parser.add_argument('--oauth2-bearer')
        self.parser.add_argument('--proxy-header')
        self.parser.add_argument('-p', '--proxytunnel')
        self.parser.add_argument('-P', '--ftp-port')
        self.parser.add_argument('--pass')
        self.parser.add_argument('--path-as-is')
        self.parser.add_argument('--post301')
        self.parser.add_argument('--post302')
        self.parser.add_argument('--post303')
        self.parser.add_argument('--proto')
        self.parser.add_argument('--proto-default')
        self.parser.add_argument('--proto-redir')
        self.parser.add_argument('--proxy-anyauth')
        self.parser.add_argument('--proxy-basic')
        self.parser.add_argument('--proxy-digest')
        self.parser.add_argument('--proxy-negotiate')
        self.parser.add_argument('--proxy-ntlm')
        self.parser.add_argument('--proxy-service-name')
        self.parser.add_argument('--proxy1.0')
        self.parser.add_argument('--pubkey')
        self.parser.add_argument('-q', '--disable')
        self.parser.add_argument('-Q', '--quote')
        self.parser.add_argument('-r', '--range')
        self.parser.add_argument('-R', '--remote-time')
        self.parser.add_argument('--raw')
        self.parser.add_argument('--remote-name-all')
        self.parser.add_argument('--resolve')
        self.parser.add_argument('--retry')
        self.parser.add_argument('--retry-delay')
        self.parser.add_argument('--retry-max-time')
        self.parser.add_argument('-s', '--silent')
        self.parser.add_argument('--sasl-ir')
        self.parser.add_argument('--service-name')
        self.parser.add_argument('-S', '--show-error')
        self.parser.add_argument('--ssl')
        self.parser.add_argument('--ssl-reqd')
        self.parser.add_argument('--ssl-allow-beast')
        self.parser.add_argument('--ssl-no-revoke')
        self.parser.add_argument('--socks4')
        self.parser.add_argument('--socks4a')
        self.parser.add_argument('--socks5-hostname')
        self.parser.add_argument('--socks5')
        self.parser.add_argument('--socks5-gssapi-service')
        self.parser.add_argument('--socks5-gssapi-nec')
        self.parser.add_argument('--stderr')
        self.parser.add_argument('--tlsauthtype')
        self.parser.add_argument('--tlspassword')
        self.parser.add_argument('--tlsuser')
        self.parser.add_argument('--tlsv1.0')
        self.parser.add_argument('--tlsv1.1')
        self.parser.add_argument('--tlsv1.2')
        self.parser.add_argument('--tr-encoding')
        self.parser.add_argument('--trace')
        self.parser.add_argument('--trace-ascii')
        self.parser.add_argument('--trace-time')
        self.parser.add_argument('--unix-socket')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-U', '--proxy-user')
        self.parser.add_argument('--url')
        self.parser.add_argument('-v', '--verbose', action='store_true')
        self.parser.add_argument('-w', '--write-out')
        self.parser.add_argument('-X', '-x','--request')
        self.parser.add_argument('--xattr')
        self.parser.add_argument('-y', '--speed-time')
        self.parser.add_argument('-Y', '--speed-limit')
        self.parser.add_argument('-z', '--time-cond')
        self.parser.add_argument('-M', '--manual')
        self.parser.add_argument('-V', '--version')

    def parse_curl(self,curl_command,original_url):
        formatted_command = curl_command
        try:
            return self._general_curl(formatted_command,original_url)
        except ValueError as e:
            return self._embedded_curl(formatted_command,original_url)

    def _attempt_fix(self,curl_command):
        formatted = (curl_command
                    .replace('\\','')
                    .replace('\n','')
                    .replace('\'','')
                    .replace('\u201d','"')
                    .replace('\u201c','"')
                    .replace('"',''))
        formatted = re.sub('{(?:[^\r\n{}]*)(?!\r?\n{)(?!})','}',formatted)
        return formatted
    def _general_curl(self,curl_command,original_url):
        try:
            tokens = shlex.split(curl_command.rstrip().lstrip())
            parsed_args,unparsables,method,user_supplied_token = self._parse_command(tokens)
            if not any([parsed_args,method,user_supplied_token]):
                return None
            parsed_url = parsed_args.url or unparsables[0]
            return {
                'api_url': original_url,
                'method': method,
                'parsed_request': ' '.join([urlparse.urljoin(original_url,parsed_url),user_supplied_token]).rstrip(),
                'arguments': self._build_data_parse(parsed_args)
            }
        except ValueError as e:
            logging.error("{0}, Curl Command:{1} WILL ATTEMPT AS EMBEDDED CURL".format(e,curl_command))
            raise ValueError

    def _embedded_curl(self,curl_command,original_url):
        user_inserts,tokens = self._php_curl_finder(curl_command)
        parsed_args,unparsables,method,user_supplied_token = self._parse_command(tokens)
        if not any([parsed_args,method,user_supplied_token]):
            return None
        parsed_url = parsed_args.url or unparsables[0]
        return { 
            'api_url': original_url,
            'method': method,
            'parsed_request': ' '.join([parsed_url,user_supplied_token]).rstrip(),
            'arguments': self._build_data_parse(parsed_args,user_inserts) 
        }

    def _build_data_parse(self,parsed_args,user_inserts=None):
        try:
            data = str(json.loads(parsed_args.data))
        except:
            data = str(parsed_args.data) if parsed_args.data is not None else None
        return { 'data': data, 'forms': parsed_args.form, 'user_inserts': user_inserts }

    def _parse_command(self,tokenized_command):
        try:
            parsed_args, unparsables = self.parser.parse_known_args(tokenized_command)
        except ArgumentParserError as e:
            logging.error("{0}, Curl Command:{1}, WILL TRY FIXING".format(e,tokenized_command))
            try:
                parsed_args, unparsables = self.parser.parse_known_args(self._attempt_fix(tokenized_command))
                logging.info('FIX SUCCEEDED')
            except:
                logging.error("FIX FAILED: {0}, Curl Command:{1}".format(e,tokenized_command))
                return (None,None,None)
        method = parsed_args.request.upper()
        if not parsed_args.request:
            if parsed_args.data:
                method = "POST"
            else:
                method = "GET"
        user_supplied_token = ''
        if method == "POST" or method == "PUT":
            user_supplied_token = '<user_insert>'
        return (parsed_args,unparsables,method,user_supplied_token)

    def _php_curl_finder(self,curl_command):
        curl_regex = re.compile(r'curl.{0,280}',re.IGNORECASE)
        formatted_curl_command = re.sub(r'\\\"',"'",curl_command)
        dollar_var_regex = re.compile(r'\$[a-zA-Z_0-9]*',re.IGNORECASE)
        curl_match = curl_regex.search(formatted_curl_command)
        curl_match = curl_match.group()
        user_inserts = dollar_var_regex.findall(formatted_curl_command)
        try:
            curl_match = re.sub('"','',curl_match)
            tokens = shlex.split(curl_match.strip())
            self._match_replace_dollar_vars(formatted_curl_command,user_inserts,tokens)
        except Exception as e:
            logging.error(e)
            return None
        return (user_inserts,tokens)

    def _match_replace_dollar_vars(self,curl_command,user_inserts,tokens):
        formatted_inserts = [ user_insert.replace('$','') for user_insert in user_inserts ]
        search_results = [ re.compile('{0}=(?:[^\s,\"]|\"(?:\\.|[^\"])*\")+'.format(x)).search(curl_command) for x in formatted_inserts ]
        try:
            replace_text = [ x.group() for x in search_results ]
            for text in replace_text:
                matcher = re.compile("\${}".format(text.split("=")[0]))
                for i,token in enumerate(tokens):
                    if matcher.search(token):
                        tokens[i] = matcher.sub(text.split("=")[1],token)
        except:
            logging.error('Dollar Var MatchReplace: {0}, {1}'.format(curl_command,user_inserts))

