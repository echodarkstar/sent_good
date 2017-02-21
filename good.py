# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from canvas.items import Book
import re,csv
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords # Import the stop word list
with open('book_rev.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Review","Rating"])
seen =set()
class GoodSpider(CrawlSpider):
    def review_to_words(self,raw_review):
        #Remove non-letters
        letters_only = re.sub("[^a-zA-Z]", " ", raw_review)
        #Convert to lower case, split into individual words
        words = letters_only.lower().split()
        #Joining words into single string separated by space, and returning result.
        return( " ".join( words ))
    name = "good"
    def __init__(self, category=None, *args, **kwargs):
        super(GoodSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.goodreads.com/search?q={}'.format(category)]
    def parse(self,response):
        link = response.css('a[itemprop="url"]::attr(href)').extract_first()
        link = response.urljoin(link)
        yield scrapy.Request(link, callback=self.product_parse)

    def product_parse(self, response):
        book = Book()
        book['title'] = response.css('h1#bookTitle::text').extract_first().strip(' \n\t\r')
        book['author'] = response.css('a.authorName span::text').extract_first()
        book['genres'] = []
        for i in response.css('div.rightContainer div.stacked div.elementList a::text').extract():
            if "user" not in i:
                book['genres'].append(i)
        book['genres'] = ' | '.join(list(set(book['genres'])))
        for i in response.css('div.review'):
            book['user'] = i.css('a.user::attr(href)').extract_first()
            book['rating'] = (len(i.css('span.staticStars span.p10').extract()))
            rev = i.css('div.reviewText span ::text').extract()
            for j in rev:
                book['review'] = self.review_to_words(''.join(rev).replace('...more',''))
                prod_dict = {'Review': book['review'],"Rating":book['rating']}
                if book['review'] not in seen:
                    seen.add(book['review'])
                    with open('book_rev.csv', 'a', newline='') as csvfile:
                            headings = ['Review','Rating']
                            writer = csv.DictWriter(csvfile, fieldnames=headings)
                            writer.writerow(prod_dict)
