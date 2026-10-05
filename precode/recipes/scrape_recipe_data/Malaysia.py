#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Malaysia

# resepichenom.com

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
        'cookie':'_ga=GA1.2.1161230936.1639560312; _gid=GA1.2.136356029.1639560312; __gads=ID=c542524994625035-22abc43df6cc0061:T=1639560368:RT=1639560368:S=ALNI_Mbs8bdQMFnt1I6k087oD0H0TGxJ7A; __atuvc=1|50; __atuvs=61b9b4be33251426000; _gat_gtag_UA_39217844_12=1',
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
    for i in sel.xpath('//h2[@class="entry-title"]/a/@href'):
           lst.append('https://resepichenom.com/'+ i.get())
        
    
    return lst


# In[12]:


headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.1161230936.1639560312; _gid=GA1.2.136356029.1639560312; __gads=ID=c542524994625035-22abc43df6cc0061:T=1639560368:RT=1639560368:S=ALNI_Mbs8bdQMFnt1I6k087oD0H0TGxJ7A; __atuvc=1|50; __atuvs=61b9b4be33251426000; _gat_gtag_UA_39217844_12=1',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
response = requests.get('https://resepichenom.com/kategori/ayam/show',headers=headers)
sel = Selector(response.text)


# In[18]:


# 2. go through all categories and pages in the web and get all recipe htmls

def htmlAllPageSpider(category_url,page_number,htmlLst):
    """
    input: category_url, the url of first page of the recipe web
    input: page number, the total number of pages of one category
    output: htmlLst with all recipes htmls on all pages of one category
    
    """
    # initialize pageLst to store the htmls of all pages
    pageLst = []

    pageLst.append(category_url)
    
    for i in range(2,page_number+1):
        pageLst.append(category_url+"?page="+str(i))
        
    for i in pageLst:
        fillLst = htmlOnePageSpider(i, htmlLst)
    
    return fillLst


# In[19]:


# 2. go through all categories and pages in the web and get all recipe htmls
htmlOnePageSpider('https://resepichenom.com/kategori/ayam/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/ikan/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/kuih-muih/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/nasi/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/sayur/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/daging/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/sup/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/Seafood/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/kek/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/roti/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/telur/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/pasta/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/sarapan/show',htmlLst)
htmlOnePageSpider('https://resepichenom.com/kategori/mee/show',htmlLst)


# In[23]:


Malaysiaspider('https://resepichenom.com//resepi/paprik-ayam-restoran-tomyam-thai/show')


# In[20]:


# 3. go through all recipe htmls and scrape the data we want

Malaysiadata = {
    "Name of the recipe": [],
    "Total time":[],
    "Cook time": [],
    "Prep time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}


def Malaysiaspider(recipes_url):
    """
    input: recipes_url, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.1161230936.1639560312; _gid=GA1.2.136356029.1639560312; __gads=ID=c542524994625035-22abc43df6cc0061:T=1639560368:RT=1639560368:S=ALNI_Mbs8bdQMFnt1I6k087oD0H0TGxJ7A; __atuvc=1|50; __atuvs=61b9b4be33251426000; _gat_gtag_UA_39217844_12=1',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()').get(''), strict=False)
    
    return content

def fillMalaysiaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = Malaysiaspider(html)
    dic['Name of the recipe'].append(content['name'])
    dic['Total time'].append(content['totalTime'])
    dic['Prep time'].append(content['prepTime'])
    dic['Cook time'].append(content['cookTime'])
    dic['List of ingredients'].append(content['recipeIngredient'])
    dic['List of instructions'].append(content['recipeInstructions'])
    dic['Number of servings'].append(content['recipeYield'])
    dic['Category'].append(content['recipeCategory'])    


# In[108]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillMalaysiaData(html,Malaysiadata)
    except:
        time.sleep(5)


# In[109]:


# convert data to dataframe
data = pd.DataFrame(Malaysiadata)
print(data.shape)
data.head()

# save dataset
data.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Malaysia.csv")


# In[ ]:




