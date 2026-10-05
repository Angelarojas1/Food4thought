#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Latvia

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


# #### https://receptes.eu/cuisine/latviesu

# In[11]:


# 1. create a list to store all recipe htmls on one page
# initialize htmlDic to store the htmls of all recipes
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
        'cookie':'__gads=ID=e0dd70b2df9d8b85-22dea25532d200f2:T=1650379437:RT=1650379437:S=ALNI_MZt_Gjqfmar1K-qAQTYzEzBO0cwEA; cookielawinfo-checkbox-necessary=yes; _ga=GA1.2.763220901.1650379437; CookieLawInfoConsent=eyJuZWNlc3NhcnkiOnRydWV9; viewed_cookie_policy=yes; _gid=GA1.2.1908735199.1652110528; FCNEC=[["AKsRol8YW-s7SNSPxuDn-ylgoPmE7kvBIHAdhCFUBz-9dZsW2gcbJurHZHhLsEX-OLPxh-7UBuJXBRyXrooXkfoJ5nIqhaab61uuA8DKjZ034dHt_Ren8lMkLMmkX6Rkt8A8-4B6eVT_406kT1tqVJzL_xhZo2mDPA=="],null,[]]',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
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
    for i in sel.xpath('//div[@class="archive-item-share-icons"]/a[@class="archive-item-share-link aisl-twitter"]/@href'):
        lst.append(re.search('url=(.+?)&text=', i.get()).group(1))
    
    return lst


# In[12]:


htmlOnePageSpider("https://receptes.eu/cuisine/latviesu", htmlLst)


# In[13]:


for i in range(2,6):
    htmlOnePageSpider("https://receptes.eu/cuisine/latviesu/page/{}".format(i), htmlLst)


# In[14]:


# the number of recipes we have in total
len(htmlLst)


# In[25]:


# 3. go through all recipe htmls and scrape the data we want

Latviadata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def LatviaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'__gads=ID=e0dd70b2df9d8b85-22dea25532d200f2:T=1650379437:RT=1650379437:S=ALNI_MZt_Gjqfmar1K-qAQTYzEzBO0cwEA; cookielawinfo-checkbox-necessary=yes; _ga=GA1.2.763220901.1650379437; CookieLawInfoConsent=eyJuZWNlc3NhcnkiOnRydWV9; viewed_cookie_policy=yes; _gid=GA1.2.1908735199.1652110528; FCNEC=[["AKsRol8YW-s7SNSPxuDn-ylgoPmE7kvBIHAdhCFUBz-9dZsW2gcbJurHZHhLsEX-OLPxh-7UBuJXBRyXrooXkfoJ5nIqhaab61uuA8DKjZ034dHt_Ren8lMkLMmkX6Rkt8A8-4B6eVT_406kT1tqVJzL_xhZo2mDPA=="],null,[]]',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }

    response = requests.get(recipe_url,headers=headers)
    sel = Selector(response.text)
    
    # scrape dictionary containing all information that we need
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()')[1].get())
    
    return content

def fillLatviaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = LatviaSpider(html)
    dic['Name of the recipe'].append(content['name'])
    try:
        dic['Total time'].append(content['totalTime'])
    except:
        dic['Total time'].append('')
        
    try:
        dic['Prep time'].append(content['prepTime'])
    except:
        dic['Prep time'].append('')
                
    try:
        dic['Cook time'].append(content['cookTime'])
    except:
        dic['Cook time'].append('')
    
    try:
        dic['List of ingredients'].append(content['recipeIngredient'])
    except:
        dic['List of ingredients'].append('')
        
    try:
        dic['List of instructions'].append(content['recipeInstructions'])
    except:
        dic['List of instructions'].append('')
        
    try:
        dic['Number of servings'].append(content['recipeYield'])
    except:
        dic['Number of servings'].append('')
        
    try:
        dic['Category'].append(content['recipeCategory'])
    except:
        dic['Category'].append('')

# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillLatviaData(html,Latviadata)
    except:
        time.sleep(5)

# convert data to dataframe
Latvia = pd.DataFrame(Latviadata)
print(Latvia.shape)
Latvia.head()


# In[26]:


Latvia["Source"] = ["Web1" for i in range(len(Latvia))]
Latvia.head()


# In[27]:


# save dataset
Latvia.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Latvia.csv")


# In[ ]:




