#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Indonesia

# resepkoki.id

# In[1]:


# import packages
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import json
import re
from google_trans_new import google_translator 
import requests
from parsel import Selector
from pprint import pprint
import ast
import pandas as pd
from lxml import html
import requests
import pandas as pd
import numpy as np


# In[78]:


# 1. create a list to store all recipe htmls on one page
# initialize htmlLst to store the htmls of all recipes
htmlLst = []

def htmlOnePageSpider(category_url, lst):
    """
    input: category_url, the url of first page of the recipe web
    input: the initial htmlLst
    output: htmlDic with all recipe htmls on one page of one category
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.899274966.1636302399; MarketGidStorage={"0":{"svspr":"https://resepkoki.id/category/ayam-daging/","svsds":1,"TejndEEDj":"UBUiqI9Jd"},"C918445":{"page":2,"time":1636302446738}}; _gid=GA1.2.381378313.1636488043; __gads=ID=d44d6af592795f11:T=1636302399:S=ALNI_MZEbH73O51a_1FNwtgcjyBtaJo4TA',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(category_url,headers=headers)
    sel = Selector(response.text)
    for i in sel.xpath('//div[@class="masonry-grid"]/descendant::*/a/@href'):
        lst.append(i.get())
        
    
    return lst


# In[79]:


# 2. go through all pages in the web and get all recipe htmls

# initialize pageLst to store the htmls of all pages
pageLst = []

pageLst.append("https://resepkoki.id/")

for i in range(2,139):
    pageLst.append("https://resepkoki.id/page/{}/".format(i))
    
# go over each page and get recipe urls    
htmlLst = []
for i in pageLst:
    htmlLst = htmlOnePageSpider(i, htmlLst)


# In[88]:


# clean the html list

# remove the replicated links
htmlLst = list(set(htmlLst))

# only keep the links with "https://resepkoki.id/resep/"
tempLst = []
for i in htmlLst:
    if "https://resepkoki.id/resep/" in i:
        tempLst.append(i)
        
htmlLst = tempLst


# In[91]:


print("The number of recipes is {}".format(len(htmlLst)))


# In[139]:


# 3. go through all recipe htmls and scrape the data we want

Indonesiadata = {
    "Name of the recipe": [],
    "Total time": [],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def IndonesiaSpider(recipes_url):
    """
    input: recipes_url, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.899274966.1636302399; MarketGidStorage={"0":{"svspr":"https://resepkoki.id/category/ayam-daging/","svsds":1,"TejndEEDj":"UBUiqI9Jd"},"C918445":{"page":2,"time":1636302446738}}; _gid=GA1.2.381378313.1636488043; __gads=ID=d44d6af592795f11:T=1636302399:S=ALNI_MZEbH73O51a_1FNwtgcjyBtaJo4TA',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(recipes_url,headers=headers)
    response.encoding="utf-8"
    sel = Selector(response.text)
    
    # scrape dictionary containing all information that we need
    content = json.loads(sel.xpath('//script[@type = "application/ld+json"]')[1].xpath('text()').get(''))
    
    content['time'] = sel.xpath('//li[@class="single-meta-cooking-time"]/span/text()').get()
    
    return content

def fillIndonesiaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = IndonesiaSpider(html)
    dic['Name of the recipe'].append(content['name'])        
    dic['Total time'].append(content['time'])
    dic['List of ingredients'].append(content['recipeIngredient'])
    dic['List of instructions'].append(content['recipeInstructions'])
    dic['Number of servings'].append(content['recipeYield'])
    try:
        dic['Category'].append(content['recipeCategory'])
    except:
         dic['Category'].append('None')


# In[140]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillIndonesiaData(html,Indonesiadata)
    except:
        time.sleep(5)


# In[142]:


# convert data to dataframe
Indonesia = pd.DataFrame(Indonesiadata)
print(Indonesia.shape)
Indonesia.head()

# save dataset
Indonesia.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Indonesia.csv")


# In[ ]:




