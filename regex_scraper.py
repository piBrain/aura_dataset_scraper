import urllib
import re
import csv
import sys
from urllib.request import urlopen
import html2text as h2t
from IPython import embed

def get_pages(path):
    with open(path,'r') as csv_f:
        reader = csv.reader(csv_f, delimiter=',')
        pages = [page for page in reader][0]
    return pages

def main():
    try:
        pages = get_pages(sys.argv[1])
    except e:
        print(e)
    regex = re.compile(r'(GET|POST|DELETE|PUT\A) ([a-zA-z/:,0-9\-]+)')
    y =[re.findall(regex,h2t.html2text(str(urlopen(page).read()))) for page in pages]

    embed()
if __name__ == '__main__':
    main()
