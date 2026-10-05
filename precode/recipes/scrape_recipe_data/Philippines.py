#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Philippines

# panlasangpinoy.com

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


# 1. create a list to store all recipe htmls on one page
# initialize htmlLst to store the htmls of all recipes
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
        'cookie':'pg_buildfile=211117-075-nc-7f61b086bdd39a26afe60614ced63547; pg_geo={"country":"US","region":"IL","ip":"98.253.98.120"}; pg_custom_timeout=; pg_ip=98.253.98.120; pg_beacon=1; pg_mm2_cookie_a=bed0a9b4-acf2-4b57-a298-f8d01ff509b2; pg_session_id=8ecdc5ee-2674-45a5-9b15-1053d2b6985d; pg_tc=not-sampled; _ga=GA1.2.847607561.1639564002; _gid=GA1.2.665633559.1639564002; pg_analytics=disabled; aasd=3|1639564002087; __aaxsc=2; __gads=ID=9314ae1b531f57d1:T=1639564002:S=ALNI_MbsaBwWTmkw3DwhTTyhRzbWhcRwKQ; __qca=P0-1463611837-1639564067477; _gat_gtag_UA_8984034_3=1; pg_session_depth=4; pg_canonical_session=7c2ff4c4e326a0fe5c8fe364884c441f; FCNEC=[["AKsRol96ZCf8zuZ86-oXgiNw9WZFTaeThr7Kb3p9itqhcofgbMugtx3K5zaf3EFGPouUyfqlxH5DnvHVB5VcqREGRvhkfIvxcrSfoCtZcb2rBnY2_okq8qAgcuTPTtfy0T-GTyTmQshlZfDv2E0f0MTkID_53dPQYg=="],null,[]]',
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
    for i in range(10):   
        lst.append(sel.xpath('//main[@class="content"]/article')[0].xpath('//h2[@class="entry-title"]/a/@href')[i].get())
        
    
    return lst


# In[3]:


# 2. go through all categories and pages in the web and get all recipe htmls

# initialize pageLst to store the htmls of all pages
pageLst = []

pageLst.append('https://panlasangpinoy.com/categories/recipes/')
    
for i in range(2,178):
    pageLst.append('https://panlasangpinoy.com/categories/recipes/page/{}/'.format(i))
    
for i in pageLst:
    htmlLst = htmlOnePageSpider(i, htmlLst)
    
# drop duplicates
htmlLst = list(set(htmlLst))

print("The number of recipes is {}".format(len(htmlLst)))


# In[4]:


htmlLst


# In[17]:


headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'pg_buildfile=211117-075-nc-7f61b086bdd39a26afe60614ced63547; pg_geo={"country":"US","region":"IL","ip":"98.253.98.120"}; pg_custom_timeout=; pg_ip=98.253.98.120; pg_beacon=1; pg_mm2_cookie_a=bed0a9b4-acf2-4b57-a298-f8d01ff509b2; pg_session_id=8ecdc5ee-2674-45a5-9b15-1053d2b6985d; pg_tc=not-sampled; _ga=GA1.2.847607561.1639564002; _gid=GA1.2.665633559.1639564002; pg_analytics=disabled; aasd=3|1639564002087; __aaxsc=2; __gads=ID=9314ae1b531f57d1:T=1639564002:S=ALNI_MbsaBwWTmkw3DwhTTyhRzbWhcRwKQ; __qca=P0-1463611837-1639564067477; _gat_gtag_UA_8984034_3=1; pg_session_depth=4; pg_canonical_session=7c2ff4c4e326a0fe5c8fe364884c441f; FCNEC=[["AKsRol96ZCf8zuZ86-oXgiNw9WZFTaeThr7Kb3p9itqhcofgbMugtx3K5zaf3EFGPouUyfqlxH5DnvHVB5VcqREGRvhkfIvxcrSfoCtZcb2rBnY2_okq8qAgcuTPTtfy0T-GTyTmQshlZfDv2E0f0MTkID_53dPQYg=="],null,[]]',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
response = requests.get('https://panlasangpinoy.com/ginataang-bitsuelas/',headers=headers)
response.encoding="utf-8"
sel = Selector(response.text)


# In[31]:


# 3. go through all recipe htmls and scrape the data we want

Philippinesdata = {
    "Name of the recipe": [],
    "Cook time": [],
    "Prep time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}


def Philippinesspider(recipes_url):
    """
    input: recipes_url, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'pg_buildfile=211117-075-nc-7f61b086bdd39a26afe60614ced63547; pg_geo={"country":"US","region":"IL","ip":"98.253.98.120"}; pg_custom_timeout=; pg_ip=98.253.98.120; pg_beacon=1; pg_mm2_cookie_a=bed0a9b4-acf2-4b57-a298-f8d01ff509b2; pg_session_id=8ecdc5ee-2674-45a5-9b15-1053d2b6985d; pg_tc=not-sampled; _ga=GA1.2.847607561.1639564002; _gid=GA1.2.665633559.1639564002; pg_analytics=disabled; aasd=3|1639564002087; __aaxsc=2; __gads=ID=9314ae1b531f57d1:T=1639564002:S=ALNI_MbsaBwWTmkw3DwhTTyhRzbWhcRwKQ; __qca=P0-1463611837-1639564067477; _gat_gtag_UA_8984034_3=1; pg_session_depth=4; pg_canonical_session=7c2ff4c4e326a0fe5c8fe364884c441f; FCNEC=[["AKsRol96ZCf8zuZ86-oXgiNw9WZFTaeThr7Kb3p9itqhcofgbMugtx3K5zaf3EFGPouUyfqlxH5DnvHVB5VcqREGRvhkfIvxcrSfoCtZcb2rBnY2_okq8qAgcuTPTtfy0T-GTyTmQshlZfDv2E0f0MTkID_53dPQYg=="],null,[]]',
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
    
    # scrape dictionary containing all information that we need
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()').get(''), strict=False)['@graph'][-1]
    
    return content

def fillPhilippinesData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = Philippinesspider(html)
    if content['cookTime']:
        dic['Name of the recipe'].append(content['name'])
        try:
            dic['Prep time'].append(content['prepTime'])
        except:
            dic['Prep time'].append('')
        
        dic['Cook time'].append(content['cookTime'])
        dic['List of ingredients'].append(content['recipeIngredient'])
        dic['List of instructions'].append(content['recipeInstructions'])
        try:
            dic['Number of servings'].append(content['recipeYield'])
        except:
            dic['Number of servings'].append([])
        try:
            dic['Category'].append(content['recipeCategory'])
        except:
            dic['Category'].append([])


# In[32]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillPhilippinesData(html,Philippinesdata)
    except:
        time.sleep(5)


# In[33]:


# convert data to dataframe
data = pd.DataFrame(Philippinesdata)
print(data.shape)
data.head()

# save dataset
data.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Philippines.csv")

