import data_cleaner

passing_simple_cases = [
    ['GET','this/will/pass/inspection'],
    ['POST', 'this/works'],
    ['PUT', 'yup/thisguy/too'],
    ['DELETE','this/works']
]

failing_simple_cases = [
    ['GET', 'COLORS'],
    ['POST', 'request'],
    ['POST',''],
    ['POST','request,/fail/wrong']
]

curl_cases = [


]

potential_garbage_cases = [

]

cleaner = data_cleaner.DataCleaner()


for x in passing_simple_cases:
    assert cleaner._simple_case(x).shouldnt.eql(None)

for x in failing_simple_cases:
    assert cleaner._simple_case(x).should.eql(None)
