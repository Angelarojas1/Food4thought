#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Germany

# https://www.chefkoch.de/rs/s0t29,65/Europa-Deutschland-Rezepte.html

# In[2]:


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


# In[16]:


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
        'cookie':'amp-access=amp-hWyby6JzYXiAZeCkArDUbQ; _ga=amp-UAgQz8Zs__Pqu42odTzpIw; _sp_v1_uid=1:685:64ba9742-f9cb-415f-a67d-23581a937836; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbKKRmbkgRgGtbE6MUqpIGZeaU4OkF0CVlBdi1tCKRYAmuD4I1IAAAA=; _sp_v1_csv=null; _sp_v1_lt=1:; _sp_v1_data=2:437077:1642562383:0:1:-1:1:0:0:_:-1; _sp_v1_opt=1:login|true:last_id|11:; _sp_v1_consent=1!0:-1:-1:-1:-1:-1',
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
    for i in json.loads(sel.xpath('//script[@type="application/ld+json"]/text()').get(''))['itemListElement']:
        lst.append(i['url'])
        
    return lst


# In[14]:


htmlOnePageSpider('https://www.chefkoch.de/rs/s0t29,65/Europa-Deutschland-Rezepte.html', htmlLst)


# In[15]:


# 2. go through all categories and pages in the web and get all recipe htmls

def htmlAllPageSpider(htmlLst):
    """
    output: htmlLst with all recipes htmls on all pages of one category
    
    """
    # initialize pageLst to store the htmls of all pages
    pageLst = []
    
    for i in range(25):
        pageLst.append('https://www.chefkoch.de/rs/s{}t29,65/Europa-Deutschland-Rezepte.html'.format(i))
        
    for i in pageLst:
        fillLst = htmlOnePageSpider(i, htmlLst)
    
    return list(set(fillLst))


# In[17]:


htmlAllPageSpider(htmlLst)


# In[18]:


# the number of recipes we have in total
len(htmlLst)


# In[25]:


# 3. go through all recipe htmls and scrape the data we want

Germanydata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def GermanySpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'amp-access=amp-hWyby6JzYXiAZeCkArDUbQ; _ga=amp-UAgQz8Zs__Pqu42odTzpIw; _sp_v1_uid=1:685:64ba9742-f9cb-415f-a67d-23581a937836; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbKKRmbkgRgGtbE6MUqpIGZeaU4OkF0CVlBdi1tCKRYAmuD4I1IAAAA=; _sp_v1_csv=null; _sp_v1_lt=1:; _sp_v1_data=2:437077:1642562383:0:1:-1:1:0:0:_:-1; _sp_v1_opt=1:login|true:last_id|11:; _sp_v1_consent=1!0:-1:-1:-1:-1:-1',
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

def fillGermanyData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = GermanySpider(html)
    dic['Name of the recipe'].append(content['name'])
    dic['Total time'].append(content['totalTime'])
    dic['Prep time'].append(content['prepTime'])
    dic['List of ingredients'].append(content['recipeIngredient'])
    dic['List of instructions'].append(content['recipeInstructions'])
    dic['Number of servings'].append(content['recipeYield'])
    dic['Category'].append(content['recipeCategory'])    


# In[26]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillGermanyData(html,Germanydata)
    except:
        time.sleep(5)


# In[27]:


# convert data to dataframe
Germany = pd.DataFrame(Germanydata)
print(Germany.shape)
Germany.head()

# save dataset
Germany.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Germany.csv")


# In[ ]:




