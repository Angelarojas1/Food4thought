#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Fiji

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


# #### https://thatfijitaste.com/

# In[10]:


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
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(category_url,headers=headers)
    sel = Selector(response.text)
    for i in sel.xpath('//div[@class="post-thumb"]/a/@href'):
        lst.append(i.get())
    
    return lst


# In[11]:


htmlOnePageSpider("https://thatfijitaste.com/", htmlLst)


# In[12]:


for i in range(2,6):
    htmlOnePageSpider("https://thatfijitaste.com/page/{}/".format(i), htmlLst)


# In[13]:


# the number of recipes we have in total
len(htmlLst)


# In[32]:


FijiSpider('https://thatfijitaste.com/fiji-puri/')


# In[36]:


# 3. go through all recipe htmls and scrape the data we want

Fijidata = {
    "Name of the recipe":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
}

def FijiSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(recipe_url,headers=headers)
    sel = Selector(response.text)
    
    # scrape dictionary containing all information that we need
    content = {}
    
    content['name'] = sel.xpath('//h1[@class="entry-title fn"]/text()').get()
    content['recipeYield'] = sel.xpath('//div[@class="detail-item detail-item-0"]/p/text()').get()
    content['prepTime'] = sel.xpath('//div[@class="detail-item detail-item-1"]/p/text()').get()
    content['cookTime'] = sel.xpath('//div[@class="detail-item detail-item-2"]/p/text()').get()
    
    lst = []
    for i in sel.xpath('//li[@class="ingredient"]/text() | //li[@class="ingredient-item"]/p/text()'):
        lst.append(i.get())
    content['recipeIngredient'] = lst
        
    lst = []
    for i in sel.xpath('//li[@class="instruction"]/text() | //li[@class="direction-step"]/text()'):
        lst.append(i.get())
    content['recipeInstructions'] = lst
      
    return content

def fillFijiData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = FijiSpider(html)
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
        

# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillFijiData(html,Fijidata)
    except:
        time.sleep(5)

# convert data to dataframe
Fiji = pd.DataFrame(Fijidata)
print(Fiji.shape)
Fiji.head()


# In[37]:


Fiji["Source"] = ["Web1" for i in range(len(Fiji))]
Fiji.head()


# In[38]:


# save dataset
Fiji.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Fiji.csv")


# In[ ]:




