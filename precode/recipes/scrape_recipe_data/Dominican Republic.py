#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Dominican Republic

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


# #### https://www.dominicancooking.com/recipes/traditional-dominican

# In[12]:


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
        'cookie':'usprivacy=1---; _pbjs_userid_consent_data=3524755945110770; __gads=ID=0d5ee638cfb248f7:T=1650153253:S=ALNI_MZAiC2HLfoCF8bgfomibsaH07fKnw; usprivacy=1---; cto_bidid=sBXmll9vTU00dEdJTk8zMDMwRWtNMTJHVzB3TGo5bVdVRkl5UFdoYSUyQkpVOUdBWGtEUGJlSjBwcmtSclNnNyUyRmE2TlZmdFpIUjhMNEVVWHVUQ3Nwb09xUDFzcnZ5azExJTJCbVJsQkYwQnczMUVPbjcyVUtKcWQ1OTY3djNVcXJna0olMkJSSWpR; _gid=GA1.2.2071035043.1652747838; __gpi=UID=00000437f67a3175:T=1650153253:RT=1652747839:S=ALNI_MZTyyZ1RUNuZ5B_mc9sk3e9l8uG1w; _lr_geo_location=US; cto_bundle=h2Ha9V91Mk9NM1FKS0FUQ2RXaUw5TDFmNUVHR1pTMzRlU1RMMkFBMnNiVmlBTGZ5THVKNW1XNnVBTHp5TUN2UlNJYTlmY01xZlB4ejlhczhqJTJCM1dldjFqdGRnQ1M2UGUwMTVEQUlhJTJGb283U3lLVmswUDl2VXlJY2hCMTVCTHZVc21UTVkxNFV1WXFhJTJCQ0Y2ZFNPJTJGSm1QRFVIQ3NsNU9QenhldHhZZm00ZXVqYnlySXdZQkFUOTRTZjFmRVEzZEVRbU9XTkdpclVHT2xNUjhwT0VWVTZnVzg2NmclM0QlM0Q; _ga_Y5X76N9XG7=GS1.1.1652747837.3.1.1652748186.0; _ga_ZBCBXZES8X=GS1.1.1652747837.3.1.1652748186.0; _ga=GA1.2.124193610.1650153251',
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
    for i in sel.xpath('//div[@class="feast-category-index  feast-recipe-index"]/ul/li[@class="listing-item"]/a/@href'):
        lst.append(i.get())
    
    return lst


# In[13]:


htmlOnePageSpider("https://www.dominicancooking.com/recipes/traditional-dominican", htmlLst)


# In[14]:


for i in range(2,12):
    htmlOnePageSpider("https://www.dominicancooking.com/recipes/traditional-dominican/page/{}".format(i), htmlLst)


# In[15]:


# the number of recipes we have in total
len(htmlLst)


# In[25]:


# 3. go through all recipe htmls and scrape the data we want

DominicanRepublicdata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def DominicanRepublicSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'usprivacy=1---; _pbjs_userid_consent_data=3524755945110770; __gads=ID=0d5ee638cfb248f7:T=1650153253:S=ALNI_MZAiC2HLfoCF8bgfomibsaH07fKnw; usprivacy=1---; cto_bidid=sBXmll9vTU00dEdJTk8zMDMwRWtNMTJHVzB3TGo5bVdVRkl5UFdoYSUyQkpVOUdBWGtEUGJlSjBwcmtSclNnNyUyRmE2TlZmdFpIUjhMNEVVWHVUQ3Nwb09xUDFzcnZ5azExJTJCbVJsQkYwQnczMUVPbjcyVUtKcWQ1OTY3djNVcXJna0olMkJSSWpR; _gid=GA1.2.2071035043.1652747838; __gpi=UID=00000437f67a3175:T=1650153253:RT=1652747839:S=ALNI_MZTyyZ1RUNuZ5B_mc9sk3e9l8uG1w; _lr_geo_location=US; cto_bundle=h2Ha9V91Mk9NM1FKS0FUQ2RXaUw5TDFmNUVHR1pTMzRlU1RMMkFBMnNiVmlBTGZ5THVKNW1XNnVBTHp5TUN2UlNJYTlmY01xZlB4ejlhczhqJTJCM1dldjFqdGRnQ1M2UGUwMTVEQUlhJTJGb283U3lLVmswUDl2VXlJY2hCMTVCTHZVc21UTVkxNFV1WXFhJTJCQ0Y2ZFNPJTJGSm1QRFVIQ3NsNU9QenhldHhZZm00ZXVqYnlySXdZQkFUOTRTZjFmRVEzZEVRbU9XTkdpclVHT2xNUjhwT0VWVTZnVzg2NmclM0QlM0Q; _ga_Y5X76N9XG7=GS1.1.1652747837.3.1.1652748186.0; _ga_ZBCBXZES8X=GS1.1.1652747837.3.1.1652748186.0; _ga=GA1.2.124193610.1650153251',
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

def fillDominicanRepublicData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = DominicanRepublicSpider(html)
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
        fillDominicanRepublicData(html,DominicanRepublicdata)
    except:
        time.sleep(5)

# convert data to dataframe
DominicanRepublic = pd.DataFrame(DominicanRepublicdata)
print(DominicanRepublic.shape)
DominicanRepublic.head()


# In[26]:


DominicanRepublic["Source"] = ["Web1" for i in range(len(DominicanRepublic))]
DominicanRepublic.head()


# In[27]:


# save dataset
DominicanRepublic.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/DominicanRepublic.csv")

