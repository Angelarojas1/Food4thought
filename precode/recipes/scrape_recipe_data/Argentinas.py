#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Argentinas

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


# In[2]:


# 1. create a dictionary to store all recipe htmls on one page
# initialize htmlDic to store the htmls of all recipes
htmlDic = {}

def htmlOnePageSpider(category_url, dic):
    """
    input: category_url, the url of first page of the recipe web
    input: the initial htmlDic
    output: htmlDic with all recipe htmls on one page of one category
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'recipes_arg=d2cc77b1db095418b587052dc1ef36af; _ga=amp-_oK3xz_NQb1Zy-zNUVs9jQ',
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
    for i in sel.xpath('//div[@class="listAll"]/div[@class="itemPublic"]'):
        htmlLink = i.xpath('./a/@href').get('')
        recipeName = i.xpath('./a/h2/text()').get('')
        dic[recipeName] = htmlLink
    
    return dic


# In[3]:


# 2. go through all pages in the web and get all recipe htmls

def htmlAllPageSpider(category_url,page_number):
    """
    input: category_url, the url of first page of the recipe web
    input: page_number, the total number of pages of one category
    output: htmlDic with all recipe htmls on all pages of one category
    
    """
    # initialize pageLst to store the htmls of all pages
    pageLst = []

    pageLst.append(category_url)

    for i in range(2,page_number+1):
        pageLst.append(category_url+"?pagina="+str(i))
    
    # go over each page and get recipe urls    
    htmlDic = {}
    for i in pageLst:
        htmlDic = htmlOnePageSpider(i,htmlDic) 
        
    print("The number of recipes is {}".format(len(htmlDic)))
    return htmlDic


# In[40]:


# 3. go through all recipe htmls and scrape the data we want

Argentinasdata = {
    "Name of the recipe": [],
    "Total time": [],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def Argentinasspider(recipes_url):
    """
    input: recipes_url, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'recipes_arg=d2cc77b1db095418b587052dc1ef36af; _ga=amp-_oK3xz_NQb1Zy-zNUVs9jQ',
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
    
    # get the ingredient list
    ingredientLst = []
    for i in sel.xpath('//div[@class="ingredientList"]/div[@class="ingredient"]/span'):
        ingredientLst.append(i.xpath('text()').get())
    
    dic['List of ingredients'] = ingredientLst
    
    # get total time
    try:
        dic['Total time'] = sel.xpath('//div[@class="itemCompleteTopRight"]/p[strong="Preparación:"]/span/text()').get('')
    except:
        dic['Total time'] = ''
    
    # get the number of servings
    try:
        dic['Number of servings'] = sel.xpath('//div[@class="itemCompleteTopRight"]/p[strong="Porciones:"]/span/text()').get('')
    except:
        dic['Number of servings'] = ''
    
    # get the instruction list
    instructionLst = []
    for i in sel.xpath('//div[@class="itemCompleteBottomItem itemCompleteBottomPreparation"]/div[@class="pageComplete"]/ol/li'):
        instructionLst.append(i.xpath('text()').get())
        
    dic['List of instructions'] = instructionLst
    
    # get the category
    dic['Category'] = json.loads(sel.xpath('//script[@type = "application/ld+json"]/text()').get(''))['recipeCategory']
    
    return dic


def fillArgentinasData(key,dic):
    """
    input: key, the key in html dic
    output: fill in data
    
    """
    content = Argentinasspider(htmlDic[key])
    dic["Name of the recipe"].append(key)
    dic["Total time"].append(content['Total time'])
    dic["List of ingredients"].append(content['List of ingredients'])
    dic["List of instructions"].append(content['List of instructions'])
    dic["Number of servings"].append(content['Number of servings'])
    dic["Category"].append(content['Category'])


# In[41]:


# go through all recipe urls in one category 
import time

htmlDic = htmlAllPageSpider("https://www.recetas-argentinas.com/recetas",30)
for key in htmlDic:
    try:
        fillArgentinasData(key,Argentinasdata)
    except:
        time.sleep(5)


# In[43]:


# convert data to dataframe
Argentinas = pd.DataFrame(Argentinasdata)
print(Argentinas.shape)
Argentinas.head()

# save dataset
Argentinas.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Argentinas.csv")

