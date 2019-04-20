import sys
import json
import time
import urllib
from urllib import parse
from urllib import request

class Book:
    title = ""
    url = ""
    raters = 0
    avg_rating = 0
    bayes_avg = 0

def cal_bayes_avg(books):
    raters = 0
    rating = 0
    for book in books:
        raters += book.raters
        rating += book.avg_rating * book.raters
    avg_raters = raters / len(books)
    avg_rating = rating / raters

    print("avg_raters: " + str(avg_raters))
    print("avg_rating: " + str(avg_rating))

    for book in books:
        book.bayes_avg = (avg_raters * avg_rating + book.avg_rating * book.raters) / (book.raters + avg_raters)

def search(url, text, start=0):
    print("search index: " + str(start))
    fp = request.urlopen(url + '&q=' + parse.quote(text) + '&start=' + str(start))
    content = fp.read().decode("utf8")
    fp.close()
    return content

def parse_data(data, records):
    for b in data['books']:
        raters = b['rating']['numRaters']
        rating = float(b['rating']['average'])
        if raters > 0:
            book = Book()
            book.avg_rating = rating
            book.raters = raters
            book.title = b['title']
            book.url = b['alt']
            records.append(book)
    return data['start'], data['count'], data['total']

def search_and_parse(url, records, text, start=0):
    return parse_data(json.loads(search(url, text, start)), records)

def collect_data(books, searching_text):
    base_url = "https://api.douban.com/v2"
    search_path = "/book/search"
    apikey = "0b2bdeda43b5688921839c8ecb20399b"
    url = base_url + search_path + '?apikey=' + apikey
    _, count, total = search_and_parse(url, books, searching_text)
    if total > 10000:
        total = 10000
    if total > count:
        for s in range(count, total - (total % count) + 1, count):
            search_and_parse(url, books, searching_text, s)

def sort_by_weighted_rating(book):
    return book.bayes_avg

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 top_books.py <searching_text>')
        exit()

    books = []
    searching_text = sys.argv[1]
    collect_data(books, searching_text)
    cal_bayes_avg(books)
    books.sort(key=sort_by_weighted_rating, reverse=True)

    top_books = books[:50]

    output_file = 'books/' + searching_text + '.md'
    output = open(output_file, 'w', encoding='UTF-8')
    output.write('# Top Books of \'' + searching_text + '\'\n\n')
    output.write('Date: ' + time.asctime(time.localtime()) + '\n\n')
    output.write('| Title | Weighted Ranting |\n')
    output.write('|:----- |:---------------- |\n')
    for book in top_books:
        output.write('| [' + book.title + '](' + book.url + ') | ' + str(book.bayes_avg) + '|\n')
    output.close()

    print('Output: ' + output_file)
    
main()
