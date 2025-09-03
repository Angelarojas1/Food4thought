#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Mauritius

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


# #### https://mauritianfoodrecipes.com/all-recipes/

# In[8]:


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
        'cookie':'__gads=ID=bea12aa85414438e-220a02a632d200f2:T=1650384423:RT=1650384423:S=ALNI_MYyatFUAwSrXJkDXopiHyaV9Eh86A; _gid=GA1.2.924293879.1652099852; _ga_DQTMR4BBNX=GS1.1.1652099845.1.1.1652099859.0; _ga=GA1.2.1472695399.1650384424',
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
    for i in sel.xpath('//figure[@class="elementor-image-box-img"]/a/@href'):
        lst.append(i.get())
    
    return lst


# In[9]:


htmlOnePageSpider("https://mauritianfoodrecipes.com/all-recipes/", htmlLst)


# In[10]:


# the number of recipes we have in total
len(htmlLst)


# In[62]:


# 3. go through all recipe htmls and scrape the data we want

Mauritiusdata = {
    "Name of the recipe":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def MauritiusSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'__gads=ID=bea12aa85414438e-220a02a632d200f2:T=1650384423:RT=1650384423:S=ALNI_MYyatFUAwSrXJkDXopiHyaV9Eh86A; _gid=GA1.2.924293879.1652099852; _ga_DQTMR4BBNX=GS1.1.1652099845.1.1.1652099859.0; _ga=GA1.2.1472695399.1650384424',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()').get())['@graph'][-1]
    
    # if all information isn't in the content
    if 'name' not in content:
        content ={
            'name':'',
            'prepTime':'',
            'cookTime':'',
            'recipeIngredient':'',
            'recipeInstructions':'',
            'recipeYield':''
        }
        
        content['name'] = sel.xpath('//h1[@class="page-header-title clr"]/text()').get()
        content['prepTime'] = sel.xpath('//li[@class="elementor-icon-list-item elementor-inline-item"]/span[@class="elementor-icon-list-text"]/text()')[1].get()
        content['cookTime'] = sel.xpath('//li[@class="elementor-icon-list-item elementor-inline-item"]/span[@class="elementor-icon-list-text"]/text()')[2].get()
        content['recipeYield'] = sel.xpath('//li[@class="elementor-icon-list-item elementor-inline-item"]/span[@class="elementor-icon-list-text"]/text()')[3].get()
        
        lst = []
        for i in sel.xpath('//li[@class="elementor-icon-list-item"]/span[@class="elementor-icon-list-text"]/text()'):
            lst.append(i.get())
            
        content['recipeIngredient'] = lst
        
        lst = []
        for i in sel.xpath('//div[@class="elementor-text-editor elementor-clearfix"]/ol/li/text()'):
            lst.append(i.get())
            
        content['recipeInstructions'] = lst
        
    return content

def fillMauritiusData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = MauritiusSpider(html)
    dic['Name of the recipe'].append(content['name'])
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
        fillMauritiusData(html,Mauritiusdata)
    except:
        time.sleep(5)

# convert data to dataframe
Mauritius = pd.DataFrame(Mauritiusdata)
print(Mauritius.shape)
Mauritius.head()


# In[63]:


Mauritius["Source"] = ["Web1" for i in range(len(Mauritius))]
Mauritius.head()


# In[65]:


# save dataset
Mauritius.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Mauritius.csv")


# In[ ]:




