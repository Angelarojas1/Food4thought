#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Mozambique

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


# #### https://www.sbs.com.au/food/cuisine/mozambican

# In[11]:


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
        'cookie':'at_check=true; _ga=GA1.3.1792221838.1650768218; AMCVS_5BD3248D541C319B0A4C98C6@AdobeOrg=1; _gcl_au=1.1.320362789.1650768218; _fbp=fb.2.1650768218267.588341819; s_cc=true; _cb=I9DZ9DrFxUvbmcXB; aam_uuid=87393916760910473647345340690129581144; __gads=ID=678a9af5e086b422:T=1650768219:S=ALNI_MYPMFwHue1qXff2-FuUGWqelECiog; s_sq=[[B]]; _gid=GA1.3.972293906.1652121010; AMCV_5BD3248D541C319B0A4C98C6@AdobeOrg=1585540135|MCIDTS|19122|MCMID|87376036454763747047342378282379895084|MCAAMLH-1652796343|7|MCAAMB-1652796343|RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y|MCCIDH|-2041533806|MCOPTOUT-1652198743s|NONE|MCAID|2FD5C74F0515A8D2-40000649925735BE|vVersion|4.4.0; _cb_svref=https://www.google.com/; __gpi=UID=000004b0a9696f8c:T=1650768219:RT=1652191543:S=ALNI_MalCMp0Uup4Aclp2pbeJBzdhKBELw; mbox=PC#585c5d80c96040efbf0a02a9179c040a.34_0#1714013019|session#4a6a646903934956ab3316e27daf14e7#1652193441; _chartbeat2=.1636304326101.1652191581098.0000000011000011.iY7HqDjIz0ks2_oXBbSef5D5I_lP.2; s_nr=1652191581334-Repeat',
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
    for i in sel.xpath('//div[@class="view-content"]/div/div/a/@href'):
        lst.append(i.get())
    
    return lst


# In[12]:


htmlOnePageSpider("https://www.sbs.com.au/food/cuisine/mozambican", htmlLst)


# In[14]:


# drop links that are not recipes
lst = []
for i in htmlLst:
    if "/food/recipes/" in i:
        lst.append("https://www.sbs.com.au/"+i)
        
htmlLst = lst


# In[15]:


# the number of recipes we have in total
len(htmlLst)


# In[17]:


# 3. go through all recipe htmls and scrape the data we want

Mozambiquedata = {
    "Name of the recipe":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def MozambiqueSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'at_check=true; _ga=GA1.3.1792221838.1650768218; AMCVS_5BD3248D541C319B0A4C98C6@AdobeOrg=1; _gcl_au=1.1.320362789.1650768218; _fbp=fb.2.1650768218267.588341819; s_cc=true; _cb=I9DZ9DrFxUvbmcXB; aam_uuid=87393916760910473647345340690129581144; __gads=ID=678a9af5e086b422:T=1650768219:S=ALNI_MYPMFwHue1qXff2-FuUGWqelECiog; s_sq=[[B]]; _gid=GA1.3.972293906.1652121010; AMCV_5BD3248D541C319B0A4C98C6@AdobeOrg=1585540135|MCIDTS|19122|MCMID|87376036454763747047342378282379895084|MCAAMLH-1652796343|7|MCAAMB-1652796343|RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y|MCCIDH|-2041533806|MCOPTOUT-1652198743s|NONE|MCAID|2FD5C74F0515A8D2-40000649925735BE|vVersion|4.4.0; _cb_svref=https://www.google.com/; __gpi=UID=000004b0a9696f8c:T=1650768219:RT=1652191543:S=ALNI_MalCMp0Uup4Aclp2pbeJBzdhKBELw; mbox=PC#585c5d80c96040efbf0a02a9179c040a.34_0#1714013019|session#4a6a646903934956ab3316e27daf14e7#1652193441; _chartbeat2=.1636304326101.1652191581098.0000000011000011.iY7HqDjIz0ks2_oXBbSef5D5I_lP.2; s_nr=1652191581334-Repeat',
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
    content = {
        'name':'',
        'prepTime':'',
        'cookTime':'',
        'recipeIngredient':'',
        'recipeInstructions':'',
        'recipeYield':'',
        'recipeCategory':''
    }
    
    content['name'] = sel.xpath('//meta[@itemprop="name"]/@content').get()
    content['prepTime'] = sel.xpath('//meta[@itemprop="prepTime"]/@content').get()
    content['cookTime'] = sel.xpath('//meta[@itemprop="cookTime"]/@content').get()
    content['recipeYield'] = sel.xpath('//div[@itemprop="recipeYield"]/text()').get()
    content['recipeCategory'] = sel.xpath('//meta[@itemprop="recipeCategory"]/@content').get()
    
    
    lst = []
    length = len(sel.xpath('//div[@class="field field-name-field-ingredients field-type-text-long field-label-above cXenseParse"]/ul/li'))
    for i in range(length):
        try:
            lst.append([sel.xpath('//div[@class="field field-name-field-ingredients field-type-text-long field-label-above cXenseParse"]/ul/li/strong/text()')[i].get(),
                   sel.xpath('//div[@class="field field-name-field-ingredients field-type-text-long field-label-above cXenseParse"]/ul/li/text()')[i].get()])
        except:
            lst.append(['',
                   sel.xpath('//div[@class="field field-name-field-ingredients field-type-text-long field-label-above cXenseParse"]/ul/li/text()')[i].get()])
            
    
    content['recipeIngredient'] = lst
    
    lst = []
    for i in sel.xpath('//div[@itemprop = "recipeInstructions"]/p/text()'):
        lst.append(i.get())
    content['recipeInstructions'] = lst
    
    
    return content

def fillMozambiqueData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = MozambiqueSpider(html)
    dic['Name of the recipe'].append(content['name'])
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
        fillMozambiqueData(html,Mozambiquedata)
    except:
        time.sleep(5)

# convert data to dataframe
Mozambique = pd.DataFrame(Mozambiquedata)
print(Mozambique.shape)
Mozambique.head()


# In[18]:


Mozambique["Source"] = ["Web1" for i in range(len(Mozambique))]
Mozambique.head()


# In[19]:


# save dataset
Mozambique.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Mozambique.csv")


# In[ ]:




