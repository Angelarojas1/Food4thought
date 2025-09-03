#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Thailand

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


# #### https://rasamalaysia.com/recipes/thai-recipes/

# In[3]:


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
        'cookie': '_ga=GA1.2.1298634517.1650842328; _gid=GA1.2.78407197.1650842328; _pbjs_userid_consent_data=3524755945110770; _pubCommonId=cbea3ee3-3286-4db6-a674-2edcc57770b7; _lr_env_src_ats=false; mv_tokens={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; mv_tokens_invalidate-verizon-pushes={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; cto_bidid=QRyr2V9FUVUxcHBPa3VJazE1TWRuV2Y3dCUyRmdFOU5DaWcxMEdZUHo4UjdXTUVwVnFCM2hJd3VKN2d1ZTViWndUUXRsenBKV3o3akI4UE8zdUdVZHFLeTVWUTQ3ZXdNc1NrZjNvSEI1WDVsQmU1UDNjeUN6bzhEaENFYlNEcFJ2MFJ2TjBo; cto_bundle=c9JT2V9iRHkzZm9IbCUyRnZiVDNFMVozbTBRRHRqSCUyRjNxODZubVNiT1FTUklVTmE5SExBa05kRlJrdGQ3UmRHWlR3bGhqYmZUREtWUjhGJTJGczlmMjN3VlpiRG9ZbGhPOGdldTBhN0VnaUpjU0lxVnllOTVETmZQdVd4ckVuMFg2N0YyaUFkMzRDZkM3Y0J1a1FETFBtQzNHdEhNVlElM0QlM0Q; __gads=ID=1f50e15f3097906f:T=1650842332:S=ALNI_MZ_H1g4FuA825XrZ77oTRn9swwTmw; __gpi=UID=0000045a02f923d9:T=1650842332:RT=1650904278:S=ALNI_MbbVHA9v8kD65LJuOWbrsKGaztCvQ',
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
    for i in sel.xpath('//main[@class="content"]/article')[0].xpath("//a[@class='entry-image-link']/@href"):
        lst.append(i.get())
    
    return lst


# In[4]:


htmlOnePageSpider("https://rasamalaysia.com/recipes/thai-recipes/", htmlLst)


# In[5]:


htmlOnePageSpider("https://rasamalaysia.com/recipes/thai-recipes/page/2/", htmlLst)


# In[6]:


# the number of recipes we have in total
len(htmlLst)


# In[37]:


# 3. go through all recipe htmls and scrape the data we want

Thailanddata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
}

def ThailandSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '_ga=GA1.2.1298634517.1650842328; _gid=GA1.2.78407197.1650842328; _pbjs_userid_consent_data=3524755945110770; _pubCommonId=cbea3ee3-3286-4db6-a674-2edcc57770b7; _lr_env_src_ats=false; mv_tokens={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; mv_tokens_invalidate-verizon-pushes={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; cto_bidid=QRyr2V9FUVUxcHBPa3VJazE1TWRuV2Y3dCUyRmdFOU5DaWcxMEdZUHo4UjdXTUVwVnFCM2hJd3VKN2d1ZTViWndUUXRsenBKV3o3akI4UE8zdUdVZHFLeTVWUTQ3ZXdNc1NrZjNvSEI1WDVsQmU1UDNjeUN6bzhEaENFYlNEcFJ2MFJ2TjBo; cto_bundle=c9JT2V9iRHkzZm9IbCUyRnZiVDNFMVozbTBRRHRqSCUyRjNxODZubVNiT1FTUklVTmE5SExBa05kRlJrdGQ3UmRHWlR3bGhqYmZUREtWUjhGJTJGczlmMjN3VlpiRG9ZbGhPOGdldTBhN0VnaUpjU0lxVnllOTVETmZQdVd4ckVuMFg2N0YyaUFkMzRDZkM3Y0J1a1FETFBtQzNHdEhNVlElM0QlM0Q; __gads=ID=1f50e15f3097906f:T=1650842332:S=ALNI_MZ_H1g4FuA825XrZ77oTRn9swwTmw; __gpi=UID=0000045a02f923d9:T=1650842332:RT=1650904278:S=ALNI_MbbVHA9v8kD65LJuOWbrsKGaztCvQ',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()')[1].get())
    
    return content

def fillThailandData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = ThailandSpider(html)
    dic['Name of the recipe'].append(content['name'])
    dic['Total time'].append(content['totalTime'])
    dic['Prep time'].append(content['prepTime'])
    try:
        dic['Cook time'].append(content['cookTime'])
    except:
        dic['Cook time'].append('')
    dic['List of ingredients'].append(content['recipeIngredient'])
    dic['List of instructions'].append(content['recipeInstructions'])
    dic['Number of servings'].append(content['recipeYield'])


# In[38]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillThailandData(html,Thailanddata)
    except:
        time.sleep(5)


# In[41]:


# convert data to dataframe
Thailand = pd.DataFrame(Thailanddata)
print(Thailand.shape)
Thailand.head()


# In[42]:


# generate source indicator
Thailand["Source"] = ["Web1" for i in range(len(Thailand))]
Thailand.head()


# In[43]:


# save dataset
Thailand.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Thailand.csv")


# In[ ]:




