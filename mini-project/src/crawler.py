from __future__ import division
import re
import numpy as np
import sys
import urllib
import urlparse
import random
from bs4 import BeautifulSoup
from textRank import extractKeyphrases

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
    
#This function will return all the urls on a page, and return the start url if there is an error or no urls
def parse_links(url, url_start):
    url_list = []
    myopener = MyOpener()
    try:
        #open, read, and parse the text using beautiful soup
        page = myopener.open(url)
        text = page.read()
        page.close()
        soup = BeautifulSoup(text)

        #find all hyperlinks using beautiful soup
        for tag in soup.findAll('a', href=True):
            #concatenate the base url with the path from the hyperlink
            tmp = urlparse.urljoin(url, tag['href'])
            try:
                domain(tmp)
            except:
                continue
            #we want to stay in the daily cal domain. This becomes more relevant later
            if domain(tmp).endswith('dailycal.org'):
                url_list.append(tmp)

        if len(url_list) == 0:
            return [url_start]
        return url_list
    except:
        return [url_start]


#finds invariant distribution of certain set of pages
def pagerank(url_start,num_iterations):
    curr=url_start
    visit_history={}
    for i in range(num_iterations):
        print i, "Visiting URL: ", curr
        if curr not in visit_history.keys():
            visit_history[curr]=1.0/(num_iterations)
        else:
            visit_history[curr]+=1.0/(num_iterations)
        url_list=parse_links(curr,url_start)
        curr=random.choice(url_list)
    return visit_history

def textrank(current_url):
    #returns the top keywords in a certain article(keywords are adjusted for article length)
    myopener = MyOpener()
    page = myopener.open(current_url)
    text = page.read()
    page.close()
    soup=BeautifulSoup(text)
    return extractKeyphrases(text)


## TODO: modify this do search daily cal
def analyze_articles(url_start,num_visits):
    # bad urls help take care of some pathologies that ruin our surfing
    # you might have to be smart with try-catches depending on your application
    #TODO: add list of bad urls in our surfing

    #Creating a dictionary to keep track of the importance of terms across articles
    word_dict = {}
    current_url = url_start

    for i in range(num_of_visits):
        if random.random() < 0.9: #follow a link!
            print  i , ' Visiting... ', current_url
            url_list = parse_links(current_url, url_start)
            current_url = random.choice(url_list)
            #TODO: deal with pathologies

            myopener = MyOpener()
            page = myopener.open(current_url)
            text = page.read().lower()
            page.close()
            #TODO add textrank computation here

        else: #click 'home' button!
            #TODO: may want to change this
            current_url = url_start
    word_ranks = [pair for pair in sorted(profdict.items(), key=lambda item: item[1], reverse=True)]
    return word_ranks

if __name__=="__main__":
    print pagerank("http://www.dailycal.org",100)
    #print domain("javascript:")


