#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Haiti

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


# #### https://haitian-recipes.com/recipes/

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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.601717413.1650164172; tk_or="https://www.google.com/"; __gads=ID=f5aac5ed8b52dff7-22deac9531d20091:T=1650164172:RT=1650164172:S=ALNI_MamDQi-zy3s7Dxk5jsd2j3unq1s7w; __atssc=google;3; _gid=GA1.2.1505548612.1652704852; tk_r3d=""; tk_lr=""; __atuvc=0|16,0|17,0|18,3|19,4|20; __atuvs=62824654d53cf04c003',
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
    for i in sel.xpath('//div[@class="box-image"]/a/@href'):
        lst.append("https://haitian-recipes.com/"+i.get())
    
    return lst


# In[11]:


htmlOnePageSpider("https://haitian-recipes.com/appetizers/", htmlLst)
htmlOnePageSpider("https://haitian-recipes.com/desserts/", htmlLst)
htmlOnePageSpider("https://haitian-recipes.com/main-dishes/", htmlLst)
htmlOnePageSpider("https://haitian-recipes.com/quick-and-easy/", htmlLst)
htmlOnePageSpider("https://haitian-recipes.com/recipes/side-dishes", htmlLst)
htmlOnePageSpider("https://haitian-recipes.com/soups-salads/", htmlLst)


# In[12]:


# the number of recipes we have in total
len(htmlLst)


# In[35]:


# 3. go through all recipe htmls and scrape the data we want

Haitidata = {
    "Name of the recipe":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
}

def HaitiSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.601717413.1650164172; tk_or="https://www.google.com/"; __gads=ID=f5aac5ed8b52dff7-22deac9531d20091:T=1650164172:RT=1650164172:S=ALNI_MamDQi-zy3s7Dxk5jsd2j3unq1s7w; __atssc=google;3; _gid=GA1.2.1505548612.1652704852; tk_r3d=""; tk_lr=""; __atuvc=0|16,0|17,0|18,3|19,4|20; __atuvs=62824654d53cf04c003',
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
    content = {}
    
    content['name'] = sel.xpath('//h2[@class="uppercase"]/strong/text() | //h1[@class="uppercase"]/strong/span/text()').get()
    content['prepTime'] = sel.xpath('//div[@class="icon-box-text last-reset"]/h6/text()')[0].get()
    content['cookTime'] = sel.xpath('//div[@class="icon-box-text last-reset"]/h6/text()')[1].get()
    content['recipeYield'] = sel.xpath('//div[@class="icon-box-text last-reset"]/h6/text()')[2].get()
    
    lst = []
    for i in sel.xpath('//div[@class="col-inner"]/ul/li/text()'):
        lst.append(i.get())
    content['recipeIngredient'] = lst
    
    lst = []
    for i in sel.xpath('//div[@class="elm text-edit gf-elm-left gf-elm-center-sm"]/p/text() | //div[@class="elm text-edit gf-elm-left"]/p/text()'):
        lst.append(i.get())
    content['recipeInstructions'] = lst
    
    return content

def fillHaitiData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = HaitiSpider(html)
    dic['Name of the recipe'].append(content['name'])
    try:
        dic['Prep time'].append(content['preplTime'])
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
        fillHaitiData(html,Haitidata)
    except:
        time.sleep(5)

# convert data to dataframe
Haiti = pd.DataFrame(Haitidata)
print(Haiti.shape)
Haiti.head()


# In[36]:


Haiti["Source"] = ["Web1" for i in range(len(Haiti))]
Haiti.head()


# In[37]:


# save dataset
Haiti.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Haiti.csv")


# In[ ]:




