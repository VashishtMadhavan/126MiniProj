from __future__ import division
import re
import numpy as np
import sys
import urllib
import urlparse
import random
from bs4 import BeautifulSoup
from textRank import extractKeyphrases
import operator

#constant variables
#set of non-alphanumeric characters
#run .strip(delchars) to get rid of all the unknown characters in an article
delchars = ''.join(c for c in map(chr, range(256)) if not c.isalnum())
#stop words in english read from stopwords.txt
f=open('stopwords.txt','r')
stop_words=[line.strip(delchars) for line in f]
f.close()


#http://wolfprojects.altervista.org/articles/change-urllib-user-agent/ 
class MyOpener(urllib.FancyURLopener):
   version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'

#This function will parse a url to give you the domain. Test it!
def domain(url):
    #urlparse breaks down the url passed it, and you split the hostname up 
    #Ex: hostname="www.google.com" becomes ['www', 'google', 'com']
    hostname = urlparse.urlparse(url).hostname.split(".")
    hostname = ".".join(len(hostname[-2]) < 4 and hostname[-3:] or hostname[-2:])
    return hostname

def cleanText(list_tags):
    for tag in list_tags:
        if tag.has_attr('id'):
            list_tags.remove(tag)
    text=' '.join(t.get_text() for t in list_tags)
    return text


def getArticleText(article_url):
    myopener = MyOpener()
    try:
        page = myopener.open(article_url)
    except:
        return ""
    text = page.read()
    page.close()
    soup=BeautifulSoup(text, "html5lib")
    try:
        articleTitle=soup.find_all('h2','entry-title')[0].get_text()
    except:
        articleTitle=" "
    try:
        articleContent= cleanText(soup.find_all('div','entry-content')[0].find_all('p'))
    except:
        articleContent=" "
    return articleTitle + " "+articleContent

#This function will return all the urls on a page, and return the start url if there is an error or no urls
def parse_links(url, url_start, domain_name):
    url_list = []
    myopener = MyOpener()
    try:
        #open, read, and parse the text using beautiful soup
        page = myopener.open(url)
        text = page.read()
        page.close()
        soup = BeautifulSoup(text,"html5lib")
        #anytime dailycal throws a bad url, add some info about the url in this
        bad_urls=['email-protection','.jpg','http://donate', 'http://apply','http://advertise']

        #find all hyperlinks using beautiful soup
        for tag in soup.findAll('a', href=True):
            #concatenate the base url with the path from the hyperlink
            tmp = urlparse.urljoin(url, tag['href'])
            try:
                domain(tmp)
            except:
                continue
            #we want to stay in the daily cal domain. This becomes more relevant later
            if domain(tmp).endswith(domain_name):
                checkBad=False
                #regex match for dates in urls as they denote articles
                match=re.search(r'(\d+/\d+/\d+)',tmp)
                for bad in bad_urls:
                    if tmp.endswith(bad) or tmp.startswith(bad):
                        checkBad=True
                if not checkBad and match and tmp!=url:
                    url_list.append(tmp)
        if len(url_list) == 0:
            return [url_start]
        return url_list
    except:
        return [url_start]


#finds invariant distribution of certain set of pages
def pagerank(url_start,num_iterations, domain_name):
    curr=url_start
    visit_history={}
    for i in range(num_iterations):
        print i, "Visiting URL: ", curr
        if curr not in visit_history.keys():
            visit_history[curr]=1.0/(num_iterations)
        else:
            visit_history[curr]+=1.0/(num_iterations)
        url_list=parse_links(curr,url_start, domain_name)
        curr=random.choice(url_list)
    return visit_history

def textrank(current_url):
    #returns the top keywords in a certain article(keywords are adjusted for article length)
    text= getArticleText(current_url)
    return extractKeyphrases(text)


#calculates a combined rank based on pagerank and textrank
def analyze_articles_and_words(page_ranks):
    words_and_articles = {}
    for page in page_ranks.keys():
        # normalized over top 20
        rank = page_ranks[page]
        word_scores = textrank(page)
        for word, word_weight in word_scores:
            if words_and_articles.get(word):
                words_and_articles[word] += word_weight * rank   
            else:
                words_and_articles[word] = word_weight * rank
    # factor = 1.0/sum(words_and_articles.itervalues())
    # return {k: v*factor for k, v in words_and_articles.iteritems()}
    return sorted(words_and_articles.items(), key=operator.itemgetter(1), reverse=True)

#run this algorithm a certain number of simulation trials
#accounts for variability in each crawling simulation
def simulate(url_start,num_iterations,domain_name):
    words_ranks={}
    for i in range(num_iterations):
        print "Crawler Iteration ", i
        print "-----------------"
        results=analyze_articles_and_words(pagerank(url_start, 100, domain_name))
        for word,weight in results:
            if not words_ranks.get(word):
                words_ranks[word]=weight/num_iterations
            else:
                words_ranks[word]+=weight/num_iterations

    for x in words_ranks.keys():
        print "Word: " + x + " " + "Score: " + str(words_ranks[x])



if __name__=="__main__":
   simulate("http://www.dailycal.org", 5, "dailycal.org")
