#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Liberia

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


# #### https://cleanfoodiecravings.com/category/recipe/

# In[6]:


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
        'cookie':'fd-form-5eea5bd2b9c153002b5ae1e6-subscribed=true; _ga=GA1.2.136252238.1650380282; mv_tokens={"mv_uuid":"c1617790-407e-11ec-8982-011c090675ab","version":"invalidate-verizon-pushes"}; _pbjs_userid_consent_data=3524755945110770; _pubCommonId=a62a2746-9c7c-4508-b1b2-12e66642f95a; _lr_env_src_ats=false; mv_tokens_invalidate-verizon-pushes={"mv_uuid":"c1617790-407e-11ec-8982-011c090675ab","version":"invalidate-verizon-pushes"}; cto_bidid=Uw2St19OMEF5NFBucXBOR1MlMkJJSGdCZWIxbTA2TWRJdjFxSjdIc2dpanNmUUJJZHpLa3NBdlN3MDlsZmEwSVNFQjZsa0FuQzFEVzF4anN4diUyRkpaWUhXT1FNZWolMkY0Z0Fkem0lMkZNUjljSmxOajBYWm0wamptUGhTTUFHeElGVnB5VjhyYzhVZFI1WXMyTXNFOEZhOVowS2VSZ0RJT0JtZ0t2eXBYYzFScXBCSjVJREhPYyUzRA; __gads=ID=a85cd355f45b64db:T=1650380284:S=ALNI_MZZPEo3dAXcCTHp-nDelaMNDGspAA; fd-form-5eea5bd2b9c153002b5ae1e6-subscribed=true; _gid=GA1.2.1341782506.1652108693; _svsid=ce02936d0d70492aae1376dd5e46d7cf; __gpi=UID=0000049657a7b950:T=1650380284:RT=1652108695:S=ALNI_MYfx9Oo48a4SuATuy4HMzsiQQcaLw; cto_bundle=wStdHl9PZlplWGdBNXRLRjRqJTJGTzdZJTJGQ1ZXUldyUUx2aFZUNVdHWlFGMkJWV01aRE1YUHlaTXc1bEdqZ20xa0IlMkZOMEdFdlNxNnRUUWxEdjBvelV2M0JMbjl3aFhtSWRsdE1vejZsekV4cFc4VDNDRXRlM251eFhDSzVvaFdQY0JVUWtHRUFYcG1SY1JMQ3NFUzUwZVJGVU5HVkxrVVlJY0VhU2w0R2NRNVBqRmhMczUwcE5jTjFWJTJGc3F2RVZ0bk00dm1iQklmSDRwQVBTeFo3UWNGRzNqWUE2UlElM0QlM0Q',
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
    for i in sel.xpath('//main[@class="content"]/article/header/a/@href'):
        lst.append(i.get())
    
    return lst


# In[7]:


htmlOnePageSpider("https://cleanfoodiecravings.com/category/recipe/", htmlLst)


# In[8]:


for i in range(2,13):
    htmlOnePageSpider("https://cleanfoodiecravings.com/category/recipe/page/{}/".format(i), htmlLst)


# In[9]:


# the number of recipes we have in total
len(htmlLst)


# In[21]:


# 3. go through all recipe htmls and scrape the data we want

Liberiadata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
}

def LiberiaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'fd-form-5eea5bd2b9c153002b5ae1e6-subscribed=true; _ga=GA1.2.136252238.1650380282; mv_tokens={"mv_uuid":"c1617790-407e-11ec-8982-011c090675ab","version":"invalidate-verizon-pushes"}; _pbjs_userid_consent_data=3524755945110770; _pubCommonId=a62a2746-9c7c-4508-b1b2-12e66642f95a; _lr_env_src_ats=false; mv_tokens_invalidate-verizon-pushes={"mv_uuid":"c1617790-407e-11ec-8982-011c090675ab","version":"invalidate-verizon-pushes"}; cto_bidid=Uw2St19OMEF5NFBucXBOR1MlMkJJSGdCZWIxbTA2TWRJdjFxSjdIc2dpanNmUUJJZHpLa3NBdlN3MDlsZmEwSVNFQjZsa0FuQzFEVzF4anN4diUyRkpaWUhXT1FNZWolMkY0Z0Fkem0lMkZNUjljSmxOajBYWm0wamptUGhTTUFHeElGVnB5VjhyYzhVZFI1WXMyTXNFOEZhOVowS2VSZ0RJT0JtZ0t2eXBYYzFScXBCSjVJREhPYyUzRA; __gads=ID=a85cd355f45b64db:T=1650380284:S=ALNI_MZZPEo3dAXcCTHp-nDelaMNDGspAA; fd-form-5eea5bd2b9c153002b5ae1e6-subscribed=true; _gid=GA1.2.1341782506.1652108693; _svsid=ce02936d0d70492aae1376dd5e46d7cf; __gpi=UID=0000049657a7b950:T=1650380284:RT=1652108695:S=ALNI_MYfx9Oo48a4SuATuy4HMzsiQQcaLw; cto_bundle=wStdHl9PZlplWGdBNXRLRjRqJTJGTzdZJTJGQ1ZXUldyUUx2aFZUNVdHWlFGMkJWV01aRE1YUHlaTXc1bEdqZ20xa0IlMkZOMEdFdlNxNnRUUWxEdjBvelV2M0JMbjl3aFhtSWRsdE1vejZsekV4cFc4VDNDRXRlM251eFhDSzVvaFdQY0JVUWtHRUFYcG1SY1JMQ3NFUzUwZVJGVU5HVkxrVVlJY0VhU2w0R2NRNVBqRmhMczUwcE5jTjFWJTJGc3F2RVZ0bk00dm1iQklmSDRwQVBTeFo3UWNGRzNqWUE2UlElM0QlM0Q',
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
    
    return content

def fillLiberiaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = LiberiaSpider(html)
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
        

# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillLiberiaData(html,Liberiadata)
    except:
        time.sleep(5)

# convert data to dataframe
Liberia = pd.DataFrame(Liberiadata)
print(Liberia.shape)
Liberia.head()


# In[22]:


Liberia["Source"] = ["Web1" for i in range(len(Liberia))]
Liberia.head()


# In[23]:


# save dataset
Liberia.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Liberia.csv")


# In[ ]:




