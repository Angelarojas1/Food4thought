#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Jamaica

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


# #### https://www.jcskitchen.com/Jamaican-Food-Recipes

# In[22]:


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
        'cookie':'ASP.NET_SessionId=3hoonvopqydhrvwxw0qeanih; __utmc=249431452; __utmz=249431452.1652121739.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not provided); _fbp=fb.1.1652121738866.820468787; listType=2; __utma=249431452.1352843145.1652121739.1652194187.1652636159.3; __insp_wid=1548000467; __insp_slim=1652636159201; __insp_nv=true; __insp_targlpu=aHR0cHM6Ly93d3cuamNza2l0Y2hlbi5jb20vSmFtYWljYW4tRm9vZC1SZWNpcGVz; __insp_targlpt=SmFtYWljYW4gRm9vZCBSZWNpcGVzIC0gQ2FyaWJiZWFuIEZvb2QgUmVjaXBlcyAtIElzbGFuZCBGb29kIFJlY2lwZXM=; __insp_norec_sess=true',
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
    for i in sel.xpath('//ul[@class="recipesList"]/li/div[@class="description"]/a/@href'):
        lst.append('https://www.jcskitchen.com/'+i.get())
    
    return lst


# In[23]:


htmlOnePageSpider("https://www.jcskitchen.com/Jamaican-Food-Recipes", htmlLst)


# In[24]:


# the number of recipes we have in total
len(htmlLst)


# In[31]:


# 3. go through all recipe htmls and scrape the data we want

Jamaicadata = {
    "Name of the recipe":[],
    "Total time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
}

def JamaicaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'ASP.NET_SessionId=3hoonvopqydhrvwxw0qeanih; __utmc=249431452; __utmz=249431452.1652121739.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not provided); _fbp=fb.1.1652121738866.820468787; listType=2; __utma=249431452.1352843145.1652121739.1652194187.1652636159.3; __insp_wid=1548000467; __insp_slim=1652636159201; __insp_nv=true; __insp_targlpu=aHR0cHM6Ly93d3cuamNza2l0Y2hlbi5jb20vSmFtYWljYW4tRm9vZC1SZWNpcGVz; __insp_targlpt=SmFtYWljYW4gRm9vZCBSZWNpcGVzIC0gQ2FyaWJiZWFuIEZvb2QgUmVjaXBlcyAtIElzbGFuZCBGb29kIFJlY2lwZXM=; __insp_norec_sess=true',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()').get())
    
    return content

def fillJamaicaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = JamaicaSpider(html)
    dic['Name of the recipe'].append(content['name'])
    try:
        dic['Total time'].append(content['totalTime'])
    except:
        dic['Total time'].append('')
                
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
        

# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillJamaicaData(html,Jamaicadata)
    except:
        time.sleep(5)

# convert data to dataframe
Jamaica = pd.DataFrame(Jamaicadata)
print(Jamaica.shape)
Jamaica.head()


# In[32]:


Jamaica["Source"] = ["Web1" for i in range(len(Jamaica))]
Jamaica.head()


# In[33]:


# save dataset
Jamaica.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Jamaica.csv")


# In[ ]:





# In[ ]:




