#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Slovakia

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


# #### https://dobruchut.aktuality.sk/recepty/79/slovenska-kuchyna/

# In[13]:


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
        'cookie':'_fbp=fb.1.1650830674754.627995023; __gfp_64b=PNHV5OCnpLCak6y_id7ntGnKyJx4ae0kpBjRv9PgNKz.m7|1650830675; __gads=ID=f917de9717368de1:T=1650830675:S=ALNI_MbLl0ImVFhfe-rCVdLQo3rD6klghw; hide_push_modal=true; _hjSessionUser_1775618=eyJpZCI6IjgwZDYzMGYyLWNiODAtNWM1Yi05NGNmLTFhYTllYjM3OGRhNyIsImNyZWF0ZWQiOjE2NTA4MzA2NzQ5NzUsImV4aXN0aW5nIjp0cnVlfQ==; uid=3e66c9a2-1e1e-44af-aafa-9f28ae6f6413; _gid=GA1.2.583148742.1650918349; abtest2=1-A_2-B_3-A_4-A_5-A_6-A_7-B_8-B_9-B_; TS01f7a0f2=015c8fe40ed7a29d31ce17d7881dbf3f3e7bd9e6eb9bf3b082aba7cd0002a7fe581ead2c6f815d71eace36a346fb736f29a37d7dfcfe54ebcfb2615af83741cb6a0b3e5169a06331a072c6979cda17b7fdfb08b3f9bdfbb30966f700bec6bd41515e2b67df; __gpi=UID=000004b706cea9e3:T=1650830675:RT=1650986114:S=ALNI_MbpXZ5NJeOde95s67hIPibxXmWgZg; TS01dc1985=015c8fe40e23bd3b31b108d0c0d925f3b0c419fbba6179e28dbb8a4522c69c2d4f2b61e6888c6045924d5be6aa0fe25551e54bfde8; _gat=1; _gat_UA-31353448-2=1; azTrackerTestCookie=2; _ga_JRDL74JXW9=GS1.1.1651001152.4.0.1651001152.0; _hjSession_1775618=eyJpZCI6ImM2YjA3Yjg2LTAyZGQtNGViNC1hMjAxLTMwNzc2OGY3NTk4MCIsImNyZWF0ZWQiOjE2NTEwMDExNTI2MzgsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; FCNEC=[["AKsRol-LK-gh4avVrxYujwxdqNxe5t4L7RtH-MPXwDiKMiSuGcQ7rYTb5eEiag-116jco93JejjQ2VUw5dol4QNAGFFMu31JmpGJtTQTA58GJXWFWiE47RjUm5bjqIgwx3ECwo9MAgCDRC3mRNZHOwHfvm7D9scOaw=="],null,[]]; _ga=GA1.2.834803908.1650830674; _gat_rasgroup=1; TScb90d893027=08e5e65cc0ab2000d3a8917a5912ba6d3da621beea7d8324086bb7df60aac2e28d4be2c87840f1d7082bc8188e1130005afdbf0e69d1184b098a12e8faf6a8b793fd8738c54a623c77951575a7653eeffbaf59281d97ad3c6b315bb00a51c41f',
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
    for i in sel.xpath("//li[@class='recipe-list-item']/div/a[@class='image-wrapper']/@href"):
        lst.append(i.get())
    
    return lst


# In[14]:


htmlOnePageSpider("https://dobruchut.aktuality.sk/recepty/79/slovenska-kuchyna/", htmlLst)


# In[15]:


for i in range(2,173):
    htmlOnePageSpider("https://dobruchut.aktuality.sk/recepty/79/slovenska-kuchyna/{}/".format(i), htmlLst)


# In[16]:


# the number of recipes we have in total
len(htmlLst)


# In[21]:


# 3. go through all recipe htmls and scrape the data we want

Slovakiadata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[]
}

def SlovakiaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_fbp=fb.1.1650830674754.627995023; __gfp_64b=PNHV5OCnpLCak6y_id7ntGnKyJx4ae0kpBjRv9PgNKz.m7|1650830675; __gads=ID=f917de9717368de1:T=1650830675:S=ALNI_MbLl0ImVFhfe-rCVdLQo3rD6klghw; hide_push_modal=true; _hjSessionUser_1775618=eyJpZCI6IjgwZDYzMGYyLWNiODAtNWM1Yi05NGNmLTFhYTllYjM3OGRhNyIsImNyZWF0ZWQiOjE2NTA4MzA2NzQ5NzUsImV4aXN0aW5nIjp0cnVlfQ==; uid=3e66c9a2-1e1e-44af-aafa-9f28ae6f6413; _gid=GA1.2.583148742.1650918349; abtest2=1-A_2-B_3-A_4-A_5-A_6-A_7-B_8-B_9-B_; TS01f7a0f2=015c8fe40ed7a29d31ce17d7881dbf3f3e7bd9e6eb9bf3b082aba7cd0002a7fe581ead2c6f815d71eace36a346fb736f29a37d7dfcfe54ebcfb2615af83741cb6a0b3e5169a06331a072c6979cda17b7fdfb08b3f9bdfbb30966f700bec6bd41515e2b67df; __gpi=UID=000004b706cea9e3:T=1650830675:RT=1650986114:S=ALNI_MbpXZ5NJeOde95s67hIPibxXmWgZg; TS01dc1985=015c8fe40e23bd3b31b108d0c0d925f3b0c419fbba6179e28dbb8a4522c69c2d4f2b61e6888c6045924d5be6aa0fe25551e54bfde8; _gat=1; _gat_UA-31353448-2=1; azTrackerTestCookie=2; _ga_JRDL74JXW9=GS1.1.1651001152.4.0.1651001152.0; _hjSession_1775618=eyJpZCI6ImM2YjA3Yjg2LTAyZGQtNGViNC1hMjAxLTMwNzc2OGY3NTk4MCIsImNyZWF0ZWQiOjE2NTEwMDExNTI2MzgsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; FCNEC=[["AKsRol-LK-gh4avVrxYujwxdqNxe5t4L7RtH-MPXwDiKMiSuGcQ7rYTb5eEiag-116jco93JejjQ2VUw5dol4QNAGFFMu31JmpGJtTQTA58GJXWFWiE47RjUm5bjqIgwx3ECwo9MAgCDRC3mRNZHOwHfvm7D9scOaw=="],null,[]]; _ga=GA1.2.834803908.1650830674; _gat_rasgroup=1; TScb90d893027=08e5e65cc0ab2000d3a8917a5912ba6d3da621beea7d8324086bb7df60aac2e28d4be2c87840f1d7082bc8188e1130005afdbf0e69d1184b098a12e8faf6a8b793fd8738c54a623c77951575a7653eeffbaf59281d97ad3c6b315bb00a51c41f',
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

def fillSlovakiaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = SlovakiaSpider(html)
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
        fillSlovakiaData(html,Slovakiadata)
    except:
        time.sleep(5)

# convert data to dataframe
Slovakia = pd.DataFrame(Slovakiadata)
print(Slovakia.shape)
Slovakia.head()


# In[22]:


Slovakia["Source"] = ["Web1" for i in range(len(Slovakia))]
Slovakia.head()


# In[23]:


# save dataset
Slovakia.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Slovakia.csv")


# In[ ]:




