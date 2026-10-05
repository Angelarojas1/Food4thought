#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Bosnia and Herzegovina

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


# #### https://www.all-thats-jas.com/category/bosnia-and-herzegovina/

# In[4]:


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
        'cookie':'growme_version={"name":"7.85.8","version":"7.85.8"}; utm_source=; utm_campaign=; _pbjs_userid_consent_data=3524755945110770; _pubCommonId=d92e6730-d95c-4e78-a20b-88835268c712; mv_tokens={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; mv_tokens_invalidate-verizon-pushes={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; cto_bidid=i-2W4V9CM24wdmpCdG1XOHR2dVhTc2RJOGNZMmhnOFBlUFBkb1RlUVVNQWhpdktLSEg5a0M4MmlYNUpaMmQySmpNVTlXJTJCJTJGTkNjWDJHcyUyRmZEQThHOHhJOG1nOG0zWk51OENzVTNjaE4lMkZIJTJCanhXMFJjdTlCdU1wdVklMkZ4RkxIR1l1aDBnbw; cto_bundle=v_0LS18yJTJCUTBDbHN4Z3N3byUyRkRtSlpKMjRNaHhheENFZnlPMWxENVRnOEpZSnJsS2M0ajR3Y2twRkM3STJKVXZVa0NoMzA2MXhvR0Z1WTIwMiUyRk91byUyRml2ZDVvZ1d2OXhHeTVSZTYxWHhpWDR2WHFqN0VYaWZrVjRZdnJLTmdwcEtDJTJCdENXSWklMkI3b3FSeGE3SGgyaGZaeGNxNkElM0QlM0Q; __gads=ID=e7dc24fa69949161:T=1649736492:S=ALNI_Maqs_KWunXmrypzPLw_cgL-MIvkpg; __qca=P0-166083142-1649736494559; _ga_4TBHSW90DN=GS1.1.1652808226.2.0.1652808226.0; mediavine_session={"depth":1,"referrer":"DIRECT","wrapperVersionGroup":{"version":"2.75.4","name":"2.75.4-QATestSites-beta-control"},"videoVersionGroup":{"name":"default","version":"9.1.2"}}; _ga=GA1.2.877879962.1649736489; _gid=GA1.2.1926129498.1652808227; _gat_gtag_UA_45644634_1=1; _lr_retry_request=true; _lr_env_src_ats=false; _svsid=d787604fdd154a2094d4786bafd7d3e5; __gpi=UID=000004b6f4162083:T=1650823283:RT=1652808228:S=ALNI_MbSL0mqH9bCvJAgTqh07d31xJqbvg',
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
    for i in sel.xpath('//a[@class="entry-image-link"]/@href'):
        lst.append(i.get())
    
    return lst


# In[5]:


htmlOnePageSpider("https://www.all-thats-jas.com/category/bosnia-and-herzegovina/", htmlLst)


# In[6]:


for i in range(2,4):
    htmlOnePageSpider("https://www.all-thats-jas.com/category/bosnia-and-herzegovina/page/{}/".format(i), htmlLst)


# In[7]:


# the number of recipes we have in total
len(htmlLst)


# In[13]:


# 3. go through all recipe htmls and scrape the data we want

BosniaAndHerzegovinadata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def BosniaAndHerzegovinaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'growme_version={"name":"7.85.8","version":"7.85.8"}; utm_source=; utm_campaign=; _pbjs_userid_consent_data=3524755945110770; _pubCommonId=d92e6730-d95c-4e78-a20b-88835268c712; mv_tokens={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; mv_tokens_invalidate-verizon-pushes={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; cto_bidid=i-2W4V9CM24wdmpCdG1XOHR2dVhTc2RJOGNZMmhnOFBlUFBkb1RlUVVNQWhpdktLSEg5a0M4MmlYNUpaMmQySmpNVTlXJTJCJTJGTkNjWDJHcyUyRmZEQThHOHhJOG1nOG0zWk51OENzVTNjaE4lMkZIJTJCanhXMFJjdTlCdU1wdVklMkZ4RkxIR1l1aDBnbw; cto_bundle=v_0LS18yJTJCUTBDbHN4Z3N3byUyRkRtSlpKMjRNaHhheENFZnlPMWxENVRnOEpZSnJsS2M0ajR3Y2twRkM3STJKVXZVa0NoMzA2MXhvR0Z1WTIwMiUyRk91byUyRml2ZDVvZ1d2OXhHeTVSZTYxWHhpWDR2WHFqN0VYaWZrVjRZdnJLTmdwcEtDJTJCdENXSWklMkI3b3FSeGE3SGgyaGZaeGNxNkElM0QlM0Q; __gads=ID=e7dc24fa69949161:T=1649736492:S=ALNI_Maqs_KWunXmrypzPLw_cgL-MIvkpg; __qca=P0-166083142-1649736494559; _ga_4TBHSW90DN=GS1.1.1652808226.2.0.1652808226.0; mediavine_session={"depth":1,"referrer":"DIRECT","wrapperVersionGroup":{"version":"2.75.4","name":"2.75.4-QATestSites-beta-control"},"videoVersionGroup":{"name":"default","version":"9.1.2"}}; _ga=GA1.2.877879962.1649736489; _gid=GA1.2.1926129498.1652808227; _gat_gtag_UA_45644634_1=1; _lr_retry_request=true; _lr_env_src_ats=false; _svsid=d787604fdd154a2094d4786bafd7d3e5; __gpi=UID=000004b6f4162083:T=1650823283:RT=1652808228:S=ALNI_MbSL0mqH9bCvJAgTqh07d31xJqbvg',
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

def fillBosniaAndHerzegovinaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = BosniaAndHerzegovinaSpider(html)
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
        fillBosniaAndHerzegovinaData(html,BosniaAndHerzegovinadata)
    except:
        time.sleep(5)

# convert data to dataframe
BosniaAndHerzegovina = pd.DataFrame(BosniaAndHerzegovinadata)
print(BosniaAndHerzegovina.shape)
BosniaAndHerzegovina.head()


# In[14]:


BosniaAndHerzegovina["Source"] = ["Web1" for i in range(len(BosniaAndHerzegovina))]
BosniaAndHerzegovina.head()


# In[15]:


# save dataset
BosniaAndHerzegovina.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/BosniaAndHerzegovina.csv")


# In[ ]:




