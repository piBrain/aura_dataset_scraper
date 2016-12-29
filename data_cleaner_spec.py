import data_cleaner
import sure
import unittest
import IPython as ip

class DataCleanerTest(unittest.TestCase):

    def setUp(self):
        self.cleaner = data_cleaner.DataCleaner()

    def test_simple_case(self):
        simple_case = {'original_text': '', 'request':[['GET','this/will/pass/inspection']] }
        self.cleaner._simple_case(simple_case).should.eql( { 'arguments': { 'data':'' },'parsed_request':'GET this/will/pass/inspection' } )

    def test_multiple_simple_case(self):
        multiple_simple_case = {'original_text': '','request':[['GET','this/will/pass/inspection'],['POST','this/too']] }
        valid = [
            { 'arguments': { 'data':'' }, 'parsed_request':'GET this/will/pass/inspection' },
            { 'arguments': { 'data':'' }, 'parsed_request':'POST this/too' }
        ]
        self.cleaner._simple_case(multiple_simple_case).should.eql(valid)

    def test_potential_garbage_case(self):
        these_should_all_be_garbage = [
         {'data':'', 'request':[['GET', 'COLORS']] },
         {'data':'', 'request':[['GET', 'requests']] },
        ]
        for invalid in these_should_all_be_garbage:
            with self.subTest(invalid['request'][0][1], invalid=invalid):
                self.cleaner._potential_garbage_case(invalid).should.eql(None)
    def test_simple_curl_case(self):
        simple_curl = {'data':'', 'request':[''], 'original_text': 'curl http://www.example.com'}
        (self.cleaner._curl_format_case(simple_curl)
             .should.eql({
                 'arguments': {'data': None, 'forms': None, 'user_inserts': None},
                 'parsed_request': 'GET http://www.example.com'
             }))

    def test_complex_curl_case(self):
        complex_curl = {
                'request':[''],
                'original_text': 'curl -X POST http://www.example.com -d \'{ "auth": { "user": "abc", "password": "def"} }\''
        }
        (self.cleaner._curl_format_case(complex_curl)
             .should.eql({
                 'arguments': {'data': "{'auth': {'user': 'abc', 'password': 'def'}}", 'forms': None, 'user_inserts': None},
                 'parsed_request': 'POST http://www.example.com <user_insert>'
             }))

    def test_mangled_curl_case(self):
        mangled_curl = {
        "original_text": '''
            <![cdata[
            \r\napi_key=...
            \r\nkey_secret=...
            \r\nservice_endpoint=\"https://$api_key:$key_secret@text.s4.ontotext.com/v1/news\"
            \r\n\r\n# office word document file name
            \r\nms_word_document=...
            \r\ncontent_type=\"application/msword\"
            \r\n\r\njson_request=\"{\\\"documenttype\\\" : \\\"$content_type\\\"}\"
            \r\n\r\ncurl -x post -f \"meta=$json_request;type=application/json\" -f \"data=@$ms_word_document\" $service_endpoint
            \r\n]]>"
        ''',
        "request": [["POST","-F"]]
        }

        (self.cleaner._curl_format_case(mangled_curl)
             .should.eql({
                 'arguments': {'data': None, 'forms': ['meta="{\'documenttype\' : \'$content_type\'}";type=application/json', 'data=@...'], 'user_inserts': ['$api_key', '$key_secret', '$content_type', '$json_request', '$ms_word_document', '$service_endpoint']},
                 'parsed_request': 'POST "https://$api_key:$key_secret@text.s4.ontotext.com/v1/news"'
             }))

    def test_simple_row_type(self):
        row = {
            'original_text': '',
            'request':[['GET','this/will/pass/inspection']]
        }
        self.cleaner._get_row_type(row).should.eql('simple')

    def test_curl_row_type(self):
        row = {
            'original_text': 'Im a curl -x post -d {"key":"data"} -f "form=abc" www.example.com',
            'request': ['GET','www.iman.com/example/']
        }
        self.cleaner._get_row_type(row).should.eql('curl')

    def test_garbage_row_type(self):
        rows = [
            {
                'original_text': '',
                'request': [['GET','request,']]
            },
            {
                'original_text': '',
                'request': [['GET','COLORS']]
            }
        ]
        for x in rows:
            with self.subTest(x['request'][0][1], x=x):
                self.cleaner._get_row_type(x).should.eql('potential_garbage')

    def test_multi_garbage_row_type(self):
        with self.subTest('Multi-Garbage'):
            garbage_row = {
             'original_text': '',
             'request': [['GET','COLORS'],['GET','request']]
            }
            self.cleaner._get_row_type(garbage_row).should.eql('potential_garbage')

        with self.subTest('Half-Garbage'):
            half_garbage_row = {
             'original_text': '',
             'request': [['GET','request,'],['GET','this/is/valid/example']]
            }
            self.cleaner._get_row_type(half_garbage_row).should.eql('simple')





if __name__ == '__main__':
    unittest.main()
