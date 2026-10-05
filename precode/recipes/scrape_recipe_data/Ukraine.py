#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Ukraine
# 

# https://1000.menu/catalog/ukrainskaya-kuxnya

# In[40]:


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


# In[52]:


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
        'cookie':'_ga=GA1.2.408305898.1643785519; _fbp=fb.1.1643785519163.2028577201; _ym_uid=163340738294028923; _ym_d=1643785520; _gid=GA1.2.570941813.1645570148; _ym_isad=2; SYSESSINFO[xr_msout]=true; __gads=ID=69080e4c2b19f3cc-22748f1e22d100fc:T=1645570176:RT=1645570176:S=ALNI_MZ5FKPbc-NeKfUP49Q34KfByDkmSA; SYSESSINFO[xr_stegs]=1; SYSESSINFO[xr_sl]=true; PHPSESSID=fe3c9e24227c7932a8d1d461a7355200; XRSESSKEY=6jc6y0apm6e1rxxvdfd3uwxscstfaqp7; _ym_visorc=b; LentaInformStorage={"0":{},"C664375":{"page":2,"time":1645595479779}}',
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
    for i in sel.xpath('//div[@class="cooking-block"]/div/div[@class="photo is-relative"]/a/@href'):
        lst.append("https://1000.menu/"+i.get())
        
    return lst


# In[53]:


# 2. go through all categories and pages in the web and get all recipe htmls
categoryLst = []

categoryLst.append("https://1000.menu/catalog/ukrainskaya-kuxnya")
categoryLst.append("https://1000.menu/catalog/ukrainskaya-kuxnya/2")

for i in categoryLst:
    htmlLst = htmlOnePageSpider(i, htmlLst)
    
print(len(htmlLst))


# In[54]:


htmlLst


# In[7]:


# 3. go through all recipe htmls and scrape the data we want

Ukrainedata = {
    "Name of the recipe":[],
    "Total time":[],
    "List of ingredients": [],
    "List of instructions":[],
    'Number of servings':[],
    "Category":[]
}

def UkraineSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'geo_last_ip=1660772984; geo_ip_country=US; geo_ip_city_id=97725; geo_ip_oblast_id=3315; geo_ip_okrug_id=0; geo_last_ip=1660772984; geo_ip_country=US; geo_ip_city_id=97725; geo_ip_oblast_id=3315; geo_ip_okrug_id=0; events_stat_user_id=56204ce5-16d7-43cc-bb1b-3c594f14b210; tmr_lvid=e73ceedd6c09fc02fc2b63ee72cdfd55; tmr_lvidTS=1641870489424; _ym_uid=164187048981812996; _ym_d=1641870489; __gads=ID=427c2b2797124bfd:T=1641870488:S=ALNI_MbcgKyokq0L2w3HJ286poA0BbW7gg; informb_stat_user_id=2930542317; __utmz=1.1641870647.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not provided); PHPSESSID=mihmbqdc5qe4fg8fqgeck485qh; __utmc=1; geo_ip_set=1645566591; geo_ip_set=1645566591; __utma=1.808993664.1641870489.1644588362.1645566594.9; __utmt=1; _ym_isad=2; events_stat_ses_id={"sesId":34051,"expires":1645567681614}; __utmb=1.4.10.1645566594; tmr_detect=0|1645566784213; tmr_reqNum=72',
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

def fillUkraineData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = UkraineSpider(html)
    dic['Name of the recipe'].append(content['name'])
    dic['Total time'].append(content['totalTime'])
    dic['Prep time'].append(content['prepTime'])
    dic['List of ingredients'].append(content['recipeIngredient'])
    dic['List of instructions'].append(content['recipeInstructions'])
    dic['Number of servings'].append(content['recipeYield'])
    dic['Category'].append(content['recipeCategory'])    


# In[39]:


headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'geo_last_ip=1660772984; geo_ip_country=US; geo_ip_city_id=97725; geo_ip_oblast_id=3315; geo_ip_okrug_id=0; geo_last_ip=1660772984; geo_ip_country=US; geo_ip_city_id=97725; geo_ip_oblast_id=3315; geo_ip_okrug_id=0; events_stat_user_id=56204ce5-16d7-43cc-bb1b-3c594f14b210; tmr_lvid=e73ceedd6c09fc02fc2b63ee72cdfd55; tmr_lvidTS=1641870489424; _ym_uid=164187048981812996; _ym_d=1641870489; __gads=ID=427c2b2797124bfd:T=1641870488:S=ALNI_MbcgKyokq0L2w3HJ286poA0BbW7gg; informb_stat_user_id=2930542317; __utmz=1.1641870647.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not provided); PHPSESSID=mihmbqdc5qe4fg8fqgeck485qh; __utmc=1; geo_ip_set=1645566591; geo_ip_set=1645566591; __utma=1.808993664.1641870489.1644588362.1645566594.9; __utmt=1; _ym_isad=2; events_stat_ses_id={"sesId":34051,"expires":1645567681614}; __utmb=1.4.10.1645566594; tmr_detect=0|1645566784213; tmr_reqNum=72',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
response = requests.get('https://www.russianfood.com/recipes/recipe.php?rid=166281',headers=headers)
sel = Selector(response.text)


# In[ ]:





# In[ ]:





# In[ ]:





# In[8]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillRussiaData(html,Russiadata)
    except:
        time.sleep(5)


# In[9]:


# convert data to dataframe
Russia = pd.DataFrame(Russiadata)
print(Russia.shape)
Russia.head()

# save dataset
Russia.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Russia.csv")


# In[ ]:





# In[ ]:





# In[ ]:




