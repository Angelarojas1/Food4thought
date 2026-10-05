#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Azerbaijan

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


# In[9]:


# 1. create a dictionary to store all recipe htmls on one page
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
        'cookie':'_ga=GA1.2.882548573.1657714799; _gid=GA1.2.1713198775.1657714799; cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; __gads=ID=f3b0e806f42054de-22f87e3dc7d300e3:T=1657714799:RT=1657714799:S=ALNI_MbqaiCtumqrR7niJvBM0i_LnzAfmg; __gpi=UID=00000644a8d43e51:T=1657714799:RT=1657714799:S=ALNI_MZlXj5Ud6RkGRM51PXSubAGK2FNQQ; SHR_E=4cd7b4282df34846ab4ac024fabc2a928acf9b32ddcf6e0d5d143443e0794263e6d6866853b29b281ba88e2aef15b06012496e7122f5182113d80a2e7ee4712aa779b6d7d47f00500238b982aebece42c06abcdb572f550e011b76af1dff2bd8ea9cabb6d002d099f96da1c25cca770fe438503b7dab08b35a50f4b75cabdfd9d8d7a889af4bc989d222497a1d0139bfe56951dc2c0686d02eef87d57197852de8131876fab9e658f8de09fcca83ec6393f69b8e1e49c82f21f9a1c415898a6b50bd976905e6ee0bcc121dd09dbc469e2dc9fdf85531af35e93522508f66b32d77cdef5cd9104669ca29a15ccd8b35a6e067b0db69d43d1c9f1e36b2c12fcf08',
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
    for i in sel.xpath('//li[@class="ei-item"]/div/a/@href'):
        lst.append(i.get())
    
    return lst


# In[10]:


# 2. go through all pages in the web and get all recipe htmls
htmlOnePageSpider('https://azcookbook.com/index/recipes/main-dishes/',htmlLst)
htmlOnePageSpider('https://azcookbook.com/index/recipes/meat/',htmlLst)
htmlOnePageSpider('https://azcookbook.com/index/recipes/pasta-and-dumplings/',htmlLst)
htmlOnePageSpider('https://azcookbook.com/index/recipes/poultry/',htmlLst)
htmlOnePageSpider('https://azcookbook.com/index/recipes/rice-grains-and-legumes/',htmlLst)
htmlOnePageSpider('https://azcookbook.com/index/recipes/side-dishes/',htmlLst)
htmlOnePageSpider('https://azcookbook.com/index/recipes/soups-and-stews/',htmlLst)


# In[48]:


Azerbaijanspider( 'https://azcookbook.com/2014/02/17/baked-lemon-garlic-steelhead-trout/')


# In[11]:


len(htmlLst)


# In[41]:


# 3. go through all recipe htmls and scrape the data we want

Azerbaijandata = {
    "Name of the recipe": [],
    "Total time": [],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def Azerbaijanspider(recipes_url):
    """
    input: recipes_url, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.882548573.1657714799; _gid=GA1.2.1713198775.1657714799; cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; __gads=ID=f3b0e806f42054de-22f87e3dc7d300e3:T=1657714799:RT=1657714799:S=ALNI_MbqaiCtumqrR7niJvBM0i_LnzAfmg; __gpi=UID=00000644a8d43e51:T=1657714799:RT=1657714799:S=ALNI_MZlXj5Ud6RkGRM51PXSubAGK2FNQQ; SHR_E=4cd7b4282df34846ab4ac024fabc2a928acf9b32ddcf6e0d5d143443e0794263e6d6866853b29b281ba88e2aef15b06012496e7122f5182113d80a2e7ee4712aa779b6d7d47f00500238b982aebece42c06abcdb572f550e011b76af1dff2bd8ea9cabb6d002d099f96da1c25cca770fe438503b7dab08b35a50f4b75cabdfd9d8d7a889af4bc989d222497a1d0139bfe56951dc2c0686d02eef87d57197852de8131876fab9e658f8de09fcca83ec6393f69b8e1e49c82f21f9a1c415898a6b50bd976905e6ee0bcc121dd09dbc469e2dc9fdf85531af35e93522508f66b32d77cdef5cd9104669ca29a15ccd8b35a6e067b0db69d43d1c9f1e36b2c12fcf08',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
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
    
    # initialize the output dictionary
    dic = {}
    
    dic['Name of the recipe'] = sel.xpath('//div[@itemprop="name"]/text()').get()
    
    # get the ingredient list
    ingredientLst = []
    for i in sel.xpath('//li[@class="ingredient"]/text()'):
        ingredientLst.append(i.get())
    
    dic['List of ingredients'] = ingredientLst
    
    # get total time
    try:
        dic['Total time'] = sel.xpath('//time[@itemprop="totalTime"]/@datetime').get()
    except:
        dic['Total time'] = ''
        
    try:
        dic['Prep time'] = sel.xpath('//time[@itemprop="prepTime"]/@datetime').get()
    except:
        dic['Prep time'] = ''
        
    try:
        dic['Cook time'] = sel.xpath('//time[@itemprop="cookTime"]/@datetime').get()
    except:
        dic['Cook time'] = ''
    
    # get the number of servings
    try:
        dic['Number of servings'] = sel.xpath('//span[@itemprop="recipeYield"]/text()').get()
    except:
        dic['Number of servings'] = ''
    
    # get the instruction list
    instructionLst = []
    for i in sel.xpath('//li[@class="instruction"]/text()'):
        instructionLst.append(i.get())
        
    dic['List of instructions'] = instructionLst
    
    
    return dic


def fillAzerbaijanData(html,dic):
    """
    input:html
    output: fill in data
    
    """
    content = Azerbaijanspider(html)
    dic["Name of the recipe"].append(content['Name of the recipe'])
    dic["Total time"].append(content['Total time'])
    dic["Prep time"].append(content['Prep time'])
    dic["Cook time"].append(content['Cook time'])
    dic["List of ingredients"].append(content['List of ingredients'])
    dic["List of instructions"].append(content['List of instructions'])
    dic["Number of servings"].append(content['Number of servings'])


# In[43]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillAzerbaijanData(html,Azerbaijandata)
    except:
        time.sleep(5)


# In[45]:


Azerbaijandata


# In[44]:


# convert data to dataframe
Azerbaijan = pd.DataFrame(Azerbaijandata)
print(Azerbaijan.shape)
Azerbaijan.head()

# save dataset
Azerbaijan.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Azerbaijan.csv")

