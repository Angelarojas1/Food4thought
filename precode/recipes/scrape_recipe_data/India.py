#!/usr/bin/env python
# coding: utf-8

# ### Scrape all recipes on India website

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


# #### https://www.archanaskitchen.com/recipes

# In[2]:


# 1. create a list to store all recipe htmls on one page
# initialize htmlLst to store the htmls of all recipes
htmlLst = []

def htmlOnePageSpider(category_url, Lst):
    """
    input: category_url, the url of first page of one category
    input: the initial htmlDic
    output: htmlDic with all recipe htmls on one page of one category
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':"fa064abbb551a92c7bedb55d4a8775bd=3sc6s4cnk7tpgslubf9l9pjj0d; _ga=GA1.2.698262372.1629345126; _gid=GA1.2.581268248.1629345126; _fbp=fb.1.1629345126191.1914696563; __gads=ID=35eb4f2e78fc832f-228abf3ae8c9003b:T=1629345126:RT=1629345126:S=ALNI_MZz78bJbB_O987zxZdVz2wjo5R_dg",
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
    for i in sel.xpath('//div[@class="blogRecipe  col-md-3"]'):
        htmlLink = "https://www.archanaskitchen.com/" + i.xpath('.//div[@class="card h-100 shadow-sm "]/a/@href').get('')
        Lst.append(htmlLink)
    return Lst


# In[3]:


htmlOnePageSpider("https://www.archanaskitchen.com/recipes",htmlLst)


# In[5]:


# 2. go through all pages in and get all recipe htmls
# initialize pageLst to store the htmls of all pages
pageLst = []
pageLst.append("https://www.archanaskitchen.com/recipes")

for i in range(2,337):
    pageLst.append("https://www.archanaskitchen.com/recipes/page-"+str(i))
pageLst


# In[9]:


htmlLst = []
for i in pageLst:
    htmlLst = htmlOnePageSpider(i,htmlLst)  
htmlLst


# In[10]:


len(htmlLst)


# In[11]:


# store the list to a json file
with open("/Users/xixi/Dropbox/food4thought/data/raw/IndiaHtml.txt","w") as fp:
    json.dump(htmlLst,fp)


# In[12]:


# 3. go through all recipe htmls and scrape the data we want
Indiadata = {
    "Name of the recipe": [],
    "Total time": [],
    "Prep time": [],
    "Cook time": [],
    "Number of servings": [],
    "List of ingredients": [],
    "List of instructions": [],
    "recipeCategory":[],
    "Equipments Used" :[],
    "Cuisine":[]
}


# In[63]:


def Indiaspider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':"fa064abbb551a92c7bedb55d4a8775bd=3sc6s4cnk7tpgslubf9l9pjj0d; _ga=GA1.2.698262372.1629345126; _gid=GA1.2.581268248.1629345126; _fbp=fb.1.1629345126191.1914696563; __gads=ID=35eb4f2e78fc832f-228abf3ae8c9003b:T=1629345126:RT=1629345126:S=ALNI_MZz78bJbB_O987zxZdVz2wjo5R_dg",
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
    
    dic={}
    dic['Name of the recipe'] = sel.xpath('//meta[@name="twitter:title"]/@content').get('')
    
    instructionLst = []
    for i in sel.xpath('////div[@class="col-md-8 col-12 recipeinstructions"]/ol/li/p/text()'):
        instructionLst.append(i.get())
        
    dic['List of instructions'] = instructionLst
    
    try:
        dic['recipeCategory'] = sel.xpath('//div[@class="row cuisineandcourse"]/div[@class="col-12 course"]/span/text()').get('')
    except:
        dic['recipeCategory'] = ''
        
    try:
        dic['Equipments Used'] = sel.xpath('//div[@class="row cuisineandcourse"]/div[@class="col-12 products"]/a/text()').get('')
    except:
        dic['Equipments Used'] = ''
        
    try:
        dic['Prep time'] = sel.xpath('//div[@class="row RecipeServesTime"]/div[@class="col-md-2 col-3"]/span[@itemprop="prepTime"]/p/text()').get('')
    except:
        dic['Prep time'] = ''
        
    try:
        dic['Cook time'] = sel.xpath('//div[@class="row RecipeServesTime"]/div[@class="col-md-2 col-3"]/span[@itemprop="cookTime"]/p/text()').get('')
    except:
        dic['Cook time'] = ''
        
    try:
        dic['Total time'] = sel.xpath('//div[@class="row RecipeServesTime"]/div[@class="col-md-2 col-3"]/span[@itemprop="totalTime"]/p/text()').get('')
    except:
        dic['Total time'] = ''
    
    try:
        dic['Number of servings'] = int(re.findall(r'\d+',sel.xpath('//div[@class="row RecipeServesTime"]/div[@class="col-md-2 col-4 recipeYield"]/span[@itemprop="recipeYield"]/p/text()').get(''))[0])
    except:
        dic['Number of servings'] = ''
    
    ingredientLst = []
    length = len(sel.xpath('//li[@itemprop = "ingredients"]/span[@class="ingredient_name"]'))
    for i in range(length):
        ingredientLst.append([sel.xpath('//li[@itemprop = "ingredients"]')[i].xpath('text()')[0].get().strip(),
                             sel.xpath('//li[@itemprop = "ingredients"]/span[@class="ingredient_name"]/text()')[i].get()])
    
    dic['List of ingredients'] = ingredientLst
    
    try:
        dic['Cuisine'] = sel.xpath('//span[@itemprop="recipeCuisine"]/a/text()').get()
        
    except:
        dic['Cuisine'] = ''
    
    return dic


# In[65]:


def fillIndiaData(url,dic):
    content = Indiaspider(url)
    dic['Name of the recipe'].append(content['Name of the recipe'])
    dic['recipeCategory'].append(content['recipeCategory'])
    dic['Cuisine'].append(content['Cuisine'])
    dic['Equipments Used'].append(content['Equipments Used'])
    dic['Prep time'].append(content['Prep time'])
    dic['Cook time'].append(content['Cook time'])
    dic['Total time'].append(content['Total time'])
    dic['Number of servings'].append(content['Number of servings'])
    dic['List of ingredients'].append(content['List of ingredients'])
    dic['List of instructions'].append(content['List of instructions'])


# In[66]:


import time
for i in htmlLst:
    try:
        fillIndiaData(i,Indiadata)
    except:
        time.sleep(5)


# #### 6. Convert dictionary to data frame

# In[67]:


India = pd.DataFrame(Indiadata)
India.head()


# In[68]:


India.shape


# In[69]:


India["Source"] = ["Web1" for i in range(len(India))]
India.head()


# In[70]:


# save the dataset
India.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/India.csv")


# In[ ]:




