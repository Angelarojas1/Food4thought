#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Lebanon

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


# #### https://feelgoodfoodie.net/recipe/category/type/lebanese-inspired/

# In[7]:


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
        'cookie':'usprivacy=1---; usprivacy=1---; cppro-ft=true; cppro-ft-style=true; _ga=GA1.2.437647682.1650379836; _pbjs_userid_consent_data=3524755945110770; __gads=ID=dc838628840a46e0:T=1650379836:S=ALNI_MbHSDTftGmVBAYPdrpr9Fgb23mg-w; _lr_env_src_ats=false; cto_bidid=m9W4FV9NJTJGZ3RTeDhRTm1UWEZuN1JLVDJVSVZIcDY1eWNSdUp1NWxzcHFXQXIlMkZrdmNGUXc1UTl5cVZtcG9xZnVoRDdGdktnTW9jWkt6eTcxM3dCeHd4Z1FEWGhwMnRxdXBiSVZwJTJGYSUyQnglMkJDWGVNTGF2QnIwJTJCRmh1bHk2eFVCemN3WW4yamxvYzhWenhXRFVITU5od2UwcnN2dUElM0QlM0Q; wprm_analytics_visitor=625ecc451061e1.63685359; cp_style_29902=true; _omappvp=J4QYQTP4gErP8y6iDFvUWThH0xXXMu0r4Y7cXwyrTMCm0edMz798FO8bMyikHLBvWu8rmxHGD2YcqLWbvZz2nbBEaSMawRFY; _gid=GA1.2.215668828.1652109804; __adblocker=false; __gpi=UID=00000444ee51a5a0:T=1650379836:RT=1652109804:S=ALNI_MZaI_6R-pnaqpKXOVxQI0x2r_KPkg; omSeen-k6hxgtxkphxp9axhsvsi=1652109805699; omSeen-awpgqgbikmcdgzz5kwzf=1652109805699; _lr_geo_location=US; om-k6hxgtxkphxp9axhsvsi=1652109807147; om-awpgqgbikmcdgzz5kwzf=1652109807147; cto_bundle=kvset19GcVlmdGd6VlBXdGZuNDRjYWQ5SFByZ2E3MGZxcGlEMTRXY0dDTWFmSkMwQ2RkbTZTMTJDUjk4MHdpRm5aaUUlMkJuWHhwYXR4dXI4YyUyQllzdVJlRVBPZHhDTUE0JTJCVlg0UGFacVl4Y3owTiUyRkdYNWl0dFRKQVNKUG45NTJNWSUyQjJDZDdiRE8zMWlqTCUyQmR3WWlWdHBWdHJEa1RkYktVNUklMkZ1cG85NjVMMmptWVNOTDVEUUM5dGslMkZrMEluV2dqJTJCcVBnMyUyRmdyZmZqSUE4MnZ2N01pdzVRU0FhdWclM0QlM0Q',
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
    for i in sel.xpath('//div[@class="post-summary__image"]/a/@href'):
        lst.append(i.get())
    
    return lst


# In[8]:


htmlOnePageSpider("https://feelgoodfoodie.net/recipe/category/type/lebanese-inspired/", htmlLst)


# In[9]:


for i in range(2,8):
    htmlOnePageSpider("https://feelgoodfoodie.net/recipe/category/type/lebanese-inspired/?_paged={}".format(i), htmlLst)


# In[10]:


# the number of recipes we have in total
len(htmlLst)


# In[16]:


# 3. go through all recipe htmls and scrape the data we want

Lebanondata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def LebanonSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'usprivacy=1---; usprivacy=1---; cppro-ft=true; cppro-ft-style=true; _ga=GA1.2.437647682.1650379836; _pbjs_userid_consent_data=3524755945110770; __gads=ID=dc838628840a46e0:T=1650379836:S=ALNI_MbHSDTftGmVBAYPdrpr9Fgb23mg-w; _lr_env_src_ats=false; cto_bidid=m9W4FV9NJTJGZ3RTeDhRTm1UWEZuN1JLVDJVSVZIcDY1eWNSdUp1NWxzcHFXQXIlMkZrdmNGUXc1UTl5cVZtcG9xZnVoRDdGdktnTW9jWkt6eTcxM3dCeHd4Z1FEWGhwMnRxdXBiSVZwJTJGYSUyQnglMkJDWGVNTGF2QnIwJTJCRmh1bHk2eFVCemN3WW4yamxvYzhWenhXRFVITU5od2UwcnN2dUElM0QlM0Q; wprm_analytics_visitor=625ecc451061e1.63685359; cp_style_29902=true; _omappvp=J4QYQTP4gErP8y6iDFvUWThH0xXXMu0r4Y7cXwyrTMCm0edMz798FO8bMyikHLBvWu8rmxHGD2YcqLWbvZz2nbBEaSMawRFY; _gid=GA1.2.215668828.1652109804; __adblocker=false; __gpi=UID=00000444ee51a5a0:T=1650379836:RT=1652109804:S=ALNI_MZaI_6R-pnaqpKXOVxQI0x2r_KPkg; omSeen-k6hxgtxkphxp9axhsvsi=1652109805699; omSeen-awpgqgbikmcdgzz5kwzf=1652109805699; _lr_geo_location=US; om-k6hxgtxkphxp9axhsvsi=1652109807147; om-awpgqgbikmcdgzz5kwzf=1652109807147; cto_bundle=kvset19GcVlmdGd6VlBXdGZuNDRjYWQ5SFByZ2E3MGZxcGlEMTRXY0dDTWFmSkMwQ2RkbTZTMTJDUjk4MHdpRm5aaUUlMkJuWHhwYXR4dXI4YyUyQllzdVJlRVBPZHhDTUE0JTJCVlg0UGFacVl4Y3owTiUyRkdYNWl0dFRKQVNKUG45NTJNWSUyQjJDZDdiRE8zMWlqTCUyQmR3WWlWdHBWdHJEa1RkYktVNUklMkZ1cG85NjVMMmptWVNOTDVEUUM5dGslMkZrMEluV2dqJTJCcVBnMyUyRmdyZmZqSUE4MnZ2N01pdzVRU0FhdWclM0QlM0Q',
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

def fillLebanonData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = LebanonSpider(html)
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
        fillLebanonData(html,Lebanondata)
    except:
        time.sleep(5)

# convert data to dataframe
Lebanon = pd.DataFrame(Lebanondata)
print(Lebanon.shape)
Lebanon.head()


# In[17]:


Lebanon["Source"] = ["Web1" for i in range(len(Lebanon))]
Lebanon.head()


# In[18]:


# save dataset
Lebanon.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Lebanon.csv")


# In[ ]:




