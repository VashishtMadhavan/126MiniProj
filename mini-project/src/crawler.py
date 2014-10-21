import numpy as np
from __future__ import division
import re
import sys
import urllib
import urlparse
import random
from bs4 import BeautifulSoup


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
            #we want to stay in the berkeley domain. This becomes more relevant later
            if domain(tmp).endswith('berkeley.edu'):
                url_list.append(tmp)
        if len(url_list) == 0:
            return [url_start]
        return url_list
    except:
        return [url_start]


 def pagerank(url_start,num_iterations):
 	## function to find the fraction of time spent in each page
 	##if num_iterations is high fraction of time spent in each page converges to probability of being on that page
 	##CODE HERE
 	return

##modify this do search daily cal
url_start = "http://www.eecs.berkeley.edu/Research/Areas/"
current_url = url_start
num_of_visits = 3
#List of professors obtained from the EECS page
profs = ['Abbeel','Agrawala','Alon','Anantharam','Arcak','Arias','Asanović','Bachrach','Bajcsy','Bodik','Bokor','Boser','Brewer','Canny','Chang-Hasnain','Culler','Darrell','Demmel','Fearing','Fox','Franklin','Garcia','Goldberg','Hartmann','Harvey','Hellerstein','Javey','Joseph','Katz','Keutzer','Liu','Klein','Kubiatowicz','Lee','Lustig','Maharbiz','Malik','Nguyen','Niknejad','Nikolic',"O'Brien",'Parekh','Patterson','Paxson','Pisano','Rabaey','Ramchandran','Roychowdhury','Russell','Sahai','Salahuddin','Sanders','Sangiovanni-Vincentelli','Sastry','Sen','Seshia','Shenker','Song','Song','Spanos','Stoica','Stojanovic','Tomlin','Tygar','Walrand','Wawrzynek','Wu','Yablonovitch','Yelick','Zakhor']
bad_urls = ['http://bgess.berkeley.edu/%7Ensbejr/index.html','http://superior.berkeley.edu/Berkeley/Buildings/soda.html','http://physicalplant.berkeley.edu/','http://www.eecs.berkeley.edu/Deptonly/Rosters/roster.room.cory.html',' http://www.eecs.berkeley.edu/Resguide/admin.shtml#aliases','http://www.eecs.berkeley.edu/department/EECSbrochure/c1-s3.html']
# bad urls help take care of some pathologies that ruin our surfing
# you might have to be smart with try-catches depending on your application

#Creating a dictionary to keep track of how often we come across a professor
profdict = {}
for i in profs:
    profdict[i] = 0

for i in range(num_of_visits):
    if random.random() < 0.9: #follow a link!
        print  i , ' Visiting... ', current_url
        url_list = parse_links(current_url, url_start)
        current_url = random.choice(url_list)
        if current_url in bad_urls or "iris" in current_url or "Deptonly" in current_url: #dealing with more pathologies
            current_url = url_start
        myopener = MyOpener()
        page = myopener.open(current_url)
        text = page.read().lower()
        page.close()
        #Figuring out which professor is mentioned on a page.
        ##Instead of this do a textrank of the words in an article/page
        for p in profs:
            profdict[p]+= 1 if " " + p.lower() + " " in text else 0 #can use regex re.findall(i,text), but it's overkill
    else: #click 'home' button!
        current_url = url_start
