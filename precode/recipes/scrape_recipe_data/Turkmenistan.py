#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Turkmenistan

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


# #### https://tagamlar.com/

# In[13]:


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
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "macOS",
        'Upgrade-Insecure-Requests': "1",
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }
    response = requests.get(category_url,headers=headers)
    sel = Selector(response.text)
    for i in sel.xpath("//div[@class='row']/div[@class='col-xs-6']/div/a/@href"):
        lst.append(i.get())
    
    return lst


# In[14]:


htmlOnePageSpider("https://tagamlar.com/resept/", htmlLst)


# In[15]:


htmlOnePageSpider("https://tagamlar.com/resept/?pg=2", htmlLst)


# In[16]:


# the number of recipes we have in total
len(htmlLst)


# In[21]:


# 3. go through all recipe htmls and scrape the data we want

Turkmenistandata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def TurkmenistanSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "macOS",
        'Upgrade-Insecure-Requests': "1",
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }
    response = requests.get(recipe_url,headers=headers)
    sel = Selector(response.text)
    
    # scrape dictionary containing all information that we need
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()')[2].get())
    
    return content

def fillTurkmenistanData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = TurkmenistanSpider(html)
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
        fillTurkmenistanData(html,Turkmenistandata)
    except:
        time.sleep(5)

# convert data to dataframe
Turkmenistan = pd.DataFrame(Turkmenistandata)
print(Turkmenistan.shape)
Turkmenistan.head()


# In[22]:


Turkmenistan["Source"] = ["Web1" for i in range(len(Turkmenistan))]
Turkmenistan.head()


# In[23]:


# save dataset
Turkmenistan.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Turkmenistan.csv")


# In[ ]:




