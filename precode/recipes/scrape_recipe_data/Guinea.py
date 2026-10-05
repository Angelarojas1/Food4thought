#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Guinea

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


# #### https://www.guinee-gourmande.com/

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
        'cookie':'_ga=GA1.2.1538242641.1650163037; _icl_current_language=fr; _icl_visitor_lang_js=en-us; _gid=GA1.2.1790868693.1652706069',
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
    for i in sel.xpath('//a[@class="recipes-list-thumb"]/@href'):
        lst.append("https://www.guinee-gourmande.com/"+i.get())
    
    return lst


# In[11]:


htmlOnePageSpider("https://www.guinee-gourmande.com/types/cuisine-traditionnelle/", htmlLst)
htmlOnePageSpider("https://www.guinee-gourmande.com/types/cuisine-metissee/", htmlLst)


# In[12]:


# the number of recipes we have in total
len(htmlLst)


# In[40]:


# 3. go through all recipe htmls and scrape the data we want

Guineadata = {
    "Name of the recipe":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[]
}

def GuineaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.1538242641.1650163037; _icl_current_language=fr; _icl_visitor_lang_js=en-us; _gid=GA1.2.1790868693.1652706069',
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
    
    content['name'] = sel.xpath('//div[@class="page-header"]/h2/text()').get()
    content['prepTime'] = sel.xpath('//tbody/tr/td/text()')[1].get()
    content['cookTime'] = sel.xpath('//tbody/tr/td/text()')[3].get()
    content['recipeYield'] = sel.xpath('//h3[@class="recipe-ingredients-title"]/small/text()').get()
    
    lst = []
    for i in sel.xpath('//section[@class="recipe-ingredients"]/ul/li/p/text()'):
        lst.append(i.get())
    content['recipeIngredient'] = lst
    
    lst = []
    for i in sel.xpath('//li[@class="recipe-step"]/p/text() | //li[@class="recipe-step"]/ul/li/text()'):
        lst.append(i.get())
    content['recipeInstructions'] = lst    
    
    return content

def fillGuineaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = GuineaSpider(html)
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
        fillGuineaData(html,Guineadata)
    except:
        time.sleep(5)

# convert data to dataframe
Guinea = pd.DataFrame(Guineadata)
print(Guinea.shape)
Guinea.head()


# In[41]:


Guinea["Source"] = ["Web1" for i in range(len(Guinea))]
Guinea.head()


# In[42]:


# save dataset
Guinea.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Guinea.csv")


# In[ ]:




