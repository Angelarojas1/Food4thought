#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Madagascar

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


# #### http://www.recettes-ensoleillees.com/category/recettes-malgaches/

# In[2]:


headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'PHPSESSID=bc5b27470f2138a38e02a009c5e54abc; __gads=ID=706b8a7fb416a6e6-2262e97733d2005a:T=1650382731:RT=1650382731:S=ALNI_MZI80lXfeHx8palcrwMKPBMZLukzg',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
response = requests.get('http://www.recettes-ensoleillees.com/category/recettes-malgaches/',headers=headers)
sel = Selector(response.text)


# In[4]:


sel.xpath('//main[@id="main"]/article/a/@href')[1].get()


# In[5]:


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
        'cookie':'PHPSESSID=bc5b27470f2138a38e02a009c5e54abc; __gads=ID=706b8a7fb416a6e6-2262e97733d2005a:T=1650382731:RT=1650382731:S=ALNI_MZI80lXfeHx8palcrwMKPBMZLukzg',
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
    for i in sel.xpath('//main[@id="main"]/article/a/@href'):
        lst.append(i.get())
    
    return lst


# In[6]:


htmlOnePageSpider("http://www.recettes-ensoleillees.com/category/recettes-malgaches/", htmlLst)


# In[7]:


for i in range(2,14):
    htmlOnePageSpider("http://www.recettes-ensoleillees.com/category/recettes-malgaches/page/{}/".format(i), htmlLst)


# In[8]:


# the number of recipes we have in total
len(htmlLst)


# In[15]:


# 3. go through all recipe htmls and scrape the data we want

Madagascardata = {
    "Name of the recipe":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def MadagascarSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'PHPSESSID=bc5b27470f2138a38e02a009c5e54abc; __gads=ID=706b8a7fb416a6e6-2262e97733d2005a:T=1650382731:RT=1650382731:S=ALNI_MZI80lXfeHx8palcrwMKPBMZLukzg',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()')[0].get())
    
    return content

def fillMadagascarData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = MadagascarSpider(html)
    dic['Name of the recipe'].append(content['name'])
    try:
        dic['Prep time'].append(content['totalTime'])
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
        fillMadagascarData(html,Madagascardata)
    except:
        time.sleep(5)

# convert data to dataframe
Madagascar = pd.DataFrame(Madagascardata)
print(Madagascar.shape)
Madagascar.head()


# In[16]:


Madagascar["Source"] = ["Web1" for i in range(len(Madagascar))]
Madagascar.head()


# In[22]:


Madagascar


# In[17]:


# save dataset
Madagascar.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Madagascar.csv")


# In[ ]:




